"""
Quick Fix: Load Excel data and generate immediate predictions for Sensor 3
Run this BEFORE starting mqtt_to_phi2.py

Usage:
    python quick_predict_sensor3.py
"""

import pandas as pd
import numpy as np
import joblib
import os
import json
import requests
from datetime import datetime

EXCEL_FILE = 'output.xlsx'
MODEL_DIR = 'models'
BACKEND_URL = 'http://192.168.1.147:5000/api/predictions'

print("="*80)
print("QUICK PREDICTIONS FROM EXCEL - SENSOR 3")
print("="*80)

# Load ML models
print("\n[MODELS] Loading prediction models...")
models = {}
scalers = {}

model_files = {
    'PM2.5': ('pm25_model.pkl', 'pm25_scaler.pkl'),
    'PM10': ('pm10_model.pkl', 'pm10_scaler.pkl'),
    'CO2': ('co2_model.pkl', 'co2_scaler.pkl'),
    'TVOC': ('tvoc_model.pkl', 'tvoc_scaler.pkl'),
    'Temperature': ('temperature_model.pkl', 'temperature_scaler.pkl'),
    'Humidity': ('humidity_model.pkl', 'humidity_scaler.pkl'),
    'Pressure': ('pressure_model.pkl', 'pressure_scaler.pkl')
}

for target, (model_file, scaler_file) in model_files.items():
    model_path = os.path.join(MODEL_DIR, model_file)
    scaler_path = os.path.join(MODEL_DIR, scaler_file)
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        try:
            models[target] = joblib.load(model_path)
            scalers[target] = joblib.load(scaler_path)
            print(f"  OK Loaded {target} model")
        except Exception as e:
            print(f"  ERROR loading {target}: {e}")

print(f"  OK Loaded {len(models)} models\n")

# Load Excel data
print(f"[EXCEL] Loading historical data from {EXCEL_FILE}...")
df = pd.read_excel(EXCEL_FILE)
print(f"  OK Loaded {len(df)} total records")

# Get last 100 rows
df_recent = df.tail(100)
sensor_data_buffer = df_recent.to_dict('records')
print(f"  OK Using last {len(sensor_data_buffer)} records for predictions\n")

# Generate predictions
print("[PREDICTIONS] Generating predictions...")

df_numeric = df_recent.select_dtypes(include=[np.number])
predictions = {}

for target, model in models.items():
    try:
        target_col = None
        for col in df_numeric.columns:
            if target.lower().replace('.', '').replace(' ', '') in col.lower().replace('_', ''):
                target_col = col
                break
        
        if target_col is None:
            continue
        
        last_3_values = df_numeric[target_col].iloc[-3:].values
        X = last_3_values.reshape(1, -1)
        
        scaler = scalers[target]
        X_scaled = scaler.transform(X)
        prediction = model.predict(X_scaled)[0]
        
        current = df_numeric[target_col].iloc[-1]
        
        predictions[target] = {
            'predicted': round(float(prediction), 2),
            'current': round(float(current), 2)
        }
        
    except Exception as e:
        continue

if predictions:
    print(f"  OK Generated {len(predictions)} predictions:\n")
    for target, values in predictions.items():
        arrow = "↑" if values['predicted'] > values['current'] else "↓" if values['predicted'] < values['current'] else "→"
        print(f"    {target}: {values['current']} → {values['predicted']} {arrow}")
    
    # Calculate AQI
    aqi = 0
    if 'PM2.5' in predictions:
        pm25 = predictions['PM2.5']['predicted']
        if pm25 <= 12.0:
            aqi = int((50 / 12.0) * pm25)
        elif pm25 <= 35.4:
            aqi = int(50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1))
        elif pm25 <= 55.4:
            aqi = int(100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5))
        else:
            aqi = 150
    
    # Send to backend
    print(f"\n[BACKEND] Sending predictions to AI (AQI: {aqi})...")
    
    payload = {
        'timestamp': datetime.now().isoformat(),
        'aqi': aqi,
        'pm25': predictions.get('PM2.5', {}).get('predicted', 0),
        'pm10': predictions.get('PM10', {}).get('predicted', 0),
        'co2': predictions.get('CO2', {}).get('predicted', 0),
        'tvoc': predictions.get('TVOC', {}).get('predicted', 0),
        'temperature': predictions.get('Temperature', {}).get('predicted', 0),
        'humidity': predictions.get('Humidity', {}).get('predicted', 0),
        'pressure': predictions.get('Pressure', {}).get('predicted', 0),
        'predictions': predictions,
        'sensor_data': sensor_data_buffer[-1] if sensor_data_buffer else {}
    }
    
    try:
        response = requests.post(
            BACKEND_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"  OK Sent to backend successfully!")
            print(f"  ✓ AI now has predictions!")
        else:
            print(f"  WARNING Backend returned {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("  WARNING Backend not running (start with: python backend/server.py)")
    except Exception as e:
        print(f"  ERROR: {e}")
else:
    print("  WARNING Could not generate predictions")

print("\n" + "="*80)
print("DONE! Now you can start mqtt_to_phi2.py for live updates")
print("="*80)
