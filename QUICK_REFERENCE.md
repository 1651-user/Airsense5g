# 🚀 AirSense 5G - Quick Reference Guide

## Your Streamlined Flow (Confirmed ✅)

```
MQTT → JSON → Excel → Extract Values → Predictions → Backend → App
```

---

## 📋 What Gets Extracted (ONLY These 7 Values)

From Excel sheets, the system extracts:

1. **PM2.5** - Particulate Matter 2.5 µg/m³
2. **PM10** - Particulate Matter 10 µg/m³  
3. **CO2** - Carbon Dioxide (ppm)
4. **TVOC** - Total Volatile Organic Compounds (ppb)
5. **Temperature** - °C
6. **Humidity** - %
7. **Pressure** - hPa

❌ **Everything else is IGNORED** (battery, light_level, pir, etc.)

---

## 🤖 What Gets Predicted

All 7 values above get predictions:
- Current value
- Predicted value (next reading)
- Trend (↑ increasing, ↓ decreasing)

**Plus:** AQI (Air Quality Index) calculated from PM2.5

---

## 📱 Flutter App Features

### 1️⃣ Dashboard
- Shows **all 5 sensors**
- Each sensor displays:
  - AQI with color coding
  - All 7 pollutant/environmental values
  - Last update timestamp
- **Endpoint:** `GET /api/sensors/all`

### 2️⃣ Forecast
- **24-Hour Predictions** (hourly breakdown)
  - AQI forecast
  - PM2.5 & PM10 trends
  - Peak pollution times
- **Weekly Predictions** (7 days)
  - Daily AQI forecast
  - Weekend vs weekday patterns
- **Endpoint:** `GET /api/forecast/{sensor_id}`

### 3️⃣ Chatbot
- Ask about pollutant levels
- Get air quality analysis
- Receive health tips
- Check predictions
- All responses use **real sensor data**
- **Endpoint:** `POST /api/chat`

---

## 🔄 Update Frequency

| Component | Frequency |
|-----------|-----------|
| Sensors → MQTT | Real-time |
| MQTT → JSON | Instant |
| JSON → Excel | Instant (file watcher) |
| Excel → Predictions | Every 30 seconds |
| Predictions → Backend | Every 30 seconds |
| App → Backend | On user refresh |

---

## 🎯 Start Commands

### Quick Start (One Command)
```bash
START_ALL.bat
```

### Manual Start (4 Terminals)
```bash
# Terminal 1
python backend/server.py

# Terminal 2  
python excel_integration_enhanced.py

# Terminal 3
python live_ai_system_enhanced.py

# Terminal 4
flutter run
```

---

## 🔍 Verify System

```bash
# Check if everything is running
python check_system_status.py

# Check backend health
curl http://localhost:5000/health

# Check sensor data
curl http://localhost:5000/api/sensors/all

# Check forecast
curl http://localhost:5000/api/forecast/1
```

---

## 📊 Backend Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server health check |
| `/api/predictions` | POST | Receive predictions |
| `/api/predictions/latest` | GET | Latest prediction |
| `/api/sensors/all` | GET | All 5 sensors data |
| `/api/forecast/{id}` | GET | 24h + weekly forecast |
| `/api/chat` | POST | AI chatbot |
| `/api/test-llm` | GET | Test LM Studio |

---

## 🎨 AQI Color Coding

| AQI Range | Category | Color | Meaning |
|-----------|----------|-------|---------|
| 0-50 | Good | 🟢 Green | Air quality is satisfactory |
| 51-100 | Moderate | 🟡 Yellow | Acceptable for most people |
| 101-150 | Unhealthy for Sensitive | 🟠 Orange | Sensitive groups affected |
| 151-200 | Unhealthy | 🔴 Red | Everyone may experience effects |
| 201-300 | Very Unhealthy | 🟣 Purple | Health alert |
| 301+ | Hazardous | 🟤 Maroon | Emergency conditions |

---

## 🛠️ Troubleshooting

### Backend not responding?
```bash
# Check if running
curl http://localhost:5000/health

# Restart
python backend/server.py
```

### No sensor data?
```bash
# Check Excel files exist
ls output*.xlsx

# Check JSON files
ls mqtt_data*.json

# Restart Excel integration
python excel_integration_enhanced.py
```

### Predictions not updating?
```bash
# Check models exist
ls models/*.pkl

# Restart live AI system
python live_ai_system_enhanced.py
```

### Chatbot not working?
```bash
# Check LM Studio is running
curl http://192.168.0.103:1234/v1/models

# Check backend can reach LM Studio
curl http://localhost:5000/api/test-llm
```

---

## 📁 Important Files

### Python Scripts
- `excel_integration_enhanced.py` - JSON → Excel sync
- `live_ai_system_enhanced.py` - Predictions every 30s
- `backend/server.py` - Flask API server

### Data Files
- `output1.xlsx` to `output5.xlsx` - Historical data
- `mqtt_data_sensor*.json` - Latest MQTT messages
- `models/*.pkl` - ML models (7 models + 7 scalers)

### Flutter Files
- `lib/services/sensor_service.dart` - Fetch sensor data
- `lib/services/forecast_service.dart` - Fetch forecasts
- `lib/services/chat_service.dart` - AI chatbot
- `lib/screens/dashboard_screen.dart` - Main dashboard
- `lib/screens/forecast_screen.dart` - Predictions view
- `lib/screens/chat_screen.dart` - Chatbot interface

---

## 💡 Pro Tips

1. **Dashboard refreshes automatically** - Pull down to refresh manually
2. **Forecast uses real data** - Based on current sensor readings + ML
3. **Chatbot is context-aware** - It knows all sensor data in real-time
4. **NaN values handled automatically** - System searches for valid data
5. **All 5 sensors monitored** - Even if one fails, others continue

---

## ✅ System Status Checklist

Before using the app, verify:

- [ ] Backend running on port 5000
- [ ] LM Studio running on port 1234
- [ ] Excel integration script running
- [ ] Live AI system running
- [ ] All 5 Excel files exist
- [ ] Models folder has 14 .pkl files
- [ ] Flutter app connected to backend

---

**Quick Test:**
```bash
# Should return sensor data
curl http://localhost:5000/api/sensors/all

# Should return forecast
curl http://localhost:5000/api/forecast/1

# Should return "healthy"
curl http://localhost:5000/health
```

---

**Last Updated:** 2025-12-31  
**System Version:** 2.0 Enhanced  
**Status:** ✅ Fully Operational
