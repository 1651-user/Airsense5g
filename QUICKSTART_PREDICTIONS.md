# Quick Start Guide: Prediction Model Integration

## Prerequisites Check

Before running the prediction system, verify these requirements:

### 1. Train the Models (REQUIRED)
```bash
# Run this from the project root directory
python "train_multi_target_model (1).py"
```

This will create the `models/` directory with all required model files:
- `pm25_model.pkl` / `pm25_scaler.pkl`
- `pm10_model.pkl` / `pm10_scaler.pkl`
- `co2_model.pkl` / `co2_scaler.pkl`
- `tvoc_model.pkl` / `tvoc_scaler.pkl`
- `temperature_model.pkl` / `temperature_scaler.pkl`
- `humidity_model.pkl` / `humidity_scaler.pkl`
- `pressure_model.pkl` / `pressure_scaler.pkl`

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

This installs:
- Flask (backend server)
- pymongo (MongoDB connection)
- pandas, numpy (data processing)
- xgboost, scikit-learn (ML models)
- joblib (model loading)

### 3. Start MongoDB
Ensure MongoDB is running with am3 data:
```bash
# Check if MongoDB is running
mongosh mongodb://localhost:27017/milesiteaqi

# If not running, start it:
net start MongoDB
```

### 4. Collect Sensor Data (if needed)
If MongoDB is empty, run the MQTT collector:
```bash
python "mqtt2mongo (1).py"
```

### 5. Start LM Studio
1. Open LM Studio
2. Load TinyLlama-1.1B-Chat-v1.0 model
3. Start server (default: port 1234)
4. Update `backend/.env` if using different IP:
   ```
   LM_STUDIO_BASE_URL=http://YOUR_IP:1234/v1
   ```

## Running the System

### Step 1: Start Backend Server
```bash
cd backend
python server.py
```

Expected output:
```
Starting AirSense Backend Server on 0.0.0.0:5000
LM Studio URL: http://192.168.1.16:1234/v1
```

### Step 2: Run Predictions

**Option A: Automated (Recommended)**
```bash
# Double-click this file or run:
backend\run_predictions.bat
```

**Option B: Manual**
```bash
cd backend
python predict_and_send.py --continuous
```

### Step 3: Start Flutter App
```bash
flutter run
```

## Verification

### Test Backend Health
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-22T11:16:28",
  "lm_studio_url": "http://192.168.1.16:1234/v1"
}
```

### Test Predictions
```bash
curl http://localhost:5000/api/predictions/latest
```

Expected response:
```json
{
  "status": "success",
  "timestamp": "2025-12-22T11:16:28",
  "data": {
    "aqi": 98,
    "pm25": 35.42,
    "pm10": 52.18,
    "predictions": {
      "PM2.5": {"predicted": 35.42, "current": 34.80, "unit": "µg/m³"},
      "PM10": {"predicted": 52.18, "current": 51.30, "unit": "µg/m³"},
      ...
    }
  }
}
```

### Test LLM Connection
```bash
curl http://localhost:5000/api/test-llm
```

## Troubleshooting

### Error: "No module named 'pymongo'"
```bash
cd backend
pip install -r requirements.txt
```

### Error: "No models loaded!"
```bash
# Train models first
python "train_multi_target_model (1).py"
```

### Error: "MongoDB connection failed"
```bash
# Start MongoDB
net start MongoDB

# Or check if it's running
mongosh mongodb://localhost:27017
```

### Error: "Cannot connect to LM Studio"
1. Open LM Studio
2. Load a model (TinyLlama recommended)
3. Click "Start Server"
4. Verify URL in `backend/.env`

### Error: "No data found in MongoDB"
```bash
# Run MQTT collector
python "mqtt2mongo (1).py"
```

## System Architecture

```
┌─────────────────┐
│  MQTT Broker    │ (am3 credentials)
│  (TTN)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ mqtt2mongo.py   │ (Collects sensor data)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    MongoDB      │ (Stores sensor data)
│  ambience-3     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ predict_and_    │ (Generates predictions)
│   send.py       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Backend Server  │◄────►│  TinyLlama   │
│  (Flask)        │      │  (LM Studio) │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│  Flutter App    │ (Displays predictions + AI chat)
└─────────────────┘
```

## Next Steps

1. ✅ Train models: `python "train_multi_target_model (1).py"`
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Start MongoDB
4. ✅ Start LM Studio with TinyLlama
5. ✅ Start backend: `python backend/server.py`
6. ✅ Run predictions: `backend\run_predictions.bat`
7. ✅ Start Flutter app: `flutter run`

## Support

For detailed documentation, see:
- `backend/PREDICTION_INTEGRATION.md` - Full integration guide
- `SETUP_GUIDE.md` - General setup instructions
- `TROUBLESHOOTING.md` - Common issues
