import os

files = [f'mqtt_data_sensor{i}.json' for i in range(1, 6)]
for f in files:
    if os.path.exists(f):
        with open(f, 'w') as out:
            out.write('[]')
        print(f"Cleared {f}")
