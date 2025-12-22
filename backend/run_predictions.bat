@echo off
REM Air Quality Prediction Engine - Continuous Mode
REM This script runs the prediction engine continuously

echo ========================================
echo Air Quality Prediction Engine
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo Starting prediction engine in continuous mode...
echo Press Ctrl+C to stop
echo.

REM Run prediction script in continuous mode
python predict_and_send.py --continuous

REM Deactivate virtual environment
deactivate

echo.
echo Prediction engine stopped.
pause
