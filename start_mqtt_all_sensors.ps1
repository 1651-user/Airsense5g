# Start All 5 Sensors - MQTT Direct Connection
# PowerShell Script

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "STARTING LIVE MQTT SYSTEM - ALL 5 SENSORS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This system connects all 5 sensors directly via MQTT (no MongoDB needed)" -ForegroundColor Yellow
Write-Host "Just like Sensor 3, all sensors now connect directly to the AI!" -ForegroundColor Yellow
Write-Host ""

# Start Backend Server
Write-Host "[1/2] Starting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python server.py"
Start-Sleep -Seconds 3

# Start MQTT Client
Write-Host ""
Write-Host "[2/2] Starting Multi-Sensor MQTT Client..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python mqtt_all_sensors_live.py"

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "ALL SYSTEMS STARTED!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend Server: http://localhost:5000" -ForegroundColor White
Write-Host "MQTT Clients: All 5 sensors connected directly" -ForegroundColor White
Write-Host ""
Write-Host "What's happening:" -ForegroundColor Yellow
Write-Host " - All 5 sensors connect to their MQTT brokers" -ForegroundColor White
Write-Host " - Data is sent directly to AI backend (no MongoDB)" -ForegroundColor White
Write-Host " - AI receives real-time updates from all sensors" -ForegroundColor White
Write-Host ' - You can ask: "What is the PM2.5 level of sensor 4?"' -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the services" -ForegroundColor Yellow
