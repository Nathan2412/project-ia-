@echo off
REM Script de démarrage du frontend Vue.js en local

cd /d "%~dp0frontend"

if not exist node_modules (
    echo [INFO] Installation des dependances npm...
    call npm install
)

echo.
echo ===============================================
echo   Frontend WhatToWatch - http://localhost:8080
echo ===============================================
echo.

call npm run serve
