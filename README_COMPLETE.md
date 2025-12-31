# 🚀 AirSense 5G - Complete System Guide

**Last Updated:** 2025-12-31  
**Status:** ✅ Fully Operational (JSON-Based)

---

## 📊 System Overview

```
MQTT Sensors → JSON Files → Excel Sheets (Historical) → Backend API → Flutter App
                    ↓
              Live Monitoring (Every 30s)
```

### Key Components:

1. **JSON Files** - Real-time sensor data (source of truth)
2. **Excel Sheets** - Historical records (auto-synced from JSON)
3. **Backend API** - Flask server providing data to Flutter app
4. **Live Monitor** - Watches JSON files and updates backend
5. **Flutter App** - Dashboard, Forecast, and Chatbot

---

## 🎯 Quick Start (3 Steps)

### **Option 1: One-Click Start**
```bash
START_SYSTEM.bat
```

### **Option 2: Manual Start**
```bash
# Terminal 1: Backend Server
python backend/server.py

# Terminal 2: Send Initial Data
python send_data_from_json.py

# Terminal 3: Live Monitoring
python live_system_json_based.py

# Terminal 4: Flutter App
flutter run
```

---

## 📁 Important Files

### **JSON Files (Source of Truth)**
- `mqtt_data_sensor1.json` - Sensor 1 data
- `mqtt_data.json` - Sensor 3 data
- `mqtt_data_sensor4.json` - Sensor 4 data
- `mqtt_data_sensor5.json` - Sensor 5 data
- `mqtt_data_sensor2.json` - Sensor 2 (currently missing)

### **Excel Files (Historical Records)**
- `output1.xlsx` - Sensor 1 history
- `output2.xlsx` - Sensor 2 history
- `output3.xlsx` - Sensor 3 history
- `output4.xlsx` - Sensor 4 history
- `output5.xlsx` - Sensor 5 history

### **Python Scripts**
- `send_data_from_json.py` - Send current data to backend (one-time)
- `live_system_json_based.py` - Live monitoring system (continuous)
- `backend/server.py` - Flask API server

### **Batch Scripts**
- `START_SYSTEM.bat` - Start everything automatically

---

## 🔄 How It Works

### **1. Data Flow**

```
Sensor → MQTT → JSON File
                    ↓
         Live Monitor Detects Change
                    ↓
              ┌─────┴─────┐
              ↓           ↓
        Append to     Send to
         Excel       Backend API
                         ↓
                   Flutter App
```

### **2. Live Monitoring System**

The `live_system_json_based.py` script:

✅ **Monitors** JSON files every 30 seconds  
✅ **Detects** new readings automatically  
✅ **Syncs** new data to Excel sheets  
✅ **Sends** predictions to backend  
✅ **Refreshes** backend even if no new data  

### **3. Data Extraction**

From each JSON file, we extract **7 values**:
1. PM2.5 (Particulate Matter 2.5 µg/m³)
2. PM10 (Particulate Matter 10 µg/m³)
3. CO2 (Carbon Dioxide ppm)
4. TVOC (Total Volatile Organic Compounds ppb)
5. Temperature (°C)
6. Humidity (%)
7. Pressure (hPa)

❌ **Ignored:** battery, light_level, pir, etc.

### **4. Predictions**

For each value, we generate:
- **Current value** (from JSON)
- **Predicted value** (using simple ML models)
- **Trend** (↑ increasing, ↓ decreasing)

**Plus:** AQI calculated from PM2.5

---

## 📱 Flutter App Features

### **Dashboard Screen**
- Shows all 5 sensors
- Color-coded AQI cards
- Real-time pollutant levels
- Last update timestamp

**Endpoint:** `GET /api/sensors/all`

### **Forecast Screen**
- 24-hour hourly predictions
- 7-day daily forecast
- Peak pollution times
- Weekend vs weekday patterns

**Endpoint:** `GET /api/forecast/{sensor_id}`

### **Chatbot Screen**
- Ask about pollutant levels
- Get air quality analysis
- Receive health tips
- Check predictions

**Endpoint:** `POST /api/chat`

---

