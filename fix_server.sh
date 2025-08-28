#!/bin/bash

echo "🔧 SCRIPT DE CORRECTION DES RECOMMANDATIONS"
echo "==========================================="

# 1. Vérifier l'environnement Python
echo "1. Vérification de l'environnement Python..."
python3 --version
pip3 --version

# 2. Installer les dépendances manquantes
echo "2. Installation des dépendances..."
cd ~/project-ia-/backend
pip3 install -r requirements.txt

# 3. Vérifier les permissions
echo "3. Vérification des permissions..."
chmod +x ~/project-ia-/backend/*.py
chmod -R 755 ~/project-ia-/backend/src/
chmod -R 755 ~/project-ia-/backend/data/

# 4. Tester les imports Python
echo "4. Test des imports critiques..."
python3 -c "
import sys
import os
sys.path.insert(0, '/home/ubuntu/project-ia-/backend')

try:
    from src.recommendation_engine_v2 import modular_engine
    print('✅ Moteur de recommandation importé avec succès')
    print(f'✅ Fournisseurs API actifs: {modular_engine.api_manager.active_providers}')
    print(f'✅ Nombre d\'utilisateurs chargés: {len(modular_engine.users)}')
except Exception as e:
    print(f'❌ Erreur: {e}')
    import traceback
    traceback.print_exc()
"

# 5. Vérifier les logs du service
echo "5. Vérification des logs du service..."
sudo journalctl -u whattowatch-backend.service --no-pager -n 20

# 6. Redémarrer le service
echo "6. Redémarrage du service..."
sudo systemctl stop whattowatch-backend.service
sleep 2
sudo systemctl start whattowatch-backend.service
sudo systemctl status whattowatch-backend.service

# 7. Test de l'endpoint
echo "7. Test de l'endpoint des recommandations..."
sleep 3
curl -X GET "http://localhost:8000/api/ping" -H "Content-Type: application/json"

echo -e "\n\n🎉 CORRECTION TERMINÉE!"
echo "Vérifiez maintenant l'application web."
