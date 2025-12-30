"""
Apply Sensor 5 Data Correction to Existing Files
Fix all historical data in both JSON and Excel files
"""
import json
import pandas as pd
import os

def remap_sensor5_data(data):
    """Fix the incorrect MQTT mapping for Sensor 5"""
    corrected = data.copy()
    
    # If battery > 80, it's actually PM2.5
    if 'battery' in data and isinstance(data['battery'], (int, float)) and data['battery'] > 80:
        corrected['pm2_5'] = data['battery']
        corrected['battery'] = 100
    
    return corrected

print("="*80)
print("FIXING SENSOR 5 HISTORICAL DATA")
print("="*80)

# Fix JSON file
json_file = 'mqtt_data_sensor5.json'
if os.path.exists(json_file):
    print(f"\n[1/2] Fixing {json_file}...")
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Apply fix to all records
    corrected_data = [remap_sensor5_data(record) for record in data]
    
    # Backup original
    backup_json = json_file.replace('.json', '_backup.json')
    with open(backup_json, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  OK Backed up to {backup_json}")
    
    # Save corrected
    with open(json_file, 'w') as f:
        json.dump(corrected_data, f, indent=2)
    print(f"  OK Fixed {len(corrected_data)} records")
else:
    print(f"\n[1/2] SKIP - {json_file} not found")

# Fix Excel file
excel_file = 'output5.xlsx'
if os.path.exists(excel_file):
    print(f"\n[2/2] Fixing {excel_file}...")
    df = pd.read_excel(excel_file)
    
    # Apply fix: where battery > 80, swap to pm2_5
    mask = (df['battery'] > 80) & df['battery'].notna()
    df.loc[mask, 'pm2_5'] = df.loc[mask, 'battery']
    df.loc[mask, 'battery'] = 100
    
    # Save
    df.to_excel(excel_file, index=False)
    print(f"  OK Fixed {mask.sum()} rows")
else:
    print(f"\n[2/2] SKIP - {excel_file} not found")

print("\n" + "="*80)
print("DONE! Sensor 5 data has been corrected")
print("="*80)

# Verify last row
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    last = df.iloc[-1]
    print("\nLast row values:")
    print(f"  PM2.5: {last.get('pm2_5', 'N/A')}")
    print(f"  PM10: {last.get('pm10', 'N/A')}")
    print(f"  CO2: {last.get('co2', 'N/A')}")
    print(f"  Battery: {last.get('battery', 'N/A')}")
