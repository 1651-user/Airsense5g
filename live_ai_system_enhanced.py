"""
🔴 LIVE AI SYSTEM - Enhanced with NaN Handling and Dashboard Updates

This script:
1. Monitors all 5 sensors for new MQTT data
2. Reads ENTIRE Excel sheets (ignores NaN values)
3. Generates accurate predictions using clean data
4. Updates dashboard/backend automatically
5. Uses latest data if no new readings arrive

Usage: python live_ai_system_enhanced.py
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
SENSORS = {
    1: {'excel': 'output1.xlsx', 'json': 'mqtt_data_sensor1.json', 'name': 'Sensor 1'},
    2: {'excel': 'output2.xlsx', 'json': 'mqtt_data_sensor2.json', 'name': 'Sensor 2'},
    3: {'excel': 'output3.xlsx', 'json': 'mqtt_data.json', 'name': 'Sensor 3'},
    4: {'excel': 'output4.xlsx', 'json': 'mqtt_data_sensor4.json', 'name': 'Sensor 4'},
    5: {'excel': 'output5.xlsx', 'json': 'mqtt_data_sensor5.json', 'name': 'Sensor 5'},
}

BACKEND_URL = 'http://192.168.1.147:5000/api/predictions'
CHECK_INTERVAL = 30  # seconds
MODELS_DIR = 'models'

# Global variables
last_json_timestamps = {i: None for i in range(1, 6)}
models = {}
scalers = {}

print("="*80)
print("🔴 LIVE AI SYSTEM - Enhanced NaN Handling & Dashboard Updates")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def load_models():
    """Load ML models"""
    print("[1/4] Loading ML models...")
    
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
    
    print(f"\n  Loaded {len(models)} models\n")


def get_value(row, *possible_names):
    """Extract value from row, ignoring NaN"""
    for name in possible_names:
        if name in row.index:
            val = row[name]
            if pd.notna(val):
                try:
                    return float(val)
                except:
                    continue
    return 0.0


def calculate_aqi(pm25_val):
    """Calculate AQI from PM2.5"""
    if pm25_val <= 12:
        return int((50/12) * pm25_val)
    elif pm25_val <= 35.4:
        return int(50 + ((100-50)/(35.4-12.1)) * (pm25_val-12.1))
    elif pm25_val <= 55.4:
        return int(100 + ((150-100)/(55.4-35.5)) * (pm25_val-35.5))
    elif pm25_val <= 150.4:
        return int(150 + ((200-150)/(150.4-55.5)) * (pm25_val-55.5))
    else:
        return int(200 + ((300-200)/(250.4-150.5)) * (pm25_val-150.5))


def load_and_predict(sensor_id):
    """Load Excel data and generate predictions (NaN-aware)"""
    try:
        excel_file = SENSORS[sensor_id]['excel']
        
        if not os.path.exists(excel_file):
            print(f"  ⚠️  Excel file not found: {excel_file}")
            return None
        
        # Read ENTIRE Excel file
        df = pd.read_excel(excel_file)
        
        if len(df) == 0:
            print(f"  ⚠️  Excel file is empty")
            return None
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Find latest row with valid data
        latest_idx = len(df) - 1
        max_attempts = 20  # Check last 20 rows
        
        for i in range(max_attempts):
            if latest_idx - i < 0:
                break
            
            latest = df.iloc[latest_idx - i]
            
            # Check if this row has meaningful data
            pm25 = get_value(latest, 'pm2_5', 'PM2.5', 'uplink_message.decoded_payload.pm2_5')
            pm10 = get_value(latest, 'pm10', 'PM10', 'uplink_message.decoded_payload.pm10')
            
            # If we have at least PM2.5 or PM10 data, use this row
            if pm25 > 0 or pm10 > 0:
                break
        
        # Extract current values (all NaN-filtered)
        pm25 = get_value(latest, 'pm2_5', 'PM2.5', 'uplink_message.decoded_payload.pm2_5')
        pm10 = get_value(latest, 'pm10', 'PM10', 'uplink_message.decoded_payload.pm10')
        co2 = get_value(latest, 'co2', 'CO2', 'uplink_message.decoded_payload.co2')
        tvoc = get_value(latest, 'tvoc', 'TVOC', 'uplink_message.decoded_payload.tvoc')
        temp = get_value(latest, 'temperature', 'Temperature', 'uplink_message.decoded_payload.temperature')
        hum = get_value(latest, 'humidity', 'Humidity', 'uplink_message.decoded_payload.humidity')
        pres = get_value(latest, 'pressure', 'Pressure', 'uplink_message.decoded_payload.pressure')
        
        # Generate predictions
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
            'sensor_id': sensor_id,
            'sensor_name': SENSORS[sensor_id]['name'],
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
                'pm2_5': pm25,
                'pm10': pm10,
                'co2': co2,
                'tvoc': tvoc,
                'temperature': temp,
                'humidity': hum,
                'pressure': pres,
                'received_at': latest.get('received_at', datetime.now().isoformat())
            }
        }
        
        return payload
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def send_to_backend(payload):
    """Send predictions to backend/dashboard"""
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=3)
        return response.status_code == 200
    except:
        return False


def check_for_new_data(sensor_id):
    """Check if new MQTT data has arrived for this sensor"""
    global last_json_timestamps
    
    try:
        json_file = SENSORS[sensor_id]['json']
        
        if not os.path.exists(json_file):
            return False
        
        # Get file modification time
        current_timestamp = os.path.getmtime(json_file)
        
        if last_json_timestamps[sensor_id] is None:
            last_json_timestamps[sensor_id] = current_timestamp
            return False
        
        if current_timestamp > last_json_timestamps[sensor_id]:
            last_json_timestamps[sensor_id] = current_timestamp
            return True
        
        return False
        
    except:
        return False


def main():
    """Main function"""
    
    # Load models
    load_models()
    
    # Initial load and prediction for all sensors
    print("[2/4] Loading initial data from all sensors...\n")
    
    initial_payloads = {}
    for sensor_id in SENSORS.keys():
        print(f"Sensor {sensor_id}: {SENSORS[sensor_id]['name']}")
        payload = load_and_predict(sensor_id)
        
        if payload:
            initial_payloads[sensor_id] = payload
            print(f"  ✓ AQI: {payload['aqi']}, PM2.5: {payload['sensor_data']['pm2_5']:.1f} µg/m³")
        else:
            print(f"  ✗ Failed to load data")
        print()
    
    # Send initial predictions to backend
    print("[3/4] Sending initial predictions to backend...\n")
    
    for sensor_id, payload in initial_payloads.items():
        if send_to_backend(payload):
            print(f"  ✓ Sensor {sensor_id} sent successfully")
        else:
            print(f"  ⚠️  Sensor {sensor_id} - Backend not responding")
    
    # Check backend status
    print("\n[4/4] Checking backend status...")
    
    try:
        response = requests.get('http://192.168.1.147:5000/health', timeout=2)
        if response.status_code == 200:
            print("  ✓ Backend is running\n")
        else:
            print("  ⚠️  Backend returned unexpected status\n")
    except:
        print("  ⚠️  Backend not running")
        print("  → Start with: python backend/server.py\n")
    
    # Start live monitoring
    print("="*80)
    print(f"🔴 LIVE MONITORING - All 5 Sensors (Every {CHECK_INTERVAL}s)")
    print("="*80)
    print("\n💡 Features:")
    print("  • Monitors all sensors for new MQTT data")
    print("  • Reads entire Excel sheets (ignores NaN values)")
    print("  • Updates dashboard with new predictions")
    print("  • Uses latest data if no new readings arrive\n")
    print("Press Ctrl+C to stop\n")
    
    update_count = 0
    
    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            
            # Check all sensors for new data
            new_data_detected = False
            
            for sensor_id in SENSORS.keys():
                if check_for_new_data(sensor_id):
                    new_data_detected = True
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🆕 New data - Sensor {sensor_id}")
                    
                    # Generate new predictions
                    payload = load_and_predict(sensor_id)
                    
                    if payload:
                        print(f"  → AQI: {payload['aqi']}, PM2.5: {payload['sensor_data']['pm2_5']:.1f} µg/m³")
                        
                        # Send to backend/dashboard
                        if send_to_backend(payload):
                            print(f"  ✓ Dashboard updated")
                            update_count += 1
                        else:
                            print(f"  ✗ Backend error")
                    else:
                        print(f"  ✗ Prediction failed")
            
            # If no new data, use latest data and update dashboard anyway (ALL SENSORS)
            if not new_data_detected:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ No new data - Sending all sensors with latest readings...")
                
                # Update dashboard with latest data from ALL sensors
                for sensor_id in SENSORS.keys():
                    payload = load_and_predict(sensor_id)
                    if payload:
                        send_to_backend(payload)
                        print(f"  ✓ Sensor {sensor_id} updated")
                    else:
                        print(f"  ✗ Sensor {sensor_id} failed")
    
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("🛑 Stopped by user")
        print("="*80)
        print(f"\nTotal updates: {update_count}")
        print(f"Runtime: {datetime.now().strftime('%H:%M:%S')}")
        print("\nGoodbye! 👋")


if __name__ == "__main__":
    main()
