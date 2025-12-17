from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=os.getenv('CORS_ORIGINS', '*'))

# Configuration
LM_STUDIO_BASE_URL = os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
LM_STUDIO_MODEL = os.getenv('LM_STUDIO_MODEL', 'local-model')

# In-memory storage for latest prediction data
# In production, consider using Redis or a database
latest_prediction = {
    'timestamp': None,
    'data': None
}

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'lm_studio_url': LM_STUDIO_BASE_URL
    }), 200

# Prediction data endpoints
@app.route('/api/predictions', methods=['POST'])
def receive_prediction():
    """
    Receive prediction data from the prediction model
    
    Expected JSON format:
    {
        "timestamp": "2025-12-17T14:30:00",
        "aqi": 85,
        "pm25": 35.5,
        "pm10": 50.2,
        "co2": 400,
        "no2": 20,
        "location": {"lat": 12.9716, "lon": 77.5946},
        "forecast": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Store the prediction data
        latest_prediction['timestamp'] = datetime.now().isoformat()
        latest_prediction['data'] = data
        
        logger.info(f"Received prediction data: AQI={data.get('aqi', 'N/A')}")
        
        return jsonify({
            'status': 'success',
            'message': 'Prediction data received',
            'timestamp': latest_prediction['timestamp']
        }), 200
        
    except Exception as e:
        logger.error(f"Error receiving prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predictions/latest', methods=['GET'])
def get_latest_prediction():
    """
    Get the latest prediction data for the Flutter app
    """
    try:
        if latest_prediction['data'] is None:
            return jsonify({
                'status': 'no_data',
                'message': 'No prediction data available yet'
            }), 404
        
        return jsonify({
            'status': 'success',
            'timestamp': latest_prediction['timestamp'],
            'data': latest_prediction['data']
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Chat endpoint - proxy to LM Studio
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint that forwards requests to LM Studio
    
    Expected JSON format:
    {
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ],
        "include_context": true  // Optional: include air quality context
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({'error': 'No messages provided'}), 400
        
        messages = data['messages']
        include_context = data.get('include_context', True)
        
        # Add air quality context if requested and available
        if include_context and latest_prediction['data'] is not None:
            aqi = latest_prediction['data'].get('aqi', 'N/A')
            pm25 = latest_prediction['data'].get('pm25', 'N/A')
            context_message = {
                'role': 'system',
                'content': f"You are an air quality assistant. Current AQI: {aqi}, PM2.5: {pm25} µg/m³. Keep responses brief and helpful."
            }
            messages.insert(0, context_message)
        
        # Forward request to LM Studio
        lm_studio_url = f"{LM_STUDIO_BASE_URL}/chat/completions"
        
        payload = {
            'model': LM_STUDIO_MODEL,
            'messages': messages,
            'temperature': 0.9,  # Higher temperature for faster generation
            'max_tokens': 150  # Reduced from 500 to 150 for faster responses
        }
        
        logger.info(f"Forwarding chat request to LM Studio: {lm_studio_url}")
        
        try:
            response = requests.post(
                lm_studio_url,
                json=payload,
                timeout=120  # Increased timeout to 120 seconds for slower models
            )
            
            if response.status_code == 200:
                lm_response = response.json()
                
                # Extract the assistant's message
                if 'choices' in lm_response and len(lm_response['choices']) > 0:
                    assistant_message = lm_response['choices'][0]['message']['content']
                    
                    return jsonify({
                        'status': 'success',
                        'response': assistant_message,
                        'model': LM_STUDIO_MODEL
                    }), 200
                else:
                    return jsonify({
                        'error': 'Unexpected response format from LM Studio',
                        'raw_response': lm_response
                    }), 500
            else:
                logger.error(f"LM Studio error: {response.status_code} - {response.text}")
                return jsonify({
                    'error': f'LM Studio returned status {response.status_code}',
                    'details': response.text
                }), 500
                
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to LM Studio. Is it running?")
            return jsonify({
                'error': 'Cannot connect to LM Studio',
                'message': 'Please ensure LM Studio is running and accessible at ' + LM_STUDIO_BASE_URL
            }), 503
        except requests.exceptions.Timeout:
            logger.error("LM Studio request timed out")
            return jsonify({
                'error': 'Request to LM Studio timed out',
                'message': 'The AI model took too long to respond'
            }), 504
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Test endpoint for LM Studio connection
@app.route('/api/test-llm', methods=['GET'])
def test_llm():
    """Test connection to LM Studio"""
    try:
        # Try to get available models
        models_url = f"{LM_STUDIO_BASE_URL}/models"
        response = requests.get(models_url, timeout=5)
        
        if response.status_code == 200:
            return jsonify({
                'status': 'connected',
                'message': 'Successfully connected to LM Studio',
                'models': response.json()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'LM Studio returned status {response.status_code}'
            }), 500
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'status': 'disconnected',
            'message': 'Cannot connect to LM Studio. Please ensure it is running.',
            'url': LM_STUDIO_BASE_URL
        }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    
    logger.info(f"Starting AirSense Backend Server on {host}:{port}")
    logger.info(f"LM Studio URL: {LM_STUDIO_BASE_URL}")
    
    app.run(host=host, port=port, debug=True)
