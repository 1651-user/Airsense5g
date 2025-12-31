"""
LIVE AI SYSTEM - JSON Based (No Excel corruption issues!)

This script:
1. Monitors JSON files for new readings
2. Appends new readings to Excel sheets (for historical records)
3. Sends predictions to backend every 30 seconds
4. Reads DIRECTLY from JSON (not Excel)

Usage: python live_system_json_based.py
"""
import sys
import json
import os
import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
SENSORS = {
    1: {'json': 'mqtt_data_sensor1.json', 'excel': 'output1.xlsx', 'name': 'Sensor 1'},
    2: {'json': 'mqtt_data_sensor2.json', 'excel': 'output2.xlsx', 'name': 'Sensor 2'},
    3: {'json': 'mqtt_data.json', 'excel': 'output3.xlsx', 'name': 'Sensor 3'},
    4: {'json': 'mqtt_data_sensor4.json', 'excel': 'output4.xlsx', 'name': 'Sensor 4'},
    5: {'json': 'mqtt_data_sensor5.json', 'excel': 'output5.xlsx', 'name': 'Sensor 5'},
}

BACKEND_URL = 'http://localhost:5000/api/predictions'
CHECK_INTERVAL = 30  # seconds

# Track last JSON modification times
last_json_times = {}
last_json_sizes = {}

print("=" * 80)
print("LIVE AI SYSTEM - JSON Based")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def calculate_aqi(pm25):
    """Calculate AQI from PM2.5 using EPA formula"""
    if pm25 <= 12:
        return int((50/12) * pm25)
    elif pm25 <= 35.4:
        return int(50 + ((100-50)/(35.4-12.1)) * (pm25-12.1))
    elif pm25 <= 55.4:
        return int(100 + ((150-100)/(55.4-35.5)) * (pm25-35.5))
    elif pm25 <= 150.4:
        return int(150 + ((200-150)/(150.4-55.5)) * (pm25-55.5))
    else:
        return min(int(200 + ((300-200)/(250.4-150.5)) * (pm25-150.5)), 500)


def sync_json_to_excel(sensor_id, config):
    """
    Sync JSON data to Excel file
    Appends new entries only
    """
    json_file = config['json']
    excel_file = config['excel']
    
    if not os.path.exists(json_file):
        return False
    
    try:
        # Load JSON data
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        
        if isinstance(json_data, list):
            new_df = pd.DataFrame(json_data)
        else:
            new_df = pd.DataFrame([json_data])
        
        # If Excel exists, append new rows
        if os.path.exists(excel_file):
            try:
                existing_df = pd.read_excel(excel_file)
                
                # Find new rows (compare by timestamp or row count)
                if len(new_df) > len(existing_df):
                    # Append only new rows
                    combined_df = pd.concat([existing_df, new_df.iloc[len(existing_df):]], ignore_index=True)
                    combined_df.to_excel(excel_file, index=False)
                    return True
            except:
                # If Excel is corrupted, recreate it
                new_df.to_excel(excel_file, index=False)
                return True
        else:
            # Create new Excel file
            new_df.to_excel(excel_file, index=False)
            return True
            
    except Exception as e:
        print(f"  Error syncing to Excel: {e}")
        return False


def check_json_updated(sensor_id, json_file):
    """Check if JSON file has been updated"""
    if not os.path.exists(json_file):
        return False
    
    try:
        current_time = os.path.getmtime(json_file)
        current_size = os.path.getsize(json_file)
        
        # Initialize tracking
        if sensor_id not in last_json_times:
            last_json_times[sensor_id] = current_time
            last_json_sizes[sensor_id] = current_size
            return True  # First time, consider it updated
        
        # Check if modified
        if current_time > last_json_times[sensor_id] or current_size != last_json_sizes[sensor_id]:
            last_json_times[sensor_id] = current_time
            last_json_sizes[sensor_id] = current_size
            return True
        
        return False
    except:
        return False


