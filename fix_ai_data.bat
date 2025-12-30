@echo off
echo ================================================================================
echo FIXING AI DATA - Complete Automation
echo ================================================================================
echo.
echo This will:
echo  1. Kill any old backend servers
echo  2. Start the backend fresh
echo  3. Load predictions from Excel for all 5 sensors
echo  4. Verify data reached the backend
echo.
pause

echo.
echo [1/4] Killing old backend processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq C:\WINDOWS\system32\cmd.exe - python*" 2>nul
timeout /t 2 >nul

echo.
echo [2/4] Starting backend server...
start "Backend Server" cmd /k "cd backend && python server.py"
timeout /t 5 >nul

echo.
echo [3/4] Loading predictions for all sensors...
python start_with_predictions.py

echo.
echo [4/4] Testing if AI has data...
curl -s http://localhost:5000/api/test-llm

echo.
echo ================================================================================
echo DONE! Now test your Flutter app:
echo  - Ask: "What is the PM2.5 level of sensor 4?"
echo  - Expected: "Sensor 4 has PM2.5 of 103.0..."
echo ================================================================================
pause
