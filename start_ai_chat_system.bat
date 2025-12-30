@echo off
echo ================================================================================
echo   AirSense 5G - Complete System Startup
echo ================================================================================
echo.
echo This will start all required services for AI chat with live data:
echo   1. Backend Server (Flask)
echo   2. MQTT Pipeline (Data collection and predictions)
echo.
echo Make sure LM Studio is running with a model loaded!
echo.
pause

echo.
echo [1/2] Starting Backend Server...
echo.
start "AirSense Backend" cmd /k "cd /d %~dp0 && python backend/server.py"
timeout /t 3 /nobreak > nul

echo.
echo [2/2] Starting MQTT Pipeline...
echo.
start "AirSense MQTT Pipeline" cmd /k "cd /d %~dp0 && python mqtt_to_phi2.py"
timeout /t 2 /nobreak > nul

echo.
echo ================================================================================
echo   All Services Started!
echo ================================================================================
echo.
echo Services running in separate windows:
echo   - Backend Server (http://localhost:5000)
echo   - MQTT Pipeline (collecting data and generating predictions)
echo.
echo Next steps:
echo   1. Ensure LM Studio is running (http://192.168.0.103:1234)
echo   2. Wait for MQTT data to be received (check MQTT Pipeline window)
echo   3. Run the Flutter app and open the Chat screen
echo   4. Ask: "Show the pollutant levels"
echo.
echo To test the system, run: python test_data_flow.py
echo.
pause
