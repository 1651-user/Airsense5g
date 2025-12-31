# AirSense 5G - Streamlined Data Flow

**Last Updated:** 2025-12-31

---

## 📊 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 1: DATA ACQUISITION                      │
│                    MQTT → JSON → Excel                           │
└─────────────────────────────────────────────────────────────────┘

5 Air Quality Sensors (Sensor 1-5)
         ↓ MQTT Protocol
JSON Files (mqtt_data_sensor*.json)
         ↓ excel_integration_enhanced.py
Excel Files (output1.xlsx - output5.xlsx)
         ↓
Historical Data Storage with columns:
  - uplink_message.decoded_payload.pm2_5
  - uplink_message.decoded_payload.pm10
  - uplink_message.decoded_payload.co2
  - uplink_message.decoded_payload.tvoc
  - uplink_message.decoded_payload.temperature
  - uplink_message.decoded_payload.humidity
  - uplink_message.decoded_payload.pressure


┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: EXTRACT REQUIRED VALUES                     │
│                  Excel → Clean Data                              │
└─────────────────────────────────────────────────────────────────┘

live_ai_system_enhanced.py reads Excel files and extracts ONLY:
  ✓ PM2.5      (Particulate Matter 2.5)
  ✓ PM10       (Particulate Matter 10)
  ✓ CO2        (Carbon Dioxide)
  ✓ TVOC       (Total Volatile Organic Compounds)
  ✓ Temperature
  ✓ Humidity
  ✓ Pressure

❌ IGNORES: All other columns (battery, light_level, pir, etc.)

🔧 NaN Handling:
  - Reads entire Excel sheet
  - Searches last 20 rows for valid data
  - Uses most recent non-NaN values


┌─────────────────────────────────────────────────────────────────┐
│                STEP 3: GENERATE PREDICTIONS                      │
│                   ML Models → Predictions                        │
└─────────────────────────────────────────────────────────────────┘

Input: Current values (PM2.5, PM10, CO2, TVOC, Temp, Humidity, Pressure)
         ↓
