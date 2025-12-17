class PredictionData {
  final DateTime timestamp;
  final int aqi;
  final double pm25;
  final double pm10;
  final double co2;
  final double no2;
  final Location? location;
  final List<ForecastData>? forecast;

  PredictionData({
    required this.timestamp,
    required this.aqi,
    required this.pm25,
    required this.pm10,
    required this.co2,
    required this.no2,
    this.location,
    this.forecast,
  });

  factory PredictionData.fromJson(Map<String, dynamic> json) {
    return PredictionData(
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      aqi: json['aqi'] ?? 0,
      pm25: (json['pm25'] ?? 0).toDouble(),
      pm10: (json['pm10'] ?? 0).toDouble(),
      co2: (json['co2'] ?? 0).toDouble(),
      no2: (json['no2'] ?? 0).toDouble(),
      location:
          json['location'] != null ? Location.fromJson(json['location']) : null,
      forecast: json['forecast'] != null
          ? (json['forecast'] as List)
              .map((f) => ForecastData.fromJson(f))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'aqi': aqi,
      'pm25': pm25,
      'pm10': pm10,
      'co2': co2,
      'no2': no2,
      'location': location?.toJson(),
      'forecast': forecast?.map((f) => f.toJson()).toList(),
    };
  }

  String getAqiCategory() {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for Sensitive Groups';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very Unhealthy';
    return 'Hazardous';
  }

  String getHealthAdvice() {
    if (aqi <= 50) {
      return 'Air quality is good. Enjoy outdoor activities!';
    } else if (aqi <= 100) {
      return 'Air quality is acceptable. Sensitive individuals should limit prolonged outdoor exertion.';
    } else if (aqi <= 150) {
      return 'Sensitive groups should reduce prolonged outdoor exertion.';
    } else if (aqi <= 200) {
      return 'Everyone should reduce prolonged outdoor exertion.';
    } else if (aqi <= 300) {
      return 'Avoid prolonged outdoor exertion. Everyone should stay indoors.';
    } else {
      return 'Health alert! Avoid all outdoor activities.';
    }
  }
}

class Location {
  final double lat;
  final double lon;
  final String? name;

  Location({
    required this.lat,
    required this.lon,
    this.name,
  });

  factory Location.fromJson(Map<String, dynamic> json) {
    return Location(
      lat: (json['lat'] ?? 0).toDouble(),
      lon: (json['lon'] ?? 0).toDouble(),
      name: json['name'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'lat': lat,
      'lon': lon,
      'name': name,
    };
  }
}

class ForecastData {
  final DateTime timestamp;
  final int aqi;
  final double pm25;

  ForecastData({
    required this.timestamp,
    required this.aqi,
    required this.pm25,
  });

  factory ForecastData.fromJson(Map<String, dynamic> json) {
    return ForecastData(
      timestamp: DateTime.parse(json['timestamp']),
      aqi: json['aqi'] ?? 0,
      pm25: (json['pm25'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'timestamp': timestamp.toIso8601String(),
      'aqi': aqi,
      'pm25': pm25,
    };
  }
}
