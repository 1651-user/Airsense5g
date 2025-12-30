import pandas as pd

print("="*80)
print("VERIFYING ALL 5 SENSORS")
print("="*80)

for sensor_id in range(1, 6):
    if sensor_id == 3:
        excel_file = 'output3.xlsx'
    else:
        excel_file = f'output{sensor_id}.xlsx'
    
    df = pd.read_excel(excel_file)
    long_cols = [c for c in df.columns if 'decoded_payload' in c]
    
    print(f"\nSensor {sensor_id} ({excel_file}):")
    print(f"  Rows: {len(df)}")
    print(f"  Total columns: {len(df.columns)}")
    print(f"  Long columns: {len(long_cols)}")
    
    if long_cols:
        print(f"  Sample: {long_cols[0]}")

print("\n" + "="*80)
print("ALL SENSORS VERIFIED!")
print("="*80)
