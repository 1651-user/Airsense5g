@echo off
echo ================================================================================
echo STARTING LIVE MQTT SYSTEM - ALL 5 SENSORS
echo ================================================================================
echo.
echo This system connects all 5 sensors directly via MQTT (no MongoDB needed)
echo Just like Sensor 3, all sensors now connect directly to the AI!
echo.

echo [1/2] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python server.py"
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting Multi-Sensor MQTT Client...
start "MQTT All Sensors" cmd /k "python mqtt_all_sensors_live.py"

echo.
echo ================================================================================
echo ALL SYSTEMS STARTED!
echo ================================================================================
echo.
echo Backend Server: http://localhost:5000
echo MQTT Clients: All 5 sensors connected directly
echo.
echo What's happening:
echo  - All 5 sensors connect to their MQTT brokers
echo  - Data is sent directly to AI backend (no MongoDB)
echo  - AI receives real-time updates from all sensors
echo  - You can ask: "What is the PM2.5 level of sensor 4?"
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
taskkill /FI "WINDOWTITLE eq Backend Server*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq MQTT All Sensors*" /T /F >nul 2>&1

echo.
echo All services stopped.
pause
