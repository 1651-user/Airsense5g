"""
Phi-2 Server Endpoint Discovery
Finds the correct API paths for your Phi-2 server at 192.168.1.147:1234
"""
import sys
import requests
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

PHI2_URL = 'http://192.168.1.147:1234'

print("="*80)
print("🔍 PHI-2 SERVER ENDPOINT DISCOVERY")
print("="*80)
print(f"\nServer: {PHI2_URL}\n")

# Common endpoint patterns to test
endpoints_to_test = {
    'Health Checks': [
        '/health',
        '/api/health',
        '/v1/health',
        '/status',
        '/ping',
        '/',
    ],
    'Chat/Completions': [
        '/api/chat',
        '/v1/chat/completions',
        '/chat/completions',
        '/completions',
        '/v1/completions',
        '/chat',
        '/api/completions',
    ],
    'Predictions': [
        '/api/predictions',
        '/predictions',
        '/v1/predictions',
        '/predict',
        '/api/predict',
    ],
    'Models': [
        '/v1/models',
        '/models',
        '/api/models',
    ]
}

test_payload = {
    'messages': [{'role': 'user', 'content': 'Hello'}],
    'message': 'Hello',
    'prompt': 'Hello',
    'model': 'phi-2'
}

working_endpoints = {}

for category, paths in endpoints_to_test.items():
    print(f"\n{'='*80}")
    print(f"Testing {category}")
    print(f"{'='*80}")
    
    for path in paths:
        url = f"{PHI2_URL}{path}"
        
        # Try GET
        try:
            response = requests.get(url, timeout=3)
            if response.status_code not in [404, 405]:
                status = "✅" if response.status_code == 200 else "⚠️"
                print(f"{status} GET  {path:30} → {response.status_code}")
                if response.status_code == 200:
                    try:
                        print(f"     Response: {json.dumps(response.json(), indent=2)[:200]}")
                    except:
                        print(f"     Response: {response.text[:200]}")
                    working_endpoints[f"GET {path}"] = response.status_code
        except requests.exceptions.Timeout:
            print(f"⏱️  GET  {path:30} → Timeout")
        except Exception as e:
            pass
        
        # Try POST with different payloads
        for payload_type, payload in [
            ('chat', {'messages': [{'role': 'user', 'content': 'test'}]}),
            ('simple', {'message': 'test'}),
            ('predictions', {'aqi': 100, 'pm25': 50}),
        ]:
            try:
                response = requests.post(url, json=payload, timeout=3)
                if response.status_code not in [404, 405]:
                    status = "✅" if response.status_code == 200 else "⚠️"
                    print(f"{status} POST {path:30} [{payload_type}] → {response.status_code}")
                    if response.status_code == 200:
                        try:
                            resp_json = response.json()
                            print(f"     Response: {json.dumps(resp_json, indent=2)[:200]}")
                            working_endpoints[f"POST {path} [{payload_type}]"] = response.status_code
                        except:
                            print(f"     Response: {response.text[:200]}")
            except requests.exceptions.Timeout:
                continue
            except Exception as e:
                continue

print("\n" + "="*80)
print("📊 SUMMARY OF WORKING ENDPOINTS")
print("="*80)

if working_endpoints:
    for endpoint, status in working_endpoints.items():
        print(f"✅ {endpoint} → Status {status}")
else:
    print("⚠️  No standard endpoints found with 200 responses")
    print("\nThe server is running but may use custom endpoints.")
    print("Let me try to discover more information...")

# Additional discovery - try to get server info
print("\n" + "="*80)
print("🔍 ADDITIONAL DISCOVERY")
print("="*80)

# Try common LLM server paths
llm_paths = [
    '/v1/models',
    '/api/v1/models',
    '/models',
    '/',
    '/docs',
    '/api/docs',
    '/swagger',
    '/openapi.json',
]

for path in llm_paths:
    try:
        response = requests.get(f"{PHI2_URL}{path}", timeout=2)
        if response.status_code == 200:
            print(f"\n✅ Found: {path}")
            try:
                data = response.json()
                print(json.dumps(data, indent=2)[:500])
            except:
                print(response.text[:500])
    except:
        pass

print("\n" + "="*80)
print("💡 RECOMMENDATIONS")
print("="*80)

print("\nBased on the 'Unexpected endpoint' error, your server might be:")
print("1. LM Studio (uses /v1/chat/completions)")
print("2. Ollama (uses /api/chat or /api/generate)")
print("3. Text Generation WebUI (uses /api/v1/generate)")
print("4. Custom Phi-2 server with specific endpoints")

print("\n📝 Next Steps:")
print("1. Check what software is running your Phi-2 server")
print("2. Look at the server's documentation or startup logs")
print("3. We'll update the scripts with the correct endpoints")

print("\n" + "="*80)
