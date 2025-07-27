@echo off
REM Script pour construire le frontend pour la production

echo ===========================================
echo Construction du frontend pour PRODUCTION
echo ===========================================

cd /d %~dp0

echo.
echo Installation des dépendances...
call npm install

echo.
echo Construction des fichiers de production...
call npm run build

echo.
echo ✅ Construction terminée !
echo Les fichiers sont dans le dossier 'dist/'
echo Vous pouvez maintenant déployer le contenu du dossier 'dist/' sur votre serveur web.
echo.

pause
