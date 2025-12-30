import paho.mqtt.client as mqtt
import json
import os
import sys
import time
import requests
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Sensor configurations
SENSORS = [
    {'id': 1, 'name': 'Sensor 1', 'env_file': 'amb1.env'},
    {'id': 2, 'name': 'Sensor 2', 'env_file': 'amb2.env'},
    {'id': 3, 'name': 'Sensor 3', 'env_file': 'am3.env'},
    {'id': 4, 'name': 'Sensor 4', 'env_file': 'amb4.env'},
    {'id': 5, 'name': 'Sensor 5', 'env_file': 'amb5.env'},
]

# Backend Configuration
BACKEND_URL = 'http://192.168.1.147:5000/api/predictions'
MODEL_DIR = 'models'

# Global storage for all sensors
all_sensors_data = {}
sensor_data_buffers = {1: [], 2: [], 3: [], 4: [], 5: []}  # Historical data for predictions
MAX_BUFFER_SIZE = 10

print("="*80)
print("MULTI-SENSOR MQTT TO AI PIPELINE WITH PREDICTIONS")
print("="*80)
print(f"Connecting {len(SENSORS)} sensors directly to AI")
print(f"Backend: {BACKEND_URL}")
print("="*80)


class PredictionEngine:
    """Loads models and generates predictions for each sensor"""
    
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
    
    def predict(self, sensor_data_buffer):
        """Generate predictions from sensor data buffer"""
        if not sensor_data_buffer or len(sensor_data_buffer) < 3:
            return None
        
        try:
            df = pd.DataFrame(sensor_data_buffer)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            df_numeric = df[numeric_cols]
            
            if len(df_numeric) < 3:
                return None
            
            predictions = {}
            
            for target, model in self.models.items():
                try:
                    # Find matching column
                    target_col = None
                    for col in df_numeric.columns:
                        if target.lower().replace('.', '').replace(' ', '') in col.lower().replace('_', ''):
                            target_col = col
                            break
                    
                    if target_col is None:
                        continue
                    
                    # Get last 3 values
                    last_3_values = df_numeric[target_col].iloc[-3:].values
                    X = last_3_values.reshape(1, -1)
                    
                    # Scale and predict
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


# Initialize prediction engine
prediction_engine = PredictionEngine()


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


