"""
Combine All Sensor Data into One Excel File

This script combines:
1. Historical data from output.xlsx (638 rows)
2. Live MQTT data from mqtt_data.json (current session)

Output: combined_sensor_data.xlsx
"""

import pandas as pd
import json
from datetime import datetime

print("="*80)
print("COMBINING ALL SENSOR DATA")
print("="*80)

try:
    # Step 1: Load historical data from output.xlsx
    print("\n[1/4] Loading historical data from output.xlsx...")
    df_historical = pd.read_excel('output.xlsx')
    print(f"  Loaded {len(df_historical)} historical records")
    
    # Extract sensor data columns from historical data
    sensor_cols = [col for col in df_historical.columns if 'uplink_message.decoded_payload' in col]
    if sensor_cols:
        # Create a clean historical dataframe
        df_hist_clean = df_historical[sensor_cols].copy()
        df_hist_clean.columns = [col.replace('uplink_message.decoded_payload.', '') for col in df_hist_clean.columns]
        
        # Add timestamp
        if 'received_at' in df_historical.columns:
            df_hist_clean['received_at'] = df_historical['received_at']
        
        print(f"  Extracted {len(df_hist_clean.columns)} sensor columns")
    else:
        df_hist_clean = df_historical
    
    # Step 2: Load live MQTT data from mqtt_data.json
    print("\n[2/4] Loading live MQTT data from mqtt_data.json...")
    try:
        with open('mqtt_data.json', 'r') as f:
            mqtt_data = json.load(f)
        df_live = pd.DataFrame(mqtt_data)
        print(f"  Loaded {len(df_live)} live records")
    except FileNotFoundError:
        print("  No live MQTT data found (mqtt_data.json doesn't exist)")
        df_live = pd.DataFrame()
    
    # Step 3: Combine the data
    print("\n[3/4] Combining historical and live data...")
    
    if not df_live.empty:
        # Align columns
        all_columns = list(set(df_hist_clean.columns) | set(df_live.columns))
        
        # Reindex both dataframes to have same columns
        df_hist_clean = df_hist_clean.reindex(columns=all_columns)
        df_live = df_live.reindex(columns=all_columns)
        
        # Combine
        df_combined = pd.concat([df_hist_clean, df_live], ignore_index=True)
        print(f"  Combined total: {len(df_combined)} records")
    else:
        df_combined = df_hist_clean
        print(f"  Using only historical data: {len(df_combined)} records")
    
    # Step 4: Save to Excel
    print("\n[4/4] Saving combined data to Excel...")
    
    # Sort by timestamp if available
    if 'received_at' in df_combined.columns:
        df_combined['received_at'] = pd.to_datetime(df_combined['received_at'], errors='coerce')
        # Remove timezone to make Excel compatible
        df_combined['received_at'] = df_combined['received_at'].dt.tz_localize(None)
        df_combined = df_combined.sort_values('received_at')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'combined_sensor_data_{timestamp}.xlsx'
    
    # Save to Excel
    df_combined.to_excel(output_file, index=False)
    
    print(f"\nSUCCESS! Created: {output_file}")
    print(f"  Total rows: {len(df_combined)}")
    print(f"  Total columns: {len(df_combined.columns)}")
    print(f"  Columns: {', '.join(df_combined.columns.tolist()[:10])}...")
    
    # Show data range
    if 'received_at' in df_combined.columns:
        first_date = df_combined['received_at'].min()
        last_date = df_combined['received_at'].max()
        print(f"\n  Data range:")
        print(f"    From: {first_date}")
        print(f"    To:   {last_date}")
    
    print("\n" + "="*80)
    print("DONE! Opening Excel file...")
    print("="*80)
    
    # Open the file
    import os
    os.system(f'start {output_file}')
    
except FileNotFoundError as e:
    print(f"\nERROR: File not found - {e}")
    print("Make sure output.xlsx exists in the current directory")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
