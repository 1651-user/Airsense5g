"""
Restore ALL 5 sensors to their original long column name structure
Use the earliest backups which have the original MQTT structure
"""
import pandas as pd
import os
import shutil

print("="*80)
print("RESTORING ALL 5 SENSORS TO ORIGINAL LONG COLUMN STRUCTURE")
print("="*80)

# Define which backup to use for each sensor
SENSOR_RESTORES = {
    1: {'backup': 'output1_backup_20251229.xlsx', 'output': 'output1.xlsx'},
    2: {'backup': 'output2_backup_20251229.xlsx', 'output': 'output2.xlsx'},
    3: {'backup': 'output3_backup_20251229.xlsx', 'output': 'output3.xlsx'},
    4: {'backup': 'output4_backup_20251229.xlsx', 'output': 'output4.xlsx'},
    5: {'backup': 'output5_backup.xlsx', 'output': 'output5.xlsx'},  # Use earliest backup
}

restored = []
failed = []

for sensor_id, files in SENSOR_RESTORES.items():
    backup_file = files['backup']
    output_file = files['output']
    
    print(f"\n[Sensor {sensor_id}]")
    
    if not os.path.exists(backup_file):
        print(f"  SKIP - Backup not found: {backup_file}")
        failed.append(sensor_id)
        continue
    
    try:
        # Read backup to verify it has long columns
        df = pd.read_excel(backup_file)
        long_cols = [c for c in df.columns if 'decoded_payload' in c or 'uplink_message' in c]
        
        print(f"  Backup: {len(df)} rows, {len(df.columns)} columns")
        print(f"  Long columns: {len(long_cols)}")
        
        if len(long_cols) > 5:
            # This backup has the original long structure
            shutil.copy2(backup_file, output_file)
            print(f"  ✓ Restored from {backup_file}")
            restored.append(sensor_id)
        else:
            print(f"  WARNING: Backup doesn't have long columns, skipping")
            failed.append(sensor_id)
    
    except Exception as e:
        print(f"  ERROR: {e}")
        failed.append(sensor_id)

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nRestored: {len(restored)}/5 sensors")
if restored:
    print(f"  Sensors: {restored}")

if failed:
    print(f"\nFailed/Skipped: {len(failed)}/5 sensors")
    print(f"  Sensors: {failed}")

# Verify restored files
if restored:
    print("\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    for sensor_id in restored:
        output_file = SENSOR_RESTORES[sensor_id]['output']
        df = pd.read_excel(output_file)
        long_cols = [c for c in df.columns if 'decoded_payload' in c]
        
        print(f"\nSensor {sensor_id} ({output_file}):")
        print(f"  Rows: {len(df)}")
        print(f"  Total columns: {len(df.columns)}")
        print(f"  Long columns: {len(long_cols)}")
        if long_cols:
            print(f"  Examples: {long_cols[:3]}")

print("\n" + "="*80)
print("DONE!")
print("="*80)
