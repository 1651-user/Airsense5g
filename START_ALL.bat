@echo off
REM AirSense5g - Complete System Startup
REM This script starts all required services

echo ================================================================================
echo AIRSENSE5G - COMPLETE SYSTEM STARTUP
echo ================================================================================
echo.
echo This will start:
echo   1. Backend Server (Flask API)
echo   2. MQTT Pipeline (Data Collection)
echo.
echo Keep this window open to keep services running!
echo Press Ctrl+C to stop all services
echo.
echo ================================================================================
echo.

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo [INFO] Starting Backend Server...
echo.

REM Start backend server in a new window
start "AirSense Backend Server" cmd /k "cd /d %~dp0backend && python server.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

echo [INFO] Backend server started in new window
echo.
echo [INFO] Starting MQTT Pipeline...
echo.

REM Start MQTT pipeline in a new window  
start "AirSense MQTT Pipeline" cmd /k "cd /d %~dp0 && python mqtt_to_phi2.py"

echo.
echo ================================================================================
echo ALL SERVICES STARTED!
echo ================================================================================
echo.
echo Backend Server: http://localhost:5000
echo MQTT Pipeline: Running in background
echo.
echo Two new windows have opened:
echo   - Backend Server (Flask)
echo   - MQTT Pipeline (Data Collection)
echo.
echo Keep those windows open to keep services running!
echo.
echo To stop: Close the backend and MQTT pipeline windows
echo.
echo ================================================================================
echo.
echo You can now:
echo   1. Run your Flutter app: flutter run
echo   2. Access backend API: http://localhost:5000
echo   3. Chat with Phi-2 in your app
echo.
pause
