"""
Comprehensive Check for All 5 Sensors
Check Excel files, JSON data, and MQTT mappings for all sensors
"""
import pandas as pd
import json
import os

SENSORS = {
    1: {'excel': 'output1.xlsx', 'json': 'mqtt_data_sensor1.json', 'script': 'mqtt_to_ai_sensor1.py'},
    2: {'excel': 'output2.xlsx', 'json': 'mqtt_data_sensor2.json', 'script': 'mqtt_to_ai_sensor2.py'},
    3: {'excel': 'output3.xlsx', 'json': 'mqtt_data.json', 'script': 'mqtt_to_phi2.py'},
    4: {'excel': 'output4.xlsx', 'json': 'mqtt_data_sensor4.json', 'script': 'mqtt_to_ai_sensor4.py'},
    5: {'excel': 'output5.xlsx', 'json': 'mqtt_data_sensor5.json', 'script': 'mqtt_to_ai_sensor5.py'},
}

print("="*80)
print("COMPREHENSIVE SENSOR DATA CHECK - ALL 5 SENSORS")
print("="*80)

issues_found = {}

for sensor_id, config in SENSORS.items():
    print(f"\n{'='*80}")
    print(f"SENSOR {sensor_id}")
    print(f"{'='*80}")
    
    sensor_issues = []
    
    # Check Excel file
    excel_file = config['excel']
    if os.path.exists(excel_file):
        try:
            df = pd.read_excel(excel_file)
            print(f"\n[EXCEL] {excel_file}")
            print(f"  Rows: {len(df)}")
            print(f"  Total Columns: {len(df.columns)}")
            
            # Count essential vs redundant columns
            essential_cols = [col for col in df.columns if not col.startswith('uplink_message') 
                            and not col.startswith('end_device_ids') and not col.startswith('_id')
                            and not col.startswith('correlation_ids')]
            redundant_cols = len(df.columns) - len(essential_cols)
            
            print(f"  Essential Columns: {len(essential_cols)}")
            print(f"  Redundant Columns: {redundant_cols}")
            
            if redundant_cols > 10:
                sensor_issues.append(f"Too many redundant columns ({redundant_cols})")
                print(f"  WARNING: {redundant_cols} redundant columns need cleanup")
            
            # Check last row for data sanity
            if len(df) > 0:
                last_row = df.iloc[-1]
                
                # Check for suspicious values
                suspicious = []
                
                if 'battery' in df.columns and last_row.get('battery', 0) > 80:
                    suspicious.append(f"Battery={last_row['battery']} (too high, might be PM2.5)")
                
                if 'pm2_5' in df.columns and last_row.get('pm2_5', 0) < 10:
                    suspicious.append(f"PM2.5={last_row.get('pm2_5')} (too low, might be mislabeled)")
                
                if 'co2' in df.columns:
                    co2_val = last_row.get('co2', 0)
                    if co2_val < 100 or co2_val > 5000:
                        suspicious.append(f"CO2={co2_val} (out of normal range 300-2000 ppm)")
                
                if suspicious:
                    print(f"  SUSPICIOUS VALUES:")
                    for s in suspicious:
                        print(f"      - {s}")
                        sensor_issues.append(s)
                
                # Show last row key values
                print(f"\n  Last Row Values:")
                for col in ['battery', 'pm2_5', 'pm10', 'co2', 'tvoc', 'temperature', 'humidity', 'pressure']:
                    if col in df.columns:
                        val = last_row.get(col)
                        if pd.notna(val):
                            print(f"    {col}: {val}")
                
        except Exception as e:
            print(f"  ERROR reading Excel: {e}")
            sensor_issues.append(f"Excel read error: {e}")
    else:
        print(f"\n[EXCEL] {excel_file} - NOT FOUND")
        sensor_issues.append("Excel file missing")
    
    # Check JSON file
    json_file = config['json']
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if data:
                print(f"\n[JSON] {json_file}")
                print(f"  Records: {len(data) if isinstance(data, list) else 1}")
                
                # Check last record
                last_record = data[-1] if isinstance(data, list) else data
                print(f"  Last Record Keys: {list(last_record.keys())[:10]}...")  # Show first 10 keys
                
        except Exception as e:
            print(f"\n[JSON] ERROR reading {json_file}: {e}")
            sensor_issues.append(f"JSON read error: {e}")
    else:
        print(f"\n[JSON] {json_file} - NOT FOUND")
    
    # Store issues
    if sensor_issues:
        issues_found[sensor_id] = sensor_issues

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

if issues_found:
    print(f"\nFound issues in {len(issues_found)} sensor(s):\n")
    for sensor_id, issues in issues_found.items():
        print(f"Sensor {sensor_id}:")
        for issue in issues:
            print(f"  - {issue}")
        print()
else:
    print("\nAll sensors look good!")

print("="*80)
