@echo off
REM Start Backend Server with Debug Logging

echo Starting AirSense Backend Server...
echo.
echo Backend will run at: http://localhost:5000
echo.
echo Keep this window open!
echo Press Ctrl+C to stop
echo.

cd /d %~dp0
python server.py

pause
