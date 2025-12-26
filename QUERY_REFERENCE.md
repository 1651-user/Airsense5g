# Quick Reference - AI Chat Queries

## Pollutant Level Queries

### Show All Pollutants
```
"Show the pollutant levels"
"What are the current pollutant levels?"
"Display all air quality metrics"
"Show me the air quality data"
```

**Expected Response:**
- AQI with category
- PM2.5, PM10, CO2, TVOC levels
- Temperature, humidity, pressure
- Predicted values with trends

### Specific Pollutants
```
"What is the PM2.5 level?"
"Show me the CO2 concentration"
"How high is the TVOC?"
"What's the particulate matter level?"
```

**Expected Response:**
- Specific pollutant value with unit
- Current vs predicted comparison
- Health implications

### Air Quality Index
```
"What's the AQI?"
"What is the air quality index?"
"Is the air quality good?"
"Show me the AQI level"
```

**Expected Response:**
- AQI number
- Category (Good, Moderate, etc.)
- Health recommendations

## Prediction Queries

### Future Forecasts
```
"What are the predictions?"
"Will air quality improve?"
"Show predicted values"
"What's the forecast?"
```

**Expected Response:**
- Predicted values for all pollutants
- Trend indicators (↑/↓)
- Comparison with current values

### Specific Predictions
```
"Will PM2.5 increase?"
"What's the CO2 forecast?"
"Is air quality getting better or worse?"
```

**Expected Response:**
- Specific pollutant prediction
- Trend direction and magnitude
- Time frame

## Health & Safety Queries

### General Safety
```
"Is it safe to go outside?"
"Can I exercise outdoors?"
"Should I wear a mask?"
"Is the air quality safe?"
```

**Expected Response:**
- Current AQI assessment
- Specific recommendations
- Vulnerable group warnings

### Activity-Specific
```
"Can I go for a run?"
"Is it safe for children to play outside?"
"Should I open windows?"
"Can I do outdoor sports?"
```

**Expected Response:**
- Activity-specific advice
- Current pollutant levels
- Alternative suggestions

### Health Conditions
```
"I have asthma, is it safe?"
"Recommendations for heart patients?"
"What about elderly people?"
"COPD patient precautions?"
```

**Expected Response:**
- Condition-specific thresholds
- Current vs safe levels
- Specific precautions

## Environmental Queries

### Temperature & Humidity
```
"What's the temperature?"
"Show me the humidity level"
"What are the environmental conditions?"
```

**Expected Response:**
- Temperature in °C
- Humidity percentage
- Pressure in hPa

### Indoor Air Quality
```
"How's the indoor air quality?"
"Should I use an air purifier?"
"What about ventilation?"
```

**Expected Response:**
- CO2 and TVOC levels
- Ventilation recommendations
- Air purifier suggestions

## Comparison Queries

### Time-Based
```
"How does this compare to yesterday?"
"Is air quality better than usual?"
"What's the trend?"
```

**Expected Response:**
- Current vs predicted comparison
- Trend indicators
- Historical context (if available)

### Threshold-Based
```
"Is PM2.5 above safe levels?"
"Are we exceeding WHO guidelines?"
"Is CO2 too high?"
```

**Expected Response:**
- Current value vs threshold
- Exceedance amount
- Health implications

## Data Queries

### Raw Data
```
"Show all sensor readings"
"Give me the raw data"
"What are all the measurements?"
```

**Expected Response:**
- Complete sensor data
- All pollutant values
- Environmental parameters

### Specific Sensors
```
"What sensors are active?"
"Show sensor status"
"Which pollutants are monitored?"
```

**Expected Response:**
- List of active sensors
- Monitored parameters
- Data freshness

## Example Conversations

### Conversation 1: Morning Check
```
User: "Good morning! What's the air quality like?"

AI: "Good morning! Based on current sensor readings:

Air Quality Index: 45 (Good)

Current Pollutant Levels:
• PM2.5: 8.2 µg/m³
• PM10: 15.3 µg/m³
• CO2: 395 ppm

Temperature: 22.5°C
Humidity: 58%

The air quality is good. It's safe for all outdoor activities!"
```

