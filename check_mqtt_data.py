"""
Check MQTT data and diagnose why past two days' data might be missing
"""

import sys
import json
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("MQTT Data Diagnostic")
print("="*80)

try:
    # Read the JSON file
    with open('mqtt_data.json', 'r') as f:
        data = json.load(f)
    
    print(f"\n✓ Successfully loaded mqtt_data.json")
    print(f"  Total records: {len(data)}")
    
    if not data:
        print("\n❌ ERROR: No data in mqtt_data.json!")
        print("   The file is empty. MQTT pipeline may not be receiving data.")
        exit()
    
    # Check timestamps
    print(f"\n📅 Timestamp Analysis:")
    print(f"  First record: {data[0].get('received_at', 'N/A')}")
    print(f"  Last record:  {data[-1].get('received_at', 'N/A')}")
    
    # Parse timestamps and check date range
    timestamps = []
    for record in data:
        ts_str = record.get('received_at', '')
        if ts_str:
            try:
                # Parse ISO format timestamp
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                timestamps.append(ts)
            except:
                pass
    
    if timestamps:
        oldest = min(timestamps)
        newest = max(timestamps)
        date_range = (newest - oldest).days
        
        print(f"\n📊 Date Range:")
        print(f"  Oldest: {oldest.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Newest: {newest.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Span: {date_range} days")
        
        # Check if data is from past 2 days
        now = datetime.now(oldest.tzinfo) if oldest.tzinfo else datetime.now()
        two_days_ago = now - timedelta(days=2)
        
        print(f"\n🔍 Data Coverage:")
        print(f"  Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Two days ago: {two_days_ago.strftime('%Y-%m-%d %H:%M:%S')}")
        
        recent_records = [ts for ts in timestamps if ts >= two_days_ago]
        print(f"  Records from past 2 days: {len(recent_records)} / {len(timestamps)}")
        
        if len(recent_records) < len(timestamps):
            print(f"\n⚠️  WARNING: Some data is older than 2 days!")
            print(f"     This is expected - mqtt_data.json keeps last 100 records.")
    
    # Check data structure
    print(f"\n📋 Data Structure:")
    if data:
        sample = data[0]
        print(f"  Sample record keys: {list(sample.keys())}")
        
        # Check for sensor values
        sensor_keys = [k for k in sample.keys() if k not in ['received_at', 'timestamp']]
        print(f"  Sensor fields: {sensor_keys}")
    
    # THE ISSUE: mqtt_data.json only keeps last 100 records
    print(f"\n💡 IMPORTANT:")
    print(f"   mqtt_data.json is configured to keep only the last 100 records.")
    print(f"   See mqtt_to_phi2.py line 209: 'if len(existing_data) > 100'")
    print(f"   ")
    print(f"   If you need historical data from past 2 days:")
    print(f"   1. Check if you have older Excel exports")
    print(f"   2. Consider using a database (MongoDB) for long-term storage")
    print(f"   3. Or increase the limit in mqtt_to_phi2.py")
    
    print(f"\n✓ Diagnostic complete!")
    
except FileNotFoundError:
    print("\n❌ ERROR: mqtt_data.json not found!")
    print("   Make sure the MQTT pipeline is running.")
    
except json.JSONDecodeError as e:
    print(f"\n❌ ERROR: Invalid JSON in mqtt_data.json!")
    print(f"   {e}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("="*80)
