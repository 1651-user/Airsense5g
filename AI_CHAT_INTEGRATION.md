# AI Chat Integration - Pollutant Levels & Live Data

## Overview

The AirSense 5G system now properly integrates **live sensor data** and **predictions** into the AI chat. When users ask questions like "show the pollutant levels" or similar queries, the AI will respond with actual real-time values.

## How It Works

### Data Flow

```
MQTT Sensor → mqtt_to_phi2.py → Backend Server → AI (Phi-2) → Flutter App
     ↓              ↓                   ↓              ↓
  Raw Data    Predictions         Context Data    User Response
```

### Components

1. **MQTT Pipeline** (`mqtt_to_phi2.py`)
   - Receives live sensor data from MQTT broker
   - Saves data to `mqtt_data.json`
   - Generates predictions using trained ML models
   - Sends predictions + sensor data to backend

2. **Backend Server** (`backend/server.py`)
   - Stores latest prediction data in memory
   - Provides `/api/predictions/latest` endpoint for Flutter app
   - Injects air quality context into AI chat requests
   - Proxies chat requests to LM Studio (Phi-2)

3. **AI Context Enhancement**
   - System prompt includes:
     - Current AQI with category (Good, Moderate, etc.)
     - Current sensor readings (PM2.5, PM10, CO2, TVOC, etc.)
     - Predicted values with trend indicators (↑/↓)
     - Timestamp of data
   - AI is instructed to use actual values when responding

4. **Flutter App** (`lib/services/bytez_service.dart`)
   - Sends user messages to backend
   - Backend automatically includes air quality context
   - Displays AI responses with real data

## Example AI Context

When a user asks "Show the pollutant levels", the AI receives this context:

```
You are an air quality assistant with access to real-time sensor data and predictions.
When users ask about pollutant levels or air quality, provide the actual values from the data below.

Data timestamp: 2025-12-26T11:00:00

Air Quality Index (AQI): 85 (Moderate)

CURRENT SENSOR READINGS:
  • PM2.5: 35.2 µg/m³
  • PM10: 52.8 µg/m³
  • CO2: 412 ppm
  • TVOC: 125 ppb
  • Temperature: 24.5°C
  • Humidity: 65%
  • Pressure: 1013.2 hPa

PREDICTED VALUES (Next Reading):
  • PM2.5: 36.8µg/m³ (↑ +1.6)
  • PM10: 54.2µg/m³ (↑ +1.4)
  • CO2: 408ppm (↓ -4.0)
  • TVOC: 130ppb (↑ +5.0)
  • Temperature: 24.6°C (↑ +0.1)
  • Humidity: 64% (↓ -1.0)

IMPORTANT: When asked about pollutant levels, air quality, or sensor data, use the ACTUAL VALUES from above.
```

## Testing the Integration

### 1. Start the Backend Server

```bash
python backend/server.py
```

Or use the batch file:
```bash
start_backend.bat
```

### 2. Start the MQTT Pipeline

```bash
python mqtt_to_phi2.py
```

Or use the batch file:
```bash
run_mqtt_phi2.bat
```

### 3. Ensure LM Studio is Running