ML Models (models/*.pkl):
  - pm2_5_model.pkl + scaler
  - pm10_model.pkl + scaler
  - co2_model.pkl + scaler
  - tvoc_model.pkl + scaler
  - temperature_model.pkl + scaler
  - humidity_model.pkl + scaler
  - pressure_model.pkl + scaler
         ↓
Output: Predicted values for next reading

AQI Calculation:
  - Calculated from PM2.5 using EPA formula
  - Categories: Good (0-50), Moderate (51-100), Unhealthy (101+)


┌─────────────────────────────────────────────────────────────────┐
│                  STEP 4: SEND TO BACKEND                         │
│              Predictions → Flask Server → Storage                │
└─────────────────────────────────────────────────────────────────┘

POST /api/predictions
{
  "sensor_id": 1,
  "sensor_name": "Sensor 1",
  "aqi": 85,
  "timestamp": "2025-12-31T11:52:00",
  "sensor_data": {
    "pm2_5": 35.2,
    "pm10": 52.8,
    "co2": 412,
    "tvoc": 125,
    "temperature": 24.5,
    "humidity": 65,
    "pressure": 1013
  },
  "predictions": {
    "PM2.5": {"current": 35.2, "predicted": 35.9},
    "PM10": {"current": 52.8, "predicted": 53.8},
    ...
  }
}

Backend stores data in memory for:
  - Dashboard display
  - AI Chatbot context
  - Forecast generation


┌─────────────────────────────────────────────────────────────────┐
│                  STEP 5: FLUTTER APP                             │
│                  User Interface Layer                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  1. DASHBOARD SCREEN                                          │
│     GET /api/sensors/all                                      │
│                                                               │
│     Displays:                                                 │
│     ┌─────────┬─────────┬─────────┬─────────┬─────────┐     │
│     │Sensor 1 │Sensor 2 │Sensor 3 │Sensor 4 │Sensor 5 │     │
│     │AQI: 85  │AQI: 72  │AQI: 91  │AQI: 68  │AQI: 78  │     │
│     │Moderate │Good     │Moderate │Good     │Moderate │     │
│     └─────────┴─────────┴─────────┴─────────┴─────────┘     │
│                                                               │
│     Each card shows:                                          │
│       • AQI with color coding                                 │
│       • PM2.5 level                                           │
│       • PM10 level                                            │
│       • CO2 level                                             │
│       • TVOC level                                            │
│       • Temperature, Humidity, Pressure                       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  2. FORECAST SCREEN                                           │
│     GET /api/forecast/[sensor_id]                             │
│                                                               │
│     Displays:                                                 │
│     • 24-Hour Predictions                                     │
│       - Hourly AQI forecast                                   │
│       - PM2.5 & PM10 trends                                   │
│       - Peak pollution times                                  │
│                                                               │
│     • Weekly Predictions                                      │
│       - Daily AQI forecast (7 days)                           │
│       - Weekend vs weekday patterns                           │
│       - Long-term trends                                      │
│                                                               │
│     Charts:                                                   │
│       - Line charts for trends                                │
│       - Bar charts for comparisons                            │
│       - Color-coded by AQI category                           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  3. CHATBOT SCREEN                                            │
│     POST /api/chat                                            │
│                                                               │
│     AI Assistant Features:                                    │
│     • Real-time sensor data access                            │
│     • Pollutant level queries                                 │
│     • Air quality analysis                                    │
│     • Health recommendations                                  │
│     • Prediction insights                                     │
│                                                               │
│     Example Queries:                                          │
│     User: "What are the current pollutant levels?"            │
│     AI: "Based on Sensor 3:                                   │
│          PM2.5: 35.2 µg/m³ (Moderate)                        │
│          PM10: 52.8 µg/m³                                     │
│          CO2: 412 ppm (Normal)                                │
│          TVOC: 125 ppb (Low)                                  │
│          Air quality is moderate..."                          │
│                                                               │
│     User: "Should I go for a run?"                            │
│     AI: "Current AQI is 85 (Moderate). Sensitive groups       │
│          should reduce prolonged outdoor exertion..."         │
│                                                               │
│     User: "What's the forecast for tomorrow?"                 │
│     AI: "Tomorrow's predicted AQI: 78 (Moderate).             │
│          Best time for outdoor activities: 6-8 AM..."         │
└──────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM REQUIREMENTS                           │
└─────────────────────────────────────────────────────────────────┘

Running Services:
  1. MQTT Broker (for sensor data)
  2. excel_integration_enhanced.py (JSON → Excel sync)
  3. live_ai_system_enhanced.py (Predictions every 30s)
  4. backend/server.py (Flask API on port 5000)
  5. LM Studio (Phi-2 AI model on port 1234)
  6. Flutter App (Mobile/Desktop)

Files Required:
  • Excel: output1.xlsx - output5.xlsx
  • JSON: mqtt_data_sensor*.json
  • Models: models/*.pkl (7 models + 7 scalers)
  • Config: .env files for each sensor


┌─────────────────────────────────────────────────────────────────┐
│                      QUICK START                                 │
└─────────────────────────────────────────────────────────────────┘

Option 1: One-Click Start
  > START_ALL.bat

Option 2: Manual Start
  Terminal 1: python backend/server.py
  Terminal 2: python excel_integration_enhanced.py
  Terminal 3: python live_ai_system_enhanced.py
  Terminal 4: flutter run (in lib/)

Verify System:
  > python check_system_status.py


┌─────────────────────────────────────────────────────────────────┐
│                    DATA UPDATE FREQUENCY                         │
└─────────────────────────────────────────────────────────────────┘

MQTT → JSON:        Real-time (as sensors transmit)
JSON → Excel:       Immediate (file watcher)
Excel → Predictions: Every 30 seconds
Predictions → Backend: Every 30 seconds
Backend → App:      On-demand (user refresh)
AI Context:         Real-time (with each chat message)


┌─────────────────────────────────────────────────────────────────┐
│                      KEY FEATURES                                │
└─────────────────────────────────────────────────────────────────┘

✅ Real-time data from 5 sensors
✅ Automatic NaN/missing value handling
✅ ML-based predictions for all pollutants
✅ AQI calculation using EPA standards
✅ 24-hour and weekly forecasts
✅ AI chatbot with sensor context
✅ Color-coded dashboard by air quality
✅ Health recommendations
✅ Historical data storage in Excel
✅ RESTful API for all data access


┌─────────────────────────────────────────────────────────────────┐
│                    ENDPOINTS SUMMARY                             │
└─────────────────────────────────────────────────────────────────┘

Backend API (http://localhost:5000):

GET  /health
     → Server health check

POST /api/predictions
     → Receive prediction data from Python scripts

GET  /api/predictions/latest
     → Get latest prediction for single sensor

GET  /api/sensors/all
     → Get current data from all 5 sensors

POST /api/chat
     → Chat with AI (includes sensor context)

GET  /api/test-llm
     → Test LM Studio connection

GET  /api/forecast/[sensor_id]?hours=24
     → Get hourly forecast (TO BE IMPLEMENTED)

GET  /api/forecast/[sensor_id]?days=7
     → Get daily forecast (TO BE IMPLEMENTED)
