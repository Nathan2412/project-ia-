@echo off
echo 🚀 Démarrage de WhatToWatch Backend (Local)...
cd /d "c:\Users\berda\Documents\project-ia\project-ia-\backend"

echo 🌐 Serveur local: http://127.0.0.1:8000
echo 🌍 Serveur production: http://51.75.124.76/api/
echo 📝 Pour arrêter, appuyez sur Ctrl+C

"C:/Users/berda/Documents/project-ia/project-ia-/.venv/Scripts/python.exe" api.py
pause

echo.
echo 2. Démarrage de l'interface utilisateur (frontend)...
echo Attendez que l'installation des dépendances soit terminée...
echo.

cd /d %~dp0\frontend
call npm install
echo.
call npm run serve

echo.
echo Fin du script
