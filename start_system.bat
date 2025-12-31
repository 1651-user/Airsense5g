@echo off
REM AirSense 5G - Complete System Startup (JSON-Based)
REM This script starts all required services

echo ================================================================================
echo  AIRSENSE 5G - SYSTEM STARTUP
echo ================================================================================
echo.
echo This will start:
echo   1. Backend Server (Flask API on port 5000)
echo   2. Send initial sensor data to backend
echo   3. Live monitoring system (updates every 30 seconds)
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

echo [1/3] Starting Backend Server...
echo.

REM Check if backend is already running
curl -s http://localhost:5000/health >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   Backend is already running!
) else (
    echo   Starting backend in new window...
    start "AirSense Backend" cmd /k "cd /d %~dp0 && python backend/server.py"
    timeout /t 3 /nobreak >nul
    echo   Backend started!
)

echo.
echo [2/3] Sending initial sensor data...
echo.

REM Send initial data from JSON files
python send_data_from_json.py

echo.
echo [3/3] Starting live monitoring system...
echo.
echo   This will:
echo   - Monitor JSON files for new readings
echo   - Sync to Excel automatically
echo   - Send updates to backend every 30 seconds
echo.

REM Start live monitoring in new window
start "AirSense Live Monitor" cmd /k "cd /d %~dp0 && python live_system_json_based.py"

timeout /t 2 /nobreak >nul

echo.
echo ================================================================================
echo  ALL SERVICES STARTED!
echo ================================================================================
echo.
echo Running Services:
echo   Backend API:    http://localhost:5000
echo   Live Monitor:   Running in separate window
echo.
echo Two windows are now open:
echo   1. Backend Server (Flask) - Keep this open!
echo   2. Live Monitor - Updates every 30 seconds
echo.
echo ================================================================================
echo.
echo Next Steps:
echo   1. Open your Flutter app
echo   2. Refresh the dashboard (pull down)
echo   3. You should see sensor data!
echo.
echo To stop: Close the Backend and Live Monitor windows
echo.
pause
