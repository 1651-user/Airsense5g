@echo off
REM Air Quality Prediction Engine - Single Run
REM This script runs the prediction engine once

echo ========================================
echo Air Quality Prediction Engine
echo Single Prediction Mode
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
echo Running prediction...
echo.

REM Run prediction script once
python predict_and_send.py

REM Deactivate virtual environment
deactivate

echo.
echo Done!
pause