### Conversation 2: Exercise Planning
```
User: "Can I go for a run?"

AI: "Based on current conditions:

AQI: 45 (Good)
PM2.5: 8.2 µg/m³ (Well below 12 µg/m³ threshold)
PM10: 15.3 µg/m³

Yes, it's safe to go for a run! The air quality is good 
and all pollutant levels are low. Enjoy your workout!"
```

### Conversation 3: Health Concern
```
User: "I have asthma. Is it safe to go outside?"

AI: "For individuals with asthma, let me check the levels:

Current PM2.5: 8.2 µg/m³ (Safe - below 35 µg/m³)
AQI: 45 (Good)

Yes, it's safe for you to go outside. The PM2.5 level 
is well below the threshold for asthma patients. However, 
keep your rescue inhaler with you as a precaution."
```

### Conversation 4: Detailed Analysis
```
User: "Show the pollutant levels"

AI: "Based on current sensor readings:

Air Quality Index: 85 (Moderate)

CURRENT POLLUTANT LEVELS:
• PM2.5: 35.2 µg/m³
• PM10: 52.8 µg/m³
• CO2: 412 ppm
• TVOC: 125 ppb

ENVIRONMENTAL CONDITIONS:
• Temperature: 24.5°C
• Humidity: 65%
• Pressure: 1013.2 hPa

PREDICTIONS (Next Reading):
• PM2.5: 36.8 µg/m³ (↑ +1.6)
• PM10: 54.2 µg/m³ (↑ +1.4)
• CO2: 408 ppm (↓ -4.0)

The air quality is moderate. Sensitive individuals should 
consider limiting prolonged outdoor activities."
```

## Tips for Best Results

### Be Specific
✅ "What is the PM2.5 level?"
❌ "Tell me about air"

### Use Natural Language
✅ "Is it safe to go outside?"
✅ "Can I exercise outdoors?"
✅ "Show the pollutant levels"

### Ask Follow-up Questions
```
User: "What's the AQI?"
AI: "The current AQI is 85 (Moderate)..."

User: "What does that mean for running?"
AI: "For running with AQI at 85..."
```

### Request Specific Data
✅ "Show me the CO2 levels"
✅ "What are the predictions for PM2.5?"
✅ "Is TVOC high?"

## Common Response Patterns

### Good Air Quality (AQI 0-50)
- "Air quality is good"
- "Safe for all activities"
- "No health concerns"

### Moderate Air Quality (AQI 51-100)
- "Air quality is moderate"
- "Sensitive individuals should be cautious"
- "Generally acceptable"

### Unhealthy for Sensitive Groups (AQI 101-150)
- "Sensitive individuals should limit outdoor activities"
- "General public less likely to be affected"
- "Consider indoor alternatives"

### Unhealthy (AQI 151-200)
- "Everyone should limit prolonged outdoor exertion"
- "Sensitive groups should avoid outdoor activities"
- "Health effects may be experienced"

## Troubleshooting

### AI Gives Generic Responses
**Problem:** AI says "Check the dashboard" instead of showing values

**Solution:**
1. Verify backend is running
2. Check MQTT pipeline is receiving data
3. Ensure predictions are being sent to backend
4. Run: `python test_data_flow.py`

### AI Shows Old Data
**Problem:** Values seem outdated

**Solution:**
1. Check MQTT pipeline is receiving new data
2. Verify backend has latest predictions
3. Check timestamp in AI response

### AI Doesn't Understand Question
**Problem:** AI gives irrelevant response

**Solution:**
1. Rephrase question more clearly
2. Use suggested questions as templates
3. Be more specific about what you want

## Quick Commands

### Test System
```bash
python test_data_flow.py
```

### Start All Services
```bash
start_ai_chat_system.bat
```

### Check Backend Data
```bash
curl http://localhost:5000/api/predictions/latest
```

### View MQTT Data
```bash
type mqtt_data.json
```

---

**Remember:** The AI has access to real-time sensor data and predictions. 
Ask specific questions to get the most accurate and helpful responses!
