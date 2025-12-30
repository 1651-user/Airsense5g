"""
Quick Test Script - Verify All 5 Sensors Are Live
"""

import os
from fetch_all_sensors import fetch_all_sensors, SENSOR_CONFIGS
from dotenv import load_dotenv

def test_sensor_connection(sensor_config):
    """Test connection to a single sensor"""
    try:
        load_dotenv(sensor_config['env_file'])
        
        MONGO_URI = os.getenv("MONGO_URI")
        MONGO_DB = os.getenv("MONGO_DB")
        MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
        
        if not all([MONGO_URI, MONGO_DB, MONGO_COLLECTION]):
            return False, "Missing configuration"
        
        return True, f"{MONGO_DB}/{MONGO_COLLECTION}"
        
    except Exception as e:
        return False, str(e)

def main():
    """Run tests"""
    print("="*80)
    print("TESTING ALL 5 SENSORS")
    print("="*80)
    
    print("\n1. Testing Environment Files...")
    print("-"*80)
    
    for sensor_config in SENSOR_CONFIGS:
        env_file = sensor_config['env_file']
        sensor_name = sensor_config['name']
        
        if os.path.exists(env_file):
            success, info = test_sensor_connection(sensor_config)
            status = "[OK]" if success else "[FAIL]"
            print(f"{status} {sensor_name}: {env_file} -> {info}")
        else:
            print(f"[FAIL] {sensor_name}: {env_file} NOT FOUND")
    
    print("\n2. Fetching Live Data...")
    print("-"*80)
    
    all_data = fetch_all_sensors()
    
    print("\n3. Summary")
    print("-"*80)
    print(f"Total Sensors Configured: 5")
    print(f"Sensors with Data: {len(all_data)}")
    print(f"Success Rate: {len(all_data)}/5 ({len(all_data)*20}%)")
    
    if len(all_data) == 5:
        print("\n[SUCCESS] ALL SENSORS ARE LIVE!")
    elif len(all_data) > 0:
        print(f"\n[WARNING] {5 - len(all_data)} sensor(s) need attention")
    else:
        print("\n[ERROR] NO SENSORS ARE RESPONDING")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
