import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:airsense_5g/models/sensor_model.dart';
import 'package:airsense_5g/models/sensor_reading_model.dart';
import 'package:airsense_5g/services/api_client.dart';

class SensorService {
  static final SensorService _instance = SensorService._internal();
  factory SensorService() => _instance;
  SensorService._internal();

  final _apiClient = ApiClient();
  final _random = Random();

  final List<Map<String, dynamic>> _sensorLocations = [
    {
      'id': 'sensor_1',
      'name': 'Sensor 1',
      'location': 'Location 1',
      'lat': 37.7749,
      'lon': -122.4194
    },
    {
      'id': 'sensor_2',
      'name': 'Sensor 2',
      'location': 'Location 2',
      'lat': 37.7849,
      'lon': -122.4094
    },
    {
      'id': 'sensor_3',
      'name': 'Sensor 3',
      'location': 'Location 3',
      'lat': 37.7649,
      'lon': -122.4294
    },
    {
      'id': 'sensor_4',
      'name': 'Sensor 4',
      'location': 'Location 4',
      'lat': 37.7949,
      'lon': -122.4194
    },
    {
      'id': 'sensor_5',
      'name': 'Sensor 5',
      'location': 'Location 5',
      'lat': 37.7749,
      'lon': -122.3994
    },
  ];

  /// Fetch ALL sensors with REAL data from backend
  Future<List<Sensor>> getAllSensors() async {
    try {
      debugPrint('🌐 Fetching real sensor data from backend...');

      // Call the new endpoint that returns all sensors
      final response = await _apiClient.get('/api/sensors/all');

      if (response.statusCode == 200) {
        final data = response.data;

        if (data['status'] == 'success' && data['sensors'] != null) {
          final sensorsData = data['sensors'] as Map<String, dynamic>;

          final sensors = <Sensor>[];

          // Parse each sensor
          sensorsData.forEach((sensorKey, sensorInfo) {
            // Extract sensor number from key (e.g., "sensor_1" -> 1)
            final sensorNumStr = sensorKey.replaceAll('sensor_', '');
            final sensorNum = int.tryParse(sensorNumStr) ?? 0;

            if (sensorNum > 0 && sensorNum <= _sensorLocations.length) {
              final location = _sensorLocations[sensorNum - 1];

              // Parse pollutants
              final pollutants = sensorInfo['pollutants'] ?? {};
              final environmental = sensorInfo['environmental'] ?? {};

              final sensor = Sensor(
                id: sensorKey,
                name: sensorInfo['name'] ?? location['name'],
                location: location['location'] as String,
                latitude: location['lat'] as double,
                longitude: location['lon'] as double,
                currentData: SensorData(
                  pm25: (pollutants['pm2_5'] ?? 0).toDouble(),
                  pm10: (pollutants['pm10'] ?? 0).toDouble(),
                  co2: (pollutants['co2'] ?? 0).toDouble(),
                  no2: (pollutants['no2'] ?? 0)
                      .toDouble(), // May not be available
                  so2: (pollutants['so2'] ?? 0)
                      .toDouble(), // May not be available
                  o3: (pollutants['o3'] ?? 0)
                      .toDouble(), // May not be available
                  aqi: (sensorInfo['aqi'] ?? 0).toInt(),
                  temperature: (environmental['temperature'] ?? 0).toDouble(),
                  humidity: (environmental['humidity'] ?? 0).toDouble(),
                  pressure: (environmental['pressure'] ?? 0).toDouble(),
                  timestamp: DateTime.now(),
                ),
              );

              sensors.add(sensor);
            }
          });

          debugPrint('✅ Fetched ${sensors.length} REAL sensors from backend');
          return sensors;
        } else if (data['status'] == 'no_data') {
          debugPrint('⚠️ No sensor data available yet from backend');

          // Return sensors with placeholder data
          return _sensorLocations.map((location) {
            return Sensor(
              id: location['id'] as String,
              name: location['name'] as String,
              location: location['location'] as String,
              latitude: location['lat'] as double,
              longitude: location['lon'] as double,
              currentData: SensorData(
                pm25: 0,
                pm10: 0,
                co2: 0,
                no2: 0,
                so2: 0,
                o3: 0,
                aqi: 0,
                temperature: 0,
                humidity: 0,
                pressure: 0,
                timestamp: DateTime.now(),
              ),
            );
          }).toList();
        }
      }

      throw Exception('Failed to load sensors: ${response.statusCode}');
    } catch (e) {
      debugPrint('❌ Error fetching sensors from backend: $e');

      // Fallback: Return sensors with zero data if backend fails
      return _sensorLocations.map((location) {
        return Sensor(
          id: location['id'] as String,
          name: location['name'] as String,
          location: location['location'] as String,
          latitude: location['lat'] as double,
          longitude: location['lon'] as double,
          currentData: SensorData(
            pm25: 0,
            pm10: 0,
            co2: 0,
            no2: 0,
            so2: 0,
            o3: 0,
            aqi: 0,
            temperature: 0,
            humidity: 0,
            pressure: 0,
            timestamp: DateTime.now(),
          ),
        );
      }).toList();
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

  /// Fetch real sensor history (if available from backend)
  /// Note: This may need backend implementation
  Future<List<SensorReading>> getSensorHistory(String sensorId,
      {int hours = 24}) async {
    try {
      // TODO: Implement backend endpoint for historical data
      // For now, generate sample data based on current reading

      final sensor = await getSensorById(sensorId);
      if (sensor == null) return [];

      await Future.delayed(const Duration(milliseconds: 400));

      final now = DateTime.now();
      final currentPM25 = sensor.currentData.pm25;

      final readings = List.generate(hours, (index) {
        final timestamp = now.subtract(Duration(hours: hours - index));

        // Generate realistic variations around current value
        final pm25Variation = currentPM25 + (_random.nextDouble() - 0.5) * 20;
        final pm10Variation =
            sensor.currentData.pm10 + (_random.nextDouble() - 0.5) * 30;

        return SensorReading(
          sensorId: sensorId,
          timestamp: timestamp,
          pm25: pm25Variation.clamp(0, 500),
          pm10: pm10Variation.clamp(0, 500),
          co2: sensor.currentData.co2 + (_random.nextDouble() - 0.5) * 100,
          no2: 5 + _random.nextDouble() * 45,
          so2: 2 + _random.nextDouble() * 18,
          o3: 10 + _random.nextDouble() * 90,
          aqi: _calculateAQI(pm25Variation, pm10Variation),
        );
      });

      debugPrint(
          '✅ Generated ${readings.length} historical readings for $sensorId');
      return readings;
    } catch (e) {
      debugPrint('❌ Get sensor history error: $e');
      return [];
    }
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
    if (pm25 <= 150.4)
      return (150 + (pm25 - 55.4) / (150.4 - 55.4) * 50).round();
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
