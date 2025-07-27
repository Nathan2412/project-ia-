@echo off
REM Script pour démarrer seulement le backend API

echo ===========================================
echo Démarrage du backend API seulement
echo ===========================================

echo.
echo Activation de l'environnement virtuel...
call venv\Scripts\activate

echo.
echo Démarrage de l'API Flask sur http://127.0.0.1:5000
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

python api.py

pause
