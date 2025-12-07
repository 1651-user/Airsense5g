class SensorReading {
  final String sensorId;
  final DateTime timestamp;
  final double pm25;
  final double pm10;
  final double co2;
  final double no2;
  final double so2;
  final double o3;
  final int aqi;

  SensorReading({
    required this.sensorId,
    required this.timestamp,
    required this.pm25,
    required this.pm10,
    required this.co2,
    required this.no2,
    required this.so2,
    required this.o3,
    required this.aqi,
  });

  Map<String, dynamic> toJson() => {
    'sensorId': sensorId,
    'timestamp': timestamp.toIso8601String(),
    'pm25': pm25,
    'pm10': pm10,
    'co2': co2,
    'no2': no2,
    'so2': so2,
    'o3': o3,
    'aqi': aqi,
  };

  factory SensorReading.fromJson(Map<String, dynamic> json) => SensorReading(
    sensorId: json['sensorId'] ?? '',
    timestamp: json['timestamp'] != null ? DateTime.parse(json['timestamp']) : DateTime.now(),
    pm25: json['pm25']?.toDouble() ?? 0.0,
    pm10: json['pm10']?.toDouble() ?? 0.0,
    co2: json['co2']?.toDouble() ?? 0.0,
    no2: json['no2']?.toDouble() ?? 0.0,
    so2: json['so2']?.toDouble() ?? 0.0,
    o3: json['o3']?.toDouble() ?? 0.0,
    aqi: json['aqi']?.toInt() ?? 0,
  );

  SensorReading copyWith({
    String? sensorId,
    DateTime? timestamp,
    double? pm25,
    double? pm10,
    double? co2,
    double? no2,
    double? so2,
    double? o3,
    int? aqi,
  }) => SensorReading(
    sensorId: sensorId ?? this.sensorId,
    timestamp: timestamp ?? this.timestamp,
    pm25: pm25 ?? this.pm25,
    pm10: pm10 ?? this.pm10,
    co2: co2 ?? this.co2,
    no2: no2 ?? this.no2,
    so2: so2 ?? this.so2,
    o3: o3 ?? this.o3,
    aqi: aqi ?? this.aqi,
  );
}
