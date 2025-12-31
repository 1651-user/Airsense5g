# AirSense 5G - Complete System Flow Summary

## ✅ VERIFIED IMPLEMENTATION

Your streamlined flow is now **fully implemented** and working as follows:

---

## 📡 **STEP 1: MQTT → JSON → Excel**

```
5 Sensors (AM3 devices)
    ↓ MQTT Protocol (Real-time)
mqtt_data_sensor1.json
mqtt_data_sensor2.json  
mqtt_data.json (Sensor 3)
mqtt_data_sensor4.json
mqtt_data_sensor5.json
    ↓ excel_integration_enhanced.py (File Watcher)
output1.xlsx (Sensor 1)
output2.xlsx (Sensor 2)
output3.xlsx (Sensor 3)
output4.xlsx (Sensor 4)
output5.xlsx (Sensor 5)
```

**What happens:**
- Sensors send MQTT messages continuously
- Python scripts save to JSON files
- Excel integration watches JSON files
- New rows appended to Excel (never new columns)
- Duplicate timestamps removed automatically

---

## 🔍 **STEP 2: Extract Required Values**

```python
# live_ai_system_enhanced.py reads Excel and extracts ONLY:

✓ PM2.5       (Particulate Matter 2.5 µg/m³)
✓ PM10        (Particulate Matter 10 µg/m³)
✓ CO2         (Carbon Dioxide ppm)
✓ TVOC        (Total Volatile Organic Compounds ppb)
✓ Temperature (°C)
✓ Humidity    (%)
✓ Pressure    (hPa)

❌ IGNORES: battery, light_level, pir, etc.
```

**NaN Handling:**
- Reads entire Excel sheet
- Searches last 20 rows for valid data
- Uses most recent non-NaN values
- Never crashes on missing data

---

## 🤖 **STEP 3: Generate Predictions**

```
Current Values → ML Models → Predicted Values

Models used:
  • pm2_5_model.pkl + scaler
  • pm10_model.pkl + scaler
  • co2_model.pkl + scaler
  • tvoc_model.pkl + scaler
  • temperature_model.pkl + scaler
  • humidity_model.pkl + scaler
  • pressure_model.pkl + scaler

Output:
  {
    "PM2.5": {"current": 35.2, "predicted": 35.9},
    "PM10": {"current": 52.8, "predicted": 53.8},
    "CO2": {"current": 412, "predicted": 408},
    ...
  }

AQI Calculation:
  - Calculated from PM2.5 using EPA formula
  - Range: 0-500 (Good to Hazardous)
```

**Frequency:** Every 30 seconds for all 5 sensors

---

## 🌐 **STEP 4: Backend API**

```
POST /api/predictions
← Receives predictions from Python

GET /api/sensors/all
→ Returns all 5 sensors data

GET /api/forecast/{sensor_id}
→ Returns 24-hour & weekly predictions

POST /api/chat
→ AI chatbot with sensor context
```

**Backend stores:**
- Latest data from all 5 sensors
- Current + predicted values
- Timestamp of last update

---

## 📱 **STEP 5: Flutter App**

### **1. Dashboard Screen** (`dashboard_screen.dart`)

```dart
GET /api/sensors/all

Displays:
┌─────────────────────────────────────────────────┐
│  Sensor 1    Sensor 2    Sensor 3    Sensor 4  │
│  AQI: 85     AQI: 72     AQI: 91     AQI: 68   │
│  Moderate    Good        Moderate    Good      │
│                                                  │
│  Each card shows:                                │
│  • PM2.5 level                                   │
│  • PM10 level                                    │
│  • CO2 level                                     │
│  • TVOC level                                    │
│  • Temperature                                   │
│  • Humidity                                      │
│  • Pressure                                      │
└─────────────────────────────────────────────────┘
```

**Color Coding:**
- 🟢 Green: AQI 0-50 (Good)
- 🟡 Yellow: AQI 51-100 (Moderate)
- 🟠 Orange: AQI 101-150 (Unhealthy for Sensitive)
- 🔴 Red: AQI 151+ (Unhealthy)

---

### **2. Forecast Screen** (`forecast_screen.dart`)

```dart
GET /api/forecast/{sensor_id}?hours=24&days=7

Displays:
┌─────────────────────────────────────────────────┐
│  📊 24-Hour Forecast                             │
│  ────────────────────────────────────────────   │
│  Hour  AQI   PM2.5   PM10   Category            │
│  12:00  85   35.2    52.8   Moderate            │
│  13:00  88   36.1    54.2   Moderate            │
│  14:00  92   37.8    56.7   Moderate            │
│  ...                                             │
│                                                  │
│  📅 Weekly Forecast                              │
│  ────────────────────────────────────────────   │
│  Day       AQI   PM2.5   Category               │
│  Tuesday    85   35.2    Moderate               │
│  Wednesday  78   32.1    Moderate               │
│  Thursday   82   33.8    Moderate               │
│  ...                                             │
└─────────────────────────────────────────────────┘
```

