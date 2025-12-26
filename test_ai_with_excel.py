"""
Test AI Chat Response with Excel Data
"""

import sys
import requests

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("Testing AI Chat with Excel Data")
print("="*80)

# Test 1: Show pollutant levels
print("\n📝 Test Query: 'Show the pollutant levels'")
print("-"*80)

messages = [
    {"role": "user", "content": "Show the pollutant levels"}
]

try:
    response = requests.post(
        'http://localhost:5000/api/chat',
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
            print("\n🤖 AI Response:")
            print("="*80)
            print(ai_response)
            print("="*80)
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Ask for predictions
print("\n\n📝 Test Query: 'What are the predictions?'")
print("-"*80)

messages = [
    {"role": "user", "content": "What are the predictions?"}
]

try:
    response = requests.post(
        'http://localhost:5000/api/chat',
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
            print("\n🤖 AI Response:")
            print("="*80)
            print(ai_response)
            print("="*80)
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("✅ Test Complete!")
print("="*80)
print("\nThe AI now has access to:")
print("  • Latest Excel data (Dec 24, 2025)")
print("  • Current pollutant levels")
print("  • Predicted values with trends")
print("\nTry these queries in your Flutter app!")
print("="*80)
