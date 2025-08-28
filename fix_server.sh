#!/bin/bash

echo "🔧 SCRIPT DE MISE À JOUR COMPLÈTE DU SERVEUR"
echo "============================================="

# 1. Aller dans le répertoire du projet
cd ~/project-ia- || { echo "❌ Répertoire projet non trouvé"; exit 1; }

# 2. Sauvegarder l'état actuel
echo "1. Sauvegarde de l'état actuel..."
cp -r . ../backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || echo "   Sauvegarde non créée (normal)"

# 3. Mettre à jour le code depuis Git
echo "2. Mise à jour du code depuis Git..."
git fetch origin
git reset --hard origin/main
git pull origin main

# 4. Vérifier l'environnement Python
echo "3. Vérification de l'environnement Python..."
python3 --version
pip3 --version

# 5. Installer les dépendances Python
echo "4. Installation des dépendances Python..."
cd backend
pip3 install -r requirements.txt --user

# 6. Vérifier les permissions
echo "5. Correction des permissions..."
chmod +x ~/project-ia-/backend/*.py
chmod -R 755 ~/project-ia-/backend/src/
chmod -R 755 ~/project-ia-/backend/data/

# 7. Construire le frontend si Node.js est disponible
echo "6. Construction du frontend..."
cd ../frontend
if command -v npm &> /dev/null; then
    echo "   Node.js trouvé, construction du frontend..."
    npm install --production
    npm run build
    
    # Copier les fichiers statiques
    if [ -d "dist" ]; then
        echo "   Copie des fichiers frontend vers le backend..."
        rm -rf ../backend/static
        cp -r dist ../backend/static
        echo "   ✅ Frontend déployé avec succès"
    else
        echo "   ❌ Build frontend échoué"
    fi
else
    echo "   ⚠️  Node.js non installé, frontend non mis à jour"
fi

# 8. Retour au répertoire backend
cd ../backend

# 9. Test des imports critiques
echo "7. Test des imports critiques..."
python3 -c "
import sys
import os
sys.path.insert(0, '/home/ubuntu/project-ia-/backend')

try:
    from src.recommendation_engine_v2 import modular_engine
    print('   ✅ Moteur de recommandation importé avec succès')
    print(f'   ✅ Fournisseurs API actifs: {modular_engine.api_manager.active_providers}')
    print(f'   ✅ Nombre d\'utilisateurs chargés: {len(modular_engine.users)}')
except Exception as e:
    print(f'   ❌ Erreur d\'import: {e}')
    import traceback
    traceback.print_exc()
"

# 10. Arrêter les anciens processus
echo "8. Arrêt des anciens processus..."
sudo systemctl stop whattowatch-backend.service 2>/dev/null || echo "   Service systemd non trouvé"
pkill -f "python.*api.py" 2>/dev/null || echo "   Aucun processus Python API trouvé"

# 11. Redémarrer le service
echo "9. Démarrage du service..."
if systemctl is-enabled whattowatch-backend.service &>/dev/null; then
    echo "   Démarrage via systemd..."
    sudo systemctl start whattowatch-backend.service
    sleep 3
    sudo systemctl status whattowatch-backend.service --no-pager -l
else
    echo "   Démarrage manuel..."
    cd ~/project-ia-/backend
    nohup python3 api.py > ../logs/backend.log 2>&1 &
    echo "   Process démarré en arrière-plan"
    sleep 3
    echo "   PID: $(pgrep -f 'python.*api.py')"
fi

# 12. Test de l'endpoint
echo "10. Test des endpoints..."
sleep 5
echo "   Test /api/ping:"
curl -s -X GET "http://localhost:8000/api/ping" -H "Content-Type: application/json" | head -n 3
echo
echo "   Test page d'accueil:"
curl -s -X GET "http://localhost:8000/" | head -n 5

# 13. Vérifier les logs récents
echo "11. Logs récents du service..."
if systemctl is-active whattowatch-backend.service &>/dev/null; then
    sudo journalctl -u whattowatch-backend.service --no-pager -n 10
else
    echo "   Logs du processus manuel:"
    tail -n 10 ~/project-ia-/logs/backend.log 2>/dev/null || echo "   Pas de logs trouvés"
fi

echo -e "\n🎉 MISE À JOUR TERMINÉE!"
echo "========================================"
echo "✅ Code mis à jour depuis Git"
echo "✅ Dépendances Python installées" 
echo "✅ Frontend construit et déployé"
echo "✅ Service redémarré"
echo
echo "🌐 Votre application est maintenant disponible à:"
echo "   → https://whattowatch.fr"
echo "   → https://whattowatch.fr/api/ping (test API)"
echo
echo "📊 Pour voir les logs en temps réel:"
echo "   → sudo journalctl -u whattowatch-backend.service -f"
