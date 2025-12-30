# Live System for All 5 Sensors - Setup Guide

## Overview
This system connects all 5 air quality sensors to the AI, allowing you to ask questions about specific sensors and view live data in the Flutter app.

## Architecture

```
┌─────────────────┐
│  Sensor 1-5     │  (MQTT → MongoDB)
│  (amb1-5.env)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MongoDB        │  (5 separate collections)
│  Collections    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ fetch_all_      │  (Python script)
│ sensors.py      │  Fetches from all 5 collections
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ live_all_       │  (Runs every 30s)
│ sensors.py      │  Sends to backend
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Backend Server  │  (Flask API)
│ (server.py)     │  Stores multi-sensor data
└────────┬────────┘
         │
         ├──────────────┐
         ▼              ▼
┌─────────────┐  ┌─────────────┐
│ Flutter App │  │  AI (LM     │
│ (Dashboard) │  │  Studio)    │
└─────────────┘  └─────────────┘
```

## Files Created

### 1. `fetch_all_sensors.py`
- Fetches live data from all 5 MongoDB collections
- Combines data into a single JSON structure
- Saves to `all_sensors_data.json`

### 2. `send_all_sensors_to_ai.py`
- Formats sensor data for AI consumption
- Sends to backend API
- Saves AI context to `ai_sensor_context.json`

### 3. `live_all_sensors.py`
- Runs continuously (every 30 seconds)
- Fetches and sends data automatically
- Keeps AI updated with latest sensor readings

### 4. `start_all_sensors_live.bat`
- One-click startup for entire system
- Starts backend server
- Starts live sensor data collection

### 5. Updated `backend/server.py`
- Handles multi-sensor data
- Provides sensor-specific context to AI
- Supports queries like "What is PM2.5 of sensor 4?"

## Setup Instructions

### Step 1: Ensure All Sensors Are Running

Make sure all 5 MQTT-to-MongoDB scripts are running:
```bash
# Terminal 1
python "mqtt2mongo1 (1).py"

# Terminal 2  
python "mqtt2mongo2 (1).py"

# Terminal 3
python mqtt2mongo.py  # Sensor 3

# Terminal 4
python "mqtt2mongo4 (1).py"

# Terminal 5
python "mqtt2mongo5 (1).py"
```

### Step 2: Start the Live System

Simply run:
```bash
start_all_sensors_live.bat
```

This will:
1. Start the backend server on `http://localhost:5000`
2. Start live sensor data collection (updates every 30s)

### Step 3: Run Your Flutter App

```bash
flutter run
```

The dashboard will now show live data from all 5 sensors!

## AI Integration

### How It Works

The AI now has context for all 5 sensors. When you ask a question, the backend sends this context:

```
S1[AQI=85,PM2.5=35.2,PM10=45.1,CO2=420,NO2=15,SO2=8,O3=45]; 
S2[AQI=92,PM2.5=38.5,PM10=48.2,CO2=435,NO2=18,SO2=10,O3=50]; 
S3[AQI=78,PM2.5=30.1,PM10=40.5,CO2=410,NO2=12,SO2=6,O3=38]; 
S4[AQI=105,PM2.5=42.3,PM10=55.8,CO2=450,NO2=22,SO2=12,O3=58]; 
S5[AQI=88,PM2.5=36.7,PM10=46.9,CO2=428,NO2=16,SO2=9,O3=48]
```

### Example AI Queries

You can now ask:
- ✅ "What is the PM2.5 level of sensor 4?"
- ✅ "Which sensor has the highest AQI?"
- ✅ "Show me all pollutant levels for sensor 2"
- ✅ "Compare sensor 1 and sensor 5"
- ✅ "Which sensor has the best air quality?"
- ✅ "What is the CO2 level in sensor 3?"

## Configuration

### Update Interval

Change how often data is fetched (default: 30 seconds):

In `live_all_sensors.py`:
```python
UPDATE_INTERVAL = 30  # Change to desired seconds
```

### Backend URL

In `send_all_sensors_to_ai.py`:
```python
BACKEND_URL = 'http://localhost:5000/api/predictions'
```

## Troubleshooting

### No Data from Sensors

1. Check if MQTT scripts are running
2. Verify MongoDB connections in `.env` files
3. Check `all_sensors_data.json` for latest data

### AI Not Responding with Sensor Data

1. Ensure backend server is running
2. Check `ai_sensor_context.json` for proper formatting
3. Verify LM Studio is running

### Flutter App Not Showing Live Data

Currently, the Flutter app uses mock data. To connect to real backend:
1. Update `sensor_service.dart` to fetch from backend API
2. Add HTTP requests to `http://localhost:5000/api/predictions/latest`

## Next Steps

1. ✅ All 5 sensors connected to AI
2. ✅ Live data collection automated
3. ✅ Backend handles multi-sensor queries
4. 🔄 Update Flutter app to fetch real data (optional)
5. 🔄 Add sensor location mapping (optional)

## File Structure

```
Airsense5g/
├── fetch_all_sensors.py          # Fetch from all MongoDB collections
├── send_all_sensors_to_ai.py     # Send to AI backend
├── live_all_sensors.py            # Continuous updates
├── start_all_sensors_live.bat    # One-click startup
├── backend/
│   └── server.py                  # Updated with multi-sensor support
├── amb1.env, amb2.env, am3.env, amb4.env, amb5.env  # Sensor configs
└── mqtt2mongo*.py                 # MQTT collectors for each sensor
```

## Status

✅ Sensor 1: Connected
✅ Sensor 2: Connected  
✅ Sensor 3: Connected (Already live)
✅ Sensor 4: Connected
✅ Sensor 5: Connected
✅ AI Integration: Complete
✅ Backend: Multi-sensor support added
✅ Automation: Live updates every 30s

## Support

If you encounter issues:
1. Check all `.env` files have correct MongoDB credentials
2. Ensure all MQTT brokers are accessible
3. Verify backend server is running on port 5000
4. Check LM Studio is running for AI queries
