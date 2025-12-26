@echo off
echo ================================================================================
echo   AIRSENSE 5G - LIVE AI SYSTEM STARTUP
echo ================================================================================
echo.
echo This will start:
echo   1. Backend Server (Flask)
echo   2. Live AI System (Auto-updates every 30 seconds)
echo.
echo Press any key to start...
pause >nul

echo.
echo ================================================================================
echo Starting Backend Server...
echo ================================================================================
start "AirSense Backend" cmd /k "cd /d %~dp0 && python backend\server.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo ================================================================================
echo Starting Live AI System...
echo ================================================================================
start "AirSense Live AI" cmd /k "cd /d %~dp0 && python live_ai_system.py"

echo.
echo ================================================================================
echo   SYSTEM STARTED!
echo ================================================================================
echo.
echo Two windows have opened:
echo   1. Backend Server - Keep this running
echo   2. Live AI System - Auto-updates every 30 seconds
echo.
echo The Live AI System will:
echo   - Load all Excel data on startup
echo   - Generate predictions
echo   - Send to backend
echo   - Check for new MQTT data every 30 seconds
echo   - Auto-update predictions when new data arrives
echo.
echo To test:
echo   1. Open your Flutter app
echo   2. Go to Chat screen
echo   3. Ask: "Show the pollutant levels"
echo   4. See live data with predictions!
echo.
echo Press any key to close this window...
pause >nul
