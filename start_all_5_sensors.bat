@echo off
echo ================================================================================
echo STARTING ALL 5 SENSORS - MQTT TO AI PIPELINE
echo ================================================================================
echo.
echo This system runs all 5 sensors exactly like Sensor 3
echo Each sensor:
echo  - Connects to its MQTT broker
echo  - Generates ML predictions
echo  - Sends data to AI backend
echo.

echo [1/8] Loading Excel data and generating predictions for all sensors...
python start_with_predictions.py
echo.
echo Press any key to continue to MQTT connections...
pause >nul

echo.
echo [2/8] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python server.py"
timeout /t 3 /nobreak >nul

echo.
echo [2/7] Starting Excel Sync (saves MQTT data to Excel)...
start "Excel Sync" cmd /k "python simple_excel_sync.py"
timeout /t 2 /nobreak >nul

echo.
echo [3/7] Starting Sensor 1...
start "Sensor 1" cmd /k "python mqtt_to_ai_sensor1.py"
timeout /t 2 /nobreak >nul

echo.
echo [4/7] Starting Sensor 2...
start "Sensor 2" cmd /k "python mqtt_to_ai_sensor2.py"
timeout /t 2 /nobreak >nul

echo.
echo [5/7] Starting Sensor 3 (existing)...
start "Sensor 3" cmd /k "python mqtt_to_phi2.py"
timeout /t 2 /nobreak >nul

echo.
echo [6/7] Starting Sensor 4...
start "Sensor 4" cmd /k "python mqtt_to_ai_sensor4.py"
timeout /t 2 /nobreak >nul

echo.
echo [7/7] Starting Sensor 5...
start "Sensor 5" cmd /k "python mqtt_to_ai_sensor5.py"

echo.
echo ================================================================================
echo ALL 5 SENSORS STARTED!
echo ================================================================================
echo.
echo Backend Server: http://localhost:5000
echo.
echo Sensor Windows:
echo  - Sensor 1: MQTT -^> JSON -^> Predictions -^> AI
echo  - Sensor 2: MQTT -^> JSON -^> Predictions -^> AI
echo  - Sensor 3: MQTT -^> JSON -^> Predictions -^> AI (existing)
echo  - Sensor 4: MQTT -^> JSON -^> Predictions -^> AI
echo  - Sensor 5: MQTT -^> JSON -^> Predictions -^> AI
echo.
echo AI can now answer questions about ALL sensors!
echo Examples:
echo  - "What is the PM2.5 level of sensor 4?"
echo  - "Which sensor has the highest AQI?"
echo  - "Show me predictions for sensor 2"
echo.
echo Press any key to stop all services...
pause >nul

echo.
echo Stopping all services...
taskkill /FI "WINDOWTITLE eq Backend Server*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Sensor 1*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Sensor 2*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Sensor 3*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Sensor 4*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Sensor 5*" /T /F >nul 2>&1

echo.
echo All services stopped.
pause
