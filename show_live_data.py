"""
Show Latest Live Data from output.xlsx

This script displays the most recent sensor readings in a clear, readable format.
"""

import sys
import pandas as pd
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("📊 LATEST LIVE SENSOR DATA")
print("="*80)

try:
    # Read Excel file
    df = pd.read_excel('output.xlsx')
    
    # Get the last row with sensor data
    # Filter rows that have pm2_5 data
    sensor_data = df[df['pm2_5'].notna()]
    
    if len(sensor_data) == 0:
        print("\n❌ No sensor data found in output.xlsx")
        exit(1)
    
    # Get the latest reading
    latest = sensor_data.iloc[-1]
    
    # Display timestamp
    timestamp = latest.get('received_at', 'Unknown')
    print(f"\n📅 Timestamp: {timestamp}")
    print(f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display sensor readings
    print("\n" + "="*80)
    print("🌡️  CURRENT SENSOR READINGS")
    print("="*80)
    
    # Air Quality
    pm25 = latest.get('pm2_5', 'N/A')
    pm10 = latest.get('pm10', 'N/A')
    
    if pm25 != 'N/A':
        # Calculate AQI
        if pm25 <= 12:
            aqi = int((50/12) * pm25)
        elif pm25 <= 35.4:
            aqi = int(50 + ((100-50)/(35.4-12.1)) * (pm25-12.1))
        elif pm25 <= 55.4:
            aqi = int(100 + ((150-100)/(55.4-35.5)) * (pm25-35.5))
        else:
            aqi = int(150 + ((200-150)/(150.4-55.5)) * (pm25-55.5))
        
        aqi_cat = "Good" if aqi <= 50 else "Moderate" if aqi <= 100 else "Unhealthy for Sensitive Groups" if aqi <= 150 else "Unhealthy"
        
        print(f"\n🎯 Air Quality Index (AQI): {aqi} ({aqi_cat})")
    
    print(f"\n💨 Particulate Matter:")
    print(f"   PM2.5:       {pm25} µg/m³")
    print(f"   PM10:        {pm10} µg/m³")
    
    # Gases
    co2 = latest.get('co2', 'N/A')
    tvoc = latest.get('tvoc', 'N/A')
    
    print(f"\n🧪 Gases:")
    print(f"   CO2:         {co2} ppm")
    print(f"   TVOC:        {tvoc} ppb")
    
    # Environmental
    temp = latest.get('temperature', 'N/A')
    hum = latest.get('humidity', 'N/A')
    pres = latest.get('pressure', 'N/A')
    
    print(f"\n🌡️  Environmental:")
    print(f"   Temperature: {temp}°C")
    print(f"   Humidity:    {hum}%")
    print(f"   Pressure:    {pres} hPa")
    
    # Device Status
    battery = latest.get('battery', 'N/A')
    light = latest.get('light_level', 'N/A')
    pir = latest.get('pir', 'N/A')
    
    print(f"\n🔋 Device Status:")
    print(f"   Battery:     {battery}%")
    print(f"   Light Level: {light}")
    print(f"   Motion:      {pir}")
    
    # Show last 5 readings
    print("\n" + "="*80)
    print("📈 LAST 5 READINGS")
    print("="*80)
    
    last_5 = sensor_data.tail(5)[['received_at', 'pm2_5', 'pm10', 'co2', 'temperature']]
    print("\n" + last_5.to_string(index=False))
    
    print("\n" + "="*80)
    print(f"✅ Total sensor readings in file: {len(sensor_data)}")
    print("="*80)
    
except FileNotFoundError:
    print("\n❌ Error: output.xlsx not found!")
    print("   Run: python json_to_excel.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
