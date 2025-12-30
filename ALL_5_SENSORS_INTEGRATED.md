# ✅ ALL 5 SENSORS INTEGRATED - COMPLETE GUIDE

## 🎉 What Has Been Done

All 5 sensors are now integrated exactly like Sensor 3! Each sensor has its own MQTT-to-AI pipeline with ML predictions.

## 📁 Files Created

### Individual Sensor Pipelines:
1. **`mqtt_to_ai_sensor1.py`** - Sensor 1 pipeline (uses `amb1.env`)
2. **`mqtt_to_ai_sensor2.py`** - Sensor 2 pipeline (uses `amb2.env`)
3. **`mqtt_to_phi2.py`** - Sensor 3 pipeline (existing, uses `am3.env`)
4. **`mqtt_to_ai_sensor4.py`** - Sensor 4 pipeline (uses `amb4.env`)
5. **`mqtt_to_ai_sensor5.py`** - Sensor 5 pipeline (uses `amb5.env`)

### Startup Script:
- **`start_all_5_sensors.bat`** - One-click startup for all 5 sensors + backend

---

## 🚀 How to Start All 5 Sensors

### Quick Start (Recommended):
```bash
start_all_5_sensors.bat
```

This will open **6 terminal windows**:
1. Backend Server
2. Sensor 1
3. Sensor 2
4. Sensor 3
5. Sensor 4
6. Sensor 5

### Manual Start (Alternative):

**Terminal 1 - Backend:**
```powershell
cd backend
python server.py
```

**Terminal 2 - Sensor 1:**
```powershell
python mqtt_to_ai_sensor1.py
```

**Terminal 3 - Sensor 2:**
```powershell
python mqtt_to_ai_sensor2.py
```

**Terminal 4 - Sensor 3:**
```powershell
python mqtt_to_phi2.py
```

**Terminal 5 - Sensor 4:**
```powershell
python mqtt_to_ai_sensor4.py
```

**Terminal 6 - Sensor 5:**
```powershell
python mqtt_to_ai_sensor5.py
```

---

## 💡 How Each Sensor Works

Each sensor follows the **exact same pattern as Sensor 3**:

```
MQTT Broker
     ↓
 Receive Data
     ↓
 Save to JSON (mqtt_data_sensorX.json)
     ↓
 Buffer Last 10 Readings
     ↓
 Generate ML Predictions (need 3+ readings)
     ↓
 Calculate AQI
     ↓
 Send to Backend Server
     ↓
 AI Receives Context
```

---

## 📊 What Each Sensor Does

| Sensor | Script | JSON File | Environment | MQTT Topic |
|--------|--------|-----------|-------------|------------|
| Sensor 1 | `mqtt_to_ai_sensor1.py` | `mqtt_data_sensor1.json` | `amb1.env` | `ambience-1` |
| Sensor 2 | `mqtt_to_ai_sensor2.py` | `mqtt_data_sensor2.json` | `amb2.env` | `ambience-2` |
| Sensor 3 | `mqtt_to_phi2.py` | `mqtt_data.json` | `am3.env` | `ambience-3` |
| Sensor 4 | `mqtt_to_ai_sensor4.py` | `mqtt_data_sensor4.json` | `amb4.env` | `ambience-4` |
| Sensor 5 | `mqtt_to_ai_sensor5.py` | `mqtt_data_sensor5.json` | `amb5.env` | `ambience-5` |

---

## 🤖 ML Predictions

Each sensor generates predictions for:
- ✅ **PM2.5** (µg/m³)
- ✅ **PM10** (µg/m³)
- ✅ **CO2** (ppm)
- ✅ **TVOC** (ppb)
- ✅ **Temperature** (°C)
- ✅ **Humidity** (%)
- ✅ **Pressure** (hPa)

---

## 💬 AI Integration

The AI now receives data and predictions from **all 5 sensors**!

### Example Terminal Output:

```
Sensor 1:
  AQI: 85
  PM2.5: 35.2
  Predictions: PM2.5 → 36.1 µg/m³ ↑

Sensor 2:
  AQI: 92
  PM2.5: 38.5
  Predictions: PM2.5 → 39.2 µg/m³ ↑

Sensor 3:
  AQI: 78
  PM2.5: 30.1
  Predictions: PM2.5 → 31.2 µg/m³ ↑

Sensor 4:
  AQI: 105
  PM2.5: 42.3
  Predictions: PM2.5 → 43.1 µg/m³ ↑

Sensor 5:
  AQI: 88
  PM2.5: 36.7
  Predictions: PM2.5 → 37.5 µg/m³ ↑
```

