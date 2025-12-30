"""
Integrated MQTT to AI Pipeline - Sensor 1

This script:
1. Connects to MQTT broker (sensor 1)
2. Saves data to JSON file
3. Generates predictions using trained models
4. Sends predictions to backend server
5. AI receives predictions as context

Usage:
    python mqtt_to_ai_sensor1.py
"""

import paho.mqtt.client as mqtt
import json
import os
import sys
import time
import pandas as pd
import numpy as np
import joblib
import requests
from datetime import datetime
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables for Sensor 1
load_dotenv('amb1.env')

# MQTT Configuration
MQTT_BROKER = os.getenv('MQTT_BROKER', 'au1.cloud.thethings.industries')
MQTT_PORT = int(os.getenv('MQTT_PORT', '1883'))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'v3/milesight-aqi@lora-demo/devices/ambience-1/up')
MQTT_USERNAME = os.getenv('MQTT_USERNAME', 'milesight-aqi@lora-demo')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', '')

# Backend Configuration
BACKEND_URL = 'http://192.168.1.147:5000/api/predictions'

# File paths
JSON_FILE = 'mqtt_data_sensor1.json'
EXCEL_FILE = 'output1.xlsx'
MODEL_DIR = 'models'
SENSOR_ID = 1
SENSOR_NAME = 'Sensor 1'

# Global data storage
sensor_data_buffer = []
MAX_BUFFER_SIZE = 100  # Use last 100 readings from Excel + MQTT
excel_data_loaded = False

print("="*80)
print(f"MQTT TO AI PIPELINE - {SENSOR_NAME}")
print("="*80)
print(f"\nMQTT Broker: {MQTT_BROKER}")
print(f"Topic: {MQTT_TOPIC}")
print(f"Backend: {BACKEND_URL}")
print(f"JSON File: {JSON_FILE}")
print("="*80)