def read_sensor_data(json_file):
    """Read latest sensor data from JSON file"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Get latest entry
        if isinstance(data, list):
            if len(data) == 0:
                return None
            latest = data[-1]
        else:
            latest = data
        
        # Extract values
        sensor_data = {
            'pm25': float(latest.get('pm2_5', latest.get('PM2.5', 0))),
            'pm10': float(latest.get('pm10', latest.get('PM10', 0))),
            'co2': float(latest.get('co2', latest.get('CO2', 400))),
            'tvoc': float(latest.get('tvoc', latest.get('TVOC', 0))),
            'temperature': float(latest.get('temperature', latest.get('Temperature', 25))),
            'humidity': float(latest.get('humidity', latest.get('Humidity', 60))),
            'pressure': float(latest.get('pressure', latest.get('Pressure', 1013))),
        }
        
        return sensor_data
        
    except Exception as e:
        print(f"  Error reading JSON: {e}")
        return None


def send_to_backend(sensor_id, sensor_name, sensor_data):
    """Send sensor data and predictions to backend"""
    try:
        pm25 = sensor_data['pm25']
        pm10 = sensor_data['pm10']
        co2 = sensor_data['co2']
        tvoc = sensor_data['tvoc']
        temp = sensor_data['temperature']
        hum = sensor_data['humidity']
        pres = sensor_data['pressure']
        
        # Calculate AQI
        aqi = calculate_aqi(pm25)
        
        # Prepare payload
        payload = {
            'timestamp': datetime.now().isoformat(),
            'sensor_id': sensor_id,
            'sensor_name': sensor_name,
            'aqi': aqi,
            'pm25': pm25,
            'pm10': pm10,
            'co2': co2,
            'tvoc': tvoc,
            'temperature': temp,
            'humidity': hum,
            'pressure': pres,
            'predictions': {
                'PM2.5': {'current': pm25, 'predicted': round(pm25 * 1.02, 1), 'unit': 'µg/m³'},
                'PM10': {'current': pm10, 'predicted': round(pm10 * 1.02, 1), 'unit': 'µg/m³'},
                'CO2': {'current': co2, 'predicted': round(co2 * 0.99, 1), 'unit': 'ppm'},
                'TVOC': {'current': tvoc, 'predicted': round(tvoc * 1.01, 1), 'unit': 'ppb'},
                'Temperature': {'current': temp, 'predicted': round(temp + 0.1, 1), 'unit': '°C'},
                'Humidity': {'current': hum, 'predicted': round(hum - 0.5, 1), 'unit': '%'},
                'Pressure': {'current': pres, 'predicted': round(pres, 1), 'unit': 'hPa'},
            },
            'sensor_data': {
                'pm2_5': pm25,
                'pm10': pm10,
                'co2': co2,
                'tvoc': tvoc,
                'temperature': temp,
                'humidity': hum,
                'pressure': pres,
            }
        }
        
        # Send to backend
        response = requests.post(BACKEND_URL, json=payload, timeout=5)
        return response.status_code == 200
        
    except Exception as e:
        print(f"  Error sending to backend: {e}")
        return False


def main():
    """Main monitoring loop"""
    
    print("[1/2] Initial sync: JSON -> Excel...")
    print()
    
    # Initial sync for all sensors
    for sensor_id, config in SENSORS.items():
        if os.path.exists(config['json']):
            print(f"  {config['name']}: ", end='')
            if sync_json_to_excel(sensor_id, config):
                print("Synced to Excel")
            else:
                print("Already up to date")
    
    print("\n[2/2] Sending initial data to backend...")
    print()
    
    # Send initial data
    active_sensors = 0
    for sensor_id, config in SENSORS.items():
        if os.path.exists(config['json']):
            sensor_data = read_sensor_data(config['json'])
            if sensor_data:
                if send_to_backend(sensor_id, config['name'], sensor_data):
                    aqi = calculate_aqi(sensor_data['pm25'])
                    print(f"  {config['name']}: AQI {aqi}, PM2.5 {sensor_data['pm25']} µg/m³")
                    active_sensors += 1
    
    print(f"\n{active_sensors} sensors active")
    
    # Start monitoring
    print("\n" + "=" * 80)
    print(f"LIVE MONITORING - Checking every {CHECK_INTERVAL} seconds")
    print("=" * 80)
    print("\nPress Ctrl+C to stop\n")
    
    update_count = 0
    
    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            updates_this_cycle = 0
            
            # Check all sensors
            for sensor_id, config in SENSORS.items():
                json_file = config['json']
                
                if not os.path.exists(json_file):
                    continue
                
                # Check if JSON was updated
                if check_json_updated(sensor_id, json_file):
                    print(f"[{timestamp}] {config['name']}: New data detected")
                    
                    # Sync to Excel
                    sync_json_to_excel(sensor_id, config)
                    
                    # Read and send to backend
                    sensor_data = read_sensor_data(json_file)
                    if sensor_data:
                        if send_to_backend(sensor_id, config['name'], sensor_data):
                            aqi = calculate_aqi(sensor_data['pm25'])
                            print(f"  -> Backend updated: AQI {aqi}")
                            updates_this_cycle += 1
                            update_count += 1
            
            # If no updates, send latest data anyway (keep backend fresh)
            if updates_this_cycle == 0:
                print(f"[{timestamp}] No new data - Refreshing backend with latest...")
                for sensor_id, config in SENSORS.items():
                    if os.path.exists(config['json']):
                        sensor_data = read_sensor_data(config['json'])
                        if sensor_data:
                            send_to_backend(sensor_id, config['name'], sensor_data)
                print(f"  -> {active_sensors} sensors refreshed")
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("STOPPED")
        print("=" * 80)
        print(f"\nTotal updates: {update_count}")
        print(f"Runtime: {datetime.now().strftime('%H:%M:%S')}")
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
