class SensorReading {
  final String sensorId;
  final DateTime timestamp;
  final double pm25;
  final double pm10;
  final double co2;
  final double tvoc;
  final int aqi;

  SensorReading({
    required this.sensorId,
    required this.timestamp,
    required this.pm25,
    required this.pm10,
    required this.co2,
    required this.tvoc,
    required this.aqi,
  });

  Map<String, dynamic> toJson() => {
        'sensorId': sensorId,
        'timestamp': timestamp.toIso8601String(),
        'pm25': pm25,
        'pm10': pm10,
        'co2': co2,
        'tvoc': tvoc,
        'aqi': aqi,
      };

  factory SensorReading.fromJson(Map<String, dynamic> json) => SensorReading(
        sensorId: json['sensorId'] ?? '',
        timestamp: json['timestamp'] != null
            ? DateTime.parse(json['timestamp'])
            : DateTime.now(),
        pm25: json['pm25']?.toDouble() ?? 0.0,
        pm10: json['pm10']?.toDouble() ?? 0.0,
        co2: json['co2']?.toDouble() ?? 0.0,
        tvoc: json['tvoc']?.toDouble() ?? 0.0,
        aqi: json['aqi']?.toInt() ?? 0,
      );

  SensorReading copyWith({
    String? sensorId,
    DateTime? timestamp,
    double? pm25,
    double? pm10,
    double? co2,
    double? tvoc,
    int? aqi,
  }) =>
      SensorReading(
        sensorId: sensorId ?? this.sensorId,
        timestamp: timestamp ?? this.timestamp,
        pm25: pm25 ?? this.pm25,
        pm10: pm10 ?? this.pm10,
        co2: co2 ?? this.co2,
        tvoc: tvoc ?? this.tvoc,
        aqi: aqi ?? this.aqi,
      );
}
