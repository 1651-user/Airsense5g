# Air Quality Prediction Model Integration

## Overview

This integration connects the multi-target air quality prediction model with TinyLlama SLM in the AirSense Flutter app. The system predicts air quality parameters (PM2.5, PM10, CO2, TVOC, Temperature, Humidity, Pressure) using trained XGBoost models and provides context-aware AI responses.

## Architecture

```
MongoDB (am3 data) → Prediction Engine → Backend Server → Flutter App
                                              ↓
                                        TinyLlama SLM
```

## Components

### 1. Prediction Engine (`predict_and_send.py`)
- Loads trained XGBoost models from `models/` directory
- Connects to MongoDB using am3 credentials
- Fetches latest sensor data
- Generates predictions for all targets
- Sends predictions to backend server

### 2. Backend Server (`server.py`)
- Receives prediction data at `/api/predictions`
- Serves predictions to Flutter app at `/api/predictions/latest`
- Enhances TinyLlama chat responses with prediction context
- Provides health check and LLM test endpoints

### 3. Flutter App
- Fetches predictions via `PredictionService`
- Displays multi-target predictions in UI
- Chat with TinyLlama includes air quality context

## Setup Instructions

### Prerequisites

1. **Trained Models**: Run the training script first
   ```bash
   python train_multi_target_model (1).py
   ```
   This creates model files in the `models/` directory.

2. **MongoDB**: Ensure MongoDB is running with am3 data
   ```bash
   # Check if MongoDB is running
   mongosh mongodb://localhost:27017/milesiteaqi
   ```

3. **LM Studio**: Start LM Studio with TinyLlama model
   - Open LM Studio
   - Load TinyLlama-1.1B-Chat-v1.0
   - Start server on port 1234

### Installation

1. **Install Python Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Edit `backend/.env` if needed
   - Default settings use am3 credentials from the file

### Running the System

#### Option 1: Automated (Recommended)

**Continuous Predictions** (updates every 60 seconds):
```bash
cd backend
run_predictions.bat
```

**Single Prediction**:
```bash
cd backend
run_prediction_once.bat
```

#### Option 2: Manual

1. **Start Backend Server**
   ```bash
   cd backend
   python server.py
   ```

2. **Run Predictions** (in new terminal)
   ```bash
   cd backend
   python predict_and_send.py --continuous
   ```

3. **Start Flutter App**
   ```bash
   flutter run
   ```

## Usage

### Prediction Engine CLI

```bash
# Single prediction
python predict_and_send.py

# Continuous mode (runs every 60 seconds)
python predict_and_send.py --continuous
```

### API Endpoints

**Health Check**:
```bash
curl http://localhost:5000/health
```

**Get Latest Predictions**:
```bash
curl http://localhost:5000/api/predictions/latest
```

**Test LLM Connection**:
```bash
curl http://localhost:5000/api/test-llm
```

**Chat with Context**:
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the air quality?"}],
    "include_context": true
  }'
```

## Configuration

### Environment Variables (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | `mongodb://localhost:27017/milesiteaqi` |
| `MONGO_DB` | Database name | `milesiteaqi` |
| `MONGO_COLLECTION` | Collection name | `ambience-3` |
| `MODEL_DIR` | Models directory | `../models` |
| `PREDICTION_INTERVAL` | Prediction interval (seconds) | `60` |
| `LM_STUDIO_BASE_URL` | LM Studio API URL | `http://192.168.1.16:1234/v1` |
| `FLASK_PORT` | Backend server port | `5000` |

### Prediction Targets

The system predicts the following parameters:

| Target | Unit | Model File |
|--------|------|------------|
| PM2.5 | µg/m³ | `pm25_model.pkl` |
| PM10 | µg/m³ | `pm10_model.pkl` |
| CO2 | ppm | `co2_model.pkl` |
| TVOC | ppb | `tvoc_model.pkl` |
| Temperature | °C | `temperature_model.pkl` |
| Humidity | % | `humidity_model.pkl` |
| Pressure | hPa | `pressure_model.pkl` |

## Troubleshooting

### Models Not Found
```
✗ Model files not found for PM2.5
```
**Solution**: Run the training script first:
```bash
python train_multi_target_model (1).py
```

### MongoDB Connection Failed
```
✗ MongoDB connection failed: [Errno 111] Connection refused
```
**Solution**: Start MongoDB service:
```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### Backend Connection Error
```
⚠️ Cannot connect to backend server
```
**Solution**: Ensure backend server is running:
```bash
cd backend
python server.py
```

### LM Studio Not Connected
```
⚠️ Cannot connect to LM Studio
```
**Solution**: 
1. Start LM Studio
2. Load TinyLlama model
3. Start server (default port 1234)
4. Update `LM_STUDIO_BASE_URL` in `.env` if using different IP/port

### No Data in MongoDB
```
⚠ No data found in MongoDB
```
**Solution**: Run MQTT data collector:
```bash
python mqtt2mongo (1).py
```

## Data Flow

1. **MQTT → MongoDB**: `mqtt2mongo (1).py` collects sensor data
2. **MongoDB → Predictions**: `predict_and_send.py` generates predictions
3. **Predictions → Backend**: Sent to `/api/predictions` endpoint
4. **Backend → Flutter**: App fetches from `/api/predictions/latest`
5. **Chat Context**: TinyLlama receives prediction data in system prompt

## Example Output

```
================================================================================
AIR QUALITY PREDICTION ENGINE
================================================================================

Loading prediction models...
  ✓ Loaded PM2.5 model
  ✓ Loaded PM10 model
  ✓ Loaded CO2 model
  ✓ Loaded TVOC model
  ✓ Loaded Temperature model
  ✓ Loaded Humidity model
  ✓ Loaded Pressure model

Successfully loaded 7 models

Connecting to MongoDB: mongodb://localhost:27017/milesiteaqi
  ✓ Connected to MongoDB
  ✓ Collection 'ambience-3' has 1523 documents

Fetching latest sensor data...
  ✓ Fetched 10 samples with 15 features

Generating predictions...
  ✓ PM2.5: 35.42 µg/m³ (current: 34.80)
  ✓ PM10: 52.18 µg/m³ (current: 51.30)
  ✓ CO2: 412.35 ppm (current: 410.00)
  ✓ TVOC: 125.67 ppb (current: 123.50)
  ✓ Temperature: 24.32 °C (current: 24.10)
  ✓ Humidity: 65.45 % (current: 65.20)
  ✓ Pressure: 1013.25 hPa (current: 1013.00)

Sending predictions to backend: http://localhost:5000/api/predictions
  ✓ Successfully sent predictions (AQI: 98)

Waiting 60 seconds until next prediction...
```

## Flutter Integration

The Flutter app automatically displays predictions when available:

```dart
// Fetch predictions
final predictionService = PredictionService();
final predictions = await predictionService.getLatestPredictions();

// Access prediction data
if (predictions != null) {
  print('AQI: ${predictions.aqi}');
  print('PM2.5: ${predictions.pm25} µg/m³');
  print('Temperature: ${predictions.temperature}°C');
  print('Humidity: ${predictions.humidity}%');
}
```

## License

Part of the AirSense5G project.
