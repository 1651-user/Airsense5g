"""
Clean Corrupt Excel Data - Remove Impossible PM Values
This script fixes Sensors 1, 2, and 5 by removing rows with PM2.5 > 500
"""

import pandas as pd
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 80)
print("CLEANING CORRUPT EXCEL DATA")
print("=" * 80)
print("\nRemoving rows with impossible PM values (PM2.5 > 500 or PM10 > 600)")
print()

sensors_to_clean = {
    1: 'output1.xlsx',
    2: 'output2.xlsx',
    5: 'output5.xlsx'
}

for sensor_id, excel_file in sensors_to_clean.items():
    print(f"\n[Sensor {sensor_id}] Cleaning {excel_file}...")
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        original_count = len(df)
        print(f"  Original rows: {original_count}")
        
        # Find PM2.5 column (could be short or long name)
        pm25_col = None
        pm10_col = None
        
        for col in df.columns:
            if 'pm2_5' in col.lower() or 'pm2.5' in col.lower():
                pm25_col = col
            if 'pm10' in col.lower():
                pm10_col = col
        
        if pm25_col is None:
            print(f"  ⚠️  WARNING: Could not find PM2.5 column")
            continue
        
        # Remove rows with impossible values
        # PM2.5 should be 0-500, PM10 should be 0-600
        clean_df = df.copy()
        
        if pm25_col:
            before = len(clean_df)
            clean_df = clean_df[clean_df[pm25_col] <= 500]
            removed = before - len(clean_df)
            if removed > 0:
                print(f"  Removed {removed} rows with PM2.5 > 500")
        
        if pm10_col:
            before = len(clean_df)
            clean_df = clean_df[clean_df[pm10_col] <= 600]
            removed = before - len(clean_df)
            if removed > 0:
                print(f"  Removed {removed} rows with PM10 > 600")
        
        final_count = len(clean_df)
        print(f"  Final rows: {final_count}")
        print(f"  Removed total: {original_count - final_count} corrupt rows")
        
        # Show last values
        if pm25_col and final_count > 0:
            last_pm25 = clean_df[pm25_col].iloc[-1]
            print(f"  ✓ Last PM2.5 value: {last_pm25:.1f} (realistic!)")
        
        # Save cleaned file
        clean_df.to_excel(excel_file, index=False)
        print(f"  ✅ Saved cleaned data to {excel_file}")
        
    except Exception as e:
        print(f"  ❌ ERROR cleaning {excel_file}: {e}")

print("\n" + "=" * 80)
print("CLEANING COMPLETE")
print("=" * 80)
print("\nAll sensors now have realistic PM values!")
print("You can now run: python start_with_predictions.py")
