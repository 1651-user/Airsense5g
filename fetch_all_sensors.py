"""
Fetch data from all 5 sensors and combine into a single dataset
This script fetches data from MongoDB collections for all sensors
"""

import os
import json
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables for each sensor
SENSOR_CONFIGS = [
    {'id': 1, 'env_file': 'amb1.env', 'name': 'Sensor 1'},
    {'id': 2, 'env_file': 'amb2.env', 'name': 'Sensor 2'},
    {'id': 3, 'env_file': 'am3.env', 'name': 'Sensor 3'},
    {'id': 4, 'env_file': 'amb4.env', 'name': 'Sensor 4'},
    {'id': 5, 'env_file': 'amb5.env', 'name': 'Sensor 5'},
]

def fetch_sensor_data(sensor_config):
    """Fetch latest data from a specific sensor"""
    try:
        # Load environment for this sensor
        load_dotenv(sensor_config['env_file'])
        
        MONGO_URI = os.getenv("MONGO_URI")
        MONGO_DB = os.getenv("MONGO_DB")
        MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
        
        if not all([MONGO_URI, MONGO_DB, MONGO_COLLECTION]):
            print(f"⚠ Missing config for {sensor_config['name']}")
            return None
        
        # Connect to MongoDB
        client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Fetch latest document
        latest_doc = collection.find_one(sort=[('received_at', -1)])
        
        if not latest_doc:
            print(f"⚠ No data found for {sensor_config['name']}")
            client.close()
            return None
        
        # Extract sensor data
        sensor_data = {
            'sensor_id': sensor_config['id'],
            'sensor_name': sensor_config['name'],
            'timestamp': latest_doc.get('received_at', datetime.now()),
        }
        
        # Extract pollutant values (handle different field names)
        field_mappings = {
            'pm2_5': ['pm2_5', 'pm25', 'PM2.5'],
            'pm10': ['pm10', 'PM10'],
            'co2': ['co2', 'CO2'],
            'tvoc': ['tvoc', 'TVOC'],
            'no2': ['no2', 'NO2'],
            'so2': ['so2', 'SO2'],
            'o3': ['o3', 'O3'],
            'temperature': ['temperature', 'temp'],
            'humidity': ['humidity', 'hum'],
            'pressure': ['pressure', 'press']
        }
        
        for key, possible_fields in field_mappings.items():
            for field in possible_fields:
                if field in latest_doc:
                    sensor_data[key] = latest_doc[field]
                    break
            if key not in sensor_data:
                sensor_data[key] = 0  # Default value
        
        # Calculate AQI from PM2.5
        if 'pm2_5' in sensor_data:
            sensor_data['aqi'] = calculate_aqi(sensor_data['pm2_5'])
        else:
            sensor_data['aqi'] = 0
        
        client.close()
        print(f"✅ Fetched data for {sensor_config['name']} - AQI: {sensor_data['aqi']}")
        
        return sensor_data
        
    except Exception as e:
        print(f"❌ Error fetching {sensor_config['name']}: {e}")
        return None

def calculate_aqi(pm25):
    """Calculate AQI from PM2.5 value"""
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

def fetch_all_sensors():
    """Fetch data from all 5 sensors"""
    print("="*80)
    print("FETCHING DATA FROM ALL 5 SENSORS")
    print("="*80)
    
    all_sensor_data = []
    
    for sensor_config in SENSOR_CONFIGS:
        sensor_data = fetch_sensor_data(sensor_config)
        if sensor_data:
            all_sensor_data.append(sensor_data)
    
    print(f"\n✅ Successfully fetched data from {len(all_sensor_data)}/5 sensors")
    
    return all_sensor_data

def save_to_json(data, filename='all_sensors_data.json'):
    """Save all sensor data to JSON file"""
    try:
        # Convert timestamps to strings
        for sensor in data:
            if 'timestamp' in sensor and hasattr(sensor['timestamp'], 'isoformat'):
                sensor['timestamp'] = sensor['timestamp'].isoformat()
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'sensors': data
            }, f, indent=2)
        
        print(f"\n✅ Saved data to {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")
        return False

def main():
    """Main function"""
    # Fetch all sensor data
    all_data = fetch_all_sensors()
    
    if all_data:
        # Save to JSON
        save_to_json(all_data)
        
        # Print summary
        print("\n" + "="*80)
        print("SENSOR DATA SUMMARY")
        print("="*80)
        for sensor in all_data:
            print(f"\n{sensor['sensor_name']}:")
            print(f"  AQI: {sensor['aqi']}")
            print(f"  PM2.5: {sensor.get('pm2_5', 'N/A')} µg/m³")
            print(f"  PM10: {sensor.get('pm10', 'N/A')} µg/m³")
            print(f"  CO2: {sensor.get('co2', 'N/A')} ppm")
            print(f"  Temperature: {sensor.get('temperature', 'N/A')} °C")
            print(f"  Humidity: {sensor.get('humidity', 'N/A')} %")
    else:
        print("\n❌ No sensor data available")

if __name__ == "__main__":
    main()
