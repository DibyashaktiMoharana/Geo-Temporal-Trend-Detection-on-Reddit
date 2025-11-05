@echo off
echo ================================
echo Reddit Trend Analysis Frontend
echo Setup Script
echo ================================
echo.

echo [1/3] Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Checking backend services...
echo Please ensure the following services are running:
echo   - Analysis Model API on http://localhost:5000
echo   - Data Scraper API on http://localhost:8000
echo.

echo [3/3] Starting development server...
echo The application will open at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev
