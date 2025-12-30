import requests
import json

# Test LM Studio chat endpoint
url = "http://192.168.0.103:1234/v1/chat/completions"

payload = {
    "model": "llama-2-7b-chat",
    "messages": [
        {"role": "user", "content": "Say hello in one word"}
    ],
    "temperature": 0.7,
    "max_tokens": 10
}

print("Testing LM Studio chat endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=payload, timeout=60)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.Timeout:
    print("\nERROR: Request timed out!")
    print("This means LM Studio is taking too long to respond.")
    print("\nPossible solutions:")
    print("1. Make sure the local server is actually started in LM Studio")
    print("2. Try a smaller/faster model")
    print("3. Check LM Studio console for errors")
except Exception as e:
    print(f"\nERROR: {e}")
