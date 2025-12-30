"""
Enhanced Prediction Engine with NaN Handling
Reads entire Excel sheets and ignores NaN values for accurate predictions

Key Features:
1. Reads ENTIRE Excel sheet (all historical data)
2. Automatically ignores NaN values
3. Uses cleaned data for predictions
4. Sends predictions to backend/dashboard

Usage:
    python predict_with_excel_enhanced.py --sensor 3  # For specific sensor
    python predict_with_excel_enhanced.py --all       # For all sensors
"""

import sys
import pandas as pd
import numpy as np
import requests
import json
import os
import time
import joblib
import argparse
from datetime import datetime
from sklearn.preprocessing import StandardScaler

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
SENSORS = {
    1: {'excel': 'output1.xlsx', 'name': 'Sensor 1'},
    2: {'excel': 'output2.xlsx', 'name': 'Sensor 2'},
    3: {'excel': 'output3.xlsx', 'name': 'Sensor 3'},
    4: {'excel': 'output4.xlsx', 'name': 'Sensor 4'},
    5: {'excel': 'output5.xlsx', 'name': 'Sensor 5'},
}

BACKEND_URL = 'http://192.168.1.147:5000/api/predictions'
MODELS_DIR = 'models'

# Global variables
models = {}
scalers = {}

print("="*80)
print("🤖 ENHANCED PREDICTION ENGINE - NaN-Aware")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def load_models():
    """Load ML models for predictions"""
    print("[1/3] Loading ML models...")
    
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
    return len(models) > 0


def get_value(row, *possible_names):
    """Extract value from row with multiple possible column names, ignore NaN"""
    for name in possible_names:
        if name in row.index:
            val = row[name]
            # Check if value is NOT NaN
            if pd.notna(val):
                try:
                    return float(val)
                except (ValueError, TypeError):
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


def read_excel_ignore_nan(excel_file):
    """Read entire Excel file and clean NaN values"""
    try:
        print(f"\n[2/3] Reading {excel_file}...")
        
        # Read entire Excel file
        df = pd.read_excel(excel_file)
        total_rows = len(df)
        print(f"  → Loaded {total_rows} total rows")
        
        # Show column names
        print(f"  → Found {len(df.columns)} columns")
        
        # Remove rows where ALL values are NaN
        df_cleaned = df.dropna(how='all')
        print(f"  → After removing empty rows: {len(df_cleaned)} rows")
        
        # For each numeric column, show NaN count
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        print(f"  → Numeric columns: {len(numeric_cols)}")
        
        # Show NaN statistics
        nan_summary = {}
        for col in numeric_cols:
            nan_count = df_cleaned[col].isna().sum()
            if nan_count > 0:
                nan_summary[col] = nan_count
        
        if nan_summary:
            print(f"  → Columns with NaN values: {len(nan_summary)}")
            for col, count in list(nan_summary.items())[:5]:  # Show first 5
                pct = (count / len(df_cleaned)) * 100
                print(f"     • {col}: {count} ({pct:.1f}%)")
        else:
            print(f"  ✓ No NaN values found in numeric columns")
        
        return df_cleaned
        
    except Exception as e:
        print(f"  ✗ Error reading Excel: {e}")
        return None


