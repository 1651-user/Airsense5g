"""
Quick check of Sensor 5 Excel data
"""
import pandas as pd

print("="*80)
print("CHECKING SENSOR 5 EXCEL DATA")
print("="*80)

df = pd.read_excel('output5.xlsx')
print(f"\nTotal rows: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")

# Show last 10 rows
print("\n" + "="*80)
print("LAST 10 ROWS:")
print("="*80)
print(df.tail(10).to_string())

# Show specific columns for last row
print("\n" + "="*80)
print("LAST ROW VALUES:")
print("="*80)
last_row = df.iloc[-1]
print(f"PM2.5: {last_row.get('pm2_5', 'NOT FOUND')}")
print(f"PM10: {last_row.get('pm10', 'NOT FOUND')}")
print(f"CO2: {last_row.get('co2', 'NOT FOUND')}")
print(f"TVOC: {last_row.get('tvoc', 'NOT FOUND')}")
print(f"Temperature: {last_row.get('temperature', 'NOT FOUND')}")
print(f"Humidity: {last_row.get('humidity', 'NOT FOUND')}")
print(f"Pressure: {last_row.get('pressure', 'NOT FOUND')}")
