"""
Complete Startup Script - All 5 Sensors with Excel Predictions
Loads historical data from Excel and generates immediate predictions for all sensors

Usage:
    python start_with_predictions.py
"""

import sys
import pandas as pd
import numpy as np
import joblib
import os
import json
import requests
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Sensor configurations
SENSORS = {
    1: {'excel': 'output1.xlsx', 'name': 'Sensor 1'},
    2: {'excel': 'output2.xlsx', 'name': 'Sensor 2'},
    3: {'excel': 'output3.xlsx', 'name': 'Sensor 3'},
    4: {'excel': 'output4.xlsx', 'name': 'Sensor 4'},
    5: {'excel': 'output5.xlsx', 'name': 'Sensor 5'},
}

MODEL_DIR = 'models'
BACKEND_URL = 'http://192.168.1.147:5000/api/predictions'

print("="*80)
print("LOADING ALL 5 SENSORS WITH EXCEL PREDICTIONS")
print("="*80)

# Load ML models once (shared across all sensors)
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


def calculate_aqi(pm25):
    """Calculate AQI from PM2.5"""
    if pm25 <= 12.0:
        return int((50 / 12.0) * pm25)
    elif pm25 <= 35.4:
        return int(50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1))
    elif pm25 <= 55.4:
        return int(100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5))
    elif pm25 <= 150.4:
        return int(150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5))
    elif pm25 <= 250.4:
        return int(200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5))
    else:
        return int(300 + ((500 - 300) / (500.4 - 250.5)) * (pm25 - 250.5))


