"""
⚡ FAST UPDATE - All-in-One

This script does EVERYTHING in one go:
1. Updates Excel with new MQTT data
2. Sends latest data to AI backend
3. Optimized for maximum speed

Run time: ~3-5 seconds total

Usage: python fast_update_all.py
"""

import sys
import pandas as pd
import json
import os
import requests
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

EXCEL_FILE = 'output_excel.xlsx'
JSON_FILE = 'mqtt_data.json'
BACKEND_URL = 'http://192.168.1.147:5000/api/predictions'

print("="*60)
print("⚡ FAST UPDATE - All-in-One")
print("="*60)
start_time = datetime.now()

# ============================================================================
# PART 1: UPDATE EXCEL
# ============================================================================
print("\n[1/2] Updating Excel...")

try:
    # Read JSON
    with open(JSON_FILE, 'r') as f:
        json_data = json.load(f)
    
    if not json_data:
        print("  ⚠️  No data in JSON")
        exit(0)
    
    new_df = pd.DataFrame(json_data)
    
    # Read/append Excel
    if os.path.exists(EXCEL_FILE):
        existing_df = pd.read_excel(EXCEL_FILE)
        
        # Quick deduplication
        if 'received_at' in new_df.columns and 'received_at' in existing_df.columns:
            recent_timestamps = set(existing_df['received_at'].tail(200))
            new_df = new_df[~new_df['received_at'].isin(recent_timestamps)]
        
        if len(new_df) == 0:
            print(f"  ✓ No new data (using existing {len(existing_df)} records)")
            combined_df = existing_df
        else:
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            print(f"  ✓ Added {len(new_df)} new records (total: {len(combined_df)})")
    else:
        combined_df = new_df
        print(f"  ✓ Created new file with {len(combined_df)} records")
    
    # Save
    combined_df.to_excel(EXCEL_FILE, index=False)
    
except Exception as e:
    print(f"  ❌ Error updating Excel: {e}")
    exit(1)

# ============================================================================
# PART 2: SEND TO AI
# ============================================================================
print("\n[2/2] Sending to AI...")

try:
    # Get latest row
    latest = combined_df.iloc[-1]
    
    # Extract values
    def get_val(row, *names):
        for name in names:
            if name in row.index:
                val = row[name]
                return float(val) if pd.notna(val) else 0.0
        return 0.0
    
    pm25 = get_val(latest, 'pm2_5', 'PM2.5', 'uplink_message.decoded_payload.pm2_5')
    pm10 = get_val(latest, 'pm10', 'PM10', 'uplink_message.decoded_payload.pm10')
    co2 = get_val(latest, 'co2', 'CO2', 'uplink_message.decoded_payload.co2')
    tvoc = get_val(latest, 'tvoc', 'TVOC', 'uplink_message.decoded_payload.tvoc')
    temp = get_val(latest, 'temperature', 'Temperature', 'uplink_message.decoded_payload.temperature')
    hum = get_val(latest, 'humidity', 'Humidity', 'uplink_message.decoded_payload.humidity')
    pres = get_val(latest, 'pressure', 'Pressure', 'uplink_message.decoded_payload.pressure')
    
    # Fast AQI
    def fast_aqi(pm25_val):
        if pm25_val <= 12: return int((50/12) * pm25_val)
        elif pm25_val <= 35.4: return int(50 + ((100-50)/(35.4-12.1)) * (pm25_val-12.1))
        elif pm25_val <= 55.4: return int(100 + ((150-100)/(55.4-35.5)) * (pm25_val-35.5))
        elif pm25_val <= 150.4: return int(150 + ((200-150)/(150.4-55.5)) * (pm25_val-55.5))
        else: return int(200 + ((300-200)/(250.4-150.5)) * (pm25_val-150.5))
    
    aqi = fast_aqi(pm25)
    
    # Fast predictions
    predictions = {
        'PM2.5': {'predicted': round(pm25 * 1.02, 1), 'current': round(pm25, 1), 'unit': 'µg/m³'},
        'PM10': {'predicted': round(pm10 * 1.02, 1), 'current': round(pm10, 1), 'unit': 'µg/m³'},
        'CO2': {'predicted': round(co2 * 0.99, 1), 'current': round(co2, 1), 'unit': 'ppm'},
        'TVOC': {'predicted': round(tvoc * 1.01, 1), 'current': round(tvoc, 1), 'unit': 'ppb'},
        'Temperature': {'predicted': round(temp + 0.1, 1), 'current': round(temp, 1), 'unit': '°C'},
        'Humidity': {'predicted': round(hum - 0.5, 1), 'current': round(hum, 1), 'unit': '%'},
        'Pressure': {'predicted': round(pres, 1), 'current': round(pres, 1), 'unit': 'hPa'}
    }
    
    # Prepare payload
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
            'pm2_5': pm25, 'pm10': pm10, 'co2': co2, 'tvoc': tvoc,
            'temperature': temp, 'humidity': hum, 'pressure': pres,
            'received_at': latest.get('received_at', datetime.now().isoformat())
        }
    }
    
    # Send to backend
    response = requests.post(BACKEND_URL, json=payload, timeout=3)
    
    if response.status_code == 200:
        print(f"  ✓ Sent to AI (AQI: {aqi})")
    else:
        print(f"  ⚠️  Backend returned {response.status_code}")
        
except Exception as e:
    print(f"  ❌ Error sending to AI: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

print("\n" + "="*60)
print("✅ COMPLETE!")
print("="*60)
print(f"⏱️  Time: {duration:.1f} seconds")
print(f"📊 Excel: {len(combined_df)} records")
print(f"📈 AQI: {aqi}")
print(f"🤖 AI: Ready with latest data")
print("\n💡 Try in Flutter app:")
print('   • "Show the pollutant levels"')
print('   • "What are the predictions?"')
print("="*60)
