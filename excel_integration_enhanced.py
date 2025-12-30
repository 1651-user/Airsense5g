"""
Enhanced Excel Integration for All Sensors
Automatically loads historical data and appends new MQTT data to Excel

Key Features:
1. Appends new data as ROWS (preserves existing columns)
2. Handles NaN values gracefully
3. Maintains data integrity
4. Real-time monitoring for all 5 sensors

Usage:
    python excel_integration_enhanced.py
"""

import sys
import pandas as pd
import json
import time
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Sensor configurations
SENSORS = {
    1: {'json': 'mqtt_data_sensor1.json', 'excel': 'output1.xlsx'},
    2: {'json': 'mqtt_data_sensor2.json', 'excel': 'output2.xlsx'},
    3: {'json': 'mqtt_data.json', 'excel': 'output3.xlsx'},  # Sensor 3
    4: {'json': 'mqtt_data_sensor4.json', 'excel': 'output4.xlsx'},
    5: {'json': 'mqtt_data_sensor5.json', 'excel': 'output5.xlsx'},
}

print("="*80)
print("ENHANCED EXCEL INTEGRATION - APPEND NEW ROWS ONLY")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def append_to_excel(sensor_id, new_data):
    """Append new data as a new row - preserves existing column structure"""
    excel_file = SENSORS[sensor_id]['excel']
    
    try:
        # Load existing Excel
        if os.path.exists(excel_file):
            df_existing = pd.read_excel(excel_file)
            existing_columns = df_existing.columns.tolist()
            print(f"[Sensor {sensor_id}] Excel has {len(df_existing)} rows, {len(existing_columns)} columns")
        else:
            print(f"[Sensor {sensor_id}] Excel file not found: {excel_file}")
            return False
        
        # Create DataFrame from new data (single row)
        if isinstance(new_data, dict):
            df_new = pd.DataFrame([new_data])
        elif isinstance(new_data, list):
            df_new = pd.DataFrame(new_data)
        else:
            print(f"[Sensor {sensor_id}] Invalid data type")
            return False
        
        # Map JSON short names to Excel long names
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
        
        # Rename columns to match Excel structure
        df_new = df_new.rename(columns=column_mapping)
        
        # Create a new row with ONLY existing columns
        new_row = pd.DataFrame(columns=existing_columns)
        
        # Fill in values from new data, leave rest as NaN
        for col in existing_columns:
            if col in df_new.columns:
                new_row.loc[0, col] = df_new[col].iloc[0]
            else:
                new_row.loc[0, col] = pd.NA
        
        # Add timestamp if not present
        if 'received_at' in existing_columns and pd.isna(new_row.loc[0, 'received_at']):
            new_row.loc[0, 'received_at'] = datetime.now().isoformat()
        
        # Validate and filter data (reject extreme outliers)
        pm25_col = 'uplink_message.decoded_payload.pm2_5'
        if pm25_col in df_new.columns:
            val = df_new[pm25_col].iloc[0]
            if pd.notna(val) and val > 500:
                print(f"[Sensor {sensor_id}] ⚠️ REJECTED: PM2.5 value {val} is too high (possible sensor error)")
                return False

        # Append the new row to existing data
        df_combined = pd.concat([df_existing, new_row], ignore_index=True)
        
        # Remove duplicates based on timestamp (keep latest)
        if 'received_at' in df_combined.columns:
            # Convert to datetime for comparison
            df_combined['received_at_temp'] = pd.to_datetime(df_combined['received_at'], errors='coerce')
            df_combined = df_combined.sort_values('received_at_temp')
            df_combined = df_combined.drop_duplicates(subset=['received_at_temp'], keep='last')
            df_combined = df_combined.drop(columns=['received_at_temp'])
        
        # Save back to Excel
        df_combined.to_excel(excel_file, index=False)
        print(f"[Sensor {sensor_id}] ✓ Appended 1 row → Total: {len(df_combined)} rows")
        return True
        
    except PermissionError:
        print(f"[Sensor {sensor_id}] ✗ Cannot save - {excel_file} is open")
        return False
    except Exception as e:
        print(f"[Sensor {sensor_id}] ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def sync_json_to_excel(sensor_id):
    """Sync latest JSON data to Excel"""
    json_file = SENSORS[sensor_id]['json']
    
    if not os.path.exists(json_file):
        print(f"[Sensor {sensor_id}] JSON file not found: {json_file}")
        return
    
    try:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        
        if json_data:
            # Get last record
            last_record = json_data[-1] if isinstance(json_data, list) else json_data
            append_to_excel(sensor_id, last_record)
        else:
            print(f"[Sensor {sensor_id}] No data in JSON file")
    except Exception as e:
        print(f"[Sensor {sensor_id}] Error reading JSON: {e}")


class JSONFileHandler(FileSystemEventHandler):
    """Monitor JSON files for changes"""
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Check if it's one of our sensor JSON files
        for sensor_id, config in SENSORS.items():
            if event.src_path.endswith(config['json']):
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [Sensor {sensor_id}] 🆕 New MQTT data detected")
                time.sleep(0.5)  # Wait for file write to complete
                sync_json_to_excel(sensor_id)
                break


def initial_sync():
    """Initial sync of all JSON files to Excel"""
    print("\n[INITIAL SYNC] Syncing all sensors...\n")
    for sensor_id in SENSORS.keys():
        sync_json_to_excel(sensor_id)
    print("\n[INITIAL SYNC] Complete\n")


def main():
    """Main function"""
    
    # Initial sync
    initial_sync()
    
    # Setup file watcher
    event_handler = JSONFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    
    print("="*80)
    print("🔴 MONITORING MQTT FILES - Append new rows automatically")
    print("="*80)
    print("\n💡 New readings will be appended as NEW ROWS (columns preserved)")
    print("💡 No new columns will be created")
    print("💡 NaN values will be handled gracefully\n")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[SHUTDOWN] Stopping Excel integration...")
        observer.stop()
        observer.join()
        print("[SHUTDOWN] Stopped")


if __name__ == "__main__":
    main()
