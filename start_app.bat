@echo off
setlocal
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

:: 1. Check and Setup Backend (InvestLens Kernel)
echo.
echo [1/2] Checking Backend Environment...
cd investlens-kernel

if not exist "venv" (
    echo [SETUP] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    
    echo [SETUP] Installing dependencies...
    cmd /c "venv\Scripts\activate && pip install -r requirements.txt"
    
    echo [SETUP] Backend setup complete!
) else (
    echo [OK] Virtual environment found.
)
cd ..

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

:: Launch Backend in new window
start "InvestLens Kernel" cmd /k "cd investlens-kernel && call venv\Scripts\activate && python -m uvicorn main:app --reload --port 8000"

:: Launch Frontend in new window
start "InvestLens Web" cmd /k "cd investlens-web && npm run dev"

echo ------------------------------------------
echo Backend API: http://localhost:8000
echo Web App:     http://localhost:3000
echo ------------------------------------------
echo Services are running in separate windows.
echo Do not close them while using the app.
echo.
pause
