@echo off
REM Script pour démarrer le système de recommandation de films (backend + frontend)

echo ===========================================
echo Démarrage du système de recommandation
echo ===========================================

echo.
echo 1. Démarrage de l'API REST (backend)...
start cmd /k "cd /d %~dp0 && python api.py"

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
