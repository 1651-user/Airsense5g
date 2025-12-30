# 🚀 Complete AI Air Quality System Setup

## ✅ System Architecture

```
MQTT Sensor → mqtt_to_phi2.py → Backend Wrapper (localhost:5000) → Phi-2 (192.168.0.103:1234)
     ↓                                    ↓
mqtt_data.json                    Stores predictions
     ↓                                    ↓
output.xlsx                        Flutter App can query
```

## 📋 Prerequisites

1. ✅ **Phi-2 running on LM Studio** at `http://192.168.0.103:1234`
2. ✅ **Python 3.11** installed
3. ✅ **Required packages**: `pip install flask requests pandas openpyxl paho-mqtt joblib scikit-learn`

## 🎯 Quick Start

### Option 1: Automatic (Recommended)

Simply double-click: **`start_system.bat`**

This will open 2 windows:
- **Backend Wrapper** - Connects to Phi-2
- **MQTT Pipeline** - Receives sensor data

### Option 2: Manual

**Terminal 1 - Start Backend Wrapper:**
```bash
python backend_wrapper.py
```

**Terminal 2 - Start MQTT Pipeline:**
```bash
python mqtt_to_phi2.py
```

## 🔧 What Each Component Does

### 1. **backend_wrapper.py** (Port 5000)
- Receives predictions from MQTT pipeline
- Stores latest air quality data
- Translates requests to Phi-2's OpenAI-compatible API
- Provides `/api/chat` endpoint for Flutter app

### 2. **mqtt_to_phi2.py**
- Connects to MQTT broker
- Receives sensor data
- Generates predictions using ML models
- Sends to backend wrapper
- Saves to `mqtt_data.json`

### 3. **json_to_excel.py** (Optional)
- Converts `mqtt_data.json` to `output.xlsx`
- Run manually: `python json_to_excel.py`

### 4. **live_ai_system.py** (Alternative)
- Auto-updates every 30 seconds
- Checks for new MQTT data
- Updates Excel automatically
- Sends predictions to backend

## 📡 API Endpoints

### Backend Wrapper (localhost:5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/predictions` | POST | Receive predictions |
| `/api/predictions/latest` | GET | Get latest predictions |
| `/api/chat` | POST | Chat with AI (uses prediction context) |
| `/api/test-llm` | GET | Test Phi-2 connection |

### Example Chat Request:
```json
POST http://localhost:5000/api/chat
{
  "message": "What is the current air quality?"
}
```

### Example Response:
```json
{
  "response": "The current AQI is 165 (Unhealthy). PM2.5 is 84 µg/m³...",
  "timestamp": "2025-12-26T22:00:00",
  "has_context": true
}
```

## 🔍 Troubleshooting

### Backend Wrapper won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <PID> /F
```

### Phi-2 not responding
1. Check LM Studio is running
2. Verify URL: `http://192.168.0.103:1234`
3. Test: `python discover_phi2_endpoints.py`

### MQTT not connecting
1. Check internet connection
2. Verify credentials in `am3.env`
3. Check firewall settings

### Excel permission denied
- Close `output.xlsx` in Excel
- The script will retry automatically (3 attempts)

## 📊 Files Overview

| File | Purpose |
|------|---------|
| `backend_wrapper.py` | Flask server connecting to Phi-2 |
| `mqtt_to_phi2.py` | MQTT → Predictions → Backend |
| `live_ai_system.py` | Auto-updating system (30s intervals) |
| `json_to_excel.py` | JSON → Excel converter |
| `start_system.bat` | One-click startup |
| `mqtt_data.json` | Latest sensor data |
| `output.xlsx` | Historical data |
| `models/` | Trained ML models |

## ✨ Features

- ✅ Real-time MQTT sensor data
- ✅ ML-based predictions (7 pollutants)
- ✅ AI chat with context awareness
- ✅ Automatic Excel updates
- ✅ Retry logic for file locks
- ✅ GPU-accelerated Phi-2
- ✅ OpenAI-compatible API

## 🎯 Next Steps

1. **Start the system**: Run `start_system.bat`
2. **Verify backend**: Visit `http://localhost:5000/health`
3. **Test chat**: `curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d "{\"message\":\"test\"}"`
4. **Connect Flutter app**: Point to `http://localhost:5000/api/chat`

## 📱 Flutter Integration

Update your Flutter app's API endpoint to:
```dart
final apiUrl = 'http://192.168.0.103:5000/api/chat';
// Or if on same machine: 'http://localhost:5000/api/chat'
```

The backend will automatically include the latest sensor data in every chat response!

---

**Need help?** Check the logs in the terminal windows or run `python check_system_status.py`
