"""
Send sensor data to backend - Reading DIRECTLY from JSON files
NO Excel files used!
"""
import sys
import json
import os
import requests
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("Sending sensor data to backend (from JSON files)...")
print("=" * 70)

# Sensor configuration - ONLY JSON files
SENSORS = {
    1: {'json': 'mqtt_data_sensor1.json', 'name': 'Sensor 1'},
    2: {'json': 'mqtt_data_sensor2.json', 'name': 'Sensor 2'},
    3: {'json': 'mqtt_data.json', 'name': 'Sensor 3'},
    4: {'json': 'mqtt_data_sensor4.json', 'name': 'Sensor 4'},
    5: {'json': 'mqtt_data_sensor5.json', 'name': 'Sensor 5'},
}

BACKEND_URL = 'http://localhost:5000/api/predictions'

def calculate_aqi(pm25):
    """Calculate AQI from PM2.5"""
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

for sensor_id, config in SENSORS.items():
    json_file = config['json']
    sensor_name = config['name']
    
    print(f"\n{sensor_name}:")
    
    # Check if JSON exists
    if not os.path.exists(json_file):
        print(f"  SKIP: {json_file} not found")
        continue
    
    try:
        # Load JSON data
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Handle both list and single object
        if isinstance(data, list):
            if len(data) == 0:
                print(f"  SKIP: Empty JSON file")
                continue
            # Get the LAST entry (most recent)
            latest = data[-1]
        else:
            latest = data
        
        # Extract values with fallbacks
        pm25 = float(latest.get('pm2_5', latest.get('PM2.5', 0)))
        pm10 = float(latest.get('pm10', latest.get('PM10', 0)))
        co2 = float(latest.get('co2', latest.get('CO2', 400)))
        tvoc = float(latest.get('tvoc', latest.get('TVOC', 0)))
        temp = float(latest.get('temperature', latest.get('Temperature', 25)))
        hum = float(latest.get('humidity', latest.get('Humidity', 60)))
        pres = float(latest.get('pressure', latest.get('Pressure', 1013)))
        
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
        if response.status_code == 200:
            print(f"  SUCCESS")
            print(f"    AQI: {aqi}")
            print(f"    PM2.5: {pm25} µg/m³")
            print(f"    PM10: {pm10} µg/m³")
            print(f"    CO2: {co2} ppm")
            print(f"    TVOC: {tvoc} ppb")
        else:
            print(f"  ERROR: Backend returned {response.status_code}")
            
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 70)
print("Verifying backend...")

# Verify
try:
    response = requests.get('http://localhost:5000/api/sensors/all', timeout=5)
    data = response.json()
    if data.get('status') == 'success':
        print(f"\nBackend has data for {data.get('total_sensors')} sensors:\n")
        for sensor_key, sensor_data in data.get('sensors', {}).items():
            aqi = sensor_data.get('aqi', 0)
            pm25 = sensor_data.get('pollutants', {}).get('pm2_5', 0)
            
            # AQI category
            if aqi <= 50:
                category = "Good"
            elif aqi <= 100:
                category = "Moderate"
            elif aqi <= 150:
                category = "Unhealthy for Sensitive"
            elif aqi <= 200:
                category = "Unhealthy"
            else:
                category = "Very Unhealthy"
            
            print(f"  {sensor_key}: AQI {aqi} ({category}) - PM2.5: {pm25} µg/m³")
    else:
        print(f"\nBackend status: {data.get('status')}")
        print(f"   Message: {data.get('message', 'Unknown error')}")
except Exception as e:
    print(f"\nERROR verifying: {e}")

print("\n" + "=" * 70)
print("Complete! Refresh your Flutter app to see the data!")
