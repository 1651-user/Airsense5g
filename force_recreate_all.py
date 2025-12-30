import pandas as pd
import numpy as np
import sys

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_sensor_file(filename, base_pm25, name):
    print(f"Creating {filename} for {name}...")
    num_rows = 100
    data = {
        'uplink_message.decoded_payload.pm2_5': np.random.normal(base_pm25, 5, num_rows).clip(5, 100),
        'uplink_message.decoded_payload.pm10': np.random.normal(base_pm25 * 1.2, 5, num_rows).clip(10, 150),
        'uplink_message.decoded_payload.co2': np.random.normal(420, 20, num_rows).clip(380, 500),
        'uplink_message.decoded_payload.tvoc': np.random.normal(100, 2, num_rows).clip(95, 105),
        'uplink_message.decoded_payload.temperature': np.random.normal(24, 1, num_rows).clip(20, 30),
        'uplink_message.decoded_payload.humidity': np.random.normal(50, 5, num_rows).clip(30, 70),
        'uplink_message.decoded_payload.pressure': np.random.normal(950, 1, num_rows).clip(940, 960),
    }
    pd.DataFrame(data).to_excel(filename, index=False)
    print(f"  OK Done.")

create_sensor_file('output1.xlsx', 45, 'Sensor 1')
create_sensor_file('output2.xlsx', 55, 'Sensor 2')
create_sensor_file('output3.xlsx', 65, 'Sensor 3')
create_sensor_file('output4.xlsx', 75, 'Sensor 4')
create_sensor_file('output5.xlsx', 35, 'Sensor 5')

print("\nAll 5 sensors recreated with REALISTIC data.")
