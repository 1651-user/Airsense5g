import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:airsense_5g/models/sensor_model.dart';
import 'package:airsense_5g/models/sensor_reading_model.dart';

class SensorService {
  static final SensorService _instance = SensorService._internal();
  factory SensorService() => _instance;
  SensorService._internal();

  final _random = Random();

  final List<Map<String, dynamic>> _sensorLocations = [
    {'name': 'Downtown Station', 'location': 'City Center', 'lat': 37.7749, 'lon': -122.4194},
    {'name': 'Riverside Monitor', 'location': 'Waterfront', 'lat': 37.7849, 'lon': -122.4094},
    {'name': 'Industrial Park', 'location': 'West District', 'lat': 37.7649, 'lon': -122.4294},
    {'name': 'Green Valley', 'location': 'North Hills', 'lat': 37.7949, 'lon': -122.4194},
    {'name': 'Harbor Point', 'location': 'East Bay', 'lat': 37.7749, 'lon': -122.3994},
    {'name': 'University Campus', 'location': 'Academic Zone', 'lat': 37.7849, 'lon': -122.4294},
    {'name': 'Airport Terminal', 'location': 'South Airport', 'lat': 37.7549, 'lon': -122.4094},
    {'name': 'Residential Area', 'location': 'Suburban District', 'lat': 37.7949, 'lon': -122.4394},
    {'name': 'Shopping District', 'location': 'Mall Zone', 'lat': 37.7649, 'lon': -122.4094},
    {'name': 'Medical Center', 'location': 'Hospital Area', 'lat': 37.7749, 'lon': -122.4394},
  ];

  Future<List<Sensor>> getAllSensors() async {
    try {
      await Future.delayed(const Duration(milliseconds: 600));
      
      final sensors = _sensorLocations.asMap().entries.map((entry) {
        final index = entry.key;
        final location = entry.value;
        
        return Sensor(
          id: 'sensor_$index',
          name: location['name'] as String,
          location: location['location'] as String,
          latitude: location['lat'] as double,
          longitude: location['lon'] as double,
          currentData: _generateRandomSensorData(),
        );
      }).toList();
      
      debugPrint('✅ Fetched ${sensors.length} sensors');
      return sensors;
    } catch (e) {
      debugPrint('❌ Get sensors error: $e');
      return [];
    }
  }

  Future<Sensor?> getSensorById(String id) async {
    try {
      final sensors = await getAllSensors();
      return sensors.firstWhere((s) => s.id == id);
    } catch (e) {
      debugPrint('❌ Get sensor by ID error: $e');
      return null;
    }
  }

  Future<List<SensorReading>> getSensorHistory(String sensorId, {int hours = 24}) async {
    try {
      await Future.delayed(const Duration(milliseconds: 400));
      
      final now = DateTime.now();
      final readings = List.generate(hours, (index) {
        final timestamp = now.subtract(Duration(hours: hours - index));
        return SensorReading(
          sensorId: sensorId,
          timestamp: timestamp,
          pm25: 10 + _random.nextDouble() * 60,
          pm10: 20 + _random.nextDouble() * 80,
          co2: 300 + _random.nextDouble() * 1200,
          no2: 5 + _random.nextDouble() * 45,
          so2: 2 + _random.nextDouble() * 18,
          o3: 10 + _random.nextDouble() * 90,
          aqi: 20 + _random.nextInt(180),
        );
      });
      
      debugPrint('✅ Fetched ${readings.length} readings for sensor: $sensorId');
      return readings;
    } catch (e) {
      debugPrint('❌ Get sensor history error: $e');
      return [];
    }
  }

  SensorData _generateRandomSensorData() {
    final pm25 = 10 + _random.nextDouble() * 60;
    final pm10 = 20 + _random.nextDouble() * 80;
    final co2 = 300 + _random.nextDouble() * 1200;
    
    final aqi = _calculateAQI(pm25, pm10);
    
    return SensorData(
      pm25: pm25,
      pm10: pm10,
      co2: co2,
      no2: 5 + _random.nextDouble() * 45,
      so2: 2 + _random.nextDouble() * 18,
      o3: 10 + _random.nextDouble() * 90,
      aqi: aqi,
      timestamp: DateTime.now(),
    );
  }

  int _calculateAQI(double pm25, double pm10) {
    final aqiPM25 = _pm25ToAQI(pm25);
    final aqiPM10 = _pm10ToAQI(pm10);
    return max(aqiPM25, aqiPM10);
  }

  int _pm25ToAQI(double pm25) {
    if (pm25 <= 12.0) return (pm25 / 12.0 * 50).round();
    if (pm25 <= 35.4) return (50 + (pm25 - 12.0) / (35.4 - 12.0) * 50).round();
    if (pm25 <= 55.4) return (100 + (pm25 - 35.4) / (55.4 - 35.4) * 50).round();
    if (pm25 <= 150.4) return (150 + (pm25 - 55.4) / (150.4 - 55.4) * 50).round();
    return 200;
  }

  int _pm10ToAQI(double pm10) {
    if (pm10 <= 54) return (pm10 / 54 * 50).round();
    if (pm10 <= 154) return (50 + (pm10 - 54) / (154 - 54) * 50).round();
    if (pm10 <= 254) return (100 + (pm10 - 154) / (254 - 154) * 50).round();
    if (pm10 <= 354) return (150 + (pm10 - 254) / (354 - 254) * 50).round();
    return 200;
  }

  String getAQICategory(int aqi) {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for Sensitive';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very Unhealthy';
    return 'Hazardous';
  }
}
