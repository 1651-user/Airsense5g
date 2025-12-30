"""
Comprehensive Fix for All 5 Sensors
1. Clean up redundant columns in all Excel files
2. Fix battery/PM2.5 mapping issues in Sensors 4 and 5
3. Create backups of all files
"""
import pandas as pd
import json
import os
from datetime import datetime

SENSORS = {
    1: {'excel': 'output1.xlsx', 'json': 'mqtt_data_sensor1.json', 'script': 'mqtt_to_ai_sensor1.py'},
    2: {'excel': 'output2.xlsx', 'json': 'mqtt_data_sensor2.json', 'script': 'mqtt_to_ai_sensor2.py'},
    3: {'excel': 'output3.xlsx', 'json': 'mqtt_data.json', 'script': 'mqtt_to_phi2.py'},
    4: {'excel': 'output4.xlsx', 'json': 'mqtt_data_sensor4.json', 'script': 'mqtt_to_ai_sensor4.py'},
    5: {'excel': 'output5.xlsx', 'json': 'mqtt_data_sensor5.json', 'script': 'mqtt_to_ai_sensor5.py'},
}

# Essential columns to keep (in order)
ESSENTIAL_COLUMNS = [
    'received_at',
    'sensor_id',
    'battery',
    'pm2_5',
    'pm10',
    'co2',
    'tvoc',
    'temperature',
    'humidity',
    'pressure',
    'light_level',
    'pir'
]

# Sensors that need battery/PM2.5 fix
SENSORS_WITH_BATTERY_PM25_SWAP = [4, 5]

print("="*80)
print("COMPREHENSIVE FIX FOR ALL 5 SENSORS")
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

results = {}

for sensor_id, config in SENSORS.items():
    print(f"\n{'='*80}")
    print(f"SENSOR {sensor_id}")
    print(f"{'='*80}")
    
    excel_file = config['excel']
    json_file = config['json']
    result = {'excel': False, 'json': False, 'errors': []}
    
    # Fix Excel file
    if os.path.exists(excel_file):
        try:
            print(f"\n[1/2] Processing {excel_file}...")
            df = pd.read_excel(excel_file)
            original_cols = len(df.columns)
            print(f"  Original: {len(df)} rows, {original_cols} columns")
            
            # Keep only essential columns that exist
            existing_essential = [col for col in ESSENTIAL_COLUMNS if col in df.columns]
            df_clean = df[existing_essential].copy()
            
            # Apply battery/PM2.5 fix if needed
            if sensor_id in SENSORS_WITH_BATTERY_PM25_SWAP:
                if 'battery' in df_clean.columns and 'pm2_5' in df_clean.columns:
                    # Where battery > 80, it's actually PM2.5
                    mask = (df_clean['battery'] > 80) & df_clean['battery'].notna()
                    rows_fixed = mask.sum()
                    
                    if rows_fixed > 0:
                        df_clean.loc[mask, 'pm2_5'] = df_clean.loc[mask, 'battery']
                        df_clean.loc[mask, 'battery'] = 100
                        print(f"  Fixed battery/PM2.5 mapping in {rows_fixed} rows")
            
            # Backup
            backup_file = excel_file.replace('.xlsx', f'_backup_{datetime.now().strftime("%Y%m%d")}.xlsx')
            if not os.path.exists(backup_file):  # Don't overwrite existing backup
                df.to_excel(backup_file, index=False)
                print(f"  Backup: {backup_file}")
            
            # Save cleaned data
            df_clean.to_excel(excel_file, index=False)
            print(f"  Saved: {len(df_clean)} rows, {len(df_clean.columns)} columns")
            print(f"  Removed {original_cols - len(df_clean.columns)} redundant columns")
            
            result['excel'] = True
            
        except Exception as e:
            print(f"  ERROR: {e}")
            result['errors'].append(f"Excel: {e}")
    else:
        print(f"\n[1/2] SKIP - {excel_file} not found")
        result['errors'].append("Excel file not found")
    
    # Fix JSON file (only for sensors 4 and 5)
    if sensor_id in SENSORS_WITH_BATTERY_PM25_SWAP and os.path.exists(json_file):
        try:
            print(f"\n[2/2] Processing {json_file}...")
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Apply fix to all records
            fixed_count = 0
            for record in data:
                if 'battery' in record and isinstance(record['battery'], (int, float)) and record['battery'] > 80:
                    record['pm2_5'] = record['battery']
                    record['battery'] = 100
                    fixed_count += 1
            
            if fixed_count > 0:
                # Backup
                backup_json = json_file.replace('.json', f'_backup_{datetime.now().strftime("%Y%m%d")}.json')
                if not os.path.exists(backup_json):
                    with open(backup_json, 'w') as f:
                        json.dump(data, f, indent=2)
                
                # Save fixed data
                with open(json_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                print(f"  Fixed {fixed_count} records in {json_file}")
                result['json'] = True
            else:
                print(f"  No fixes needed for {json_file}")
                result['json'] = True
                
        except Exception as e:
            print(f"  ERROR: {e}")
            result['errors'].append(f"JSON: {e}")
    elif os.path.exists(json_file):
        print(f"\n[2/2] SKIP - {json_file} (no fixes needed for this sensor)")
        result['json'] = True
    
    results[sensor_id] = result

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

successful = sum(1 for r in results.values() if r['excel'])
failed = sum(1 for r in results.values() if r['errors'])

print(f"\nSuccessfully processed: {successful}/5 sensors")
if failed > 0:
    print(f"Failed: {failed}/5 sensors")
    print("\nErrors:")
    for sensor_id, result in results.items():
        if result['errors']:
            print(f"  Sensor {sensor_id}: {', '.join(result['errors'])}")

print("\n" + "="*80)
print("DONE! All sensor files have been cleaned and fixed")
print("="*80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
