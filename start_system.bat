@echo off
echo ================================================================================
echo Starting Complete AI System
echo ================================================================================
echo.
echo [SETUP] Creating .env file if needed...
if not exist .env (
    copy env_template.txt .env
    echo   Created .env file
) else (
    echo   .env file already exists
)
echo.
echo [1/2] Starting Backend Server (connects to Phi-2)...
echo.
start "Backend Server" cmd /k "cd backend && python server.py"
timeout /t 3 /nobreak >nul

echo [2/2] Starting MQTT to Phi-2 Pipeline...
echo.
start "MQTT Pipeline" cmd /k "python mqtt_to_phi2.py"

echo.
echo ================================================================================
echo System Started!
echo ================================================================================
echo.
echo Two windows opened:
echo   1. Backend Server (localhost:5000) - Connects to Phi-2
echo   2. MQTT Pipeline - Receives sensor data and sends predictions
echo.
echo Backend URL: http://localhost:5000
echo Phi-2 URL: http://192.168.0.103:1234
echo.
echo Press any key to close this window...
pause >nul
