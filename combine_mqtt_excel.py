"""
Combine all mqtt_data Excel files into one comprehensive file

This script merges all mqtt_data_*.xlsx files to give you complete historical data.
"""

import sys
import pandas as pd
import glob
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("Combining MQTT Data Excel Files")
print("="*80)

try:
    # Find all mqtt_data Excel files
    excel_files = glob.glob('mqtt_data_*.xlsx')
    excel_files.sort()  # Sort by filename (which includes timestamp)
    
    if not excel_files:
        print("\n❌ No mqtt_data_*.xlsx files found!")
        print("   Please run json_to_excel.py first to create Excel files.")
        exit(1)
    
    print(f"\n📁 Found {len(excel_files)} Excel files:")
    for f in excel_files:
        print(f"   • {f}")
    
    # Read and combine all Excel files
    print(f"\n🔄 Reading and combining files...")
    all_data = []
    
    for file in excel_files:
        try:
            df = pd.read_excel(file)
            all_data.append(df)
            print(f"   ✓ {file}: {len(df)} records")
        except Exception as e:
            print(f"   ✗ {file}: Error - {e}")
    
    if not all_data:
        print("\n❌ No data could be read from Excel files!")
        exit(1)
    
    # Combine all dataframes
    combined_df = pd.concat(all_data, ignore_index=True)
    
    print(f"\n📊 Combined Data:")
    print(f"   Total records before deduplication: {len(combined_df)}")
    
    # Remove duplicates based on received_at timestamp
    if 'received_at' in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset=['received_at'], keep='first')
        print(f"   Total records after deduplication: {len(combined_df)}")
        
        # Sort by timestamp
        combined_df = combined_df.sort_values('received_at')
        print(f"   ✓ Sorted by timestamp")
    else:
        print(f"   ⚠️  No 'received_at' column found - skipping deduplication")
    
    # Generate output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'mqtt_data_combined_{timestamp}.xlsx'
    
    # Save combined data
    combined_df.to_excel(output_file, index=False)
    
    print(f"\n✅ Successfully created: {output_file}")
    print(f"   Total records: {len(combined_df)}")
    print(f"   Columns: {len(combined_df.columns)}")
    
    # Show date range if possible
    if 'received_at' in combined_df.columns:
        try:
            # Convert to datetime
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
    
    print(f"\n✓ All historical data has been combined!")
    print(f"   You now have {len(combined_df)} records spanning multiple days.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("="*80)
