import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:airsense_5g/models/forecast_model.dart';

class ForecastService {
  static final ForecastService _instance = ForecastService._internal();
  factory ForecastService() => _instance;
  ForecastService._internal();

  final Dio _dio = Dio();

  // Backend server URL
  final String _baseUrl =
      kIsWeb ? 'http://localhost:5000/api' : 'http://192.168.1.16:5000/api';

  /// Get forecast from backend API
  Future<Forecast> getForecast(
      String sensorId, int currentAQI, double currentPM25) async {
    try {
      // Extract sensor number from ID (e.g., "sensor_1" -> "1")
      final sensorNum = sensorId.replaceAll('sensor_', '');

      final url = '$_baseUrl/forecast/$sensorNum?hours=24&days=7';
      debugPrint('🔮 Fetching forecast from: $url');

      final response = await _dio.get(
        url,
        options: Options(
          receiveTimeout: const Duration(seconds: 10),
          sendTimeout: const Duration(seconds: 10),
        ),
      );

      if (response.statusCode == 200) {
        final data = response.data;

        if (data['status'] == 'success') {
          // Parse hourly forecast
          final hourlyData = data['hourly'] as List;
          final hourly24 = hourlyData.map((point) {
            return ForecastPoint(
              timestamp: DateTime.parse(point['timestamp']),
              aqi: point['aqi'] as int,
              pm25: (point['pm25'] as num).toDouble(),
              pm10: (point['pm10'] as num).toDouble(),
            );
          }).toList();

          // Parse daily forecast
          final dailyData = data['daily'] as List;
          final weekly = dailyData.map((point) {
            return ForecastPoint(
              timestamp: DateTime.parse(point['date']),
              aqi: point['aqi'] as int,
              pm25: (point['pm25'] as num).toDouble(),
              pm10: (point['pm10'] as num).toDouble(),
            );
          }).toList();

          final forecast = Forecast(
            sensorId: sensorId,
            timestamp: DateTime.parse(data['timestamp']),
            hourly24: hourly24,
            weekly: weekly,
          );

          debugPrint(
              '✅ Fetched forecast: ${hourly24.length} hourly, ${weekly.length} daily points');
          return forecast;
        } else if (data['status'] == 'no_data') {
          debugPrint('⚠️ No forecast data available, generating fallback');
          return _generateFallbackForecast(sensorId, currentAQI, currentPM25);
        }
      }

      debugPrint('⚠️ Failed to fetch forecast, using fallback');
      return _generateFallbackForecast(sensorId, currentAQI, currentPM25);
    } catch (e) {
      debugPrint('❌ Forecast error: $e');
      // Return fallback forecast on error
      return _generateFallbackForecast(sensorId, currentAQI, currentPM25);
    }
  }

  /// Generate fallback forecast if backend is unavailable
  Forecast _generateFallbackForecast(
      String sensorId, int baseAQI, double basePM25) {
    final now = DateTime.now();

    // Generate simple hourly forecast
    final hourly24 = List.generate(24, (i) {
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

      final pm25 = basePM25 * variation;
      final pm10 = pm25 * 1.5;

      return ForecastPoint(
        timestamp: timestamp,
        aqi: (baseAQI * variation).round(),
        pm25: pm25,
        pm10: pm10,
      );
    });

    // Generate simple weekly forecast
    final weekly = List.generate(7, (i) {
      final timestamp = now.add(Duration(days: i));
      final isWeekend = timestamp.weekday >= 6;

      final variation = isWeekend ? 0.85 : 1.1;
      final pm25 = basePM25 * variation;
      final pm10 = pm25 * 1.5;

      return ForecastPoint(
        timestamp: timestamp,
        aqi: (baseAQI * variation).round(),
        pm25: pm25,
        pm10: pm10,
      );
    });

    return Forecast(
      sensorId: sensorId,
      timestamp: now,
      hourly24: hourly24,
      weekly: weekly,
    );
  }
}
