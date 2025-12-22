"""
Quick diagnostic script to test the full chat flow
"""
import requests
import json

print("=== AirSense Chat Diagnostic ===\n")

# Test 1: Backend health
print("1. Testing backend health...")
try:
    response = requests.get("http://localhost:5000/health", timeout=5)
    print(f"   ✓ Backend is healthy: {response.json()}")
except Exception as e:
    print(f"   ✗ Backend error: {e}")
    exit(1)

# Test 2: LM Studio connection
print("\n2. Testing LM Studio connection...")
try:
    response = requests.get("http://localhost:5000/api/test-llm", timeout=10)
    result = response.json()
    if result.get('status') == 'connected':
        print(f"   ✓ LM Studio is connected")
    else:
        print(f"   ✗ LM Studio error: {result}")
        exit(1)
except Exception as e:
    print(f"   ✗ LM Studio connection error: {e}")
    exit(1)

# Test 3: Simple chat request
print("\n3. Testing chat with simple message...")
try:
    payload = {
        "messages": [
            {"role": "user", "content": "Say hi"}
        ],
        "include_context": False  # No air quality context for speed
    }
    
    print("   Sending request...")
    response = requests.post(
        "http://localhost:5000/api/chat",
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('status') == 'success':
            print(f"   ✓ Chat works! Response: {result.get('response')}")
        else:
            print(f"   ✗ Chat error: {result}")
    else:
        print(f"   ✗ HTTP {response.status_code}: {response.text}")
        
except requests.exceptions.Timeout:
    print("   ✗ Request timed out - LM Studio is too slow")
    print("   Suggestion: Try a smaller/faster model in LM Studio")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n=== Diagnostic Complete ===")
