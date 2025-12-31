class Sensor {
  final String id;
  final String name;
  final String location;
  final double latitude;
  final double longitude;
  final SensorData currentData;

  Sensor({
    required this.id,
    required this.name,
    required this.location,
    required this.latitude,
    required this.longitude,
    required this.currentData,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'location': location,
        'latitude': latitude,
        'longitude': longitude,
        'currentData': currentData.toJson(),
      };

  factory Sensor.fromJson(Map<String, dynamic> json) => Sensor(
        id: json['id'] ?? '',
        name: json['name'] ?? '',
        location: json['location'] ?? '',
        latitude: json['latitude']?.toDouble() ?? 0.0,
        longitude: json['longitude']?.toDouble() ?? 0.0,
        currentData: json['currentData'] != null
            ? SensorData.fromJson(json['currentData'])
            : SensorData.empty(),
      );

  Sensor copyWith({
    String? id,
    String? name,
    String? location,
    double? latitude,
    double? longitude,
    SensorData? currentData,
  }) =>
      Sensor(
        id: id ?? this.id,
        name: name ?? this.name,
        location: location ?? this.location,
        latitude: latitude ?? this.latitude,
        longitude: longitude ?? this.longitude,
        currentData: currentData ?? this.currentData,
      );
}

class SensorData {
  final double pm25;
  final double pm10;
  final double co2;
  final double tvoc;
  final int aqi;
  final double temperature;
  final double humidity;
  final double pressure;
  final DateTime timestamp;

  SensorData({
    required this.pm25,
    required this.pm10,
    required this.co2,
    required this.tvoc,
    required this.aqi,
    required this.temperature,
    required this.humidity,
    required this.pressure,
    required this.timestamp,
  });

  factory SensorData.empty() => SensorData(
        pm25: 0,
        pm10: 0,
        co2: 0,
        tvoc: 0,
        aqi: 0,
        temperature: 0,
        humidity: 0,
        pressure: 0,
        timestamp: DateTime.now(),
      );

  Map<String, dynamic> toJson() => {
        'pm25': pm25,
        'pm10': pm10,
        'co2': co2,
        'tvoc': tvoc,
        'aqi': aqi,
        'temperature': temperature,
        'humidity': humidity,
        'pressure': pressure,
        'timestamp': timestamp.toIso8601String(),
      };

  factory SensorData.fromJson(Map<String, dynamic> json) => SensorData(
        pm25: json['pm25']?.toDouble() ?? 0.0,
        pm10: json['pm10']?.toDouble() ?? 0.0,
        co2: json['co2']?.toDouble() ?? 0.0,
        tvoc: json['tvoc']?.toDouble() ?? 0.0,
        aqi: json['aqi']?.toInt() ?? 0,
        temperature: json['temperature']?.toDouble() ?? 0.0,
        humidity: json['humidity']?.toDouble() ?? 0.0,
        pressure: json['pressure']?.toDouble() ?? 0.0,
        timestamp: json['timestamp'] != null
            ? DateTime.parse(json['timestamp'])
            : DateTime.now(),
      );

  SensorData copyWith({
    double? pm25,
    double? pm10,
    double? co2,
    double? tvoc,
    int? aqi,
    double? temperature,
    double? humidity,
    double? pressure,
    DateTime? timestamp,
  }) =>
      SensorData(
        pm25: pm25 ?? this.pm25,
        pm10: pm10 ?? this.pm10,
        co2: co2 ?? this.co2,
        tvoc: tvoc ?? this.tvoc,
        aqi: aqi ?? this.aqi,
        temperature: temperature ?? this.temperature,
        humidity: humidity ?? this.humidity,
        pressure: pressure ?? this.pressure,
        timestamp: timestamp ?? this.timestamp,
      );
}
