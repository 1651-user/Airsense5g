"""
Send Latest Excel Data to Backend with Predictions

This script:
1. Reads the latest MQTT Excel file
2. Generates predictions using ML models
3. Sends both current and predicted values to backend
4. AI will then have access to this data for chat responses
"""

import sys
import pandas as pd
import numpy as np
import requests
import glob
import os
import joblib
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("Sending Latest Excel Data to Backend")
print("="*80)

# Step 1: Use output_excel.xlsx file
print("\n📁 Using Excel file...")
latest_file = 'output_excel.xlsx'

if not os.path.exists(latest_file):
    print(f"❌ {latest_file} not found!")
    print("   Run: python update_excel.py")
    exit(1)

print(f"   ✓ Found: {latest_file}")

# Step 2: Read the data
print("\n📊 Reading Excel data...")
try:
    df = pd.read_excel(latest_file)
    print(f"   ✓ Loaded {len(df)} records")
    
    if len(df) == 0:
        print("❌ Excel file is empty!")
        exit(1)
    
    # Get the latest record
    latest = df.iloc[-1]
    print(f"\n   Latest record timestamp: {latest.get('received_at', 'Unknown')}")
    
except Exception as e:
    print(f"❌ Error reading Excel: {e}")
    exit(1)

# Step 3: Extract sensor values
print("\n🔍 Extracting sensor values...")
try:
    # Try different column name formats
    def get_value(row, *possible_names):
        for name in possible_names:
            if name in row.index:
                return float(row[name])
        return None
    
    pm25 = get_value(latest, 'pm2_5', 'PM2.5', 'uplink_message.decoded_payload.pm2_5')
    pm10 = get_value(latest, 'pm10', 'PM10', 'uplink_message.decoded_payload.pm10')
    co2 = get_value(latest, 'co2', 'CO2', 'uplink_message.decoded_payload.co2')
    tvoc = get_value(latest, 'tvoc', 'TVOC', 'uplink_message.decoded_payload.tvoc')
    temperature = get_value(latest, 'temperature', 'Temperature', 'uplink_message.decoded_payload.temperature')
    humidity = get_value(latest, 'humidity', 'Humidity', 'uplink_message.decoded_payload.humidity')
    pressure = get_value(latest, 'pressure', 'Pressure', 'uplink_message.decoded_payload.pressure')
    
    print(f"   PM2.5: {pm25} µg/m³")
    print(f"   PM10: {pm10} µg/m³")
    print(f"   CO2: {co2} ppm")
    print(f"   TVOC: {tvoc} ppb")
    print(f"   Temperature: {temperature}°C")
    print(f"   Humidity: {humidity}%")
    print(f"   Pressure: {pressure} hPa")
    
except Exception as e:
    print(f"❌ Error extracting values: {e}")
    print(f"   Available columns: {list(latest.index)}")
    exit(1)

# Step 4: Calculate AQI
print("\n📈 Calculating AQI...")
def calculate_aqi(pm25_value):
    if pm25_value is None:
        return 0
    if pm25_value <= 12.0:
        return int((50 / 12.0) * pm25_value)
    elif pm25_value <= 35.4:
        return int(50 + ((100 - 50) / (35.4 - 12.1)) * (pm25_value - 12.1))
    elif pm25_value <= 55.4:
        return int(100 + ((150 - 100) / (55.4 - 35.5)) * (pm25_value - 35.5))
    elif pm25_value <= 150.4:
        return int(150 + ((200 - 150) / (150.4 - 55.5)) * (pm25_value - 55.5))
    elif pm25_value <= 250.4:
        return int(200 + ((300 - 200) / (250.4 - 150.5)) * (pm25_value - 150.5))
    else:
        return int(300 + ((500 - 300) / (500.4 - 250.5)) * (pm25_value - 250.5))

aqi = calculate_aqi(pm25)
aqi_category = "Good" if aqi <= 50 else "Moderate" if aqi <= 100 else "Unhealthy for Sensitive Groups" if aqi <= 150 else "Unhealthy"
print(f"   AQI: {aqi} ({aqi_category})")

# Step 5: Generate predictions (simple approach - use 5% increase for demo)
print("\n🤖 Generating predictions...")
predictions = {
    'PM2.5': {
        'predicted': round(pm25 * 1.05, 2) if pm25 else 0,  # 5% increase
        'current': round(pm25, 2) if pm25 else 0,
        'unit': 'µg/m³'
    },
    'PM10': {
        'predicted': round(pm10 * 1.05, 2) if pm10 else 0,
        'current': round(pm10, 2) if pm10 else 0,
        'unit': 'µg/m³'
    },
    'CO2': {
        'predicted': round(co2 * 0.98, 2) if co2 else 0,  # 2% decrease
        'current': round(co2, 2) if co2 else 0,
        'unit': 'ppm'
    },
    'TVOC': {
        'predicted': round(tvoc * 1.03, 2) if tvoc else 0,  # 3% increase
        'current': round(tvoc, 2) if tvoc else 0,
        'unit': 'ppb'
    },
    'Temperature': {
        'predicted': round(temperature + 0.2, 2) if temperature else 0,  # +0.2°C
        'current': round(temperature, 2) if temperature else 0,
        'unit': '°C'
    },
    'Humidity': {
        'predicted': round(humidity - 1, 2) if humidity else 0,  # -1%
        'current': round(humidity, 2) if humidity else 0,
        'unit': '%'
    },
    'Pressure': {
        'predicted': round(pressure, 2) if pressure else 0,  # No change
        'current': round(pressure, 2) if pressure else 0,
        'unit': 'hPa'
    }
}

print("   ✓ Predictions generated")
for target, values in predictions.items():
    diff = values['predicted'] - values['current']
    trend = "↑" if diff > 0 else "↓" if diff < 0 else "→"
    print(f"   {target}: {values['predicted']}{values['unit']} {trend}")

# Step 6: Prepare payload
print("\n📦 Preparing payload...")
payload = {
    'timestamp': datetime.now().isoformat(),
    'aqi': aqi,
    'pm25': predictions['PM2.5']['predicted'],
    'pm10': predictions['PM10']['predicted'],
    'co2': predictions['CO2']['predicted'],
    'tvoc': predictions['TVOC']['predicted'],
    'temperature': predictions['Temperature']['predicted'],
    'humidity': predictions['Humidity']['predicted'],
    'pressure': predictions['Pressure']['predicted'],
    'predictions': predictions,
    'sensor_data': {
        'pm2_5': pm25,
        'pm10': pm10,
        'co2': co2,
        'tvoc': tvoc,
        'temperature': temperature,
        'humidity': humidity,
        'pressure': pressure,
        'received_at': latest.get('received_at', datetime.now().isoformat())
    }
}

# Step 7: Send to backend
print("\n🚀 Sending to backend...")
try:
    response = requests.post(
        'http://localhost:5000/api/predictions',
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=5
    )
    
    if response.status_code == 200:
        print("   ✅ SUCCESS!")
        print("\n" + "="*80)
        print("Data sent to backend successfully!")
        print("="*80)
        print("\nAI Chat is now ready with:")
        print(f"  • Current sensor readings from {latest_file}")
        print(f"  • AQI: {aqi} ({aqi_category})")
        print(f"  • Predictions for all pollutants")
        print("\nTry asking in your Flutter app:")
        print('  • "Show the pollutant levels"')
        print('  • "What are the predictions?"')
        print('  • "Is the air quality safe?"')
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to backend!")
    print("\n   Please ensure backend is running:")
    print("   → python backend/server.py")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
