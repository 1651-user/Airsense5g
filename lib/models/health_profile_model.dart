class HealthProfile {
  final String userId;
  final int age;
  final String gender;
  final List<String> conditions;
  final String activityLevel;
  final String pollutionSensitivity;
  final DateTime createdAt;
  final DateTime updatedAt;

  HealthProfile({
    required this.userId,
    required this.age,
    required this.gender,
    required this.conditions,
    required this.activityLevel,
    required this.pollutionSensitivity,
    required this.createdAt,
    required this.updatedAt,
  });

  Map<String, dynamic> toJson() => {
    'userId': userId,
    'age': age,
    'gender': gender,
    'conditions': conditions,
    'activityLevel': activityLevel,
    'pollutionSensitivity': pollutionSensitivity,
    'createdAt': createdAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  factory HealthProfile.fromJson(Map<String, dynamic> json) => HealthProfile(
    userId: json['userId'] ?? '',
    age: json['age'] ?? 0,
    gender: json['gender'] ?? '',
    conditions: List<String>.from(json['conditions'] ?? []),
    activityLevel: json['activityLevel'] ?? '',
    pollutionSensitivity: json['pollutionSensitivity'] ?? '',
    createdAt: json['createdAt'] != null ? DateTime.parse(json['createdAt']) : DateTime.now(),
    updatedAt: json['updatedAt'] != null ? DateTime.parse(json['updatedAt']) : DateTime.now(),
  );

  HealthProfile copyWith({
    String? userId,
    int? age,
    String? gender,
    List<String>? conditions,
    String? activityLevel,
    String? pollutionSensitivity,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) => HealthProfile(
    userId: userId ?? this.userId,
    age: age ?? this.age,
    gender: gender ?? this.gender,
    conditions: conditions ?? this.conditions,
    activityLevel: activityLevel ?? this.activityLevel,
    pollutionSensitivity: pollutionSensitivity ?? this.pollutionSensitivity,
    createdAt: createdAt ?? this.createdAt,
    updatedAt: updatedAt ?? this.updatedAt,
  );
}
