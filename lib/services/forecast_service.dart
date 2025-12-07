import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:airsense_5g/models/forecast_model.dart';

class ForecastService {
  static final ForecastService _instance = ForecastService._internal();
  factory ForecastService() => _instance;
  ForecastService._internal();

  final _random = Random();

  Future<Forecast> getForecast(String sensorId, int currentAQI, double currentPM25) async {
    try {
      await Future.delayed(const Duration(milliseconds: 600));
      
      final hourly24 = _generate24HourForecast(currentAQI, currentPM25);
      final weekly = _generateWeeklyForecast(currentAQI, currentPM25);
      
      final forecast = Forecast(
        sensorId: sensorId,
        timestamp: DateTime.now(),
        hourly24: hourly24,
        weekly: weekly,
      );
      
      debugPrint('✅ Generated forecast for sensor: $sensorId');
      return forecast;
    } catch (e) {
      debugPrint('❌ Get forecast error: $e');
      rethrow;
    }
  }

  List<ForecastPoint> _generate24HourForecast(int baseAQI, double basePM25) {
    final now = DateTime.now();
    final points = <ForecastPoint>[];
    
    for (int i = 0; i < 24; i++) {
      final timestamp = now.add(Duration(hours: i));
      final hour = timestamp.hour;
      
      double variation = 1.0;
      if (hour >= 6 && hour < 9) {
        variation = 1.3;
      } else if (hour >= 17 && hour < 20) {
        variation = 1.4;
      } else if (hour >= 22 || hour < 6) {
        variation = 0.8;
      }
      
      final randomFactor = 0.85 + _random.nextDouble() * 0.3;
      final pm25 = basePM25 * variation * randomFactor;
      final pm10 = pm25 * 1.5;
      final aqi = _calculateAQI(pm25, pm10);
      
      points.add(ForecastPoint(
        timestamp: timestamp,
        aqi: aqi,
        pm25: pm25,
        pm10: pm10,
      ));
    }
    
    return points;
  }

  List<ForecastPoint> _generateWeeklyForecast(int baseAQI, double basePM25) {
    final now = DateTime.now();
    final points = <ForecastPoint>[];
    
    for (int i = 0; i < 7; i++) {
      final timestamp = now.add(Duration(days: i));
      final dayOfWeek = timestamp.weekday;
      
      double variation = 1.0;
      if (dayOfWeek == DateTime.saturday || dayOfWeek == DateTime.sunday) {
        variation = 0.85;
      } else {
        variation = 1.1;
      }
      
      final randomFactor = 0.8 + _random.nextDouble() * 0.4;
      final pm25 = basePM25 * variation * randomFactor;
      final pm10 = pm25 * 1.5;
      final aqi = _calculateAQI(pm25, pm10);
      
      points.add(ForecastPoint(
        timestamp: timestamp,
        aqi: aqi,
        pm25: pm25,
        pm10: pm10,
      ));
    }
    
    return points;
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
}
