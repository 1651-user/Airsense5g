"""
Send all 5 sensor data to AI backend
This script fetches data from all sensors and sends it to the AI for context
"""

import os
import json
import requests
from fetch_all_sensors import fetch_all_sensors
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('backend/.env')

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000/api/predictions')

def format_sensor_data_for_ai(all_sensor_data):
    """Format all sensor data for AI consumption"""
    
    formatted_data = {
        'timestamp': datetime.now().isoformat(),
        'total_sensors': len(all_sensor_data),
        'sensors': {}
    }
    
    for sensor in all_sensor_data:
        sensor_id = sensor['sensor_id']
        formatted_data['sensors'][f'sensor_{sensor_id}'] = {
            'name': sensor['sensor_name'],
            'aqi': sensor.get('aqi', 0),
            'pollutants': {
                'pm2_5': sensor.get('pm2_5', 0),
                'pm10': sensor.get('pm10', 0),
                'co2': sensor.get('co2', 0),
                'tvoc': sensor.get('tvoc', 0),
                'no2': sensor.get('no2', 0),
                'so2': sensor.get('so2', 0),
                'o3': sensor.get('o3', 0),
            },
            'environmental': {
                'temperature': sensor.get('temperature', 0),
                'humidity': sensor.get('humidity', 0),
                'pressure': sensor.get('pressure', 0),
            }
        }
    
    return formatted_data

def send_to_backend(data):
    """Send formatted sensor data to backend"""
    try:
        print(f"\n📤 Sending data to backend: {BACKEND_URL}")
        
        response = requests.post(
            BACKEND_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Successfully sent data to backend")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server")
        print("   Make sure server is running: python backend/server.py")
        return False
    except Exception as e:
        print(f"❌ Error sending to backend: {e}")
        return False

def main():
    """Main function"""
    print("="*80)
    print("SENDING ALL SENSOR DATA TO AI BACKEND")
    print("="*80)
    
    # Fetch all sensor data
    all_sensor_data = fetch_all_sensors()
    
    if not all_sensor_data:
        print("\n❌ No sensor data available to send")
        return
    
    # Format for AI
    formatted_data = format_sensor_data_for_ai(all_sensor_data)
    
    # Save formatted data
    with open('ai_sensor_context.json', 'w') as f:
        json.dump(formatted_data, f, indent=2)
    print(f"\n✅ Saved AI context to ai_sensor_context.json")
    
    # Send to backend
    send_to_backend(formatted_data)
    
    # Print summary
    print("\n" + "="*80)
    print("AI CONTEXT SUMMARY")
    print("="*80)
    print(f"Total Sensors: {formatted_data['total_sensors']}")
    for sensor_key, sensor_info in formatted_data['sensors'].items():
        print(f"\n{sensor_info['name']}:")
        print(f"  AQI: {sensor_info['aqi']}")
        print(f"  PM2.5: {sensor_info['pollutants']['pm2_5']} µg/m³")
        print(f"  PM10: {sensor_info['pollutants']['pm10']} µg/m³")
        print(f"  CO2: {sensor_info['pollutants']['co2']} ppm")

if __name__ == "__main__":
    main()
