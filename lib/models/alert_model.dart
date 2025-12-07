class Alert {
  final String id;
  final String userId;
  final DateTime timestamp;
  final String pollutant;
  final String message;
  final String severity;

  Alert({
    required this.id,
    required this.userId,
    required this.timestamp,
    required this.pollutant,
    required this.message,
    required this.severity,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'userId': userId,
    'timestamp': timestamp.toIso8601String(),
    'pollutant': pollutant,
    'message': message,
    'severity': severity,
  };

  factory Alert.fromJson(Map<String, dynamic> json) => Alert(
    id: json['id'] ?? '',
    userId: json['userId'] ?? '',
    timestamp: json['timestamp'] != null ? DateTime.parse(json['timestamp']) : DateTime.now(),
    pollutant: json['pollutant'] ?? '',
    message: json['message'] ?? '',
    severity: json['severity'] ?? '',
  );

  Alert copyWith({
    String? id,
    String? userId,
    DateTime? timestamp,
    String? pollutant,
    String? message,
    String? severity,
  }) => Alert(
    id: id ?? this.id,
    userId: userId ?? this.userId,
    timestamp: timestamp ?? this.timestamp,
    pollutant: pollutant ?? this.pollutant,
    message: message ?? this.message,
    severity: severity ?? this.severity,
  );
}
