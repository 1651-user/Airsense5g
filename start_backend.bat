@echo off
echo ========================================
echo Starting AirSense Backend Server
echo ========================================
echo.
echo LM Studio should be running on port 1234
echo Backend will start on port 5000
echo.
cd /d "%~dp0backend"
python server.py
