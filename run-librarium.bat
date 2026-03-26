@echo off
cd /d "%~dp0"

echo Starting Librarium...
start "Librarium" python app.py

:: Wait a moment for Flask to start, then open the browser
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5000"
