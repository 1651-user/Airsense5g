"""
Fix Sensors 1-3: Rename long column names to short names
These sensors use uplink_message.decoded_payload.* format
We need to rename them to short names like pm2_5, pm10, etc.
"""
import pandas as pd
import os

SENSORS_TO_FIX = {
    1: {
        'backup': 'output1_backup_20251229.xlsx',
        'output': 'output1.xlsx'
    },
    2: {
        'backup': 'output2_backup_20251229.xlsx',
        'output': 'output2.xlsx'
    },
    3: {
        'backup': 'output3_backup_20251229.xlsx',
        'output': 'output3.xlsx'
    }
}

# Column name mapping
COLUMN_MAPPING = {
    'uplink_message.decoded_payload.battery': 'battery',
    'uplink_message.decoded_payload.co2': 'co2',
    'uplink_message.decoded_payload.humidity': 'humidity',
    'uplink_message.decoded_payload.light_level': 'light_level',
    'uplink_message.decoded_payload.pir': 'pir',
    'uplink_message.decoded_payload.pm10': 'pm10',
    'uplink_message.decoded_payload.pm2_5': 'pm2_5',
    'uplink_message.decoded_payload.pressure': 'pressure',
    'uplink_message.decoded_payload.temperature': 'temperature',
    'uplink_message.decoded_payload.tvoc': 'tvoc',
    'uplink_message.decoded_payload.beep': 'beep',
}

print("="*80)
print("FIXING SENSORS 1-3: RENAMING LONG COLUMNS TO SHORT NAMES")
print("="*80)

for sensor_id, files in SENSORS_TO_FIX.items():
    print(f"\n[Sensor {sensor_id}]")
    
    backup_file = files['backup']
    output_file = files['output']
    
    if not os.path.exists(backup_file):
        print(f"  SKIP - Backup not found: {backup_file}")
        continue
    
    try:
        # Read backup
        df = pd.read_excel(backup_file)
        print(f"  Loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Keep received_at and sensor_id if they exist
        essential_cols = ['received_at']
        if 'sensor_id' in df.columns:
            essential_cols.append('sensor_id')
        
        # Rename long column names to short names
        df_renamed = df.rename(columns=COLUMN_MAPPING)
        
        # Keep only essential columns + renamed sensor data columns
        short_sensor_cols = list(COLUMN_MAPPING.values())
        cols_to_keep = [c for c in essential_cols + short_sensor_cols if c in df_renamed.columns]
        
        df_final = df_renamed[cols_to_keep]
        
        # Save
        df_final.to_excel(output_file, index=False)
        print(f"  Saved: {len(df_final)} rows, {len(df_final.columns)} columns")
        print(f"  Columns: {df_final.columns.tolist()}")
        
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "="*80)
print("DONE!")
print("="*80)
