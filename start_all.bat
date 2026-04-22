@echo off
REM Lance le backend et le frontend dans deux fenetres separees

start "WhatToWatch Backend" cmd /k "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "WhatToWatch Frontend" cmd /k "%~dp0start_frontend.bat"

echo.
echo Backend : http://127.0.0.1:5000
echo Frontend: http://localhost:8080
echo.
echo Les deux serveurs ont ete lances dans des fenetres separees.
