@echo off
echo Point of Sale System - Demarrage...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Erreur: Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8 ou plus recent
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Run the POS system
echo Lancement du systeme de caisse...
python main.py

if errorlevel 1 (
    echo.
    echo Une erreur est survenue lors du lancement
    pause
)