- Open LM Studio
- Load a model (e.g., Phi-2, TinyLlama, etc.)
- Start the local server (default: http://localhost:1234)

### 4. Run the Test Script

```bash
python test_data_flow.py
```

This will verify:
- ✓ Backend server is running
- ✓ MQTT data is being collected
- ✓ Predictions are available
- ✓ AI chat responds with actual values

### 5. Test in Flutter App

Open the chat screen and try these queries:
- "Show the pollutant levels"
- "What is the current air quality?"
- "Show me the PM2.5 levels"
- "What are the predictions?"
- "Is it safe to go outside?"
- "What's the AQI?"

## Expected AI Responses

### Query: "Show the pollutant levels"

**Good Response:**
```
Based on the current sensor readings:

Air Quality Index: 85 (Moderate)

Current Pollutant Levels:
• PM2.5: 35.2 µg/m³
• PM10: 52.8 µg/m³
• CO2: 412 ppm
• TVOC: 125 ppb

Environmental Conditions:
• Temperature: 24.5°C
• Humidity: 65%
• Pressure: 1013.2 hPa

Predictions for next reading:
• PM2.5 expected to increase to 36.8 µg/m³
• PM10 expected to increase to 54.2 µg/m³

The air quality is moderate. Sensitive individuals should consider limiting prolonged outdoor activities.
```

## Troubleshooting

### AI doesn't show actual values

**Problem:** AI responds with generic messages instead of actual data

**Solutions:**
1. Check if MQTT pipeline is running and receiving data
2. Verify predictions are being sent to backend
3. Ensure backend has received prediction data:
   ```bash
   curl http://localhost:5000/api/predictions/latest
   ```
4. Check backend logs for context injection

### No prediction data available

**Problem:** Backend returns "no_data" status

**Solutions:**
1. Start MQTT pipeline: `python mqtt_to_phi2.py`
2. Wait for at least 2 sensor readings (needed for predictions)
3. Check if models are trained and available in `models/` directory
4. Verify MQTT credentials in `am3.env`

### LM Studio connection error

**Problem:** AI chat returns connection error

**Solutions:**
1. Start LM Studio application
2. Load a model (Server → Start Server)
3. Verify URL in `backend/.env`: `LM_STUDIO_BASE_URL=http://localhost:1234/v1`
4. Test connection: `curl http://localhost:1234/v1/models`

### Slow AI responses

**Problem:** AI takes too long to respond

**Solutions:**
1. Use a smaller, faster model (e.g., Phi-2 instead of larger models)
2. Reduce `max_tokens` in `backend/server.py` (currently 300)
3. Increase timeout in `lib/services/bytez_service.dart` (currently 60s)

## Configuration

### Backend Server (`backend/server.py`)

```python
# AI response settings
'temperature': 0.9,      # Creativity (0.0-1.0)
'max_tokens': 300,       # Response length
timeout=180              # Request timeout (seconds)
```

### Flutter App (`lib/services/bytez_service.dart`)

```dart
// Timeout settings
receiveTimeout: const Duration(seconds: 60),
sendTimeout: const Duration(seconds: 10),

// Context inclusion
includeContext: true,  // Include air quality data
```

### MQTT Pipeline (`mqtt_to_phi2.py`)

```python
MAX_BUFFER_SIZE = 10     # Number of readings to keep
BACKEND_URL = 'http://localhost:5000/api/predictions'
```

## Sample Questions

### Air Quality Queries
- "Show the pollutant levels"
- "What is the current air quality?"
- "Is the air quality safe?"
- "What's the AQI right now?"

### Specific Pollutants
- "Show me the PM2.5 levels"
- "What is the CO2 concentration?"
- "How high is the TVOC?"
- "What are the particulate matter levels?"

### Predictions
- "What are the predictions?"
- "Will air quality improve?"
- "What's the forecast for PM2.5?"
- "Show predicted values"

### Health Recommendations
- "Is it safe to go outside?"
- "Should I exercise outdoors?"
- "Health recommendations?"
- "Do I need a mask?"

## Updates Made

### 1. Enhanced Backend Context (`backend/server.py`)
- Added structured data formatting
- Included both current and predicted values
- Added AQI category labels
- Included trend indicators (↑/↓)
- Better instructions for AI to use actual values

### 2. Created Test Script (`test_data_flow.py`)
- Comprehensive system testing
- Verifies entire data pipeline
- Tests AI responses with actual queries
- Provides troubleshooting guidance

## Next Steps

1. **Run the test script** to verify everything is working
2. **Start all services** (backend, MQTT pipeline, LM Studio)
3. **Test in Flutter app** with various queries
4. **Monitor responses** to ensure AI uses actual values

## Support

If you encounter issues:
1. Check all services are running (backend, MQTT, LM Studio)
2. Run `test_data_flow.py` to identify the problem
3. Check logs in terminal windows
4. Verify data in `mqtt_data.json` and backend endpoint
