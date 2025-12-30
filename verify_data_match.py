import pandas as pd
import os
import sys

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=== VERIFYING EXCEL DATA MATCH ===")
for i in range(1, 6):
    file = f'output{i}.xlsx'
    if os.path.exists(file):
        try:
            df = pd.read_excel(file)
            last_row = df.iloc[-1]
            print(f"\n--- {file} (Sensor {i}) ---")
            print(f"PM2.5: {last_row.get('uplink_message.decoded_payload.pm2_5', 'N/A')}")
            print(f"PM10: {last_row.get('uplink_message.decoded_payload.pm10', 'N/A')}")
            print(f"CO2: {last_row.get('uplink_message.decoded_payload.co2', 'N/A')}")
            print(f"TVOC: {last_row.get('uplink_message.decoded_payload.tvoc', 'N/A')}")
            print(f"Temp: {last_row.get('uplink_message.decoded_payload.temperature', 'N/A')}")
            print(f"Hum: {last_row.get('uplink_message.decoded_payload.humidity', 'N/A')}")
            print(f"Pres: {last_row.get('uplink_message.decoded_payload.pressure', 'N/A')}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    else:
        print(f"{file} does not exist.")
