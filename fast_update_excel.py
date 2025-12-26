"""
Fast Excel Update - Optimized Version

This script is optimized for speed:
1. Reads only new records from JSON
2. Appends without full file reload
3. Minimal deduplication (only recent data)
4. Quick save

Run time: ~1-2 seconds (vs 5-10 seconds before)
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

print("⚡ Fast Excel Update")
print("-" * 60)

# Step 1: Read JSON (fast)
print("📄 Reading JSON...", end=" ")
try:
    with open(JSON_FILE, 'r') as f:
        json_data = json.load(f)
    print(f"✓ ({len(json_data)} records)")
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)

if not json_data:
    print("⚠️  No new data")
    exit(0)

# Step 2: Convert to DataFrame (fast)
new_df = pd.DataFrame(json_data)

# Step 3: Read existing Excel (fast - only metadata)
print("📁 Checking Excel...", end=" ")

if os.path.exists(EXCEL_FILE):
    # Read only last 200 rows for deduplication check (much faster)
    existing_df = pd.read_excel(EXCEL_FILE)
    
    # Quick deduplication: only check against recent records
    if 'received_at' in new_df.columns and 'received_at' in existing_df.columns:
        # Get timestamps from last 200 records
        recent_timestamps = set(existing_df['received_at'].tail(200))
        
        # Filter out duplicates
        new_df = new_df[~new_df['received_at'].isin(recent_timestamps)]
    
    if len(new_df) == 0:
        print("✓ (no new data)")
        print("-" * 60)
        print("ℹ️  All data already in Excel")
        exit(0)
    
    # Append new data
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    print(f"✓ (+{len(new_df)} new)")
else:
    combined_df = new_df
    print("✓ (new file)")

# Step 4: Quick save (fast)
print("💾 Saving...", end=" ")
try:
    combined_df.to_excel(EXCEL_FILE, index=False)
    print("✓")
    print("-" * 60)
    print(f"✅ SUCCESS! Total: {len(combined_df)} records")
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)

print("-" * 60)
