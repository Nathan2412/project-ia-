@echo off
REM Script pour démarrer seulement le frontend Vue.js

echo ===========================================
echo Démarrage du frontend Vue.js seulement
echo ===========================================

cd /d %~dp0

echo.
echo Installation/mise à jour des dépendances...
call npm install

echo.
echo Démarrage du serveur de développement Vue.js
echo Généralement disponible sur http://localhost:8080
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

call npm run serve

pause
