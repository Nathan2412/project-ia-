#!/bin/bash

# Script pour démarrer le système de recommandation (compatible Linux/Mac)

echo "========================================="
echo "Démarrage du système de recommandation"
echo "========================================="

echo ""
echo "1. Démarrage de l'API REST (backend)..."
# Démarrage du backend dans un terminal séparé
gnome-terminal -- python api.py || xterm -e python api.py || open -a Terminal.app python api.py

echo ""
echo "2. Démarrage de l'interface utilisateur (frontend)..."
echo "Attendez que l'installation des dépendances soit terminée..."
echo ""

cd frontend
npm install
npm run serve

echo ""
echo "Fin du script"