class PredictionEngine:
    """Loads models and generates predictions"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        print("\n[MODELS] Loading prediction models...")
        
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
                    self.models[target] = joblib.load(model_path)
                    self.scalers[target] = joblib.load(scaler_path)
                    print(f"  OK Loaded {target} model")
                except Exception as e:
                    print(f"  ERROR loading {target}: {e}")
        
        print(f"  OK Loaded {len(self.models)} models\n")
    
    def predict(self, sensor_data):
        """Generate predictions from sensor data"""
        if not sensor_data or len(sensor_data) < 3:
            return None
        
        try:
            df = pd.DataFrame(sensor_data)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            df_numeric = df[numeric_cols]
            
            if len(df_numeric) < 3:
                return None
            
            predictions = {}
            
            for target, model in self.models.items():
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
                    
                    scaler = self.scalers[target]
                    X_scaled = scaler.transform(X)
                    prediction = model.predict(X_scaled)[0]
                    
                    current = df_numeric[target_col].iloc[-1]
                    
                    predictions[target] = {
                        'predicted': round(float(prediction), 2),
                        'current': round(float(current), 2),
                        'unit': self._get_unit(target)
                    }
                    
                except Exception as e:
                    continue
            
            return predictions
            
        except Exception as e:
            return None
    
    def _get_unit(self, target):
        """Get unit for target"""
        units = {
            'PM2.5': 'µg/m³',
            'PM10': 'µg/m³',
            'CO2': 'ppm',
            'TVOC': 'ppb',
            'Temperature': '°C',
            'Humidity': '%',
            'Pressure': 'hPa'
        }
        return units.get(target, '')
    
    def calculate_aqi(self, pm25):
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


# Initialize prediction engine
prediction_engine = PredictionEngine()


def save_to_json(data):
    """Save data to JSON file"""
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        existing_data.append(data)
        
        if len(existing_data) > 100:
            existing_data = existing_data[-100:]
        
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"  ERROR saving to JSON: {e}")
        return False


def send_to_backend(predictions, sensor_data):
    """Send predictions to backend server"""
    try:
        aqi = 0
        if 'PM2.5' in predictions:
            aqi = prediction_engine.calculate_aqi(predictions['PM2.5']['predicted'])
        
        payload = {
            'sensor_id': SENSOR_ID,
            'sensor_name': SENSOR_NAME,
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
            'sensor_data': sensor_data[-1] if sensor_data else {}
        }
        
        response = requests.post(
            BACKEND_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"  OK Sent to backend (AQI: {aqi})")
            return True
        else:
            print(f"  ERROR Backend returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  WARNING Backend not running")
        return False
    except Exception as e:
        print(f"  ERROR sending to backend: {e}")
        return False


def on_connect(client, userdata, flags, rc):
    """Callback when connected to MQTT broker"""
    if rc == 0:
        print(f"\n[MQTT] Connected to broker: {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"[MQTT] Subscribed to: {MQTT_TOPIC}")
        print(f"\n[WAITING] Listening for {SENSOR_NAME} data...\n")
    else:
        print(f"\n[MQTT] Connection failed with code {rc}")


def on_message(client, userdata, msg):
    """Callback when message received from MQTT"""
    global sensor_data_buffer
    
    try:
        payload = json.loads(msg.payload.decode())
        
        if 'uplink_message' in payload and 'decoded_payload' in payload['uplink_message']:
            sensor_data = payload['uplink_message']['decoded_payload']
            sensor_data['received_at'] = payload.get('received_at', datetime.now().isoformat())
            sensor_data['sensor_id'] = SENSOR_ID
            
            print(f"\n{'='*80}")
            print(f"[MQTT] Received data from {SENSOR_NAME}")
            print(f"{'='*80}")
            
            print(f"\n[SENSOR DATA]")
            for key, value in sensor_data.items():
                if isinstance(value, (int, float)):
                    print(f"  {key}: {value}")
            
            print(f"\n[JSON] Saving to {JSON_FILE}...")
            save_to_json(sensor_data)
            print(f"  OK Saved")
            
            sensor_data_buffer.append(sensor_data)
            if len(sensor_data_buffer) > MAX_BUFFER_SIZE:
                sensor_data_buffer = sensor_data_buffer[-MAX_BUFFER_SIZE:]
            
            if len(sensor_data_buffer) >= 3:
                print(f"\n[PREDICTIONS] Generating predictions...")
                predictions = prediction_engine.predict(sensor_data_buffer)
                
                if predictions:
                    print(f"  OK Generated {len(predictions)} predictions:")
                    for target, values in predictions.items():
                        print(f"    {target}: {values['predicted']}{values['unit']} (current: {values['current']})")
                    
                    print(f"\n[BACKEND] Sending to AI backend...")
                    send_to_backend(predictions, sensor_data_buffer)
                else:
                    print(f"  WARNING Could not generate predictions")
            else:
                print(f"\n[INFO] Collecting data... ({len(sensor_data_buffer)}/{MAX_BUFFER_SIZE} samples, need 3 minimum)")
            
            print(f"\n{'='*80}\n")
            
    except Exception as e:
        print(f"\n[ERROR] Processing message: {e}\n")


def on_disconnect(client, userdata, rc):
    """Callback when disconnected from MQTT broker"""
    print(f"\n[MQTT] Disconnected from broker (code: {rc})")
    if rc != 0:
        print("[MQTT] Unexpected disconnection. Reconnecting...")


def main():
    """Main function"""
    
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    print(f"\n[MQTT] Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        print(f"\n[PIPELINE] MQTT → JSON → Predictions → AI ({SENSOR_NAME})")
        print("[INFO] Press Ctrl+C to stop\n")
        
        client.loop_forever()
        
    except KeyboardInterrupt:
        print(f"\n\n[SHUTDOWN] Stopping {SENSOR_NAME} pipeline...")
        client.disconnect()
        print("[SHUTDOWN] Pipeline stopped")
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("\nPlease check:")
        print("  1. Internet connection")
        print(f"  2. MQTT credentials in amb1.env")
        print("  3. Firewall settings")


if __name__ == "__main__":
    main()
