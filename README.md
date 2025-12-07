# AirSense 5G - Architecture Plan

## Overview
AirSense 5G is a smart air quality monitoring app that provides real-time sensor data, personalized health alerts, ML-based forecasts, and an NLP chatbot for health-related air quality queries.

## Technical Stack
- **Frontend**: Flutter with custom UI (non-Material Design aesthetic)
- **State Management**: Provider
- **HTTP Client**: Dio with JWT interceptor
- **Charts**: fl_chart for visualizations
- **Maps**: Google Maps Flutter
- **Storage**: SharedPreferences (local storage for mock data)
- **Backend**: Mocked API responses (Node.js/MongoDB structure simulated)

## Core Features

### 1. Authentication & Profile Management
- Email/password login and signup
- JWT token-based authentication with Dio interceptor
- Mandatory health profile form after signup
- Health profile includes: age, gender, health conditions (asthma, allergies, COPD, heart disease, weak immunity, elderly), activity level, pollution sensitivity

### 2. Personalized Alert System
- Real-time alert generation based on:
  - User's health profile
  - Current sensor pollutant levels (PM2.5, PM10, CO2)
- Health-specific thresholds and messaging

### 3. Dashboard Screen
- Real-time air quality from 10 sensors
- Color-coded AQI card (Good/Moderate/Hazardous)
- "Your Health Risk Today" status
- Prominent personalized alert display
- Quick stats cards

### 4. Map Screen
- Google Maps integration with 10 sensor locations
- Color-coded markers based on current AQI
- Tap marker to view sensor detail screen
- Sensor details: real-time values, 24-hour graph, forecast, personalized advice

### 5. Forecast & Analytics
- 24-hour prediction graph
- Weekly trend visualization
- "What this means for you" contextual advice based on user profile

### 6. NLP Chatbot
- Dedicated chat interface
- Simulated NLP backend (DistilBERT structure)
- Health-specific air quality queries
- Context-aware responses based on user profile

## Data Architecture

### Models (lib/models/)
1. **User** - id, name, email, createdAt
2. **HealthProfile** - userId, age, gender, conditions[], activity, sensitivity
3. **Alert** - userId, timestamp, pollutant, message, severity
4. **Sensor** - id, name, location, lat, lon, currentData (PM2.5, PM10, CO2, NO2, SO2, O3)
5. **SensorReading** - sensorId, timestamp, pollutant values
6. **Forecast** - sensorId, timestamp, predictions (24hr array, weekly array)
7. **ChatMessage** - id, userId, message, response, timestamp, isUser

### Services (lib/services/)
1. **AuthService** - Login, signup, token management, logout
2. **HealthProfileService** - CRUD operations for health profiles
3. **SensorService** - Fetch sensors, real-time data, historical data
4. **AlertService** - Generate personalized alerts based on user profile
5. **ForecastService** - Fetch ML predictions (mocked)
6. **ChatService** - Send queries, get NLP responses (mocked)
7. **ApiClient** - Dio singleton with JWT interceptor

### API Endpoints (Mocked)
- POST /auth/signup
- POST /auth/login
- GET /user/profile/:id
- PUT /user/profile/:id
- GET /sensors/realtime
- GET /sensors/history/:id
- GET /sensors/forecast/:id
- POST /chat/query
- GET /alerts/:userId

## UI Structure

### Screens (lib/screens/)
1. **SplashScreen** - Initial loading
2. **LoginScreen** - Email/password login
3. **SignupScreen** - Registration
4. **HealthProfileFormScreen** - Mandatory post-signup form
5. **DashboardScreen** - Main view with AQI, alerts, quick stats
6. **MapScreen** - Google Maps with sensor markers
7. **SensorDetailScreen** - Detailed view for selected sensor
8. **ForecastScreen** - Analytics and predictions
9. **ChatScreen** - NLP chatbot interface
10. **ProfileScreen** - User profile and settings

### Navigation
- Bottom Navigation Bar: Dashboard, Map, Forecast, Chat, Profile
- Initial route: SplashScreen → LoginScreen/DashboardScreen (based on auth status)

## Color Scheme (Medical Theme)
- **Primary**: Blue (#2196F3) - Trust, medical
- **Success/Good**: Green (#43A047) - Good AQI
- **Warning/Moderate**: Orange (#FB8C00) - Moderate AQI
- **Error/Hazardous**: Red (#E53935) - Hazardous AQI
- **Background**: Clean whites and light grays
- **Text**: Dark grays for readability

## Personalized Alert Logic

| Health Condition | Pollutant | Threshold | Message |
|-----------------|-----------|-----------|---------|
| Asthma | PM2.5 | > 35 | Avoid outdoor activity; risk of breathing issues |
| Heart Disease/Elderly | PM2.5 | > 50 | Stay indoors; pollution may affect your heart |
| Athlete | PM10 | > 80 | Avoid strenuous running outside today |
| Children/Students | CO2 | > 1200 | Poor ventilation detected. Open windows |

## Implementation Steps

1. ✅ Setup dependencies (dio, fl_chart, google_maps_flutter, shared_preferences)
2. ✅ Update theme with medical color palette
3. ✅ Create data models with toJson/fromJson/copyWith
4. ✅ Implement ApiClient with Dio and JWT interceptor
5. ✅ Create all service classes with mock data logic
6. ✅ Build authentication screens (Login, Signup, Health Profile Form)
7. ✅ Implement Dashboard screen with AQI cards and alerts
8. ✅ Build Map screen with Google Maps integration
9. ✅ Create Sensor Detail screen with charts
10. ✅ Implement Forecast screen with analytics
11. ✅ Build Chat screen with NLP interface
12. ✅ Create Profile screen
13. ✅ Setup navigation with bottom nav bar
14. ✅ Integrate personalized alert logic
15. ✅ Test and debug using compile_project tool

## Status: ✅ COMPLETE

All features have been implemented successfully with no compilation errors. The app is fully functional with mock data and ready for testing.

## Notes
- All backend interactions are mocked with local data
- JWT tokens stored in SharedPreferences
- Sample data includes 10 sensors around a city
- Charts use fl_chart with smooth animations
- Google Maps requires API key configuration
- Health profile is mandatory before accessing main app
