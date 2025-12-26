"""
Send latest Excel data to backend for Phi-2
"""
import pandas as pd
import requests
from datetime import datetime

# Read the latest data from Excel
df = pd.read_excel('output.xlsx')
latest = df.iloc[-1]

print("Latest Excel Data (Row 48):")
print(f"PM2.5: {latest['uplink_message.decoded_payload.pm2_5']}")
print(f"PM10: {latest['uplink_message.decoded_payload.pm10']}")
print(f"CO2: {latest['uplink_message.decoded_payload.co2']}")
print(f"Temperature: {latest['uplink_message.decoded_payload.temperature']}")
print(f"Humidity: {latest['uplink_message.decoded_payload.humidity']}")
print(f"Pressure: {latest['uplink_message.decoded_payload.pressure']}")
print(f"Timestamp: {latest['received_at']}")
print()

# Calculate AQI (simplified - using PM2.5)
pm25 = latest['uplink_message.decoded_payload.pm2_5']
if pm25 <= 12:
    aqi = int((50/12) * pm25)
elif pm25 <= 35.4:
    aqi = int(50 + ((100-50)/(35.4-12)) * (pm25-12))
elif pm25 <= 55.4:
    aqi = int(100 + ((150-100)/(55.4-35.4)) * (pm25-35.4))
else:
    aqi = int(150 + ((200-150)/(150.4-55.4)) * (pm25-55.4))

print(f"Calculated AQI: {aqi}")
print()

# Prepare payload for backend
payload = {
    'timestamp': datetime.now().isoformat(),
    'aqi': aqi,
    'pm25': float(latest['uplink_message.decoded_payload.pm2_5']),
    'pm10': float(latest['uplink_message.decoded_payload.pm10']),
    'co2': float(latest['uplink_message.decoded_payload.co2']),
    'temperature': float(latest['uplink_message.decoded_payload.temperature']),
    'humidity': float(latest['uplink_message.decoded_payload.humidity']),
    'pressure': float(latest['uplink_message.decoded_payload.pressure']),
    'predictions': {
        'PM2.5': {
            'predicted': float(latest['uplink_message.decoded_payload.pm2_5']),
            'current': float(latest['uplink_message.decoded_payload.pm2_5']),
            'unit': ' ug/m3'
        },
        'PM10': {
            'predicted': float(latest['uplink_message.decoded_payload.pm10']),
            'current': float(latest['uplink_message.decoded_payload.pm10']),
            'unit': ' ug/m3'
        },
        'CO2': {
            'predicted': float(latest['uplink_message.decoded_payload.co2']),
            'current': float(latest['uplink_message.decoded_payload.co2']),
            'unit': ' ppm'
        },
        'Temperature': {
            'predicted': float(latest['uplink_message.decoded_payload.temperature']),
            'current': float(latest['uplink_message.decoded_payload.temperature']),
            'unit': ' C'
        },
        'Humidity': {
            'predicted': float(latest['uplink_message.decoded_payload.humidity']),
            'current': float(latest['uplink_message.decoded_payload.humidity']),
            'unit': ' %'
        }
    }
}

print("Sending to backend...")
try:
    response = requests.post('http://localhost:5000/api/predictions', json=payload)
    if response.status_code == 200:
        print("SUCCESS! Latest Excel data sent to backend")
        print("Phi-2 will now respond with correct sensor values!")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
    print("Make sure backend is running: cd backend && python server.py")