def generate_predictions(sensor_id):
    """Generate predictions for a specific sensor from its Excel file"""
    excel_file = SENSORS[sensor_id]['excel']
    sensor_name = SENSORS[sensor_id]['name']
    
    print(f"\n{'='*80}")
    print(f"[{sensor_name}] Processing...")
    print(f"{'='*80}")
    
    if not os.path.exists(excel_file):
        print(f"  SKIP - {excel_file} not found")
        return False
    
    try:
        # Load Excel data
        print(f"[EXCEL] Loading {excel_file}...")
        df = pd.read_excel(excel_file)
        print(f"  OK Loaded {len(df)} total records")
        
        # Get last 100 rows
        df_recent = df.tail(100)
        
        # Extract ONLY the 7 target columns we care about
        target_columns = ['pm2_5', 'pm10', 'co2', 'tvoc', 'temperature', 'humidity', 'pressure']
        
        # Find columns - check both short names AND long names (for Sensor 2)
        available_cols = {}
        all_columns = df_recent.columns.tolist()
        
        for target in target_columns:
            found_col = None
            
            # Try both short and long names
            short_col = target if target in all_columns else None
            long_col = None
            
            # Find long column name
            for col in all_columns:
                if target in col.lower() and 'decoded_payload' in col.lower():
                    long_col = col
                    break
            
            # Prefer the one with more data
            if short_col and long_col:
                # Both exist - check which has more non-NaN data
                short_data = df_recent[short_col].notna().sum()
                long_data = df_recent[long_col].notna().sum()
                found_col = long_col if long_data > short_data else short_col
            elif long_col:
                found_col = long_col
            elif short_col:
                found_col = short_col
            
            if found_col:
                available_cols[target] = found_col
        
        if not available_cols:
            print(f"  SKIP - None of the target columns found")
            return False
        
        # Extract the found columns and rename to short names
        df_extracted = pd.DataFrame()
        for target, actual_col in available_cols.items():
            df_extracted[target] = df_recent[actual_col]
        
        df_numeric = df_extracted
        
        print(f"  OK Using last {len(df_recent)} records")
        print(f"  Found columns: {', '.join(available_cols.keys())}\n")
        
        # Generate predictions
        print("[PREDICTIONS] Generating...")
        predictions = {}
        
        for target, model in models.items():
            try:
                # Map target names to actual column names
                target_mapping = {
                    'PM2.5': 'pm2_5',
                    'PM10': 'pm10', 
                    'CO2': 'co2',
                    'TVOC': 'tvoc',
                    'Temperature': 'temperature',
                    'Humidity': 'humidity',
                    'Pressure': 'pressure'
                }
                
                # Get the expected column name
                expected_col = target_mapping.get(target)
                if expected_col is None:
                    continue
                
                # Find the column in dataframe
                target_col = None
                if expected_col in df_numeric.columns:
                    target_col = expected_col
                else:
                    # Try finding with long name pattern
                    for col in df_numeric.columns:
                        if expected_col in col.lower():
                            target_col = col
                            break
                
                if target_col is None:
                    continue
                
                # Drop NaN values before prediction
                df_clean = df_numeric[[target_col]].dropna()
                
                # PM2.5 model needs 8 features, others need 3
                required_values = 8 if target == 'PM2.5' else 3
                
                if len(df_clean) < required_values:
                    continue
                
                last_n_values = df_clean[target_col].iloc[-required_values:].values
                X = last_n_values.reshape(1, -1)
                
                scaler = scalers[target]
                X_scaled = scaler.transform(X)
                prediction = model.predict(X_scaled)[0]
                
                current = df_clean[target_col].iloc[-1]
                
                predictions[target] = {
                    'predicted': round(float(prediction), 2),
                    'current': round(float(current), 2)
                }
                
            except Exception as e:
                if target == 'PM2.5':
                    print(f"  DEBUG: PM2.5 prediction failed - {e}")
                continue
        
        if predictions:
            print(f"  OK Generated {len(predictions)} predictions:\n")
            for target, values in predictions.items():
                change = "UP" if values['predicted'] > values['current'] else "DOWN" if values['predicted'] < values['current'] else "SAME"
                print(f"    {target}: {values['current']} -> {values['predicted']} ({change})")
            
            return predictions
        else:
            print("  WARNING Could not generate predictions")
            return None
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def main():
    """Process all sensors and send data in multi-sensor format"""
    
    # Collect all sensor data
    all_sensor_data = {}
    successful = 0
    
    # Generate predictions for all sensors
    for sensor_id in range(1, 6):
        sensor_info = SENSORS.get(sensor_id)
        if not sensor_info:
            continue
            
        excel_file = sensor_info['excel']
        sensor_name = sensor_info['name']
        
        try:
            print(f"\n{'='*80}")
            print(f"[Sensor {sensor_id}] Processing...")
            print(f"{'='*80}")
            
            # Generate predictions
            predictions = generate_predictions(sensor_id)
            
            if predictions:
                # Calculate AQI from CURRENT PM2.5 (not predicted)
                aqi = 0
                if 'PM2.5' in predictions:
                    aqi = calculate_aqi(predictions['PM2.5']['current'])
                
                # Store in multi-sensor format
                all_sensor_data[f'sensor_{sensor_id}'] = {
                    'name': sensor_name,
                    'aqi': aqi,
                    'pollutants': {
                        'pm2_5': predictions.get('PM2.5', {}).get('current', 0),
                        'pm10': predictions.get('PM10', {}).get('current', 0),
                        'co2': predictions.get('CO2', {}).get('current', 0),
                        'tvoc': predictions.get('TVOC', {}).get('current', 0),
                    },
                    'environmental': {
                        'temperature': predictions.get('Temperature', {}).get('current', 0),
                        'humidity': predictions.get('Humidity', {}).get('current', 0),
                        'pressure': predictions.get('Pressure', {}).get('current', 0),
                    },
                    'predictions': {
                        'pm2_5': predictions.get('PM2.5', {}).get('predicted', 0),
                        'pm10': predictions.get('PM10', {}).get('predicted', 0),
                        'co2': predictions.get('CO2', {}).get('predicted', 0),
                        'tvoc': predictions.get('TVOC', {}).get('predicted', 0),
                        'temperature': predictions.get('Temperature', {}).get('predicted', 0),
                        'humidity': predictions.get('Humidity', {}).get('predicted', 0),
                        'pressure': predictions.get('Pressure', {}).get('predicted', 0),
                    }
                }
                successful += 1
                
        except Exception as e:
            print(f"  ERROR: {e}")
            continue
    
    print("\n" + "="*80)
    print(f"COMPLETE - {successful}/5 sensors loaded with predictions")
    print("="*80)
    
    # Send all sensors data to backend in multi-sensor format
    if successful > 0:
        print(f"\n[BACKEND] Sending {successful} sensors to AI...")
        multi_sensor_payload = {
            'timestamp': datetime.now().isoformat(),
            'total_sensors': successful,
            'sensors': all_sensor_data
        }
        
        try:
            response = requests.post(
                BACKEND_URL,
                json=multi_sensor_payload,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS! All {successful} sensors sent to AI backend")
                print(f"\nAI now knows:")
                for sensor_key, sensor_data in all_sensor_data.items():
                    sensor_num = sensor_key.split('_')[1]
                    pm25 = sensor_data['pollutants']['pm2_5']
                    pred_pm25 = sensor_data['predictions']['pm2_5']
                    aqi = sensor_data['aqi']
                    print(f"  - Sensor {sensor_num}: PM2.5={pm25}→{pred_pm25:.2f}, AQI={aqi}")
                print("\nYou can now ask AI:")
                print('  - "What is the PM2.5 level of sensor 4?"')
                print('  - "Which sensor has the highest AQI?"')
                print('  - "Show me all sensor predictions"')
            else:
                print(f"  ❌ Backend returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("  ❌ Backend not running - start it with: cd backend && python server.py")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    else:
        print("\n❌ WARNING: No predictions generated - check Excel files exist")


if __name__ == "__main__":
    main()
