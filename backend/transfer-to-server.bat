@echo off
echo 🚀 Transfer des fichiers vers le serveur Ubuntu...
echo.

set SERVER=ubuntu@51.75.124.76
set REMOTE_PATH=/home/ubuntu/whattowatch/backend

echo 📁 Création du répertoire distant...
ssh %SERVER% "mkdir -p %REMOTE_PATH%"

echo.
echo 📤 Transfer des fichiers Python...
scp wsgi.py %SERVER%:%REMOTE_PATH%/
scp api.py %SERVER%:%REMOTE_PATH%/
scp models.py %SERVER%:%REMOTE_PATH%/
scp config.py %SERVER%:%REMOTE_PATH%/
scp requirements.txt %SERVER%:%REMOTE_PATH%/
scp gunicorn.conf.py %SERVER%:%REMOTE_PATH%/
scp deploy-ubuntu.sh %SERVER%:%REMOTE_PATH%/

echo.
echo 📁 Transfer des dossiers...
scp -r src %SERVER%:%REMOTE_PATH%/
scp -r data %SERVER%:%REMOTE_PATH%/

echo.
echo ✅ Transfer terminé!
echo.
echo 🔧 Pour déployer sur le serveur, exécutez:
echo ssh %SERVER% "cd %REMOTE_PATH% && chmod +x deploy-ubuntu.sh && sudo ./deploy-ubuntu.sh"
echo.
pause
