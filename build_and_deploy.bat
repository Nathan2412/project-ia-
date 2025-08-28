@echo off
echo ====================================
echo    BUILD ET DEPLOIEMENT FRONTEND
echo ====================================

cd frontend

echo.
echo 1. Installation des dependances...
call npm install

echo.
echo 2. Build de production...
call npm run build

echo.
echo 3. Preparation du dossier de production...
if exist ..\backend\static rmdir /s /q ..\backend\static
mkdir ..\backend\static
xcopy /s /e /y dist\* ..\backend\static\

echo.
echo 4. Build termine !
echo Les fichiers sont prets dans backend\static\

echo.
echo 5. Deploiement sur le serveur...
cd ..
call deploy-to-server.bat

pause