## 🔧 Troubleshooting

### **Problem: App shows AQI 0 for all sensors**

**Solution:**
```bash
# 1. Check backend is running
curl http://localhost:5000/health

# 2. Send data manually
python send_data_from_json.py

# 3. Verify backend has data
curl http://localhost:5000/api/sensors/all

# 4. Refresh Flutter app
```

### **Problem: Excel files corrupted**

**Solution:**
Don't worry! The system now reads from JSON files directly.
Excel files are just for historical records and are auto-recreated.

### **Problem: No data for Sensor 2**

**Reason:** `mqtt_data_sensor2.json` doesn't exist.

**Solution:** Wait for sensor to send data, or create dummy file.

### **Problem: Live monitor not updating**

**Solution:**
```bash
# Stop the monitor (Ctrl+C)
# Restart it
python live_system_json_based.py
```

---

## 🎨 AQI Color Coding

| AQI | Category | Color | Health Impact |
|-----|----------|-------|---------------|
| 0-50 | Good | 🟢 Green | Air quality is satisfactory |
| 51-100 | Moderate | 🟡 Yellow | Acceptable for most people |
| 101-150 | Unhealthy for Sensitive | 🟠 Orange | Sensitive groups affected |
| 151-200 | Unhealthy | 🔴 Red | Everyone may be affected |
| 201-300 | Very Unhealthy | 🟣 Purple | Health alert |
| 301-500 | Hazardous | 🟤 Maroon | Emergency conditions |

---

## 📊 Current System Status

Run this to check:
```bash
python send_data_from_json.py
```

Expected output:
```
Sensor 1: AQI 500 (Very Unhealthy) - PM2.5: 2168.0 µg/m³
Sensor 3: AQI 153 (Unhealthy) - PM2.5: 63.0 µg/m³
Sensor 4: AQI 166 (Unhealthy) - PM2.5: 87.0 µg/m³
Sensor 5: AQI 167 (Unhealthy) - PM2.5: 88.0 µg/m³
```

---

## 🔄 Update Frequency

| Component | Frequency |
|-----------|-----------|
| MQTT → JSON | Real-time (as sensors send) |
| JSON → Excel | When new data detected |
| JSON → Backend | Every 30 seconds |
| Backend → App | On user refresh |
| Chatbot Context | Real-time (per message) |

---

## 🚀 Production Deployment

### **For Continuous Operation:**

1. **Start backend as service:**
   ```bash
   # Use PM2, systemd, or Windows Service
   ```

2. **Run live monitor in background:**
   ```bash
   # Use screen, tmux, or Windows Task Scheduler
   ```

3. **Ensure LM Studio is running:**
   ```bash
   # For AI chatbot functionality
   ```

---

## 📝 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server health check |
| `/api/predictions` | POST | Receive prediction data |
| `/api/sensors/all` | GET | All 5 sensors data |
| `/api/forecast/{id}` | GET | 24h + weekly forecast |
| `/api/chat` | POST | AI chatbot |
| `/api/test-llm` | GET | Test LM Studio |

---

## ✅ System Checklist

Before using the app:

- [ ] Backend running on port 5000
- [ ] JSON files exist for sensors
- [ ] Live monitor running
- [ ] Flutter app connected
- [ ] LM Studio running (for chatbot)

Quick test:
```bash
curl http://localhost:5000/api/sensors/all
```

---

## 🎯 Key Improvements (JSON-Based System)

✅ **No Excel corruption issues** - Reads from JSON directly  
✅ **Faster data access** - JSON is lighter than Excel  
✅ **Automatic Excel sync** - Historical records maintained  
✅ **Real-time monitoring** - Detects new readings instantly  
✅ **Robust error handling** - Continues even if Excel fails  
✅ **Simple architecture** - Easy to understand and maintain  

---

## 📞 Support

If you encounter issues:

1. Check this README
2. Run `python send_data_from_json.py` to verify data
3. Check backend logs
4. Restart the system with `START_SYSTEM.bat`

---

**System Version:** 3.0 - JSON Based  
**Last Tested:** 2025-12-31  
**Status:** ✅ Production Ready