def send_to_backend():
    """Send all sensor data with predictions to backend"""
    try:
        if not all_sensors_data:
            return False
        
        # Format data for backend
        formatted_data = {
            'timestamp': datetime.now().isoformat(),
            'total_sensors': len(all_sensors_data),
            'sensors': {}
        }
        
        for sensor_id, sensor_data in all_sensors_data.items():
            # Generate predictions for this sensor if we have enough data
            predictions = None
            if sensor_id in sensor_data_buffers and len(sensor_data_buffers[sensor_id]) >= 3:
                predictions = prediction_engine.predict(sensor_data_buffers[sensor_id])
            
            formatted_data['sensors'][f'sensor_{sensor_id}'] = {
                'name': f'Sensor {sensor_id}',
                'aqi': sensor_data.get('aqi', 0),
                'pollutants': {
                    'pm2_5': sensor_data.get('pm2_5', 0),
                    'pm10': sensor_data.get('pm10', 0),
                    'co2': sensor_data.get('co2', 0),
                    'tvoc': sensor_data.get('tvoc', 0),
                    'no2': sensor_data.get('no2', 0),
                    'so2': sensor_data.get('so2', 0),
                    'o3': sensor_data.get('o3', 0),
                },
                'environmental': {
                    'temperature': sensor_data.get('temperature', 0),
                    'humidity': sensor_data.get('humidity', 0),
                    'pressure': sensor_data.get('pressure', 0),
                },
                'predictions': predictions if predictions else {}
            }
        
        # Send to backend
        response = requests.post(
            BACKEND_URL,
            json=formatted_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            # Count sensors with predictions
            sensors_with_predictions = sum(1 for s in formatted_data['sensors'].values() if s['predictions'])
            print(f"[OK] Sent {len(all_sensors_data)} sensors to backend ({sensors_with_predictions} with predictions)")
            return True
        else:
            print(f"[ERROR] Backend returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[WARNING] Backend not running")
        return False
    except Exception as e:
        print(f"[ERROR] Sending to backend: {e}")
        return False


class SensorMQTTClient:
    """MQTT client for a single sensor"""
    
    def __init__(self, sensor_config):
        self.sensor_id = sensor_config['id']
        self.sensor_name = sensor_config['name']
        self.env_file = sensor_config['env_file']
        
        # Load environment
        load_dotenv(self.env_file)
        
        self.broker = os.getenv('MQTT_BROKER', 'au1.cloud.thethings.industries')
        self.port = int(os.getenv('MQTT_PORT', '1883'))
        self.topic = os.getenv('MQTT_TOPIC', '')
        self.username = os.getenv('MQTT_USERNAME', '')
        self.password = os.getenv('MQTT_PASSWORD', '')
        
        # Create MQTT client
        self.client = mqtt.Client(client_id=f"sensor_{self.sensor_id}_client")
        self.client.username_pw_set(self.username, self.password)
        
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        print(f"[{self.sensor_name}] Configured")
        print(f"  Broker: {self.broker}")
        print(f"  Topic: {self.topic}")
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected"""
        if rc == 0:
            print(f"[{self.sensor_name}] Connected to MQTT broker")
            client.subscribe(self.topic)
            print(f"[{self.sensor_name}] Subscribed to topic")
        else:
            print(f"[{self.sensor_name}] Connection failed (code {rc})")
    
    def on_message(self, client, userdata, msg):
        """Callback when message received"""
        global all_sensors_data, sensor_data_buffers
        
        try:
            # Parse MQTT message
            payload = json.loads(msg.payload.decode())
            
            # Extract sensor data
            if 'uplink_message' in payload and 'decoded_payload' in payload['uplink_message']:
                sensor_data = payload['uplink_message']['decoded_payload']
                
                # Calculate AQI if PM2.5 is available
                pm25 = sensor_data.get('pm2_5', sensor_data.get('pm25', 0))
                if pm25:
                    sensor_data['aqi'] = calculate_aqi(pm25)
                else:
                    sensor_data['aqi'] = 0
                
                # Store in global data
                all_sensors_data[self.sensor_id] = sensor_data
                
                # Add to buffer for predictions
                sensor_data_buffers[self.sensor_id].append(sensor_data)
                if len(sensor_data_buffers[self.sensor_id]) > MAX_BUFFER_SIZE:
                    sensor_data_buffers[self.sensor_id] = sensor_data_buffers[self.sensor_id][-MAX_BUFFER_SIZE:]
                
                print(f"\n[{self.sensor_name}] Data received:")
                print(f"  AQI: {sensor_data.get('aqi', 0)}")
                print(f"  PM2.5: {sensor_data.get('pm2_5', 0)}")
                print(f"  PM10: {sensor_data.get('pm10', 0)}")
                print(f"  CO2: {sensor_data.get('co2', 0)}")
                
                # Generate predictions if we have enough data
                if len(sensor_data_buffers[self.sensor_id]) >= 3:
                    predictions = prediction_engine.predict(sensor_data_buffers[self.sensor_id])
                    if predictions:
                        print(f"\n[{self.sensor_name}] Predictions generated:")
                        for target, values in predictions.items():
                            arrow = "↑" if values['predicted'] > values['current'] else "↓" if values['predicted'] < values['current'] else "→"
                            print(f"  {target}: {values['current']} → {values['predicted']} {values['unit']} {arrow}")
                
                # Send all sensors data to backend
                send_to_backend()
                
        except Exception as e:
            print(f"[{self.sensor_name}] Error processing message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        print(f"[{self.sensor_name}] Disconnected (code {rc})")
        if rc != 0:
            print(f"[{self.sensor_name}] Reconnecting...")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(self.broker, self.port, 60)
            return True
        except Exception as e:
            print(f"[{self.sensor_name}] Connection error: {e}")
            return False
    
    def start_loop(self):
        """Start MQTT loop in background"""
        self.client.loop_start()


def main():
    """Main function"""
    print("\n[INIT] Starting multi-sensor MQTT clients...\n")
    
    # Create clients for all sensors
    clients = []
    for sensor_config in SENSORS:
        client = SensorMQTTClient(sensor_config)
        if client.connect():
            client.start_loop()
            clients.append(client)
        else:
            print(f"[WARNING] Could not connect {sensor_config['name']}")
    
    print(f"\n[OK] {len(clients)}/{len(SENSORS)} sensors connected")
    print("\n[PIPELINE] MQTT → AI Backend (auto-update every 30s)")
    print("[INFO] Press Ctrl+C to stop\n")
    print("="*80)
    
    # Timer for automatic updates
    last_update = time.time()
    update_interval = 30  # seconds
    
    try:
        # Keep running
        while True:
            current_time = time.time()
            
            # Check if 30 seconds have passed
            if current_time - last_update >= update_interval:
                if all_sensors_data:
                    print(f"\n[AUTO-UPDATE] Sending latest data from {len(all_sensors_data)} sensors to backend...")
                    send_to_backend()
                    last_update = current_time
                else:
                    print(f"\n[WAITING] No sensor data received yet...")
                    last_update = current_time
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Stopping all sensors...")
        for client in clients:
            client.client.loop_stop()
            client.client.disconnect()
        print("[SHUTDOWN] All sensors stopped")


if __name__ == "__main__":
    main()
