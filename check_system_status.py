"""
Quick System Status Check
Verifies all components are running correctly
"""

import sys
import requests
import json
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("AirSense 5G - System Status Check")
print("="*80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

status = {
    'backend': False,
    'mqtt_data': False,
    'predictions': False,
    'phi2': False,
    'flutter': 'Unknown'
}

# Check 1: Backend Server
print("1️⃣  Backend Server (Flask)")
print("-" * 80)
try:
    response = requests.get('http://localhost:5000/health', timeout=3)
    if response.status_code == 200:
        print("   ✅ RUNNING on http://localhost:5000")
        status['backend'] = True
    else:
        print(f"   ⚠️  Responded with status {response.status_code}")
except:
    print("   ❌ NOT RUNNING")
    print("   → Start with: python backend/server.py")

# Check 2: MQTT Data
print("\n2️⃣  MQTT Data Collection")
print("-" * 80)
if os.path.exists('mqtt_data.json'):
    try:
        with open('mqtt_data.json', 'r') as f:
            data = json.load(f)
        
        if data:
            last_record = data[-1]
            timestamp = last_record.get('received_at', 'Unknown')
            print(f"   ✅ DATA AVAILABLE")
            print(f"   → Total records: {len(data)}")
            print(f"   → Last update: {timestamp}")
            status['mqtt_data'] = True
        else:
            print("   ⚠️  File exists but empty")
    except:
        print("   ⚠️  Error reading file")
else:
    print("   ❌ NO DATA FILE")
    print("   → Start MQTT pipeline: python mqtt_to_phi2.py")

# Check 3: Predictions
print("\n3️⃣  Predictions API")
print("-" * 80)
try:
    response = requests.get('http://localhost:5000/api/predictions/latest', timeout=3)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            pred_data = data.get('data', {})
            aqi = pred_data.get('aqi', 'N/A')
            print(f"   ✅ PREDICTIONS AVAILABLE")
            print(f"   → AQI: {aqi}")
            
            if 'predictions' in pred_data:
                pred_count = len(pred_data['predictions'])
                print(f"   → Predictions: {pred_count} pollutants")
            status['predictions'] = True
        else:
            print("   ⚠️  No prediction data yet")
            print("   → Wait for MQTT data to be received")
    else:
        print(f"   ⚠️  API returned {response.status_code}")
except:
    print("   ❌ CANNOT CONNECT")
    print("   → Ensure backend is running")

# Check 4: Phi-2 Connection
print("\n4️⃣  Phi-2 AI Model")
print("-" * 80)
try:
    response = requests.get('http://localhost:5000/api/test-llm', timeout=5)
    if response.status_code == 200:
        print("   ✅ CONNECTED")
        print("   → URL: http://192.168.0.103:1234")
        status['phi2'] = True
    else:
        print(f"   ⚠️  Status {response.status_code}")
except:
    print("   ❌ NOT CONNECTED")
    print("   → Ensure LM Studio is running on 192.168.0.103")

# Check 5: Flutter App
print("\n5️⃣  Flutter App")
print("-" * 80)
print("   ℹ️  Cannot auto-detect Flutter app status")
print("   → If you ran 'flutter run', it should be running")
print("   → Check your device/emulator")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)

all_critical_running = status['backend'] and status['mqtt_data'] and status['predictions'] and status['phi2']

if all_critical_running:
    print("\n🟢 ALL SYSTEMS OPERATIONAL!")
    print("\n✅ Backend Server: Running")
    print("✅ MQTT Data: Available")
    print("✅ Predictions: Available")
    print("✅ Phi-2 AI: Connected")
    print("\n🎉 Your system is ready to use!")
    print("\nNext Steps:")
    print("1. Open Flutter app (if not already open)")
    print("2. Go to Chat screen")
    print("3. Ask: 'Show the pollutant levels'")
    print("4. Verify AI responds with actual sensor values")
else:
    print("\n⚠️  SOME COMPONENTS NOT RUNNING")
    print("\nStatus:")
    print(f"{'✅' if status['backend'] else '❌'} Backend Server")
    print(f"{'✅' if status['mqtt_data'] else '❌'} MQTT Data")
    print(f"{'✅' if status['predictions'] else '❌'} Predictions")
    print(f"{'✅' if status['phi2'] else '❌'} Phi-2 AI")
    
    print("\nTo Fix:")
    if not status['backend']:
        print("→ Start backend: python backend/server.py")
    if not status['mqtt_data']:
        print("→ Start MQTT: python mqtt_to_phi2.py")
    if not status['phi2']:
        print("→ Start LM Studio on 192.168.0.103")

print("\n" + "="*80)
