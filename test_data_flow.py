"""
Test the complete data flow from MQTT to AI chat

This script tests:
1. MQTT data collection
2. Prediction generation
3. Backend data storage
4. AI chat context

Usage:
    python test_data_flow.py
"""

import sys
import requests
import json
import os
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
BACKEND_URL = 'http://localhost:5000'

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_backend_health():
    """Test if backend server is running"""
    print_section("1. Testing Backend Health")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Backend server is running")
            print(f"  Status: {data.get('status')}")
            print(f"  LM Studio URL: {data.get('lm_studio_url')}")
            return True
        else:
            print(f"✗ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to backend server")
        print("  Please start the backend: python backend/server.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_mqtt_data():
    """Check if MQTT data exists"""
    print_section("2. Checking MQTT Data")
    
    if os.path.exists('mqtt_data.json'):
        with open('mqtt_data.json', 'r') as f:
            data = json.load(f)
        
        print(f"✓ MQTT data file found")
        print(f"  Records: {len(data)}")
        
        if data:
            latest = data[-1]
            print(f"\n  Latest sensor reading:")
            for key, value in latest.items():
                if isinstance(value, (int, float)):
                    print(f"    {key}: {value}")
        
        return True
    else:
        print("✗ mqtt_data.json not found")
        print("  Please run: python mqtt_to_phi2.py")
        return False

def test_predictions():
    """Test if predictions are available"""
    print_section("3. Checking Predictions")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/predictions/latest", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                pred_data = data.get('data', {})
                print("✓ Predictions available")
                print(f"  Timestamp: {data.get('timestamp')}")
                print(f"  AQI: {pred_data.get('aqi', 'N/A')}")
                
                if 'predictions' in pred_data:
                    print("\n  Predicted values:")
                    for target, values in pred_data['predictions'].items():
                        if isinstance(values, dict):
                            predicted = values.get('predicted', 'N/A')
                            unit = values.get('unit', '')
                            print(f"    {target}: {predicted}{unit}")
                
                if 'sensor_data' in pred_data:
                    print("\n  Current sensor data:")
                    sensor_data = pred_data['sensor_data']
                    for key, value in sensor_data.items():
                        if isinstance(value, (int, float)):
                            print(f"    {key}: {value}")
                
                return True
            else:
                print("⚠ No prediction data available yet")
                print("  Please wait for MQTT data to be received and processed")
                return False
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_ai_chat():
    """Test AI chat with pollutant level query"""
    print_section("4. Testing AI Chat")
    
    try:
        # Test connection to LM Studio
        response = requests.get(f"{BACKEND_URL}/api/test-llm", timeout=5)
        
        if response.status_code == 200:
            print("✓ LM Studio is connected")
        else:
            print("⚠ LM Studio may not be running")
            print("  Please start LM Studio and load a model")
            return False
        
        # Send a test query
        print("\n  Sending test query: 'Show the pollutant levels'")
        
        messages = [
            {"role": "user", "content": "Show the pollutant levels"}
        ]
        
        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={
                "messages": messages,
                "include_context": True
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                ai_response = data.get('response', '')
                print("\n✓ AI Response received:")
                print(f"\n{'-'*80}")
                print(ai_response)
                print(f"{'-'*80}\n")
                
                # Check if response contains actual values
                has_values = any(char.isdigit() for char in ai_response)
                if has_values:
                    print("✓ Response contains actual data values")
                else:
                    print("⚠ Response may not contain actual data values")
                
                return True
            else:
                print(f"✗ AI error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out - AI model may be slow")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  AirSense 5G - Data Flow Test")
    print("="*80)
    
    results = {
        'Backend Health': test_backend_health(),
        'MQTT Data': test_mqtt_data(),
        'Predictions': test_predictions(),
        'AI Chat': test_ai_chat()
    }
    
    # Summary
    print_section("Test Summary")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n✓ All tests passed! The system is working correctly.")
        print("\nYou can now ask the AI questions like:")
        print("  • 'Show the pollutant levels'")
        print("  • 'What is the current air quality?'")
        print("  • 'Show me the PM2.5 levels'")
        print("  • 'What are the predictions?'")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        if not results['Backend Health']:
            print("  1. Start backend: python backend/server.py")
        if not results['MQTT Data']:
            print("  2. Start MQTT pipeline: python mqtt_to_phi2.py")
        if not results['AI Chat']:
            print("  3. Start LM Studio and load a model")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
