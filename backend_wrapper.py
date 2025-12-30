"""
Backend Wrapper for Phi-2 via LM Studio
Translates prediction data into chat requests for the AI
"""
import sys
from flask import Flask, request, jsonify
import requests
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

# Configuration
PHI2_URL = 'http://192.168.0.103:1234'
PHI2_MODEL = 'phi-2'

# Store latest prediction data
latest_predictions = {}

print("="*80)
print("🚀 Phi-2 Backend Wrapper")
print("="*80)
print(f"Phi-2 Server: {PHI2_URL}")
print(f"Model: {PHI2_MODEL}")
print(f"Listening on: http://localhost:5000")
print("="*80)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        response = requests.get(f'{PHI2_URL}/health', timeout=2)
        return jsonify({
            'status': 'healthy',
            'phi2_status': response.status_code == 200,
            'timestamp': datetime.now().isoformat()
        })
    except:
        return jsonify({
            'status': 'degraded',
            'phi2_status': False,
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/api/predictions', methods=['POST'])
def receive_predictions():
    """Receive and store prediction data"""
    global latest_predictions
    
    try:
        data = request.get_json()
        latest_predictions = data
        latest_predictions['received_at'] = datetime.now().isoformat()
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📊 Received predictions:")
        print(f"  AQI: {data.get('aqi', 'N/A')}")
        print(f"  PM2.5: {data.get('pm25', 'N/A')} µg/m³")
        print(f"  Temperature: {data.get('temperature', 'N/A')} °C")
        
        return jsonify({
            'status': 'success',
            'message': 'Predictions stored',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/predictions/latest', methods=['GET'])
def get_latest_predictions():
    """Get latest prediction data"""
    if latest_predictions:
        return jsonify(latest_predictions)
    else:
        return jsonify({'error': 'No predictions available'}), 404

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with Phi-2 using latest prediction context"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # Build context from latest predictions
        context = ""
        if latest_predictions:
            context = f"""You are an air quality expert AI assistant. Here is the latest air quality data:

Current Air Quality Index (AQI): {latest_predictions.get('aqi', 'N/A')}
PM2.5: {latest_predictions.get('pm25', 'N/A')} µg/m³
PM10: {latest_predictions.get('pm10', 'N/A')} µg/m³
CO2: {latest_predictions.get('co2', 'N/A')} ppm
TVOC: {latest_predictions.get('tvoc', 'N/A')} ppb
Temperature: {latest_predictions.get('temperature', 'N/A')} °C
Humidity: {latest_predictions.get('humidity', 'N/A')} %
Pressure: {latest_predictions.get('pressure', 'N/A')} hPa

Based on this data, answer the user's question concisely and accurately.

User question: {user_message}

Answer:"""
        else:
            context = f"User question: {user_message}\n\nAnswer:"
        
        # Send to Phi-2
        phi2_request = {
            'model': PHI2_MODEL,
            'messages': [
                {'role': 'user', 'content': context}
            ],
            'temperature': 0.7,
            'max_tokens': 200,
            'stream': False
        }
        
        response = requests.post(
            f'{PHI2_URL}/v1/chat/completions',
            json=phi2_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 💬 Chat:")
            print(f"  User: {user_message[:50]}...")
            print(f"  AI: {ai_response[:100]}...")
            
            return jsonify({
                'response': ai_response,
                'timestamp': datetime.now().isoformat(),
                'has_context': bool(latest_predictions)
            })
        else:
            return jsonify({'error': 'Phi-2 request failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-llm', methods=['GET'])
def test_llm():
    """Test LLM connection"""
    try:
        test_request = {
            'model': PHI2_MODEL,
            'messages': [
                {'role': 'user', 'content': 'Say "Hello, I am Phi-2 and I am working!"'}
            ],
            'max_tokens': 50
        }
        
        response = requests.post(
            f'{PHI2_URL}/v1/chat/completions',
            json=test_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'status': 'success',
                'response': result['choices'][0]['message']['content'],
                'model': PHI2_MODEL
            })
        else:
            return jsonify({'error': 'LLM test failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n✅ Backend wrapper ready!")
    print("📡 Waiting for predictions from MQTT pipeline...\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
