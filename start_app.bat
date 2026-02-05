@echo off
echo ==========================================
echo       Starting InvestLens System
echo ==========================================

:: 1. Start Backend (InvestLens Kernel)
echo [1/2] Launching Backend (FastAPI)...
start "InvestLens Kernel" cmd /k "cd investlens-kernel && call venv\Scripts\activate && python -m uvicorn main:app --reload --port 8000"

:: 2. Start Frontend (InvestLens Web)
echo [2/2] Launching Frontend (Next.js)...
start "InvestLens Web" cmd /k "cd investlens-web && npm run dev"

echo.
echo ==========================================
echo System is starting up!
echo ------------------------------------------
echo Backend API: http://localhost:8000
echo Web App:     http://localhost:3000
echo ==========================================
echo.
pause
