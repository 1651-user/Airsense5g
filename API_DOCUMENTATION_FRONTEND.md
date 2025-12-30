# 🌐 AirSense API Documentation - Real Data Only

## Base URL
```
http://192.168.1.147:5000
```

---

## 📊 Endpoints for Dashboard

### 1. Get All Sensors Data (RECOMMENDED for Dashboard)
**NEW ENDPOINT - Returns REAL data from all 5 sensors**

```http
GET /api/sensors/all
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "2025-12-30T12:40:00",
  "total_sensors": 5,
  "sensors": {
    "sensor_1": {
      "name": "Sensor 1",
      "aqi": 156,
      "pollutants": {
        "pm2_5": 65.3,
        "pm10": 85.7,
        "co2": 396.0,
        "tvoc": 101.0
      },
      "environmental": {
        "temperature": 25.3,
        "humidity": 48.5,
        "pressure": 947.8
      },
      "predictions": {
        "pm2_5": 66.1,
        "pm10": 86.2,
        "co2": 395.0,
        "tvoc": 100.5,
        "temperature": 25.4,
        "humidity": 48.0,
        "pressure": 948.0
      }
    },
    "sensor_2": { /* same structure */ },
    "sensor_3": { /* same structure */ },
    "sensor_4": { /* same structure */ },
    "sensor_5": { /* same structure */ }
  }
}
```

**Usage in Flutter/Dashboard:**
```dart
// Fetch all sensors
final response = await http.get(Uri.parse('http://192.168.1.147:5000/api/sensors/all'));
final data = jsonDecode(response.body);

if (data['status'] == 'success') {
  int totalSensors = data['total_sensors'];
  var sensors = data['sensors'];
  
  // Display each sensor
  sensors.forEach((sensorKey, sensorData) {
    print('${sensorData['name']}: AQI=${sensorData['aqi']}');
    print('PM2.5: ${sensorData['pollutants']['pm2_5']}');
    print('Temperature: ${sensorData['environmental']['temperature']}°C');
  });
}
```

---

### 2. Get Latest Single Sensor Data
```http
GET /api/predictions/latest
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "2025-12-30T12:40:00",
  "data": {
    "sensor_id": 3,
    "sensor_name": "Sensor 3",
    "aqi": 156,
    "pm25": 65.3,
    "pm10": 85.7,
    "co2": 396.0,
    "tvoc": 101.0,
    "temperature": 25.3,
    "humidity": 48.5,
    "pressure": 947.8,
    "timestamp": "2025-12-30T12:40:00"
  }
}
```

---

## 💬 Chat with AI (with Real Sensor Context)

### Chat with Automatic Sensor Context
```http
POST /api/chat
Content-Type: application/json
```

**Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is the current PM2.5 level?"
    }
  ],
  "include_context": true
}
```

**Response:**
```json
{
  "status": "success",
  "response": "The current PM2.5 levels across all sensors are: Sensor 1: 65.3 µg/m³, Sensor 2: 45.2 µg/m³, Sensor 3: 50.1 µg/m³, Sensor 4: 88.0 µg/m³, Sensor 5: 33.5 µg/m³. The average is 56.4 µg/m³, which is Moderate air quality.",
  "model": "phi-2"
}
```

**How it works:**
- If `include_context: true` (default), the AI automatically gets ALL sensor data
- The AI knows: AQI, PM2.5, PM10, CO2, TVOC, Temperature, Humidity, Pressure for ALL 5 sensors
- The AI can answer questions about specific sensors or compare them

**Example questions:**
```json
{
  "messages": [
    {"role": "user", "content": "Which sensor has the highest AQI?"}
  ]
}

{
  "messages": [
    {"role": "user", "content": "What is the temperature at sensor 4?"}
  ]
}

{
  "messages": [
    {"role": "user", "content": "Show me PM2.5 for all sensors"}
  ]
}

{
  "messages": [
    {"role": "user", "content": "What is the air quality prediction for sensor 3?"}
  ]
}
```

---

## 🔍 Health Check

### Check if Backend is Running
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T12:40:00",
  "lm_studio_url": "http://192.168.1.147:1234/v1"
}
```

