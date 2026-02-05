@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo       InvestLens System Launcher
echo ==========================================

:: Function to check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b
)

:: 1. Backend Environment Strategy
:: Priority 1: Root .venv (Global Project Env)
:: Priority 2: investlens-kernel/venv (Service Specific Env)

set "PYTHON_CMD="
if exist ".venv\Scripts\activate.bat" (
    echo [ENV] Found root .venv. Using it.
    set "VENV_PATH=..\.venv"
    set "ACTIVATE_CMD=..\.venv\Scripts\activate"
) else (
    if exist "investlens-kernel\venv\Scripts\activate.bat" (
        echo [ENV] Found investlens-kernel\venv. Using it.
        set "VENV_PATH=venv"
        set "ACTIVATE_CMD=venv\Scripts\activate"
    ) else (
        echo [ENV] No virtual environment found.
        echo [SETUP] Creating local venv in investlens-kernel...
        cd investlens-kernel
        python -m venv venv
        set "VENV_PATH=venv"
        set "ACTIVATE_CMD=venv\Scripts\activate"
        
        echo [SETUP] Installing dependencies...
        cmd /c "venv\Scripts\activate && pip install -r requirements.txt"
        cd ..
        echo [SETUP] Done.
    )
)

:: 2. Check Frontend (InvestLens Web)
echo.
echo [2/2] Checking Frontend Environment...
if not exist "investlens-web\node_modules" (
    echo [SETUP] node_modules not found. Running npm install...
    cd investlens-web
    call npm install
    cd ..
) else (
    echo [OK] node_modules found.
)

:: 3. Launch Services
echo.
echo ==========================================
echo       Launching Services...
echo ==========================================
echo.

:: Launch Backend
echo Launching Backend with %ACTIVATE_CMD%...
start "InvestLens Kernel" cmd /k "cd investlens-kernel && call %ACTIVATE_CMD% && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Launch Frontend
start "InvestLens Web" cmd /k "cd investlens-web && npm run dev"

echo ------------------------------------------
echo Backend API: http://localhost:8000
echo Web App:     http://localhost:3000
echo ------------------------------------------
echo Services are running in separate windows.
echo Do not close them while using the app.
echo.
pause
