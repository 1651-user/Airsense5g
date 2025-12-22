@echo off
REM MQTT to Phi-2 Pipeline
REM This script runs the integrated pipeline

echo ================================================================================
echo MQTT TO PHI-2 PIPELINE
echo ================================================================================
echo.
echo This pipeline will:
echo   1. Connect to MQTT broker (am3 sensor)
echo   2. Save data to JSON file (mqtt_data.json)
echo   3. Generate predictions using trained models
echo   4. Send predictions to backend server
echo   5. Phi-2 receives predictions as context
echo.
echo ================================================================================
echo.

REM Check if models exist
if not exist "models\pm25_model.pkl" (
    echo ERROR: Models not found!
    echo Please train models first: python train_quick.py
    echo.
    pause
    exit /b 1
)

echo [OK] Models found
echo.

REM Check if backend is running
echo [INFO] Make sure backend server is running:
echo        cd backend
echo        python server.py
echo.
echo [INFO] Make sure LM Studio is running with Phi-2
echo.

pause

echo.
echo Starting pipeline...
echo Press Ctrl+C to stop
echo.

python mqtt_to_phi2.py

pause
