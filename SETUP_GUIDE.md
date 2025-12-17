# LLaMA Integration Setup Guide

This guide will help you set up the complete integration between your prediction model, LM Studio (LLaMA), and the Flutter app.

## Prerequisites

- Python 3.8+ installed
- LM Studio installed and configured
- Flutter SDK installed
- Your air quality prediction model

## Step 1: Start LM Studio

1. **Open LM Studio**
2. **Download a model** (if you haven't already):
   - Recommended: `llama-2-7b-chat` or `mistral-7b-instruct`
   - Go to the "Discover" tab
   - Search for and download your preferred model

3. **Load the model**:
   - Go to the "Chat" tab
   - Select your downloaded model from the dropdown

4. **Start the local server**:
   - Click on the "Local Server" tab
   - Click "Start Server"
   - Note the port (usually 1234)
   - Verify it's running: Open browser to `http://localhost:1234/v1/models`

## Step 2: Configure Backend Server

1. **Navigate to backend directory**:
   ```bash
   cd c:\Users\Administrator\Airsense5g\backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Edit `.env` file** (if needed):
   ```env
   LM_STUDIO_BASE_URL=http://localhost:1234/v1
   LM_STUDIO_MODEL=local-model
   FLASK_PORT=5000
   FLASK_HOST=0.0.0.0
   ```

4. **Start the backend server**:
   ```bash
   python server.py
   ```

   You should see:
   ```
   Starting AirSense Backend Server on 0.0.0.0:5000
   LM Studio URL: http://localhost:1234/v1
   ```

5. **Test the backend** (in a new terminal):
   ```bash
   # Test health endpoint
   curl http://localhost:5000/health

   # Test LM Studio connection
   curl http://localhost:5000/api/test-llm
   ```

## Step 3: Send Prediction Data

### Option A: Use Example Script

```bash
cd c:\Users\Administrator\Airsense5g\backend
python send_prediction.py
```

### Option B: Integrate with Your Prediction Model

Add this code to your prediction model script:

```python
import requests
from datetime import datetime

def send_to_backend(aqi, pm25, pm10, co2, no2):
    data = {
        "timestamp": datetime.now().isoformat(),
        "aqi": aqi,
        "pm25": pm25,
        "pm10": pm10,
        "co2": co2,
        "no2": no2,
        "location": {
            "lat": YOUR_LATITUDE,
            "lon": YOUR_LONGITUDE,
            "name": "Your Location"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/predictions",
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            print(f"✓ Sent prediction data (AQI: {aqi})")
    except Exception as e:
        print(f"✗ Error sending data: {e}")

# Call this after your model makes a prediction
# send_to_backend(predicted_aqi, predicted_pm25, ...)
```

## Step 4: Configure Flutter App

### For Android Emulator

The app is already configured to use `http://10.0.2.2:5000` which maps to your computer's localhost.

### For iOS Simulator

No changes needed - uses `http://localhost:5000`

### For Physical Device

1. **Find your computer's IP address**:
   - Windows: `ipconfig` (look for IPv4 Address)
   - Example: `192.168.1.100`

2. **Update Flutter services**:
   
   Edit `lib/services/bytez_service.dart`:
   ```dart
   final String _baseUrl = 'http://YOUR_COMPUTER_IP:5000/api';
   ```
   
   Edit `lib/services/prediction_service.dart`:
   ```dart
   final String _baseUrl = 'http://YOUR_COMPUTER_IP:5000/api';
   ```

3. **Allow firewall access**:
   - Windows: Allow Python through Windows Firewall
   - Ensure port 5000 is accessible

## Step 5: Run the Flutter App

```bash
cd c:\Users\Administrator\Airsense5g
flutter run
```

## Testing the Integration

### Test 1: Backend Health
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-17T14:30:00",
  "lm_studio_url": "http://localhost:1234/v1"
}
```

### Test 2: LM Studio Connection
```bash
curl http://localhost:5000/api/test-llm
```

Expected response:
```json
{
  "status": "connected",
  "message": "Successfully connected to LM Studio",
  "models": {...}
}
```

### Test 3: Send Prediction Data
```bash
curl -X POST http://localhost:5000/api/predictions \
  -H "Content-Type: application/json" \
  -d '{"aqi": 85, "pm25": 35.5, "pm10": 50.2, "co2": 400, "no2": 20}'
```

### Test 4: Get Latest Prediction
```bash
curl http://localhost:5000/api/predictions/latest
```

### Test 5: Chat with LLaMA
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is the current air quality?"}]}'
```

### Test 6: Flutter App
1. Open the app
2. Navigate to Chat screen
3. Ask: "What is the current air quality?"
4. LLaMA should respond with information from the latest prediction data

## Troubleshooting

### "Cannot connect to LM Studio"

**Solutions:**
- Ensure LM Studio is running
- Check that the local server is started in LM Studio
- Verify the port in `.env` matches LM Studio's port
- Test: `curl http://localhost:1234/v1/models`

### "Cannot connect to backend server" (from Flutter)

**Solutions:**
- Ensure backend server is running: `python backend/server.py`
- For emulator: Use `http://10.0.2.2:5000`
- For physical device: Use your computer's IP address
- Check firewall settings

### "No prediction data available"

**Solutions:**
- Send test data: `python backend/send_prediction.py`
- Verify data was received: `curl http://localhost:5000/api/predictions/latest`
- Check backend server logs

### LLaMA responses are slow

**Solutions:**
- This is normal for local LLaMA models
- Consider using a smaller model (7B instead of 13B)
- Increase timeout in `bytez_service.dart` if needed
- Ensure your computer has sufficient RAM

### Chat shows old Poe API errors

**Solutions:**
- Ensure you've updated `bytez_service.dart`
- Run `flutter clean` and `flutter pub get`
- Restart the app

## Architecture Overview

```
┌─────────────────────┐
│  Prediction Model   │
│  (Your Python code) │
└──────────┬──────────┘
           │ POST /api/predictions
           ▼
┌─────────────────────┐     ┌──────────────────┐
│  Backend Server     │────▶│   LM Studio      │
│  (Flask - Port 5000)│     │   (Port 1234)    │
└──────────┬──────────┘     └──────────────────┘
           │
           │ HTTP API
           ▼
┌─────────────────────┐
│   Flutter App       │
│   (AirSense 5G)     │
└─────────────────────┘
```

## Next Steps

1. ✅ Verify all components are running
2. ✅ Test with sample prediction data
3. ✅ Test chat functionality
4. 🔄 Integrate with your actual prediction model
5. 🔄 Customize LLaMA prompts if needed
6. 🔄 Update dashboard to show prediction data

## Support

If you encounter issues:
1. Check all services are running (LM Studio, Backend, Flutter)
2. Review backend server logs
3. Check Flutter debug console
4. Verify network connectivity
