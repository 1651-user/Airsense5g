"""
Update output_excel.xlsx with new MQTT data

This script:
1. Reads mqtt_data.json
2. Appends new records to output_excel.xlsx (doesn't create new files)
3. Removes duplicates based on timestamp
4. Keeps data sorted by timestamp
"""

import sys
import pandas as pd
import json
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

EXCEL_FILE = 'output_excel.xlsx'
JSON_FILE = 'mqtt_data.json'

print("="*80)
print("Updating Excel File with New MQTT Data")
print("="*80)
print(f"\nTarget Excel: {EXCEL_FILE}")
print(f"Source JSON: {JSON_FILE}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Step 1: Read JSON data
print("📄 Reading MQTT data from JSON...")
try:
    with open(JSON_FILE, 'r') as f:
        json_data = json.load(f)
    
    print(f"   ✓ Loaded {len(json_data)} records from JSON")
    
    if not json_data:
        print("   ⚠️  No data in JSON file!")
        exit(0)
        
except FileNotFoundError:
    print(f"   ❌ {JSON_FILE} not found!")
    print("   Make sure MQTT pipeline is running: python mqtt_to_phi2.py")
    exit(1)
except Exception as e:
    print(f"   ❌ Error reading JSON: {e}")
    exit(1)

# Step 2: Convert JSON to DataFrame
print("\n📊 Converting JSON to DataFrame...")
new_df = pd.DataFrame(json_data)
print(f"   ✓ Created DataFrame with {len(new_df)} rows")

# Step 3: Read existing Excel file (if exists)
print(f"\n📁 Checking for existing Excel file...")
if os.path.exists(EXCEL_FILE):
    try:
        existing_df = pd.read_excel(EXCEL_FILE)
        print(f"   ✓ Found existing file with {len(existing_df)} rows")
        
        # Combine old and new data
        print("\n🔄 Combining old and new data...")
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        print(f"   ✓ Combined: {len(combined_df)} total rows")
        
    except Exception as e:
        print(f"   ⚠️  Error reading existing file: {e}")
        print("   Creating new file instead...")
        combined_df = new_df
else:
    print(f"   ℹ️  File doesn't exist, will create new one")
    combined_df = new_df

# Step 4: Remove duplicates based on timestamp
print("\n🧹 Removing duplicates...")
initial_count = len(combined_df)

if 'received_at' in combined_df.columns:
    combined_df = combined_df.drop_duplicates(subset=['received_at'], keep='last')
    duplicates_removed = initial_count - len(combined_df)
    print(f"   ✓ Removed {duplicates_removed} duplicate(s)")
    print(f"   ✓ Unique records: {len(combined_df)}")
    
    # Sort by timestamp
    print("\n📅 Sorting by timestamp...")
    combined_df = combined_df.sort_values('received_at')
    print(f"   ✓ Data sorted chronologically")
else:
    print("   ⚠️  No 'received_at' column found, skipping deduplication")

# Step 5: Save to Excel
print(f"\n💾 Saving to {EXCEL_FILE}...")
try:
    combined_df.to_excel(EXCEL_FILE, index=False)
    print(f"   ✓ Successfully saved!")
    
    # Show summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n📊 Excel File Updated: {EXCEL_FILE}")
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
    
    print(f"\n✅ Excel file updated successfully!")
    print(f"   New data has been appended to {EXCEL_FILE}")
    
except Exception as e:
    print(f"   ❌ Error saving Excel: {e}")
    exit(1)

print("\n" + "="*80)
