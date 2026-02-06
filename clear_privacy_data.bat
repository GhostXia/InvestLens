@echo off
REM ========================================
REM InvestLens Privacy Data Cleanup Script
REM ========================================
REM 
REM This script will permanently delete:
REM - Backend data source configurations
REM - API keys and endpoints stored in backend
REM 
REM Note: Frontend localStorage data must be 
REM cleared manually through browser settings
REM or the Settings page in the application.
REM 
REM ========================================

echo.
echo ========================================
echo  InvestLens Privacy Data Cleanup
echo ========================================
echo.
echo WARNING: This will PERMANENTLY DELETE:
echo   - Backend data source configurations
echo   - API endpoint settings
echo.
echo Frontend data (API keys, settings) stored
echo in your browser must be cleared separately
echo through the Settings page or browser.
echo.
echo ========================================
echo.

choice /C YN /M "Do you want to continue"
if errorlevel 2 goto :cancelled
if errorlevel 1 goto :cleanup

:cleanup
echo.
echo Starting cleanup...
echo.

REM Check if config directory exists
if exist "investlens-kernel\config" (
    echo [1/2] Checking backend config directory...
    
    REM Delete sources.json if it exists
    if exist "investlens-kernel\config\sources.json" (
        del /F /Q "investlens-kernel\config\sources.json"
        echo   ✓ Deleted: config/sources.json
    ) else (
        echo   ℹ No sources.json found
    )
    
    REM Delete .env if it exists (optional - uncomment if needed)
    REM if exist "investlens-kernel\.env" (
    REM     del /F /Q "investlens-kernel\.env"
    REM     echo   ✓ Deleted: .env
    REM ) else (
    REM     echo   ℹ No .env found
    REM )
) else (
    echo [1/2] No backend config directory found
)

echo.
echo [2/2] Backend cleanup complete!
echo.
echo ========================================
echo  IMPORTANT: Next Steps
echo ========================================
echo.
echo To clear frontend data (API keys, settings):
echo   1. Option A: Use the "Clear All Privacy Data"
echo      button in the Settings page
echo   2. Option B: Clear browser localStorage:
echo      - Chrome: F12 ^> Application ^> Local Storage
echo      - Firefox: F12 ^> Storage ^> Local Storage
echo      - Edge: F12 ^> Application ^> Local Storage
echo.
echo ========================================
echo.

pause
goto :eof

:cancelled
echo.
echo Cleanup cancelled. No files were deleted.
echo.
pause
goto :eof
