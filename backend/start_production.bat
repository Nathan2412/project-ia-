@echo off
REM Script pour démarrer le backend en mode production avec Gunicorn

echo ===========================================
echo Démarrage du backend en mode PRODUCTION
echo ===========================================

echo.
echo Activation de l'environnement virtuel...
call venv\Scripts\activate

echo.
echo Installation de Gunicorn si nécessaire...
pip install gunicorn

echo.
echo Démarrage du serveur Gunicorn sur port 5000
echo API disponible sur http://0.0.0.0:5000
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

gunicorn --bind 0.0.0.0:5000 --workers 4 api:app

pause
