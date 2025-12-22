# MQTT to TinyLlama Pipeline - Quick Start

## What This Does

This integrated pipeline connects everything in one script:

```
MQTT Sensor (am3) → JSON File → Prediction Models → Backend Server → TinyLlama
```

## How It Works

1. **Listens to MQTT** - Connects to am3 sensor via MQTT broker
2. **Saves to JSON** - Each message saved to `mqtt_data.json`
3. **Generates Predictions** - Uses trained models to predict air quality
4. **Sends to Backend** - Predictions sent to Flask server
5. **TinyLlama Gets Context** - AI chat includes prediction data

## Quick Start

### Step 1: Start Backend Server

```powershell
cd backend
python server.py
```

Leave this running in one terminal.

### Step 2: Start LM Studio

- Open LM Studio
- Load TinyLlama-1.1B-Chat-v1.0
- Start server (port 1234)

### Step 3: Run the Pipeline

**Option A: Using batch script (easiest)**
```powershell
# Double-click or run:
run_mqtt_pipeline.bat
```

**Option B: Manual**
```powershell
python mqtt_to_tinyllama.py
```

### Step 4: Watch It Work

You'll see output like:

```
================================================================================
MQTT TO TINYLLAMA PIPELINE
================================================================================

MQTT Broker: au1.cloud.thethings.industries
Topic: v3/milesight-aqi@lora-demo/devices/ambience-3/up
Backend: http://localhost:5000/api/predictions
JSON File: mqtt_data.json
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
[MQTT] Connected to broker: au1.cloud.thethings.industries
[MQTT] Subscribed to: v3/milesight-aqi@lora-demo/devices/ambience-3/up

[WAITING] Listening for sensor data...

================================================================================
[MQTT] Received data from ambience-3
================================================================================

[SENSOR DATA]
  pm2_5: 34.8
  pm10: 51.3
  co2: 410.0
  tvoc: 123.5
  temperature: 24.1
  humidity: 65.2
  pressure: 1013.0

[JSON] Saving to mqtt_data.json...
  OK Saved

[PREDICTIONS] Generating predictions...
  OK Generated 7 predictions:
    PM2.5: 35.42µg/m³ (current: 34.8)
    PM10: 52.18µg/m³ (current: 51.3)
    CO2: 412.35ppm (current: 410.0)
    TVOC: 125.67ppb (current: 123.5)
    Temperature: 24.32°C (current: 24.1)
    Humidity: 65.45% (current: 65.2)
    Pressure: 1013.25hPa (current: 1013.0)

[BACKEND] Sending to TinyLlama backend...
  OK Sent to backend (AQI: 98)

[TINYLLAMA] Predictions now available for AI chat!
  - TinyLlama will receive this context in chat responses
  - Flutter app can fetch predictions from backend

================================================================================
```

## What Gets Created

- **`mqtt_data.json`** - All MQTT messages (last 100)
- **Backend predictions** - Available at `http://localhost:5000/api/predictions/latest`
- **TinyLlama context** - AI responses include prediction data

## Testing the Integration

### Test 1: Check Backend Received Predictions

```powershell
curl http://localhost:5000/api/predictions/latest
```

You should see the latest predictions.

### Test 2: Chat with TinyLlama (with context)

```powershell
curl -X POST http://localhost:5000/api/chat `
  -H "Content-Type: application/json" `
  -d '{"messages": [{"role": "user", "content": "What is the air quality?"}], "include_context": true}'
```

TinyLlama will respond using the prediction data!

### Test 3: View JSON File

```powershell
cat mqtt_data.json
```

See all collected MQTT messages.

## Flutter App Integration

Once the pipeline is running:

1. Start Flutter app: `flutter run`
2. App fetches predictions from backend
3. Chat with TinyLlama includes air quality context
4. Real-time updates as new MQTT data arrives

## Data Flow

```
┌─────────────────┐
│  MQTT Sensor    │ (am3 - sends data every few minutes)
│  (ambience-3)   │
└────────┬────────┘
         │ MQTT message
         ▼
┌─────────────────────┐
│ mqtt_to_tinyllama.py│
│                     │
│ 1. Receives message │
│ 2. Saves to JSON    │ → mqtt_data.json
│ 3. Buffers data     │
│ 4. Generates preds  │ (uses trained models)
│ 5. Sends to backend │
└────────┬────────────┘
         │ HTTP POST
         ▼
┌─────────────────────┐
│  Backend Server     │ (localhost:5000)
│  (Flask)            │
│                     │
│ • Stores predictions│
│ • Serves to Flutter │
│ • Enhances TinyLlama│
└────┬───────────┬────┘
     │           │
     ▼           ▼
┌──────────┐  ┌──────────┐
│TinyLlama │  │ Flutter  │
│   SLM    │  │   App    │
└──────────┘  └──────────┘
```

## Troubleshooting

### MQTT Connection Failed
- Check internet connection
- Verify credentials in `am3.env`
- Check firewall settings

### Backend Not Running
```
WARNING Backend not running (start with: python backend/server.py)
```
Start the backend server in another terminal.

### Models Not Found
```
ERROR: Models not found!
```
Train models first:
```powershell
python train_quick.py
```

### No MQTT Messages
- MQTT sensors send data periodically (every few minutes)
- Wait for the next transmission
- Check MQTT broker status

## Files

- **`mqtt_to_tinyllama.py`** - Main pipeline script
- **`run_mqtt_pipeline.bat`** - Easy launcher
- **`mqtt_data.json`** - Collected data (auto-created)
- **`am3.env`** - MQTT credentials
- **`models/`** - Trained prediction models

## Summary

This pipeline gives you:
- ✅ Real-time MQTT data collection
- ✅ Automatic JSON storage
- ✅ Live predictions
- ✅ TinyLlama with air quality context
- ✅ Flutter app integration

All in one script!
