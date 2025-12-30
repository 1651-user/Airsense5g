"""
Quick test to verify Phi-2 connection at 192.168.1.147:1234

Usage:
    python test_phi2_connection.py
"""
import sys
import requests
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
PHI2_URL = 'http://192.168.1.147:1234'

print("="*80)
print("Testing Phi-2 Connection")
print("="*80)
print(f"\nServer: {PHI2_URL}\n")

# Test 1: Health check
print("[1/3] Testing health endpoint...")
try:
    response = requests.get(f'{PHI2_URL}/health', timeout=5)
    if response.status_code == 200:
        print(f"  ✅ Health check passed: {response.json()}")
    else:
        print(f"  ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Test 2: API predictions endpoint
print("\n[2/3] Testing predictions endpoint...")
try:
    test_payload = {
        'timestamp': '2025-12-26T22:00:00',
        'aqi': 165,
        'pm25': 84.0,
        'pm10': 99.0,
        'co2': 400.0,
        'tvoc': 100.0,
        'temperature': 20.0,
        'humidity': 59.0,
        'pressure': 949.6
    }
    
    response = requests.post(
        f'{PHI2_URL}/api/predictions',
        json=test_payload,
        timeout=5
    )
    
    if response.status_code == 200:
        print(f"  ✅ Predictions endpoint working!")
        print(f"  Response: {response.json()}")
    else:
        print(f"  ⚠️  Status: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

# Test 3: Chat endpoint
print("\n[3/3] Testing chat endpoint...")
try:
    chat_payload = {
        'message': 'What is the current air quality?'
    }
    
    response = requests.post(
        f'{PHI2_URL}/api/chat',
        json=chat_payload,
        timeout=10
    )
    
    if response.status_code == 200:
        print(f"  ✅ Chat endpoint working!")
        result = response.json()
        print(f"  AI Response: {result.get('response', 'No response')[:100]}...")
    else:
        print(f"  ⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Failed: {e}")

print("\n" + "="*80)
print("Test Complete!")
print("="*80)
