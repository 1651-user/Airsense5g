"""
Test connection to Phi-2 at http://192.168.1.147:1234
"""

import sys
import requests
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

PHI2_URL = "http://192.168.1.147:1234"

print("="*80)
print("Testing Phi-2 Connection")
print("="*80)
print(f"\nPhi-2 URL: {PHI2_URL}")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Test 1: Check if server is reachable
print("\n" + "-"*80)
print("Test 1: Server Reachability")
print("-"*80)

try:
    response = requests.get(f"{PHI2_URL}/v1/models", timeout=5)
    
    if response.status_code == 200:
        print("✅ Server is reachable!")
        
        models = response.json()
        print(f"\nAvailable models:")
        if 'data' in models:
            for model in models['data']:
                print(f"  • {model.get('id', 'Unknown')}")
        else:
            print(f"  {models}")
    else:
        print(f"⚠️  Server returned status {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to Phi-2 server!")
    print(f"\n   Please verify:")
    print(f"   1. LM Studio is running on 192.168.1.147")
    print(f"   2. Server is started in LM Studio")
    print(f"   3. Network connectivity between machines")
    print(f"   4. Firewall allows port 1234")
    exit(1)
    
except requests.exceptions.Timeout:
    print("❌ Connection timed out!")
    print(f"   Server may be slow or unreachable")
    exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 2: Send a test chat message
print("\n" + "-"*80)
print("Test 2: Chat Completion")
print("-"*80)

try:
    print("\nSending test message: 'Hello, what is air quality?'")
    
    payload = {
        "model": "phi-2",
        "messages": [
            {
                "role": "system",
                "content": "You are an air quality assistant. Current AQI: 85 (Moderate). PM2.5: 35.2 µg/m³"
            },
            {
                "role": "user",
                "content": "Hello, what is air quality?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    print("Waiting for response (this may take 10-30 seconds)...")
    
    response = requests.post(
        f"{PHI2_URL}/v1/chat/completions",
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            ai_response = result['choices'][0]['message']['content']
            print("\n✅ Chat completion successful!")
            print(f"\nAI Response:")
            print("-" * 80)
            print(ai_response)
            print("-" * 80)
        else:
            print("⚠️  Unexpected response format")
            print(f"   Response: {result}")
    else:
        print(f"❌ Chat completion failed: {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out!")
    print("   Phi-2 may be slow. Try increasing timeout or using a faster model.")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Verify backend configuration
print("\n" + "-"*80)
print("Test 3: Backend Configuration")
print("-"*80)

try:
    with open('backend/.env', 'r') as f:
        env_content = f.read()
    
    if 'http://192.168.1.147:1234' in env_content:
        print("✅ Backend .env is configured correctly")
        print(f"   LM_STUDIO_BASE_URL=http://192.168.1.147:1234/v1")
    else:
        print("⚠️  Backend .env may not be configured correctly")
        print("   Please check backend/.env file")
        
except Exception as e:
    print(f"⚠️  Could not verify backend config: {e}")

# Summary
print("\n" + "="*80)
print("Summary")
print("="*80)

print("""
✅ Phi-2 Connection Test Complete!

Next Steps:
1. If all tests passed, restart the backend server:
   python backend/server.py

2. Test the AI chat in your Flutter app:
   - Open Chat screen
   - Ask: "Show the pollutant levels"
   - Verify AI responds with actual values

3. If tests failed:
   - Ensure LM Studio is running on 192.168.1.147
   - Check network connectivity
   - Verify firewall settings
   - Try accessing http://192.168.1.147:1234 in a browser
""")

print("="*80)
