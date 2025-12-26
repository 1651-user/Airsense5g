import json
import requests
from datetime import datetime

# Read latest MQTT data
with open('mqtt_data.json', 'r') as f:
    data = json.load(f)

latest = data[-1]

print("Latest MQTT Data:")
print(f"PM2.5: {latest['pm2_5']}")
print(f"PM10: {latest['pm10']}")
print(f"CO2: {latest['co2']}")
print(f"Temperature: {latest['temperature']}")
print(f"Humidity: {latest['humidity']}")
print(f"Timestamp: {latest['received_at']}")
print()

# Calculate AQI
pm25 = latest['pm2_5']
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

# Send to backend
payload = {
    'timestamp': latest['received_at'],
    'aqi': aqi,
    'pm25': float(latest['pm2_5']),
    'pm10': float(latest['pm10']),
    'co2': float(latest['co2']),
    'tvoc': float(latest.get('tvoc', 0)),
    'temperature': float(latest['temperature']),
    'humidity': float(latest['humidity']),
    'pressure': float(latest.get('pressure', 0))
}

print("Sending to backend...")
try:
    r = requests.post('http://localhost:5000/api/predictions', json=payload, timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("SUCCESS! Latest MQTT data sent to backend")
        print("Phi-2 will now respond with this data!")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Error: {e}")
    print("Is backend running? cd backend && python server.py")
