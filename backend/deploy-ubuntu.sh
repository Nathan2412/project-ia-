#!/bin/bash
# Script de déploiement pour Ubuntu Server

set -e  # Arrêter en cas d'erreur

echo "🚀 Déploiement de WhatToWatch Backend sur Ubuntu..."

# Variables
PROJECT_DIR="/home/ubuntu/whattowatch"
BACKEND_DIR="$PROJECT_DIR/backend"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="whattowatch-backend"

echo "📁 Répertoires:"
echo "   Project: $PROJECT_DIR"
echo "   Backend: $BACKEND_DIR"
echo "   Venv: $VENV_DIR"

# 1. Créer les répertoires
echo "📂 Création des répertoires..."
sudo -u ubuntu mkdir -p "$PROJECT_DIR" "$BACKEND_DIR"

# 2. Environnement virtuel
echo "🐍 Configuration de l'environnement Python..."
if [ ! -d "$VENV_DIR" ]; then
    sudo -u ubuntu python3 -m venv "$VENV_DIR"
fi

# 3. Installer les dépendances
echo "📦 Installation des dépendances..."
sudo -u ubuntu "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u ubuntu "$VENV_DIR/bin/pip" install \
    flask==3.0.0 \
    flask-cors==6.0.1 \
    flask-sqlalchemy==3.1.1 \
    PyJWT==2.8.0 \
    pymysql==1.1.0 \
    gunicorn==21.2.0

# 4. Copier les fichiers (à adapter selon vos besoins)
echo "📋 Les fichiers doivent être copiés manuellement dans $BACKEND_DIR"
echo "   Fichiers requis:"
echo "   - api.py"
echo "   - models.py" 
echo "   - wsgi.py"
echo "   - gunicorn.conf.py"
echo "   - src/ (dossier complet)"
echo "   - data/ (dossier complet)"

# 5. Configuration du service
echo "⚙️ Configuration du service systemd..."
sudo cp "$BACKEND_DIR/whattowatch-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

# 6. Démarrage du service
echo "🚀 Démarrage du service..."
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager

# 7. Configuration Nginx (optionnel)
echo "🌐 Pour configurer Nginx, ajoutez cette configuration:"
cat << 'EOF'

# Dans /etc/nginx/sites-available/whattowatch
server {
    listen 80;
    server_name 51.75.124.76;  # Ou votre domaine

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        # Configuration pour le frontend
        try_files $uri $uri/ /index.html;
    }
}
EOF

echo "✅ Déploiement terminé!"
echo "🔗 API disponible sur: http://51.75.124.76/api/"
echo "📊 Statut du service: sudo systemctl status $SERVICE_NAME"
