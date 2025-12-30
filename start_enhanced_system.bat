@echo off
echo ================================================================================
echo  STARTING ENHANCED AI SYSTEM - NaN Handling + Dashboard Updates
echo ================================================================================
echo.
echo This will start:
echo  1. Excel Integration (Appends new rows, preserves columns)
echo  2. Live AI System (NaN-aware predictions + Dashboard updates)
echo.
echo Press Ctrl+C in any window to stop
echo.
pause

echo.
echo [1/2] Starting Excel Integration...
start "Excel Integration" cmd /k "python excel_integration_enhanced.py"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Live AI System...
start "Live AI System" cmd /k "python live_ai_system_enhanced.py"

echo.
echo ================================================================================
echo  ALL SYSTEMS STARTED
echo ================================================================================
echo.
echo  Excel Integration: Monitors MQTT files, appends new rows
echo  Live AI System: Generates predictions, updates dashboard
echo.
echo Close this window or press any key to continue...
pause >nul
