#!/bin/bash
# Script pour démarrer seulement le frontend Vue.js

echo "==========================================="
echo "Démarrage du frontend Vue.js seulement"
echo "==========================================="

echo
echo "Installation/mise à jour des dépendances..."
npm install

echo
echo "Démarrage du serveur de développement Vue.js"
echo "Généralement disponible sur http://localhost:8080"
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo

npm run serve
