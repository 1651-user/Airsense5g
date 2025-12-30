"""
Simple Excel Sync for All Sensors
Monitors JSON files and syncs to Excel every 30 seconds

Usage:
    python simple_excel_sync.py
"""

import pandas as pd
import json
import time
import os
from datetime import datetime

# Sensor configurations
SENSORS = {
    1: {'json': 'mqtt_data_sensor1.json', 'excel': 'output1.xlsx'},
    2: {'json': 'mqtt_data_sensor2.json', 'excel': 'output2.xlsx'},
    3: {'json': 'mqtt_data.json', 'excel': 'output3.xlsx'},
    4: {'json': 'mqtt_data_sensor4.json', 'excel': 'output4.xlsx'},
    5: {'json': 'mqtt_data_sensor5.json', 'excel': 'output5.xlsx'},
}

SYNC_INTERVAL = 30  # seconds

print("="*80)
print("AUTO EXCEL SYNC - ALL 5 SENSORS")
print("="*80)
print(f"Sync Interval: {SYNC_INTERVAL} seconds\n")


def sync_json_to_excel(sensor_id):
    """Sync latest JSON data to Excel - Maps to long-name columns"""
    json_file = SENSORS[sensor_id]['json']
    excel_file = SENSORS[sensor_id]['excel']
    
    if not os.path.exists(json_file):
        return False
    
    try:
        # Read JSON
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        
        if not json_data:
            return False
        
        # Read existing Excel
        if os.path.exists(excel_file):
            df_existing = pd.read_excel(excel_file)
            existing_count = len(df_existing)
            existing_columns = df_existing.columns.tolist()
        else:
            df_existing = pd.DataFrame()
            existing_count = 0
            existing_columns = []
        
        # Convert JSON to DataFrame
        if isinstance(json_data, list):
            df_new = pd.DataFrame(json_data)
        else:
            df_new = pd.DataFrame([json_data])
        
        # KEY FIX: Map JSON short names to Excel long names
        # JSON has: battery, pm2_5, pm10, etc.
        # Excel has: uplink_message.decoded_payload.battery, etc.
        column_mapping = {
            'battery': 'uplink_message.decoded_payload.battery',
            'pm2_5': 'uplink_message.decoded_payload.pm2_5',
            'pm10': 'uplink_message.decoded_payload.pm10',
            'co2': 'uplink_message.decoded_payload.co2',
            'tvoc': 'uplink_message.decoded_payload.tvoc',
            'temperature': 'uplink_message.decoded_payload.temperature',
            'humidity': 'uplink_message.decoded_payload.humidity',
            'pressure': 'uplink_message.decoded_payload.pressure',
            'light_level': 'uplink_message.decoded_payload.light_level',
            'pir': 'uplink_message.decoded_payload.pir',
        }
        
        # Rename JSON columns to match Excel long names
        df_new = df_new.rename(columns=column_mapping)
        
        # Now filter to only existing Excel columns
        if existing_columns:
            # Keep only columns that exist in Excel
            df_new = df_new[[col for col in df_new.columns if col in existing_columns]]
            
            # Add missing columns with NaN
            for col in existing_columns:
                if col not in df_new.columns:
                    df_new[col] = None
            
            # Reorder to match Excel
            df_new = df_new[existing_columns]
        
        # Combine with existing data
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # Remove duplicates based on timestamp
        if 'received_at' in df_combined.columns:
            df_combined = df_combined.drop_duplicates(subset=['received_at'], keep='last')
        
        # Save back to Excel
        df_combined.to_excel(excel_file, index=False)
        
        new_records = len(df_combined) - existing_count
        if new_records > 0:
            print(f"[Sensor {sensor_id}] Added {new_records} new record(s) to {excel_file} (total: {len(df_combined)})")
        
        return True
        
    except PermissionError:
        print(f"[Sensor {sensor_id}] SKIP - {excel_file} is open in Excel")
        return False
    except Exception as e:
        print(f"[Sensor {sensor_id}] ERROR: {e}")
        return False


def main():
    """Main loop"""
    
    print("[STARTING] Auto-sync running...")
    print("[INFO] Press Ctrl+C to stop\n")
    
    try:
        while True:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Syncing all sensors...")
            
            synced = 0
            for sensor_id in SENSORS.keys():
                if sync_json_to_excel(sensor_id):
                    synced += 1
            
            if synced > 0:
                print(f"  OK Synced {synced}/5 sensors\n")
            
            # Wait for next sync
            time.sleep(SYNC_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping Excel sync...")
        print("[SHUTDOWN] Stopped")


if __name__ == "__main__":
    main()
