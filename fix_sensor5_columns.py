"""
Fix Sensor 5 Excel Column Mapping
This script will:
1. Read the existing output5.xlsx
2. Keep only the correct short-name columns in the right order
3. Save back to output5.xlsx
"""
import pandas as pd
import os

print("="*80)
print("FIXING SENSOR 5 EXCEL COLUMN MAPPING")
print("="*80)

excel_file = 'output5.xlsx'

if not os.path.exists(excel_file):
    print(f"\nERROR: {excel_file} not found!")
    exit(1)

# Read the Excel file
print(f"\n[1/4] Reading {excel_file}...")
df = pd.read_excel(excel_file)
print(f"  OK Loaded {len(df)} rows with {len(df.columns)} columns")

# Define the columns we want to keep (in correct order)
essential_columns = [
    'received_at',
    'sensor_id',
    'battery',
    'pm2_5',      # This should be PM2.5 (88 in your data)
    'pm10',       # This should be PM10 (613 in your data)  
    'co2',        # This should be CO2 (59-60 in your data, but stored correctly)
    'tvoc',       # This should be TVOC (100)
    'temperature', # Temperature (22.4)
    'humidity',   # Humidity (60)
    'pressure',   # Pressure (949.8)
    'light_level',
    'pir'
]

# Find which columns exist
existing_essential = [col for col in essential_columns if col in df.columns]

print(f"\n[2/4] Keeping {len(existing_essential)} essential columns:")
for col in existing_essential:
    print(f"  - {col}")

# Create new dataframe with only essential columns
df_clean = df[existing_essential].copy()

# Backup original file
backup_file = excel_file.replace('.xlsx', '_backup.xlsx')
print(f"\n[3/4] Creating backup: {backup_file}")
df.to_excel(backup_file, index=False)
print(f"  OK Backup saved")

# Save cleaned data
print(f"\n[4/4] Saving cleaned data to {excel_file}...")
df_clean.to_excel(excel_file, index=False)
print(f"  OK Saved {len(df_clean)} rows with {len(df_clean.columns)} columns")

# Show last row to verify
print("\n" + "="*80)
print("VERIFICATION - Last row values:")
print("="*80)
last_row = df_clean.iloc[-1]
print(f"PM2.5: {last_row.get('pm2_5', 'NOT FOUND')}")
print(f"PM10: {last_row.get('pm10', 'NOT FOUND')}")
print(f"CO2: {last_row.get('co2', 'NOT FOUND')}")
print(f"TVOC: {last_row.get('tvoc', 'NOT FOUND')}")
print(f"Temperature: {last_row.get('temperature', 'NOT FOUND')}")  
print(f"Humidity: {last_row.get('humidity', 'NOT FOUND')}")
print(f"Pressure: {last_row.get('pressure', 'NOT FOUND')}")

print("\n" + "="*80)
print("✅ DONE! output5.xlsx has been cleaned")
print("="*80)
print("\nNOTE: Original file backed up to:", backup_file)
