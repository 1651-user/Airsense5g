# AirSense Backend Server

This backend server coordinates between your prediction model, LM Studio (LLaMA), and the Flutter app.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Edit `.env` file to match your setup:

```env
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=local-model
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
```

### 3. Start LM Studio

1. Open LM Studio
2. Load your LLaMA model
3. Start the local server (usually on port 1234)
4. Verify it's running: `http://localhost:1234/v1/models`

### 4. Start Backend Server

```bash
python server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns server status

### Prediction Data
- **POST** `/api/predictions` - Receive prediction data from your model
- **GET** `/api/predictions/latest` - Get latest prediction data

### Chat
- **POST** `/api/chat` - Send chat messages (proxies to LLaMA)
- **GET** `/api/test-llm` - Test LM Studio connection

## Sending Prediction Data

Use the example script:

```bash
python send_prediction.py
```

Or integrate with your prediction model:

```python
import requests

data = {
    "timestamp": "2025-12-17T14:30:00",
    "aqi": 85,
    "pm25": 35.5,
    "pm10": 50.2,
    "co2": 400,
    "no2": 20
}

requests.post("http://localhost:5000/api/predictions", json=data)
```

## Testing

### Test Backend Server
```bash
curl http://localhost:5000/health
```

### Test LM Studio Connection
```bash
curl http://localhost:5000/api/test-llm
```

### Test Chat
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## Troubleshooting

### Cannot connect to LM Studio
- Ensure LM Studio is running
- Check the port in `.env` matches LM Studio's port
- Verify model is loaded in LM Studio

### Flutter app cannot connect
- For Android emulator: Use `http://10.0.2.2:5000`
- For iOS simulator: Use `http://localhost:5000`
- For physical device: Use your computer's IP (e.g., `http://192.168.1.100:5000`)
- Ensure firewall allows connections on port 5000
