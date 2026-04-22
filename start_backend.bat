@echo off
REM Script de demarrage du backend Flask en local

cd /d "%~dp0backend"

REM Detecter Python (preferer 'py' sous Windows, fallback 'python')
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    set PYTHON=py
) else (
    set PYTHON=python
)

REM Activer l'environnement virtuel s'il existe, sinon le creer
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [INFO] Creation de l'environnement virtuel Python...
    %PYTHON% -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer le venv. Python est-il installe ?
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    echo [INFO] Installation des dependances...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERREUR] Installation des dependances echouee.
        pause
        exit /b 1
    )
)

set FLASK_ENV=development
set PORT=5000

echo.
echo ===============================================
echo   Backend WhatToWatch - http://127.0.0.1:5000
echo ===============================================
echo.

python api.py
pause