---

## 📈 Data Flow for Dashboard

### Recommended Update Strategy

**Option 1: Real-time Polling (Recommended)**
```dart
Timer.periodic(Duration(seconds: 30), (timer) {
  // Fetch all sensors every 30 seconds
  fetchAllSensors();
});

Future<void> fetchAllSensors() async {
  final response = await http.get(
    Uri.parse('http://192.168.1.147:5000/api/sensors/all')
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    setState(() {
      // Update your dashboard UI with real data
      sensors = data['sensors'];
    });
  }
}
```

**Option 2: On-Demand Refresh**
```dart
onRefresh: () async {
  await fetchAllSensors();
}
```

---

## 🎯 Dashboard Widget Example

```dart
class SensorCard extends StatelessWidget {
  final Map<String, dynamic> sensorData;
  
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          Text('${sensorData['name']}'),
          Text('AQI: ${sensorData['aqi']}'),
          Text('PM2.5: ${sensorData['pollutants']['pm2_5']} µg/m³'),
          Text('PM10: ${sensorData['pollutants']['pm10']} µg/m³'),
          Text('Temp: ${sensorData['environmental']['temperature']}°C'),
          Text('Humidity: ${sensorData['environmental']['humidity']}%'),
        ],
      ),
    );
  }
}
```

---

## ⚠️ Important Notes

### ✅ REAL DATA ONLY
- **NO dummy data is returned**
- All values come from actual sensor readings
- Data is updated every 30 seconds from live sensors
- If no data is available, endpoint returns `status: 'no_data'`

### Data Validation
- PM2.5/PM10: 0-500 µg/m³ (typical range 0-150)
- CO2: 300-5000 ppm (typical range 400-1000)
- TVOC: 0-500 ppb
- Temperature: 0-50°C
- Humidity: 0-100%
- Pressure: 900-1100 hPa
- AQI: 0-500

### Error Handling
```dart
try {
  final response = await http.get(Uri.parse('$baseUrl/api/sensors/all'));
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    
    if (data['status'] == 'success') {
      // Use real data
      updateDashboard(data['sensors']);
    } else if (data['status'] == 'no_data') {
      // Show "Waiting for sensor data..." message
      showWaitingMessage();
    }
  } else if (response.statusCode == 404) {
    // No data available yet
    showMessage('No data available. Sensors are initializing...');
  }
} catch (e) {
  // Network error
  showError('Cannot connect to backend. Check if server is running.');
}
```

---

## 🚀 Quick Start for Frontend

**1. Test the endpoint:**
```bash
curl http://192.168.1.147:5000/api/sensors/all
```

**2. In your Flutter app:**
```dart
final String backendUrl = 'http://192.168.1.147:5000';

// For dashboard
final sensorsResponse = await http.get(Uri.parse('$backendUrl/api/sensors/all'));

// For chatbot  
final chatResponse = await http.post(
  Uri.parse('$backendUrl/api/chat'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'messages': [
      {'role': 'user', 'content': 'What is the air quality?'}
    ]
  })
);
```

---

## 📊 Sample Real Response

Here's what you'll actually get (REAL data from your sensors):

```json
{
  "status": "success",
  "timestamp": "2025-12-30T12:40:15",
  "total_sensors": 5,
  "sensors": {
    "sensor_1": {
      "name": "Sensor 1",
      "aqi": 156,
      "pollutants": {"pm2_5": 65.3, "pm10": 85.7, "co2": 396.0, "tvoc": 101.0},
      "environmental": {"temperature": 25.3, "humidity": 48.5, "pressure": 947.8}
    },
    "sensor_3": {
      "name": "Sensor 3", 
      "aqi": 155,
      "pollutants": {"pm2_5": 66.3, "pm10": 86.7, "co2": 396.0, "tvoc": 101.0},
      "environmental": {"temperature": 25.3, "humidity": 48.5, "pressure": 947.8}
    }
  }
}
```

---

**Last Updated:** 2025-12-30  
**Backend Version:** 2.0 - Real Data Only  
**No Dummy Data - All Values from Actual Sensors** ✅
