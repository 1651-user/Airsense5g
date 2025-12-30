import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:airsense_5g/models/prediction_model.dart';

class PredictionService {
  final Dio _dio = Dio();

  // Backend server URL - Updated to use actual computer IP
  // For emulator: http://10.0.2.2:5000 (Android) or http://localhost:5000 (iOS)
  // For physical device: http://192.168.1.16:5000
  final String _baseUrl = kIsWeb
      ? 'http://localhost:5000/api'
      : 'http://192.168.1.16:5000/api'; // Use actual computer IP

  PredictionData? _cachedPrediction;
  DateTime? _lastFetchTime;

  // Cache duration - fetch new data only if cache is older than this
  final Duration _cacheDuration = const Duration(minutes: 5);

  /// Get the latest prediction data from the backend server
  Future<PredictionData?> getLatestPredictions() async {
    try {
      // Return cached data if still fresh
      if (_cachedPrediction != null &&
          _lastFetchTime != null &&
          DateTime.now().difference(_lastFetchTime!) < _cacheDuration) {
        debugPrint('Returning cached prediction data');
        return _cachedPrediction;
      }

      final url = '$_baseUrl/predictions/latest';
      debugPrint('Fetching prediction data from: $url');

      final response = await _dio.get(
        url,
        options: Options(
          receiveTimeout: const Duration(seconds: 10),
          sendTimeout: const Duration(seconds: 10),
        ),
      );

      if (response.statusCode == 200) {
        final data = response.data;

        if (data['status'] == 'success' && data['data'] != null) {
          _cachedPrediction = PredictionData.fromJson(data['data']);
          _lastFetchTime = DateTime.now();
          debugPrint(
              'Successfully fetched prediction data: AQI=${_cachedPrediction!.aqi}');
          return _cachedPrediction;
        } else if (data['status'] == 'no_data') {
          debugPrint('No prediction data available yet');
          return null;
        }
      }

      debugPrint('Failed to fetch prediction data: ${response.statusCode}');
      return null;
    } catch (e) {
      debugPrint('Error fetching prediction data: $e');
      // Return cached data if available, even if expired
      return _cachedPrediction;
    }
  }

  /// Force refresh prediction data (ignores cache)
  Future<PredictionData?> refreshPredictions() async {
    _cachedPrediction = null;
    _lastFetchTime = null;
    return await getLatestPredictions();
  }

  /// Stream of prediction data (polls every interval)
  Stream<PredictionData?> getPredictionStream({
    Duration interval = const Duration(minutes: 1),
  }) async* {
    while (true) {
      yield await getLatestPredictions();
      await Future.delayed(interval);
    }
  }

  /// Check if backend server is reachable
  Future<bool> checkServerHealth() async {
    try {
      final url = _baseUrl.replaceAll('/api', '/health');
      final response = await _dio.get(
        url,
        options: Options(
          receiveTimeout: const Duration(seconds: 5),
        ),
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Server health check failed: $e');
      return false;
    }
  }

  /// Get cached prediction data without making a network request
  PredictionData? getCachedPrediction() {
    return _cachedPrediction;
  }

  /// Clear cached data
  void clearCache() {
    _cachedPrediction = null;
    _lastFetchTime = null;
  }
}
