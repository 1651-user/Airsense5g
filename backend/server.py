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

# Storage for all sensor data (multi-sensor support)
all_sensors_data = {
    'timestamp': None,
    'sensors': {}
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
    
    Expected JSON format (single sensor):
    {
        "timestamp": "2025-12-17T14:30:00",
        "aqi": 85,
        "pm25": 35.5,
        ...
    }
    
    OR multi-sensor format:
    {
        "timestamp": "2025-12-28T12:00:00",
        "total_sensors": 5,
        "sensors": {
            "sensor_1": {...},
            "sensor_2": {...},
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if this is multi-sensor data
        if 'sensors' in data and 'total_sensors' in data:
            # Store multi-sensor data
            all_sensors_data['timestamp'] = datetime.now().isoformat()
            all_sensors_data['sensors'] = data['sensors']
            all_sensors_data['total_sensors'] = data['total_sensors']
            
            logger.info(f"Received data from {data['total_sensors']} sensors")
            
            return jsonify({
                'status': 'success',
                'message': f'Data from {data["total_sensors"]} sensors received',
                'timestamp': all_sensors_data['timestamp']
            }), 200
        else:
            # Store single sensor prediction data
            latest_prediction['timestamp'] = datetime.now().isoformat()
            latest_prediction['data'] = data
            
            # Map into all_sensors_data for multi-sensor display
            sensor_id = data.get('sensor_id')
            if sensor_id:
                sensor_key = f"sensor_{sensor_id}" if not str(sensor_id).startswith('sensor_') else str(sensor_id)
                
                # Create structure compatible with /api/sensors/all
                sensor_info = {
                    'name': data.get('sensor_name', f'Sensor {sensor_id}'),
                    'aqi': data.get('aqi', 0),
                    'pollutants': {
                        'pm2_5': data.get('sensor_data', {}).get('pm2_5', data.get('pm25', 0)),
                        'pm10': data.get('sensor_data', {}).get('pm10', data.get('pm10', 0)),
                        'co2': data.get('sensor_data', {}).get('co2', data.get('co2', 0)),
                        'tvoc': data.get('sensor_data', {}).get('tvoc', data.get('tvoc', 0)),
                    },
                    'environmental': {
                        'temperature': data.get('sensor_data', {}).get('temperature', data.get('temperature', 0)),
                        'humidity': data.get('sensor_data', {}).get('humidity', data.get('humidity', 0)),
                        'pressure': data.get('sensor_data', {}).get('pressure', data.get('pressure', 0)),
                    },
                    'predictions': data.get('predictions', {})
                }
                
                if 'sensors' not in all_sensors_data or not isinstance(all_sensors_data['sensors'], dict):
                    all_sensors_data['sensors'] = {}
                
                all_sensors_data['sensors'][sensor_key] = sensor_info
                all_sensors_data['timestamp'] = datetime.now().isoformat()
                all_sensors_data['total_sensors'] = len(all_sensors_data['sensors'])
            
            # Enhanced logging with ALL sensor data
            sensor_id = data.get('sensor_id', 'Unknown')
            sensor_name = data.get('sensor_name', 'N/A')
            timestamp = data.get('timestamp', 'N/A')
            
            # Get all pollutant values
            aqi = data.get('aqi', 0)
            pm25 = data.get('pm25', 0)
            pm10 = data.get('pm10', 0)
            co2 = data.get('co2', 0)
            tvoc = data.get('tvoc', 0)
            temp = data.get('temperature', 0)
            hum = data.get('humidity', 0)
            pres = data.get('pressure', 0)
            
            # Comprehensive log with all pollutants
            logger.info(f"📊 Sensor {sensor_id} ({sensor_name})")
            logger.info(f"   AQI: {aqi} (from PM2.5={pm25})")
            logger.info(f"   Pollutants: PM2.5={pm25}, PM10={pm10}, CO2={co2}, TVOC={tvoc}")
            logger.info(f"   Environment: Temp={temp}°C, Humidity={hum}%, Pressure={pres}hPa")
            logger.info(f"   Time: {timestamp}")
            
            return jsonify({
                'status': 'success',
                'message': 'Prediction data received',
                'timestamp': latest_prediction['timestamp']
            }), 200
        
    except Exception as e:
        logger.error(f"Error receiving prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
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

@app.route('/api/sensors/all', methods=['GET'])
def get_all_sensors():
    """
    Get the latest data from ALL 5 sensors for the dashboard
    Returns real sensor data, NO dummy data
    """
    try:
        # Return multi-sensor data if available
        if all_sensors_data.get('sensors'):
            return jsonify({
                'status': 'success',
                'timestamp': all_sensors_data.get('timestamp'),
                'total_sensors': all_sensors_data.get('total_sensors', 0),
                'sensors': all_sensors_data['sensors']
            }), 200
        
        # Fallback: if no multi-sensor data, return single sensor if available
        elif latest_prediction['data'] is not None:
            return jsonify({
                'status': 'success',
                'timestamp': latest_prediction['timestamp'],
                'total_sensors': 1,
                'sensors': {
                    'sensor_3': {
                        'name': latest_prediction['data'].get('sensor_name', 'Sensor 3'),
                        'aqi': latest_prediction['data'].get('aqi', 0),
                        'pollutants': {
                            'pm2_5': latest_prediction['data'].get('pm25', 0),
                            'pm10': latest_prediction['data'].get('pm10', 0),
                            'co2': latest_prediction['data'].get('co2', 0),
                            'tvoc': latest_prediction['data'].get('tvoc', 0),
                        },
                        'environmental': {
                            'temperature': latest_prediction['data'].get('temperature', 0),
                            'humidity': latest_prediction['data'].get('humidity', 0),
                            'pressure': latest_prediction['data'].get('pressure', 0),
                        }
                    }
                }
            }), 200
        else:
            return jsonify({
                'status': 'no_data',
                'message': 'No sensor data available yet. Please wait for sensors to send data.',
                'timestamp': None,
                'total_sensors': 0,
                'sensors': {}
            }), 404
            
    except Exception as e:
        logger.error(f"Error fetching all sensors: {str(e)}")
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
        include_context = data.get('include_context', True)  # Enabled by default for air quality context
        
        # Add air quality context if requested and available
        # Priority: Multi-sensor data > Single sensor data
        context_parts = []
        
        if include_context:
            # Check for multi-sensor data first
            if all_sensors_data.get('sensors'):
                # Build comprehensive context for all sensors
                sensor_contexts = []
                for sensor_key, sensor_info in all_sensors_data['sensors'].items():
                    sensor_num = sensor_key.split('_')[1]  # Extract number from 'sensor_1'
                    pollutants = sensor_info.get('pollutants', {})
                    environmental = sensor_info.get('environmental', {})
                    predictions = sensor_info.get('predictions', {})
                    
                    # Build sensor context with current values
                    sensor_parts = [f"Sensor {sensor_num}: AQI={sensor_info.get('aqi', 0)}"]
                    
                    # Pollutants
                    if pollutants.get('pm2_5'): sensor_parts.append(f"PM2.5={pollutants['pm2_5']}")
                    if pollutants.get('pm10'): sensor_parts.append(f"PM10={pollutants['pm10']}")
                    if pollutants.get('co2'): sensor_parts.append(f"CO2={pollutants['co2']}")
                    if pollutants.get('tvoc'): sensor_parts.append(f"TVOC={pollutants['tvoc']}")
                    
                    # Environmental
                    if environmental.get('temperature'): sensor_parts.append(f"Temp={environmental['temperature']}°C")
                    if environmental.get('humidity'): sensor_parts.append(f"Humidity={environmental['humidity']}%")
                    if environmental.get('pressure'): sensor_parts.append(f"Pressure={environmental['pressure']}mb")
                    
                    # Predictions (if available) - CRITICAL for AI to answer "what are predictions"
                    if predictions:
                        pred_parts = []
                        if predictions.get('PM2.5'): pred_parts.append(f"PM2.5→{predictions['PM2.5'].get('predicted')}")
                        if predictions.get('PM10'): pred_parts.append(f"PM10→{predictions['PM10'].get('predicted')}")
                        if predictions.get('CO2'): pred_parts.append(f"CO2→{predictions['CO2'].get('predicted')}")
                        if predictions.get('TVOC'): pred_parts.append(f"TVOC→{predictions['TVOC'].get('predicted')}")
                        if predictions.get('Temperature'): pred_parts.append(f"Temp→{predictions['Temperature'].get('predicted')}")
                        if pred_parts:
                            sensor_parts.append(f"PREDICTIONS:[{','.join(pred_parts)}]")
                    
                    sensor_contexts.append(", ".join(sensor_parts))
                
                context_parts.append(" | ".join(sensor_contexts))
                
            # Fallback to single sensor data
            elif latest_prediction['data'] is not None:
                pred_data = latest_prediction['data']
                
                # Ultra-compact context with ALL data
                parts = []
                
                # AQI
                if 'aqi' in pred_data:
                    parts.append(f"AQI={pred_data['aqi']}")
                
                # All current readings (compact)
                if 'sensor_data' in pred_data and pred_data['sensor_data']:
                    sd = pred_data['sensor_data']
                    curr = []
                    if 'pm2_5' in sd: curr.append(f"PM2.5={sd['pm2_5']}")
                    if 'pm10' in sd: curr.append(f"PM10={sd['pm10']}")
                    if 'co2' in sd: curr.append(f"CO2={sd['co2']}")
                    if 'tvoc' in sd: curr.append(f"TVOC={sd['tvoc']}")
                    if 'temperature' in sd: curr.append(f"T={sd['temperature']}")
                    if 'humidity' in sd: curr.append(f"H={sd['humidity']}")
                    if curr:
                        parts.append(",".join(curr))
                
                # Add Predictions for single sensor fallback
                if 'predictions' in pred_data and pred_data['predictions']:
                    preds = pred_data['predictions']
                    p_list = []
                    if 'PM2.5' in preds: p_list.append(f"PM2.5→{preds['PM2.5'].get('predicted')}")
                    if 'CO2' in preds: p_list.append(f"CO2→{preds['CO2'].get('predicted')}")
                    if p_list:
                        parts.append(f"PREDICTIONS:[{','.join(p_list)}]")
                
                context_parts.extend(parts)
        
        # Add context to messages if we have any
        if context_parts:
            # Construct a clear, descriptive system instruction
            context_string = "\n".join(context_parts)
            system_instruction = (
                "You are AirSense AI, an advanced air quality assistant. "
                "You have real-time access to high-precision sensors. "
                "Current air quality data:\n" + context_string + "\n\n"
                "When answering, refer to specific sensor data to give advice. "
                "Analyze trends (Predictions) if available. Keep responses informative but direct."
            )
            
            # Insert at the beginning as the primary instruction
            messages.insert(0, {
                'role': 'system', 
                'content': system_instruction
            })

        
        # Forward request to LM Studio
        lm_studio_url = f"{LM_STUDIO_BASE_URL}/chat/completions"
        
        payload = {
            'model': LM_STUDIO_MODEL,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 1200,  # Increased to prevent truncation
            'stop': ["\n\n\n", "User:"] # Prevention for loops
        }
        
        logger.info(f"Forwarding chat request to LM Studio: {lm_studio_url}")
        
        try:
            response = requests.post(
                lm_studio_url,
                json=payload,
                timeout=180  # Increased to 3 minutes for slow models
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

# Forecast endpoints
@app.route('/api/forecast/<sensor_id>', methods=['GET'])
def get_forecast(sensor_id):
    """
    Get forecast data for a specific sensor
    
    Query parameters:
    - hours: Number of hours to forecast (default: 24)
    - days: Number of days to forecast (default: 7)
    """
    try:
        hours = int(request.args.get('hours', 24))
        days = int(request.args.get('days', 7))
        
        # Get current sensor data
        sensor_key = f"sensor_{sensor_id}" if not sensor_id.startswith('sensor_') else sensor_id
        
        sensor_data = None
        if all_sensors_data.get('sensors') and sensor_key in all_sensors_data['sensors']:
            sensor_data = all_sensors_data['sensors'][sensor_key]
        elif latest_prediction['data'] is not None and sensor_key == 'sensor_3':
            # Fallback to single sensor data
            sensor_data = {
                'aqi': latest_prediction['data'].get('aqi', 50),
                'pollutants': {
                    'pm2_5': latest_prediction['data'].get('pm25', 25),
                    'pm10': latest_prediction['data'].get('pm10', 40),
                }
            }
        
        if not sensor_data:
            return jsonify({
                'status': 'no_data',
                'message': f'No data available for {sensor_key}'
            }), 404
        
        # Generate hourly forecast
        hourly_forecast = []
        base_pm25 = sensor_data['pollutants'].get('pm2_5', 25)
        base_pm10 = sensor_data['pollutants'].get('pm10', 40)
        base_aqi = sensor_data.get('aqi', 50)
        
        from datetime import datetime, timedelta
        now = datetime.now()
        
        for i in range(hours):
            timestamp = now + timedelta(hours=i)
            hour = timestamp.hour
            
            # Time-based variation (higher during rush hours)
            variation = 1.0
            if 6 <= hour < 9:  # Morning rush
                variation = 1.3
            elif 17 <= hour < 20:  # Evening rush
                variation = 1.4
            elif 22 <= hour or hour < 6:  # Night
                variation = 0.8
            
            # Add some randomness
            import random
            random_factor = 0.85 + random.random() * 0.3
            
            pm25 = round(base_pm25 * variation * random_factor, 1)
            pm10 = round(base_pm10 * variation * random_factor, 1)
            
            # Calculate AQI
            aqi = _calculate_aqi_from_pm(pm25, pm10)
            
            hourly_forecast.append({
                'timestamp': timestamp.isoformat(),
                'hour': hour,
                'aqi': aqi,
                'pm25': pm25,
                'pm10': pm10,
                'category': _get_aqi_category(aqi)
            })
        
        # Generate daily forecast
        daily_forecast = []
        for i in range(days):
            timestamp = now + timedelta(days=i)
            day_of_week = timestamp.weekday()
            
            # Weekday vs weekend variation
            variation = 0.85 if day_of_week >= 5 else 1.1
            random_factor = 0.8 + random.random() * 0.4
            
            pm25 = round(base_pm25 * variation * random_factor, 1)
            pm10 = round(base_pm10 * variation * random_factor, 1)
            aqi = _calculate_aqi_from_pm(pm25, pm10)
            
            daily_forecast.append({
                'date': timestamp.strftime('%Y-%m-%d'),
                'day_of_week': timestamp.strftime('%A'),
                'aqi': aqi,
                'pm25': pm25,
                'pm10': pm10,
                'category': _get_aqi_category(aqi)
            })
        
        return jsonify({
            'status': 'success',
            'sensor_id': sensor_key,
            'timestamp': now.isoformat(),
            'hourly': hourly_forecast,
            'daily': daily_forecast
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _calculate_aqi_from_pm(pm25, pm10):
    """Calculate AQI from PM2.5 and PM10"""
    aqi_pm25 = _pm25_to_aqi(pm25)
    aqi_pm10 = _pm10_to_aqi(pm10)
    return max(aqi_pm25, aqi_pm10)

def _pm25_to_aqi(pm25):
    """Convert PM2.5 to AQI"""
    if pm25 <= 12.0:
        return int((pm25 / 12.0) * 50)
    elif pm25 <= 35.4:
        return int(50 + ((pm25 - 12.0) / (35.4 - 12.0)) * 50)
    elif pm25 <= 55.4:
        return int(100 + ((pm25 - 35.4) / (55.4 - 35.4)) * 50)
    elif pm25 <= 150.4:
        return int(150 + ((pm25 - 55.4) / (150.4 - 55.4)) * 50)
    else:
        return 200

def _pm10_to_aqi(pm10):
    """Convert PM10 to AQI"""
    if pm10 <= 54:
        return int((pm10 / 54) * 50)
    elif pm10 <= 154:
        return int(50 + ((pm10 - 54) / (154 - 54)) * 50)
    elif pm10 <= 254:
        return int(100 + ((pm10 - 154) / (254 - 154)) * 50)
    elif pm10 <= 354:
        return int(150 + ((pm10 - 254) / (354 - 254)) * 50)
    else:
        return 200

def _get_aqi_category(aqi):
    """Get AQI category name"""
    if aqi <= 50:
        return 'Good'
    elif aqi <= 100:
        return 'Moderate'
    elif aqi <= 150:
        return 'Unhealthy for Sensitive Groups'
    elif aqi <= 200:
        return 'Unhealthy'
    elif aqi <= 300:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

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
