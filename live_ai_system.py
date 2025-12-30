"""
🔴 LIVE AI SYSTEM - Auto-Update Every 30 Seconds

This script:
1. Loads all data from Excel on startup
2. Generates predictions
3. Sends to backend
4. Checks for new MQTT data every 30 seconds
5. Auto-updates predictions when new data arrives
6. Keeps AI always up-to-date

Usage: python live_ai_system.py
"""

import sys
import pandas as pd
import numpy as np
import requests
import json
import os
import time
import joblib
from datetime import datetime
from sklearn.preprocessing import StandardScaler

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
EXCEL_FILE = 'output.xlsx'
JSON_FILE = 'mqtt_data.json'
BACKEND_URL = 'http://192.168.1.147:5000/api/predictions'
CHECK_INTERVAL = 30  # seconds
MODELS_DIR = 'models'

# Global variables
last_json_timestamp = None
models = {}
scalers = {}

print("="*80)
print("🔴 LIVE AI SYSTEM - Auto-Update Every 30 Seconds")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# STEP 1: LOAD MODELS
# ============================================================================
print("[1/5] Loading ML models...")

targets = ['pm2_5', 'pm10', 'co2', 'tvoc', 'temperature', 'humidity', 'pressure']

for target in targets:
    model_path = f'{MODELS_DIR}/{target}_model.pkl'
    scaler_path = f'{MODELS_DIR}/{target}_scaler.pkl'
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        try:
            models[target] = joblib.load(model_path)
            scalers[target] = joblib.load(scaler_path)
            print(f"  ✓ {target}")
        except Exception as e:
            print(f"  ✗ {target}: {e}")
    else:
        print(f"  ⚠️  {target}: Model not found")

print(f"\n  Loaded {len(models)} models\n")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_value(row, *possible_names):
    """Extract value from row with multiple possible column names"""
    for name in possible_names:
        if name in row.index:
            val = row[name]
            return float(val) if pd.notna(val) else 0.0
    return 0.0

def calculate_aqi(pm25_val):
    """Calculate AQI from PM2.5"""
    if pm25_val <= 12: return int((50/12) * pm25_val)
    elif pm25_val <= 35.4: return int(50 + ((100-50)/(35.4-12.1)) * (pm25_val-12.1))
    elif pm25_val <= 55.4: return int(100 + ((150-100)/(55.4-35.5)) * (pm25_val-35.5))
    elif pm25_val <= 150.4: return int(150 + ((200-150)/(150.4-55.5)) * (pm25_val-55.5))
    else: return int(200 + ((300-200)/(250.4-150.5)) * (pm25_val-150.5))

def predict_value(target, current_value, history):
    """Generate prediction using ML model"""
    if target not in models or len(history) < 3:
        # Fallback to simple prediction
        return round(current_value * 1.01, 1)
    
    try:
        # Use last 3 values
        features = np.array(history[-3:]).reshape(1, -1)
        features_scaled = scalers[target].transform(features)
        prediction = models[target].predict(features_scaled)[0]
        return round(prediction, 1)
    except:
        return round(current_value * 1.01, 1)

def load_and_predict():
    """Load Excel data and generate predictions"""
    try:
        # Read Excel
        df = pd.read_excel(EXCEL_FILE)
        
        if len(df) == 0:
            print("  ⚠️  Excel file is empty")
            return None
        
        # Get latest row
        latest = df.iloc[-1]
        
        # Extract current values
        pm25 = get_value(latest, 'pm2_5', 'PM2.5', 'uplink_message.decoded_payload.pm2_5')
        pm10 = get_value(latest, 'pm10', 'PM10', 'uplink_message.decoded_payload.pm10')
        co2 = get_value(latest, 'co2', 'CO2', 'uplink_message.decoded_payload.co2')
        tvoc = get_value(latest, 'tvoc', 'TVOC', 'uplink_message.decoded_payload.tvoc')
        temp = get_value(latest, 'temperature', 'Temperature', 'uplink_message.decoded_payload.temperature')
        hum = get_value(latest, 'humidity', 'Humidity', 'uplink_message.decoded_payload.humidity')
        pres = get_value(latest, 'pressure', 'Pressure', 'uplink_message.decoded_payload.pressure')
        
        # Get history for predictions (last 10 rows)
        history_size = min(10, len(df))
        history_df = df.tail(history_size)
        
        # Generate predictions (simple fallback for now)
        predictions = {
            'PM2.5': {
                'predicted': round(pm25 * 1.02, 1),
                'current': round(pm25, 1),
                'unit': 'µg/m³'
            },
            'PM10': {
                'predicted': round(pm10 * 1.02, 1),
                'current': round(pm10, 1),
                'unit': 'µg/m³'
            },
            'CO2': {
                'predicted': round(co2 * 0.99, 1),
                'current': round(co2, 1),
                'unit': 'ppm'
            },
            'TVOC': {
                'predicted': round(tvoc * 1.01, 1),
                'current': round(tvoc, 1),
                'unit': 'ppb'
            },
            'Temperature': {
                'predicted': round(temp + 0.1, 1),
                'current': round(temp, 1),
                'unit': '°C'
            },
            'Humidity': {
                'predicted': round(hum - 0.5, 1),
                'current': round(hum, 1),
                'unit': '%'
            },
            'Pressure': {
                'predicted': round(pres, 1),
                'current': round(pres, 1),
                'unit': 'hPa'
            }
        }
        
        # Calculate AQI
        aqi = calculate_aqi(pm25)
        
        # Prepare payload
        payload = {
            'timestamp': datetime.now().isoformat(),
            'aqi': aqi,
            'pm25': predictions['PM2.5']['predicted'],
            'pm10': predictions['PM10']['predicted'],
            'co2': predictions['CO2']['predicted'],
            'tvoc': predictions['TVOC']['predicted'],
            'temperature': predictions['Temperature']['predicted'],
            'humidity': predictions['Humidity']['predicted'],
            'pressure': predictions['Pressure']['predicted'],
            'predictions': predictions,
            'sensor_data': {
                'pm2_5': pm25, 'pm10': pm10, 'co2': co2, 'tvoc': tvoc,
                'temperature': temp, 'humidity': hum, 'pressure': pres,
                'received_at': latest.get('received_at', datetime.now().isoformat())
            }
        }
        
        return payload
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def send_to_backend(payload):
    """Send predictions to backend"""
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=3)
        return response.status_code == 200
    except:
        return False

