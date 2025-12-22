# Prediction Model to TinyLlama Connection Architecture

## Current Connection Status

### ✅ What's Connected and Ready

#### 1. **Trained Models** → **Prediction Engine**
- **Status:** ✅ READY
- **Location:** `models/` directory (14 files)
- **Models:** PM2.5, PM10, CO2, TVOC, Temperature, Humidity, Pressure
- **Connection:** `predict_and_send.py` loads these models using joblib

#### 2. **Prediction Engine** → **Backend Server**
- **Status:** ✅ CODE READY (needs to run)
- **Script:** `backend/predict_and_send.py`
- **Endpoint:** Sends predictions to `http://localhost:5000/api/predictions`
- **Data Format:**
  ```json
  {
    "timestamp": "2025-12-22T11:48:59",
    "aqi": 98,
    "pm25": 35.42,
    "pm10": 52.18,
    "predictions": {
      "PM2.5": {"predicted": 35.42, "current": 34.80, "unit": "µg/m³"},
      "PM10": {"predicted": 52.18, "current": 51.30, "unit": "µg/m³"},
      ...
    }
  }
  ```

#### 3. **Backend Server** → **TinyLlama SLM**
- **Status:** ✅ CODE READY (needs LM Studio running)
- **File:** `backend/server.py` (enhanced)
- **TinyLlama URL:** `http://192.168.1.16:1234/v1`
- **Model:** TinyLlama-1.1B-Chat-v1.0
- **Connection Type:** REST API (OpenAI-compatible)
- **Context Sent to TinyLlama:**
  ```
  "You are an air quality assistant. Current AQI: 98 
   Predictions: PM2.5: 35.42µg/m³, PM10: 52.18µg/m³, 
   CO2: 412.35ppm, TVOC: 125.67ppb, Temperature: 24.32°C, 
   Humidity: 65.45%, Pressure: 1013.25hPa 
   Keep responses brief and helpful."
  ```

#### 4. **Backend Server** → **Flutter App**
- **Status:** ✅ CODE READY
- **Endpoints:**
  - GET `/api/predictions/latest` - Fetch predictions
  - POST `/api/chat` - Chat with TinyLlama (includes prediction context)
  - GET `/health` - Health check
  - GET `/api/test-llm` - Test LM Studio connection

#### 5. **Flutter App** → **User**
- **Status:** ✅ MODELS UPDATED
- **File:** `lib/models/prediction_model.dart`
- **Fields:** pm25, pm10, co2, no2, tvoc, temperature, humidity, pressure
- **Service:** `lib/services/prediction_service.dart` (fetches from backend)
- **Chat:** `lib/services/bytez_service.dart` (connects to TinyLlama via backend)

---

## Connection Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA FLOW ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  Trained Models  │  (7 XGBoost models + scalers)
│   models/*.pkl   │  ✅ READY
└────────┬─────────┘
         │ joblib.load()
         ▼
┌──────────────────────────┐
│  Prediction Engine       │  predict_and_send.py
│  - Loads models          │  ⚠️ NEEDS: Data source (MongoDB or static)
│  - Generates predictions │
│  - Calculates AQI        │
└────────┬─────────────────┘
         │ HTTP POST /api/predictions
         ▼
┌──────────────────────────┐
│   Backend Server         │  server.py (Flask)
│   localhost:5000         │  ⚠️ NEEDS: To be started
│                          │
│  Endpoints:              │
│  • /api/predictions      │  ← Receives predictions
│  • /api/predictions/latest│ → Serves to Flutter
│  • /api/chat             │  ↔ Proxies to TinyLlama
│  • /health               │
└────┬──────────────┬──────┘
     │              │
     │              └──────────────────────┐
     │                                     │
     ▼                                     ▼
┌──────────────────────┐         ┌─────────────────────┐
│   TinyLlama SLM      │         │    Flutter App      │
│   (LM Studio)        │         │                     │
│   192.168.1.16:1234  │         │  • Displays         │
│                      │         │    predictions      │
│  ⚠️ NEEDS: Running   │         │  • Chat with        │
│                      │         │    context-aware    │
│  Receives:           │         │    TinyLlama        │
│  • User messages     │         │                     │
│  • Prediction context│         │  ✅ CODE READY      │
│                      │         │                     │
│  Returns:            │         └─────────────────────┘
│  • AI responses      │
│    (air quality      │
│     aware)           │
└──────────────────────┘
```

---

## What's Working vs What Needs Setup

### ✅ Working (Code Complete)
1. **Models trained** - 7 XGBoost models ready
2. **Prediction engine** - `predict_and_send.py` can load models and generate predictions
3. **Backend server** - Enhanced with prediction context for TinyLlama
4. **Flutter models** - Updated to handle all prediction targets
5. **Integration code** - All connections programmed

### ⚠️ Needs to Run
1. **Backend Server:**
   ```bash
   cd backend
   python server.py
   ```
   Status: Not running yet

2. **LM Studio with TinyLlama:**
   - Open LM Studio
   - Load TinyLlama-1.1B-Chat-v1.0
   - Start server on port 1234
   Status: Not running yet

3. **Prediction Engine** (optional for now):
   ```bash
   cd backend
   python predict_and_send.py
   ```
   Status: Needs data source (MongoDB or static file)

4. **Flutter App:**
   ```bash
   flutter run
   ```
   Status: Not running yet

---

## How the Connection Works

### Scenario 1: User Asks About Air Quality in Flutter App

1. **User types:** "What's the air quality like?"

2. **Flutter app** sends request to backend:
   ```
   POST http://localhost:5000/api/chat
   {
     "messages": [{"role": "user", "content": "What's the air quality like?"}],
     "include_context": true
   }
   ```

3. **Backend server:**
   - Retrieves latest prediction data from memory
   - Builds context with all prediction targets
   - Sends to TinyLlama:
     ```
     System: "You are an air quality assistant. Current AQI: 98, 
             Predictions: PM2.5: 35.42µg/m³, PM10: 52.18µg/m³..."
     User: "What's the air quality like?"
     ```

4. **TinyLlama** (via LM Studio):
   - Receives context + user message
   - Generates response using prediction data
   - Returns: "The air quality is moderate with an AQI of 98. 
              PM2.5 levels are at 35.42 µg/m³..."

5. **Backend** forwards response to Flutter

6. **Flutter app** displays AI response to user

### Scenario 2: Viewing Predictions in Flutter App

1. **Flutter app** requests predictions:
   ```
   GET http://localhost:5000/api/predictions/latest
   ```

2. **Backend** returns latest prediction data

3. **Flutter** displays all targets:
   - PM2.5: 35.42 µg/m³
   - PM10: 52.18 µg/m³
   - CO2: 412.35 ppm
   - TVOC: 125.67 ppb
   - Temperature: 24.32°C
   - Humidity: 65.45%
   - Pressure: 1013.25 hPa
   - AQI: 98 (Moderate)

---

## Connection Summary

**The connection is COMPLETE in code** but needs these services running:

1. ✅ **Models** - Trained and ready
2. ⚠️ **Backend Server** - Start with `python backend/server.py`
3. ⚠️ **LM Studio** - Start and load TinyLlama
4. ⚠️ **Flutter App** - Start with `flutter run`
5. ⚠️ **Prediction Engine** - Optional, needs MongoDB or static data

**Data Flow:**
```
Models → Predictions → Backend ↔ TinyLlama
                         ↓
                    Flutter App
```

**Key Integration Point:**
The backend server acts as the bridge, receiving predictions and enhancing TinyLlama's responses with real-time air quality context.