**Features:**
- Line charts showing trends
- Peak pollution times highlighted
- Weekend vs weekday patterns
- Based on real sensor data + ML predictions

---

### **3. Chatbot Screen** (`chat_screen.dart`)

```dart
POST /api/chat (with sensor context)

Example Conversations:
┌─────────────────────────────────────────────────┐
│ User: "What are the current pollutant levels?"  │
│                                                  │
│ AI: "Based on Sensor 3 (latest reading):        │
│     • PM2.5: 35.2 µg/m³ (Moderate)              │
│     • PM10: 52.8 µg/m³                          │
│     • CO2: 412 ppm (Normal)                     │
│     • TVOC: 125 ppb (Low)                       │
│                                                  │
│     The air quality is moderate. Sensitive      │
│     groups should consider reducing prolonged   │
│     outdoor activities."                        │
├─────────────────────────────────────────────────┤
│ User: "Is it safe to go outside?"               │
│                                                  │
│ AI: "Current AQI across all sensors:            │
│     • Sensor 1: 85 (Moderate)                   │
│     • Sensor 2: 72 (Good)                       │
│     • Sensor 3: 91 (Moderate)                   │
│                                                  │
│     It's generally safe for most people.        │
│     If you have respiratory conditions,         │
│     consider limiting strenuous activities."    │
├─────────────────────────────────────────────────┤
│ User: "What's the forecast for tomorrow?"       │
│                                                  │
│ AI: "Tomorrow's predicted AQI: 78 (Moderate)    │
│     • Morning (6-9 AM): AQI 92 (peak)          │
│     • Afternoon (12-3 PM): AQI 75              │
│     • Evening (6-9 PM): AQI 88                 │
│                                                  │
│     Best time for outdoor exercise: 12-3 PM"    │
└─────────────────────────────────────────────────┘
```

**AI Features:**
- Real-time access to all 5 sensors
- Pollutant level queries
- Air quality analysis
- Health recommendations
- Prediction insights
- Powered by Phi-2 (LM Studio)

---

## 🚀 **Quick Start Commands**

### **Start Everything:**
```bash
START_ALL.bat
```

### **Or Manual Start:**
```bash
# Terminal 1: Backend Server
python backend/server.py

# Terminal 2: Excel Integration
python excel_integration_enhanced.py

# Terminal 3: Live AI System
python live_ai_system_enhanced.py

# Terminal 4: Flutter App
flutter run
```

### **Verify System:**
```bash
python check_system_status.py
```

---

## 📊 **Data Flow Frequency**

| Stage | Frequency |
|-------|-----------|
| MQTT → JSON | Real-time (as sensors transmit) |
| JSON → Excel | Immediate (file watcher) |
| Excel → Predictions | Every 30 seconds |
| Predictions → Backend | Every 30 seconds |
| Backend → Dashboard | On user refresh |
| Backend → Forecast | On demand |
| Backend → Chatbot | Real-time (per message) |

---

## ✅ **What's Working**

✓ MQTT data collection from 5 sensors  
✓ JSON to Excel synchronization  
✓ Extract only required values (PM2.5, PM10, CO2, TVOC, Temp, Humidity, Pressure)  
✓ NaN/missing value handling  
✓ ML predictions for all pollutants  
✓ AQI calculation (EPA standard)  
✓ Backend API with all endpoints  
✓ Dashboard showing all 5 sensors  
✓ 24-hour forecast (hourly)  
✓ Weekly forecast (daily)  
✓ AI chatbot with sensor context  
✓ Health recommendations  

---

## 🎯 **Key Points**

1. **Only 7 values extracted:** PM2.5, PM10, CO2, TVOC, Temperature, Humidity, Pressure
2. **All other values ignored:** Battery, light level, PIR, etc.
3. **Predictions generated:** For all 7 values every 30 seconds
4. **Dashboard shows:** All 5 sensors with AQI + pollutant levels
5. **Forecast shows:** 24-hour hourly + 7-day daily predictions
6. **Chatbot uses:** Real-time sensor data + predictions for intelligent responses

---

## 📝 **Files Modified**

1. `backend/server.py` - Added `/api/forecast/{sensor_id}` endpoint
2. `lib/services/forecast_service.dart` - Updated to fetch from backend API
3. `STREAMLINED_FLOW.md` - Complete documentation (this file)

---

**System Status:** ✅ FULLY OPERATIONAL

**Last Updated:** 2025-12-31 11:52 IST
