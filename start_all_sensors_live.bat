@echo off
echo ================================================================================
echo STARTING LIVE SYSTEM FOR ALL 5 SENSORS
echo ================================================================================
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python server.py"
timeout /t 3 /nobreak >nul

echo.
echo Starting Live Sensor Data Collection (All 5 Sensors)...
start "Live Sensors" cmd /k "python live_all_sensors.py"

echo.
echo ================================================================================
echo ALL SYSTEMS STARTED
echo ================================================================================
echo.
echo Backend Server: http://localhost:5000
echo Live Sensors: Updating every 30 seconds
echo.
echo You can now:
echo 1. Run your Flutter app to see live data from all 5 sensors
echo 2. Ask the AI questions like:
echo    - "What is the PM2.5 level of sensor 4?"
echo    - "Which sensor has the highest AQI?"
echo    - "Show me the pollutant levels for sensor 2"
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
taskkill /FI "WINDOWTITLE eq Backend Server*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Live Sensors*" /T /F >nul 2>&1

echo.
echo All services stopped.
pause