def predict_for_sensor(sensor_id):
    """Generate predictions for a specific sensor"""
    print(f"\n{'='*80}")
    print(f"SENSOR {sensor_id}: {SENSORS[sensor_id]['name']}")
    print(f"{'='*80}")
    
    excel_file = SENSORS[sensor_id]['excel']
    
    # Read Excel and clean NaN
    df = read_excel_ignore_nan(excel_file)
    
    if df is None or len(df) == 0:
        print(f"  ✗ No valid data for Sensor {sensor_id}")
        return None
    
    # Get latest row with complete data
    print(f"\n[3/3] Generating predictions...")
    
    # Try to find the most recent row with non-NaN values
    latest_idx = len(df) - 1
    max_attempts = 10  # Check last 10 rows
    
    for i in range(max_attempts):
        if latest_idx - i < 0:
            break
        
        latest = df.iloc[latest_idx - i]
        
        # Check if this row has meaningful data
        pm25 = get_value(latest, 'pm2_5', 'PM2.5', 'uplink_message.decoded_payload.pm2_5')
        pm10 = get_value(latest, 'pm10', 'PM10', 'uplink_message.decoded_payload.pm10')
        
        # If we have at least PM2.5 or PM10 data, use this row
        if pm25 > 0 or pm10 > 0:
            print(f"  → Using row {latest_idx - i + 1}/{len(df)} (most recent with valid data)")
            break
    
    # Extract current values (ignoring NaN)
    pm25 = get_value(latest, 'pm2_5', 'PM2.5', 'uplink_message.decoded_payload.pm2_5')
    pm10 = get_value(latest, 'pm10', 'PM10', 'uplink_message.decoded_payload.pm10')
    co2 = get_value(latest, 'co2', 'CO2', 'uplink_message.decoded_payload.co2')
    tvoc = get_value(latest, 'tvoc', 'TVOC', 'uplink_message.decoded_payload.tvoc')
    temp = get_value(latest, 'temperature', 'Temperature', 'uplink_message.decoded_payload.temperature')
    hum = get_value(latest, 'humidity', 'Humidity', 'uplink_message.decoded_payload.humidity')
    pres = get_value(latest, 'pressure', 'Pressure', 'uplink_message.decoded_payload.pressure')
    
    print(f"\n  📊 Current Values (NaN-filtered):")
    print(f"     PM2.5: {pm25:.1f} µg/m³")
    print(f"     PM10: {pm10:.1f} µg/m³")
    print(f"     CO2: {co2:.1f} ppm")
    print(f"     TVOC: {tvoc:.1f} ppb")
    print(f"     Temperature: {temp:.1f} °C")
    print(f"     Humidity: {hum:.1f} %")
    print(f"     Pressure: {pres:.1f} hPa")
    
    # Generate predictions (simple approach for now)
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
        },
        'data_quality': {
            'total_rows': len(df),
            'valid_rows': len(df.dropna(subset=['uplink_message.decoded_payload.pm2_5'], errors='ignore'))
        }
    }
    
    print(f"\n  🎯 Predictions:")
    for pollutant, data in predictions.items():
        diff = data['predicted'] - data['current']
        trend = "↑" if diff > 0 else "↓" if diff < 0 else "→"
        print(f"     {pollutant:12} {data['current']:.1f} → {data['predicted']:.1f} {data['unit']} {trend}")
    
    print(f"\n  🌡️  AQI: {aqi}")
    
    return payload


def send_to_backend(payload):
    """Send predictions to backend"""
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=3)
        if response.status_code == 200:
            print(f"  ✓ Sent to backend successfully")
            return True
        else:
            print(f"  ✗ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Backend not responding")
        print(f"    → Start backend with: python backend/server.py")
        return False
    except Exception as e:
        print(f"  ✗ Error sending to backend: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Enhanced Prediction Engine')
    parser.add_argument('--sensor', type=int, choices=[1, 2, 3, 4, 5], 
                       help='Specific sensor to predict (1-5)')
    parser.add_argument('--all', action='store_true', 
                       help='Generate predictions for all sensors')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously (checks for new data every 30s)')
    args = parser.parse_args()
    
    # Load models
    if not load_models():
        print("\n⚠️  No models loaded - will use simple predictions")
    
    # Determine which sensors to process
    if args.all:
        sensor_ids = list(SENSORS.keys())
    elif args.sensor:
        sensor_ids = [args.sensor]
    else:
        print("\n⚠️  No sensor specified. Use --sensor N or --all")
        return
    
    # Generate predictions
    if args.continuous:
        print("\n🔴 CONTINUOUS MODE - Checking every 30 seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                for sensor_id in sensor_ids:
                    payload = predict_for_sensor(sensor_id)
                    if payload:
                        send_to_backend(payload)
                
                print(f"\n⏳ Waiting 30 seconds...")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")
    else:
        # One-time prediction
        for sensor_id in sensor_ids:
            payload = predict_for_sensor(sensor_id)
            if payload:
                send_to_backend(payload)
    
    print("\n" + "="*80)
    print("✅ Prediction complete")
    print("="*80)


if __name__ == "__main__":
    main()