def check_for_new_data():
    """Check if new MQTT data has arrived"""
    global last_json_timestamp
    
    try:
        if not os.path.exists(JSON_FILE):
            return False
        
        # Get file modification time
        current_timestamp = os.path.getmtime(JSON_FILE)
        
        if last_json_timestamp is None:
            last_json_timestamp = current_timestamp
            return False
        
        if current_timestamp > last_json_timestamp:
            last_json_timestamp = current_timestamp
            return True
        
        return False
        
    except:
        return False

# ============================================================================
# STEP 2: INITIAL LOAD
# ============================================================================
print("[2/5] Loading Excel data...")

payload = load_and_predict()

if payload:
    print(f"  ✓ Loaded {EXCEL_FILE}")
    print(f"  → AQI: {payload['aqi']}")
    print(f"  → PM2.5: {payload['sensor_data']['pm2_5']:.1f} µg/m³")
    print(f"\n  📊 Generated Predictions:")
    for pollutant, data in payload['predictions'].items():
        diff = data['predicted'] - data['current']
        trend = "↑" if diff > 0 else "↓" if diff < 0 else "→"
        print(f"     {pollutant:12} {data['current']:.1f} → {data['predicted']:.1f} {data['unit']} {trend}")
else:
    print("  ❌ Failed to load data")
    exit(1)

# ============================================================================
# STEP 3: SEND TO BACKEND
# ============================================================================
print("\n[3/5] Sending initial predictions to backend...")

if send_to_backend(payload):
    print("  ✓ Sent successfully")
    print(f"  ✓ AI now has {len(payload['predictions'])} predictions")
else:
    print("  ⚠️  Backend not responding (start with: python backend/server.py)")

# ============================================================================
# STEP 4: BACKEND CHECK
# ============================================================================
print("\n[4/5] Checking backend status...")

try:
    response = requests.get('http://192.168.1.147:5000/health', timeout=2)
    if response.status_code == 200:
        print("  ✓ Backend is running")
    else:
        print("  ⚠️  Backend returned unexpected status")
except:
    print("  ⚠️  Backend not running")
    print("  → Start with: python backend/server.py")

# ============================================================================
# STEP 5: LIVE MONITORING
# ============================================================================
print("\n[5/5] Starting live monitoring...")
print("="*80)
print(f"🔴 LIVE MODE - Checking every {CHECK_INTERVAL} seconds")
print("="*80)
print("\nPress Ctrl+C to stop\n")

update_count = 0

try:
    while True:
        # Wait for interval
        time.sleep(CHECK_INTERVAL)
        
        # Check for new data
        if check_for_new_data():
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🆕 New data detected!")
            
            # Update Excel
            print("  📊 Updating Excel...", end=" ")
            
            max_retries = 3
            retry_delay = 1  # seconds (shorter for live updates)
            excel_updated = False
            
            for attempt in range(max_retries):
                try:
                    with open(JSON_FILE, 'r') as f:
                        json_data = json.load(f)
                    
                    if json_data:
                        new_df = pd.DataFrame(json_data)
                        existing_df = pd.read_excel(EXCEL_FILE)
                        
                        # Quick append
                        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                        combined_df.to_excel(EXCEL_FILE, index=False)
                        print("✓")
                        excel_updated = True
                        break  # Success, exit retry loop
                    else:
                        print("⚠️  No data")
                        break
                        
                except PermissionError:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)  # Wait before retry
                    else:
                        print(f"✗ [Errno 13] Permission denied: '{EXCEL_FILE}'")
                        print(f"     💡 Close {EXCEL_FILE} in Excel to allow updates")
                        
                except Exception as e:
                    print(f"✗ {e}")
                    break
            
            # Generate new predictions
            print("  🤖 Generating predictions...", end=" ")
            payload = load_and_predict()
            
            if payload:
                print("✓")
                
                # Send to backend
                print("  🚀 Sending to AI...", end=" ")
                if send_to_backend(payload):
                    print("✓")
                    update_count += 1
                    print(f"  ✅ Update #{update_count} - AQI: {payload['aqi']}")
                else:
                    print("✗")
            else:
                print("✗")
        else:
            # No new data
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Waiting... (Updates: {update_count})", end='\r')

except KeyboardInterrupt:
    print("\n\n" + "="*80)
    print("🛑 Stopped by user")
    print("="*80)
    print(f"\nTotal updates: {update_count}")
    print(f"Runtime: {datetime.now().strftime('%H:%M:%S')}")
    print("\nGoodbye! 👋")
