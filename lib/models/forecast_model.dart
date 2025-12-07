class Forecast {
  final String sensorId;
  final DateTime timestamp;
  final List<ForecastPoint> hourly24;
  final List<ForecastPoint> weekly;

  Forecast({
    required this.sensorId,
    required this.timestamp,
    required this.hourly24,
    required this.weekly,
  });

  Map<String, dynamic> toJson() => {
    'sensorId': sensorId,
    'timestamp': timestamp.toIso8601String(),
    'hourly24': hourly24.map((e) => e.toJson()).toList(),
    'weekly': weekly.map((e) => e.toJson()).toList(),
  };

  factory Forecast.fromJson(Map<String, dynamic> json) => Forecast(
    sensorId: json['sensorId'] ?? '',
    timestamp: json['timestamp'] != null ? DateTime.parse(json['timestamp']) : DateTime.now(),
    hourly24: (json['hourly24'] as List?)?.map((e) => ForecastPoint.fromJson(e)).toList() ?? [],
    weekly: (json['weekly'] as List?)?.map((e) => ForecastPoint.fromJson(e)).toList() ?? [],
  );

  Forecast copyWith({
    String? sensorId,
    DateTime? timestamp,
    List<ForecastPoint>? hourly24,
    List<ForecastPoint>? weekly,
  }) => Forecast(
    sensorId: sensorId ?? this.sensorId,
    timestamp: timestamp ?? this.timestamp,
    hourly24: hourly24 ?? this.hourly24,
    weekly: weekly ?? this.weekly,
  );
}

class ForecastPoint {
  final DateTime timestamp;
  final int aqi;
  final double pm25;
  final double pm10;

  ForecastPoint({required this.timestamp, required this.aqi, required this.pm25, required this.pm10});

  Map<String, dynamic> toJson() => {
    'timestamp': timestamp.toIso8601String(),
    'aqi': aqi,
    'pm25': pm25,
    'pm10': pm10,
  };

  factory ForecastPoint.fromJson(Map<String, dynamic> json) => ForecastPoint(
    timestamp: json['timestamp'] != null ? DateTime.parse(json['timestamp']) : DateTime.now(),
    aqi: json['aqi']?.toInt() ?? 0,
    pm25: json['pm25']?.toDouble() ?? 0.0,
    pm10: json['pm10']?.toDouble() ?? 0.0,
  );

  ForecastPoint copyWith({DateTime? timestamp, int? aqi, double? pm25, double? pm10}) => ForecastPoint(
    timestamp: timestamp ?? this.timestamp,
    aqi: aqi ?? this.aqi,
    pm25: pm25 ?? this.pm25,
    pm10: pm10 ?? this.pm10,
  );
}
