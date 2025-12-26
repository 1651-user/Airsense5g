"""
Send sample prediction data to backend
This ensures Phi-2 has context to respond with
"""

import requests
from datetime import datetime

# Sample prediction data based on your sensor
payload = {
    'timestamp': datetime.now().isoformat(),
    'aqi': 154,
    'pm25': 64.22,
    'pm10': 85.0,
    'co2': 400.0,
    'no2': 33.8,
    'tvoc': 100.0,
    'temperature': 25.55,
    'humidity': 44.91,
    'pressure': 948.0,
    'location': {
        'lat': 0.0,
        'lon': 0.0
    },
    'predictions': {
        'PM2.5': {
            'predicted': 64.22,
            'current': 69.0,
            'unit': 'µg/m³'
        },
        'PM10': {
            'predicted': 85.0,
            'current': 85.0,
            'unit': 'µg/m³'
        },
        'CO2': {
            'predicted': 400.0,
            'current': 400.0,
            'unit': 'ppm'
        },
        'TVOC': {
            'predicted': 100.0,
            'current': 100.0,
            'unit': 'ppb'
        },
        'Temperature': {
            'predicted': 25.55,
            'current': 24.0,
            'unit': '°C'
        },
        'Humidity': {
            'predicted': 44.91,
            'current': 49.5,
            'unit': '%'
        },
        'Pressure': {
            'predicted': 948.0,
            'current': 949.6,
            'unit': 'hPa'
        }
    }
}

print("Sending sample prediction data to backend...")
print(f"AQI: {payload['aqi']}")
print(f"PM2.5: {payload['pm25']} µg/m³")
print(f"PM10: {payload['pm10']} µg/m³")
print()

try:
    response = requests.post('http://localhost:5000/api/predictions', json=payload)
    
    if response.status_code == 200:
        print("✓ SUCCESS! Prediction data sent to backend")
        print(f"  Status: {response.status_code}")
        print()
        print("Now Phi-2 will respond with actual sensor data!")
        print("Try asking in your app:")
        print("  - 'What is the current AQI?'")
        print("  - 'Show me the PM2.5 level'")
        print("  - 'Is the air quality safe?'")
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"✗ Error connecting to backend: {e}")
    print()
    print("Make sure the backend server is running:")
    print("  cd backend")
    print("  python server.py")