### AI Can Answer:
- ✅ "What is the PM2.5 level of sensor 4?"
- ✅ "Which sensor has the highest AQI?"
- ✅ "Show me predictions for sensor 2"
- ✅ "Compare sensor 1 and sensor 5"
- ✅ "What is the temperature reading from sensor 3?"

---

## 🔧 Configuration

Each sensor uses its own environment file:

### Example `amb1.env`:
```
MQTT_BROKER=au1.cloud.thethings.industries
MQTT_PORT=1883
MQTT_TOPIC=v3/milesight-aqi@lora-demo/devices/ambience-1/up
MQTT_USERNAME=milesight-aqi@lora-demo
MQTT_PASSWORD=your_password_here
MONGO_URI=mongodb+srv://...
MONGO_DB=milesiteaqi
MONGO_COLLECTION=ambience-1
```

---

## ✅ No Existing Functionality Broken

- ✅ **Sensor 3 (`mqtt_to_phi2.py`)** - Still works exactly as before
- ✅ **Backend server** - Unchanged, receives from all sensors
- ✅ **ML models** - Same models used for all sensors
- ✅ **Flutter app** - Can still connect and receive data
- ✅ **MongoDB scripts** - `mqtt2mongo*.py` still available if needed

---

## 🎯 System Architecture

```
┌─────────────────┐
│  MQTT Brokers   │  (5 separate brokers)
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
    ▼          ▼
┌────────┐  ┌────────┐
│Sensor 1│  │Sensor 2│  ... (all 5 sensors)
│Pipeline│  │Pipeline│
└───┬────┘  └───┬────┘
    │           │
    └─────┬─────┘
          ▼
    ┌──────────┐
    │  Backend │
    │  Server  │
    └─────┬────┘
          │
    ┌─────┴───────┐
    ▼             ▼
┌────────┐   ┌────────┐
│Flutter │   │   AI   │
│  App   │   │(LM Stu)│
└────────┘   └────────┘
```

---

## 📈 Expected Output

When you run `start_all_5_sensors.bat`, you'll see:

**Backend Window:**
```
Starting AirSense Backend Server on 0.0.0.0:5000
```

**Each Sensor Window:**
```
================================================================================
MQTT TO AI PIPELINE - Sensor X
================================================================================

MQTT Broker: au1.cloud.thethings.industries
Topic: v3/milesight-aqi@lora-demo/devices/ambience-X/up
Backend: http://localhost:5000/api/predictions
JSON File: mqtt_data_sensorX.json
================================================================================

[MODELS] Loading prediction models...
  OK Loaded PM2.5 model
  OK Loaded PM10 model
  OK Loaded CO2 model
  OK Loaded TVOC model
  OK Loaded Temperature model
  OK Loaded Humidity model
  OK Loaded Pressure model
  OK Loaded 7 models

[MQTT] Connecting to au1.cloud.thethings.industries:1883...
[MQTT] Connected to broker
[MQTT] Subscribed to topic
[WAITING] Listening for Sensor X data...
```

---

## 🧪 Testing

### Test Individual Sensor:
```powershell
python mqtt_to_ai_sensor1.py
```

### Test All Sensors:
```powershell
start_all_5_sensors.bat
```

### Test AI Integration:
1. Start all sensors
2. Wait for data to arrive
3. Ask AI: "What is the PM2.5 level of sensor 4?"
4. AI should respond with the actual data!

---

## 📊 Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Sensor 1 | ✅ Ready | Individual MQTT-to-AI pipeline |
| Sensor 2 | ✅ Ready | Individual MQTT-to-AI pipeline |
| Sensor 3 | ✅ Live | Existing `mqtt_to_phi2.py` |
| Sensor 4 | ✅ Ready | Individual MQTT-to-AI pipeline |
| Sensor 5 | ✅ Ready | Individual MQTT-to-AI pipeline |
| Backend | ✅ Ready | Receives from all sensors |
| ML Models | ✅ Ready | Shared across all sensors |
| AI Integration | ✅ Complete | Can answer about any sensor |

---

## 🎊 Success!

All 5 sensors are now integrated exactly like Sensor 3, with:
- ✅ Individual MQTT connections
- ✅ ML predictions for each sensor
- ✅ Real-time data streaming
- ✅ AI integration
- ✅ No existing functionality broken

**Just run `start_all_5_sensors.bat` and all sensors will be live!**
