import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import 'package:airsense_5g/models/alert_model.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/models/sensor_model.dart';

class AlertService {
  static final AlertService _instance = AlertService._internal();
  factory AlertService() => _instance;
  AlertService._internal();

  final _uuid = const Uuid();

  Future<List<Alert>> generateAlerts(String userId, HealthProfile profile, List<Sensor> sensors) async {
    try {
      await Future.delayed(const Duration(milliseconds: 300));
      
      final alerts = <Alert>[];
      
      for (final sensor in sensors) {
        final data = sensor.currentData;
        
        if (profile.conditions.contains('Asthma') && data.pm25 > 35) {
          alerts.add(Alert(
            id: _uuid.v4(),
            userId: userId,
            timestamp: DateTime.now(),
            pollutant: 'PM2.5',
            message: 'Avoid outdoor activity near ${sensor.name}; risk of breathing issues.',
            severity: 'high',
          ));
        }
        
        if ((profile.conditions.contains('Heart disease') || profile.conditions.contains('Elderly (60+)')) && data.pm25 > 50) {
          alerts.add(Alert(
            id: _uuid.v4(),
            userId: userId,
            timestamp: DateTime.now(),
            pollutant: 'PM2.5',
            message: 'Stay indoors; pollution levels at ${sensor.name} may affect your heart.',
            severity: 'high',
          ));
        }
        
        if (profile.activityLevel == 'Athlete' && data.pm10 > 80) {
          alerts.add(Alert(
            id: _uuid.v4(),
            userId: userId,
            timestamp: DateTime.now(),
            pollutant: 'PM10',
            message: 'Avoid strenuous running outside near ${sensor.name} today.',
            severity: 'medium',
          ));
        }
        
        if ((profile.activityLevel == 'Student' || profile.age < 18) && data.co2 > 1200) {
          alerts.add(Alert(
            id: _uuid.v4(),
            userId: userId,
            timestamp: DateTime.now(),
            pollutant: 'CO2',
            message: 'Poor ventilation detected at ${sensor.name}. Open windows immediately.',
            severity: 'medium',
          ));
        }
        
        if (profile.conditions.contains('Allergies') && data.pm25 > 40) {
          alerts.add(Alert(
            id: _uuid.v4(),
            userId: userId,
            timestamp: DateTime.now(),
            pollutant: 'PM2.5',
            message: 'High allergen levels at ${sensor.name}. Consider staying indoors.',
            severity: 'medium',
          ));
        }
        
        if (profile.conditions.contains('COPD') && data.pm25 > 30) {
          alerts.add(Alert(
            id: _uuid.v4(),
            userId: userId,
            timestamp: DateTime.now(),
            pollutant: 'PM2.5',
            message: 'Air quality at ${sensor.name} may worsen COPD symptoms. Stay indoors.',
            severity: 'high',
          ));
        }
        
        if (profile.conditions.contains('Weak immunity') && data.aqi > 100) {
          alerts.add(Alert(
            id: _uuid.v4(),
            userId: userId,
            timestamp: DateTime.now(),
            pollutant: 'AQI',
            message: 'Unhealthy air quality at ${sensor.name}. Limit outdoor exposure.',
            severity: 'medium',
          ));
        }
      }
      
      debugPrint('✅ Generated ${alerts.length} personalized alerts');
      return alerts;
    } catch (e) {
      debugPrint('❌ Generate alerts error: $e');
      return [];
    }
  }

  String getHealthRiskLevel(HealthProfile profile, List<Sensor> sensors) {
    if (sensors.isEmpty) return 'Unknown';
    
    final avgAQI = sensors.map((s) => s.currentData.aqi).reduce((a, b) => a + b) / sensors.length;
    final avgPM25 = sensors.map((s) => s.currentData.pm25).reduce((a, b) => a + b) / sensors.length;
    
    final hasSeriousCondition = profile.conditions.any((c) => 
      c == 'Asthma' || c == 'Heart disease' || c == 'COPD' || c == 'Elderly (60+)');
    
    if (hasSeriousCondition) {
      if (avgPM25 > 50 || avgAQI > 100) return 'High Risk';
      if (avgPM25 > 35 || avgAQI > 75) return 'Moderate Risk';
      return 'Low Risk';
    } else {
      if (avgAQI > 150) return 'High Risk';
      if (avgAQI > 100) return 'Moderate Risk';
      if (avgAQI > 50) return 'Caution';
      return 'Low Risk';
    }
  }

  String getHealthAdvice(HealthProfile profile, int aqi, double pm25) {
    final hasSeriousCondition = profile.conditions.any((c) => 
      c == 'Asthma' || c == 'Heart disease' || c == 'COPD');
    
    if (hasSeriousCondition) {
      if (pm25 > 50) return 'Stay indoors and keep windows closed. Use air purifier if available.';
      if (pm25 > 35) return 'Limit outdoor activities and wear a mask if you must go outside.';
      return 'Air quality is acceptable, but monitor your symptoms.';
    }
    
    if (aqi > 150) return 'Avoid prolonged outdoor activities. Everyone should limit exertion.';
    if (aqi > 100) return 'Sensitive groups should reduce outdoor activities.';
    if (aqi > 50) return 'Unusually sensitive people should consider reducing outdoor activities.';
    return 'Air quality is good. Enjoy your outdoor activities!';
  }
}
