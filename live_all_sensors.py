"""
Automated Live System for All 5 Sensors
Continuously fetches data from all sensors and sends to AI backend
"""

import time
import os
from datetime import datetime
from send_all_sensors_to_ai import fetch_all_sensors, format_sensor_data_for_ai, send_to_backend
import json

# Update interval in seconds (default: 30 seconds)
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '30'))

def run_continuous():
    """Run continuous updates for all sensors"""
    print("="*80)
    print("LIVE SENSOR SYSTEM - ALL 5 SENSORS")
    print("="*80)
    print(f"Update Interval: {UPDATE_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n{'='*80}")
            print(f"Update #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            
            try:
                # Fetch all sensor data
                all_sensor_data = fetch_all_sensors()
                
                if all_sensor_data:
                    # Format for AI
                    formatted_data = format_sensor_data_for_ai(all_sensor_data)
                    
                    # Send to backend
                    success = send_to_backend(formatted_data)
                    
                    if success:
                        print(f"\n✅ Successfully updated {len(all_sensor_data)} sensors")
                        
                        # Save to file for debugging
                        with open('latest_all_sensors.json', 'w') as f:
                            json.dump(formatted_data, f, indent=2)
                    else:
                        print(f"\n⚠ Failed to send data to backend")
                else:
                    print(f"\n⚠ No sensor data available")
                    
            except Exception as e:
                print(f"\n❌ Error in update cycle: {e}")
            
            # Wait for next update
            print(f"\n⏳ Waiting {UPDATE_INTERVAL} seconds until next update...")
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("STOPPED - Live sensor system terminated")
        print("="*80)

if __name__ == "__main__":
    run_continuous()
