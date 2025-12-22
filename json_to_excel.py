"""
Convert mqtt_data.json to Excel

Simple script to convert the JSON data collected by mqtt_to_tinyllama.py to Excel format.
"""

import pandas as pd
import json
from datetime import datetime

print("Converting mqtt_data.json to Excel...")

try:
    # Read the JSON file
    with open('mqtt_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} records from mqtt_data.json")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'mqtt_data_{timestamp}.xlsx'
    
    # Save to Excel
    df.to_excel(output_file, index=False)
    
    print(f"✓ Successfully created: {output_file}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")
    print(f"\nColumns: {', '.join(df.columns.tolist())}")
    
except FileNotFoundError:
    print("✗ Error: mqtt_data.json not found!")
    print("  Make sure the MQTT pipeline has received at least one message.")
    
except Exception as e:
    print(f"✗ Error: {e}")
