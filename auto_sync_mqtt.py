"""
Auto-sync MQTT data to backend for live updates
Watches mqtt_data.json and sends latest data to backend automatically
"""
import json
import time
import requests
from datetime import datetime
import os

MQTT_FILE = 'mqtt_data.json'
BACKEND_URL = 'http://localhost:5000/api/predictions'
CHECK_INTERVAL = 5  # Check every 5 seconds

last_timestamp = None

def calculate_aqi(pm25):
    """Calculate AQI from PM2.5"""
    if pm25 <= 12:
        return int((50/12) * pm25)
    elif pm25 <= 35.4:
        return int(50 + ((100-50)/(35.4-12)) * (pm25-12))
    elif pm25 <= 55.4:
        return int(100 + ((150-100)/(55.4-35.4)) * (pm25-35.4))
    else:
        return int(150 + ((200-150)/(150.4-55.4)) * (pm25-55.4))

def send_to_backend(data):
    """Send sensor data to backend"""
    try:
        pm25 = data.get('pm2_5', 0)
        aqi = calculate_aqi(pm25)
        
        payload = {
            'timestamp': datetime.now().isoformat(),
            'aqi': aqi,
            'pm25': float(data.get('pm2_5', 0)),
            'pm10': float(data.get('pm10', 0)),
            'co2': float(data.get('co2', 0)),
            'tvoc': float(data.get('tvoc', 0)),
            'temperature': float(data.get('temperature', 0)),
            'humidity': float(data.get('humidity', 0)),
            'pressure': float(data.get('pressure', 0))
        }
        
        response = requests.post(BACKEND_URL, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Synced: PM2.5={pm25}, AQI={aqi}")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Error: {e}")
        return False

def watch_mqtt_file():
    """Watch mqtt_data.json for changes and auto-sync"""
    global last_timestamp
    
    print("=" * 60)
    print("LIVE DATA AUTO-SYNC")
    print("=" * 60)
    print(f"Watching: {MQTT_FILE}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("=" * 60)
    print()
    
    while True:
        try:
            if not os.path.exists(MQTT_FILE):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for {MQTT_FILE}...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # Read latest data
            with open(MQTT_FILE, 'r') as f:
                data_list = json.load(f)
            
            if not data_list:
                time.sleep(CHECK_INTERVAL)
                continue
            
            latest = data_list[-1]
            current_timestamp = latest.get('received_at')
            
            # Check if new data
            if current_timestamp != last_timestamp:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] New data detected!")
                if send_to_backend(latest):
                    last_timestamp = current_timestamp
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] App will update automatically")
                print()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\nStopping auto-sync...")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    watch_mqtt_file()
