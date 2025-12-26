@echo off
echo ================================================================================
echo   Setup Auto-Start for MQTT Pipeline
echo ================================================================================
echo.
echo This will create a Windows Task Scheduler task to automatically start
echo the MQTT pipeline when your computer boots up.
echo.
echo This prevents data loss from Dec 24-25 from happening again!
echo.
pause

set SCRIPT_PATH=%~dp0mqtt_to_phi2.py
set PYTHON_PATH=python

echo.
echo Creating scheduled task...
echo.

schtasks /Create /TN "AirSense MQTT Pipeline" /TR "%PYTHON_PATH% %SCRIPT_PATH%" /SC ONSTART /RU SYSTEM /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ================================================================================
    echo   SUCCESS! Auto-start configured
    echo ================================================================================
    echo.
    echo The MQTT pipeline will now start automatically when Windows boots.
    echo.
    echo Task Details:
    echo   Name: AirSense MQTT Pipeline
    echo   Trigger: At system startup
    echo   Script: %SCRIPT_PATH%
    echo.
    echo To verify, open Task Scheduler and look for "AirSense MQTT Pipeline"
    echo.
    echo To disable auto-start:
    echo   schtasks /Delete /TN "AirSense MQTT Pipeline" /F
    echo.
) else (
    echo.
    echo ================================================================================
    echo   ERROR: Failed to create scheduled task
    echo ================================================================================
    echo.
    echo You may need to run this script as Administrator.
    echo Right-click this file and select "Run as administrator"
    echo.
)

pause
