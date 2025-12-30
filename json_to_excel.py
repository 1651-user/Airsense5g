"""
Convert mqtt_data.json to output_excel.xlsx

This script:
1. Reads mqtt_data.json
2. Appends new data to output_excel.xlsx
3. Removes duplicates
4. Never creates new files - always updates output_excel.xlsx
"""

import sys
import pandas as pd
import json
import os
import time
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

EXCEL_FILE = 'output.xlsx'
JSON_FILE = 'mqtt_data.json'

print("="*80)
print("Updating output_excel.xlsx with MQTT data")
print("="*80)

try:
    # Read the JSON file
    print(f"\n📄 Reading {JSON_FILE}...")
    with open(JSON_FILE, 'r') as f:
        json_data = json.load(f)
    
    print(f"   ✓ Loaded {len(json_data)} records")w
    
    if not json_data:
        print("   ⚠️  No data in JSON file")
        exit(0)
    
    # Convert to DataFrame
    new_df = pd.DataFrame(json_data)
    
    # Check if Excel file exists
    print(f"\n📁 Checking {EXCEL_FILE}...")
    
    if os.path.exists(EXCEL_FILE):
        # Read existing Excel
        existing_df = pd.read_excel(EXCEL_FILE)
        print(f"   ✓ Found existing file with {len(existing_df)} records")
        
        # Combine old and new data
        print(f"\n🔄 Combining data...")
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        print(f"   ✓ Combined: {len(combined_df)} total records")
        
        # Remove duplicates based on timestamp
        if 'received_at' in combined_df.columns:
            initial_count = len(combined_df)
            combined_df = combined_df.drop_duplicates(subset=['received_at'], keep='last')
            duplicates_removed = initial_count - len(combined_df)
            print(f"   ✓ Removed {duplicates_removed} duplicate(s)")
            
            # Sort by timestamp
            combined_df = combined_df.sort_values('received_at')
            print(f"   ✓ Sorted chronologically")
    else:
        # Create new file
        print(f"   ℹ️  File doesn't exist, creating new one")
        combined_df = new_df
    
    # Save to Excel with retry logic
    print(f"\n💾 Saving to {EXCEL_FILE}...")
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            combined_df.to_excel(EXCEL_FILE, index=False)
            print(f"   ✓ Successfully saved!")
            break  # Success, exit retry loop
            
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"   ⚠️  File is locked (probably open in Excel)")
                print(f"   ⏳ Retrying in {retry_delay} seconds... (Attempt {attempt + 2}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"   ❌ Failed after {max_retries} attempts")
                print(f"\n⚠️  SOLUTION: Close {EXCEL_FILE} in Excel and try again")
                raise  # Re-raise the error to be caught by outer exception handler
    
    # Summary
    print("\n" + "="*80)
    print("✅ SUCCESS!")
    print("="*80)
    print(f"\n📊 File: {EXCEL_FILE}")
    print(f"   Total records: {len(combined_df)}")
    print(f"   Columns: {len(combined_df.columns)}")
    
    if 'received_at' in combined_df.columns:
        try:
            combined_df['received_at_dt'] = pd.to_datetime(combined_df['received_at'])
            oldest = combined_df['received_at_dt'].min()
            newest = combined_df['received_at_dt'].max()
            date_range = (newest - oldest).days
            
            print(f"\n📅 Date Range:")
            print(f"   Oldest: {oldest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Newest: {newest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Span: {date_range} days")
        except:
            pass
    
    print(f"\n✅ All data has been updated in {EXCEL_FILE}!")
    print("="*80)
    
except FileNotFoundError:
    print("\n❌ Error: mqtt_data.json not found!")
    print("   Make sure the MQTT pipeline has received at least one message.")

except PermissionError as e:
    print(f"\n❌ Permission Error: {e}")
    print(f"\n💡 SOLUTION:")
    print(f"   1. Close {EXCEL_FILE} in Excel")
    print(f"   2. Close any other programs that might have the file open")
    print(f"   3. Run this script again")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
