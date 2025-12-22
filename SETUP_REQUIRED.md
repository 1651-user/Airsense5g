# Setup Prerequisites - Action Required

## Current Status

The prediction model integration is **complete**, but requires setup before it can run:

### ✅ Completed
- Backend integration code (`predict_and_send.py`)
- Enhanced server with TinyLlama context
- Flutter model updates
- Automation scripts
- Documentation

### ⚠️ Required Actions

You need to complete these steps before the system can work:

## Step 1: Start MongoDB

MongoDB is not currently running. You need to:

**Option A: Start MongoDB Service**
```powershell
# Open PowerShell as Administrator and run:
net start MongoDB
```

**Option B: If MongoDB is not installed**
1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Install it
3. Start the service: `net start MongoDB`

**Verify MongoDB is running:**
```powershell
mongosh mongodb://localhost:27017
```

## Step 2: Collect Sensor Data

Once MongoDB is running, collect data from the am3 sensor:

```powershell
# Run the MQTT to MongoDB collector
python "mqtt2mongo (1).py"
```

Leave this running for at least 10-15 minutes to collect enough data for training.

## Step 3: Train the Models

Once you have data in MongoDB, train the models:

```powershell
python train_models_mongodb.py
```

This will:
- Fetch data from MongoDB
- Train 7 XGBoost models (PM2.5, PM10, CO2, TVOC, Temperature, Humidity, Pressure)
- Save models to `models/` directory
- Show performance metrics

Expected output:
```
================================================================================
MULTI-TARGET AIR QUALITY PREDICTION SYSTEM (MongoDB)
================================================================================

[STEP 1] Loading data from MongoDB...
  ✓ Connected to MongoDB
  ✓ Collection 'ambience-3' has 1523 documents
  ✓ Loaded 1523 records from MongoDB

[STEP 2] Preprocessing data...
  ✓ Set datetime index from 'received_at'
  ✓ Kept 15 numeric columns
  ...

TRAINING COMPLETE!
✓ Trained 7 models for:
  - PM2.5
  - PM10
  - CO2
  - TVOC
  - Temperature
  - Humidity
  - Pressure
```

## Step 4: Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

## Step 5: Start the System

Once models are trained:

1. **Start Backend Server:**
   ```powershell
   cd backend
   python server.py
   ```

2. **Start LM Studio:**
   - Open LM Studio
   - Load TinyLlama-1.1B-Chat-v1.0
   - Start server (port 1234)

3. **Run Predictions:**
   ```powershell
   # Double-click or run:
   backend\run_predictions.bat
   ```

4. **Start Flutter App:**
   ```powershell
   flutter run
   ```

## Quick Checklist

- [ ] MongoDB installed and running
- [ ] MQTT data collector running (`mqtt2mongo (1).py`)
- [ ] Wait 10-15 minutes for data collection
- [ ] Train models (`python train_models_mongodb.py`)
- [ ] Install backend dependencies (`pip install -r backend/requirements.txt`)
- [ ] Start backend server (`python backend/server.py`)
- [ ] Start LM Studio with TinyLlama
- [ ] Run predictions (`backend\run_predictions.bat`)
- [ ] Start Flutter app (`flutter run`)

## Troubleshooting

### MongoDB Won't Start
```powershell
# Check if MongoDB service exists
sc query MongoDB

# If not installed, download from:
# https://www.mongodb.com/try/download/community
```

### No Data in MongoDB
```powershell
# Check if mqtt2mongo is running
# It should show messages like:
# ✓ Connected to MQTT broker
# ✓ Received message from ambience-3
```

### Training Fails
- Ensure MongoDB has at least 100 data points
- Check MongoDB connection: `mongosh mongodb://localhost:27017/milesiteaqi`
- Verify collection has data: `db['ambience-3'].count()`

## Next Steps

1. **Start MongoDB** (most important!)
2. **Collect data** with mqtt2mongo
3. **Train models** once you have data
4. **Run the system**

All the code is ready - you just need to set up the data pipeline!
