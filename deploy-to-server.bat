@echo off
echo ====================================
echo    DEPLOIEMENT SUR LE SERVEUR
echo ====================================

echo.
echo 1. Ajout des fichiers modifies...
git add .

echo.
echo 2. Creation du commit...
set /p commit_msg="Message du commit (ou Entree pour message auto): "
if "%commit_msg%"=="" (
    set commit_msg=Update: Deploy latest changes
)
git commit -m "%commit_msg%"

echo.
echo 3. Push vers GitHub...
git push origin main

echo.
echo 4. Connexion au serveur et mise a jour...
echo Executing remote commands on server...

ssh ubuntu@51.75.124.76 "cd ~/project-ia- && git pull origin main && sudo systemctl restart whattowatch-backend.service && echo 'Deployment completed successfully!'"

echo.
echo ====================================
echo    DEPLOIEMENT TERMINE !
echo ====================================
pause
