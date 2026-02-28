@echo off
title Installation Autobot
echo.
echo  ====================================
echo    Installation de Autobot
echo  ====================================
echo.

:: Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe.
    echo Telecharge Python sur https://www.python.org/downloads/
    echo Coche "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

echo [1/4] Creation de l'environnement virtuel...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERREUR] Impossible de creer l'environnement virtuel.
    pause
    exit /b 1
)

echo [2/4] Activation de l'environnement...
call venv\Scripts\activate.bat

echo [3/4] Installation des dependances...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [ERREUR] Impossible d'installer les dependances.
    pause
    exit /b 1
)

echo [4/4] Configuration...
if not exist .env (
    copy .env.example .env >nul
    echo.
    echo  ============================================
    echo    IMPORTANT : Configure ta cle API Anthropic
    echo  ============================================
    echo.
    echo  Ouvre le fichier .env et remplace la valeur de
    echo  ANTHROPIC_API_KEY par ta cle API.
    echo.
    echo  Pour obtenir une cle : https://console.anthropic.com/
    echo.
)

echo.
echo  ====================================
echo    Installation terminee !
echo  ====================================
echo.
echo  Pour lancer l'application :
echo    - Double-clique sur lancer.bat
echo    - Ou : venv\Scripts\python app.py
echo.
pause
