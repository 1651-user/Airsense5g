"""
Excel Integration for All Sensors
Automatically loads historical data and saves new MQTT data to Excel

This script runs alongside the sensor MQTT scripts and:
1. Loads last 100 rows from each sensor's Excel file
2. Monitors JSON files for new MQTT data
3. Appends new data to respective Excel files
4. Provides historical context for better predictions

Usage:
    python excel_integration.py
"""

import pandas as pd
import json
import time
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Sensor configurations
SENSORS = {
    1: {'json': 'mqtt_data_sensor1.json', 'excel': 'output1.xlsx'},
    2: {'json': 'mqtt_data_sensor2.json', 'excel': 'output2.xlsx'},
    3: {'json': 'mqtt_data.json', 'excel': 'output.xlsx'},  # Sensor 3
    4: {'json': 'mqtt_data_sensor4.json', 'excel': 'output4.xlsx'},
    5: {'json': 'mqtt_data_sensor5.json', 'excel': 'output5.xlsx'},
}

print("="*80)
print("EXCEL INTEGRATION FOR ALL 5 SENSORS")
print("="*80)


def append_to_excel(sensor_id, new_data):
    """Append new data to sensor's Excel file - Maps to long-name columns"""
    excel_file = SENSORS[sensor_id]['excel']
    
    try:
        # Load existing Excel
        if os.path.exists(excel_file):
            df_existing = pd.read_excel(excel_file)
            existing_columns = df_existing.columns.tolist()
        else:
            df_existing = pd.DataFrame()
            existing_columns = []
        
        # Create DataFrame from new data
        df_new = pd.DataFrame([new_data]) if isinstance(new_data, dict) else pd.DataFrame(new_data)
        
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
        
        # Rename columns
        df_new = df_new.rename(columns=column_mapping)
        
        # Filter to only existing Excel columns
        if existing_columns:
            df_new = df_new[[col for col in df_new.columns if col in existing_columns]]
            
            # Add missing columns as None
            for col in existing_columns:
                if col not in df_new.columns:
                    df_new[col] = None
            
            # Reorder to match existing Excel column order
            df_new = df_new[existing_columns]
        
        # Combine with existing data
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        
        # Remove duplicates based on timestamp
        if 'received_at' in df_combined.columns:
            df_combined = df_combined.drop_duplicates(subset=['received_at'], keep='last')
        
        # Save back to Excel
        df_combined.to_excel(excel_file, index=False)
        print(f"[Sensor {sensor_id}] Saved to {excel_file} (total: {len(df_combined)} records)")
        return True
        
    except PermissionError:
        print(f"[Sensor {sensor_id}] Cannot save - {excel_file} is open")
        return False
    except Exception as e:
        print(f"[Sensor {sensor_id}] Error: {e}")
        return False


def sync_json_to_excel(sensor_id):
    """Sync JSON data to Excel"""
    json_file = SENSORS[sensor_id]['json']
    
    if not os.path.exists(json_file):
        return
    
    try:
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        
        if json_data:
            # Get last record
            last_record = json_data[-1] if isinstance(json_data, list) else json_data
            append_to_excel(sensor_id, last_record)
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
                print(f"\n[Sensor {sensor_id}] Detected new data in {config['json']}")
                time.sleep(0.5)  # Wait for file write to complete
                sync_json_to_excel(sensor_id)
                break


def initial_sync():
    """Initial sync of all JSON files to Excel"""
    print("\n[INITIAL SYNC] Syncing all sensors...")
    for sensor_id in SENSORS.keys():
        sync_json_to_excel(sensor_id)
    print("[INITIAL SYNC] Complete\n")


def main():
    """Main function"""
    
    # Initial sync
    initial_sync()
    
    # Setup file watcher
    event_handler = JSONFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    
    print("[WATCHING] Monitoring JSON files for changes...")
    print("[INFO] Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping Excel integration...")
        observer.stop()
        observer.join()
        print("[SHUTDOWN] Stopped")


if __name__ == "__main__":
    main()
