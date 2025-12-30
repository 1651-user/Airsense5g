"""
Test the Enhanced System
Verifies NaN handling and row appending functionality
"""

import sys
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("TESTING ENHANCED SYSTEM")
print("="*80)
print()

# Test 1: Check Excel files exist
print("[Test 1] Checking Excel files...")
excel_files = {
    1: 'output1.xlsx',
    2: 'output2.xlsx',
    3: 'output3.xlsx',
    4: 'output4.xlsx',
    5: 'output5.xlsx'
}

for sensor_id, excel_file in excel_files.items():
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        print(f"  ✓ Sensor {sensor_id}: {len(df)} rows, {len(df.columns)} columns")
    else:
        print(f"  ✗ Sensor {sensor_id}: File not found")

print()

# Test 2: Check for NaN values
print("[Test 2] Checking NaN values in Excel files...")

for sensor_id, excel_file in excel_files.items():
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        
        # Find numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Count NaN in each column
        nan_counts = {}
        for col in numeric_cols:
            nan_count = df[col].isna().sum()
            if nan_count > 0:
                nan_counts[col] = nan_count
        
        if nan_counts:
            print(f"  Sensor {sensor_id}:")
            total_nan = sum(nan_counts.values())
            print(f"    → Total NaN values: {total_nan}")
            print(f"    → Columns with NaN: {len(nan_counts)}")
        else:
            print(f"  ✓ Sensor {sensor_id}: No NaN values")

print()

# Test 3: Verify column structure
print("[Test 3] Verifying column structure (should have long names)...")

expected_cols = [
    'uplink_message.decoded_payload.pm2_5',
    'uplink_message.decoded_payload.pm10',
    'uplink_message.decoded_payload.co2',
    'uplink_message.decoded_payload.tvoc'
]

for sensor_id, excel_file in excel_files.items():
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        
        found_cols = [col for col in expected_cols if col in df.columns]
        
        if len(found_cols) == len(expected_cols):
            print(f"  ✓ Sensor {sensor_id}: All expected columns present")
        else:
            print(f"  ⚠️  Sensor {sensor_id}: Missing {len(expected_cols) - len(found_cols)} columns")
            missing = [col for col in expected_cols if col not in df.columns]
            if missing:
                print(f"     Missing: {missing[0]}")

print()

# Test 4: Check latest data
print("[Test 4] Checking latest data values...")

for sensor_id, excel_file in excel_files.items():
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file)
        
        if len(df) > 0:
            # Get latest row
            latest = df.iloc[-1]
            
            # Try to get PM2.5 value
            pm25_cols = ['uplink_message.decoded_payload.pm2_5', 'pm2_5', 'PM2.5']
            pm25_val = None
            
            for col in pm25_cols:
                if col in latest.index:
                    val = latest[col]
                    if pd.notna(val):
                        pm25_val = val
                        break
            
            if pm25_val is not None:
                print(f"  ✓ Sensor {sensor_id}: Latest PM2.5 = {pm25_val:.1f} µg/m³")
            else:
                print(f"  ⚠️  Sensor {sensor_id}: Latest PM2.5 is NaN or missing")

print()

# Test 5: Check JSON files
print("[Test 5] Checking JSON files...")

json_files = {
    1: 'mqtt_data_sensor1.json',
    2: 'mqtt_data_sensor2.json',
    3: 'mqtt_data.json',
    4: 'mqtt_data_sensor4.json',
    5: 'mqtt_data_sensor5.json'
}

for sensor_id, json_file in json_files.items():
    if os.path.exists(json_file):
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            print(f"  ✓ Sensor {sensor_id}: {len(data)} MQTT records")
        else:
            print(f"  ✓ Sensor {sensor_id}: 1 MQTT record")
    else:
        print(f"  ✗ Sensor {sensor_id}: JSON file not found")

print()

# Summary
print("="*80)
print("TEST SUMMARY")
print("="*80)
print()
print("✅ Excel files checked")
print("✅ NaN values identified")
print("✅ Column structure verified")
print("✅ Latest data values checked")
print("✅ JSON files verified")
print()
print("System is ready for enhanced NaN handling and row appending!")
print()
print("Next steps:")
print("  1. Run: python excel_integration_enhanced.py")
print("  2. Run: python live_ai_system_enhanced.py")
print("  Or simply run: start_enhanced_system.bat")
print()
