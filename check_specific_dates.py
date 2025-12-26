"""
Check for data on specific dates: Dec 24 and Dec 25, 2025
"""

import sys
import json
import pandas as pd
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("Checking for Data on Dec 24 and Dec 25, 2025")
print("="*80)

# Check JSON file
print("\n📄 Checking mqtt_data.json...")
try:
    with open('mqtt_data.json', 'r') as f:
        json_data = json.load(f)
    
    print(f"   Total records: {len(json_data)}")
    
    # Parse timestamps and check dates
    dates_found = {}
    for record in json_data:
        ts_str = record.get('received_at', '')
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                date_key = ts.strftime('%Y-%m-%d')
                if date_key not in dates_found:
                    dates_found[date_key] = 0
                dates_found[date_key] += 1
            except:
                pass
    
    print("\n   Records by date:")
    for date in sorted(dates_found.keys()):
        marker = "   ⚠️ " if date in ['2025-12-24', '2025-12-25'] else "      "
        print(f"{marker}{date}: {dates_found[date]} records")
    
    if '2025-12-24' in dates_found:
        print(f"\n   ✓ Dec 24 data found: {dates_found['2025-12-24']} records")
    else:
        print(f"\n   ✗ Dec 24 data NOT found in JSON")
    
    if '2025-12-25' in dates_found:
        print(f"   ✓ Dec 25 data found: {dates_found['2025-12-25']} records")
    else:
        print(f"   ✗ Dec 25 data NOT found in JSON")

except Exception as e:
    print(f"   ✗ Error reading JSON: {e}")

# Check combined Excel file
print("\n📊 Checking combined Excel file...")
try:
    # Find the most recent combined file
    import glob
    combined_files = glob.glob('mqtt_data_combined_*.xlsx')
    if combined_files:
        combined_files.sort(reverse=True)
        latest_combined = combined_files[0]
        
        print(f"   File: {latest_combined}")
        df = pd.read_excel(latest_combined)
        print(f"   Total records: {len(df)}")
        
        # Parse timestamps
        df['received_at_dt'] = pd.to_datetime(df['received_at'])
        df['date'] = df['received_at_dt'].dt.strftime('%Y-%m-%d')
        
        date_counts = df['date'].value_counts().sort_index()
        
        print("\n   Records by date:")
        for date, count in date_counts.items():
            marker = "   ⚠️ " if date in ['2025-12-24', '2025-12-25'] else "      "
            print(f"{marker}{date}: {count} records")
        
        if '2025-12-24' in date_counts.index:
            print(f"\n   ✓ Dec 24 data found: {date_counts['2025-12-24']} records")
        else:
            print(f"\n   ✗ Dec 24 data NOT found in combined Excel")
        
        if '2025-12-25' in date_counts.index:
            print(f"   ✓ Dec 25 data found: {date_counts['2025-12-25']} records")
        else:
            print(f"   ✗ Dec 25 data NOT found in combined Excel")
    else:
        print("   ✗ No combined Excel file found")
        
except Exception as e:
    print(f"   ✗ Error reading Excel: {e}")

# Check all individual Excel files
print("\n📁 Checking all individual Excel files...")
try:
    import glob
    excel_files = glob.glob('mqtt_data_*.xlsx')
    excel_files = [f for f in excel_files if not f.startswith('mqtt_data_combined_')]
    excel_files.sort()
    
    all_dates = {}
    
    for file in excel_files:
        try:
            df = pd.read_excel(file)
            if 'received_at' in df.columns:
                df['received_at_dt'] = pd.to_datetime(df['received_at'])
                df['date'] = df['received_at_dt'].dt.strftime('%Y-%m-%d')
                
                for date in df['date'].unique():
                    if date not in all_dates:
                        all_dates[date] = []
                    all_dates[date].append(file)
        except:
            pass
    
    print(f"\n   Found data across {len(all_dates)} unique dates:")
    for date in sorted(all_dates.keys()):
        marker = "   ⚠️ " if date in ['2025-12-24', '2025-12-25'] else "      "
        print(f"{marker}{date}: in {len(all_dates[date])} file(s)")
        if date in ['2025-12-24', '2025-12-25']:
            for f in all_dates[date]:
                print(f"         - {f}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

# Final verdict
print("\n" + "="*80)
print("VERDICT:")
print("="*80)

if '2025-12-24' not in dates_found and '2025-12-25' not in dates_found:
    print("\n❌ NO DATA from Dec 24 or Dec 25, 2025")
    print("\nPossible reasons:")
    print("   1. MQTT sensor was not sending data on those days")
    print("   2. MQTT pipeline (mqtt_to_phi2.py) was not running")
    print("   3. Data was collected but has been overwritten (100 record limit)")
    print("   4. Network/connectivity issues on those dates")
    print("\nWhat to check:")
    print("   • Was the MQTT pipeline running on Dec 24-25?")
    print("   • Was the sensor powered on and connected?")
    print("   • Check system logs for those dates")
else:
    if '2025-12-24' in dates_found:
        print(f"\n✓ Dec 24 data exists: {dates_found['2025-12-24']} records")
    if '2025-12-25' in dates_found:
        print(f"✓ Dec 25 data exists: {dates_found['2025-12-25']} records")

print("="*80)
