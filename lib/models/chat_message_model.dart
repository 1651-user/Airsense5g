class ChatMessage {
  final String id;
  final String userId;
  final String message;
  final String response;
  final DateTime timestamp;
  final bool isUser;

  ChatMessage({
    required this.id,
    required this.userId,
    required this.message,
    required this.response,
    required this.timestamp,
    required this.isUser,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'userId': userId,
    'message': message,
    'response': response,
    'timestamp': timestamp.toIso8601String(),
    'isUser': isUser,
  };

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
    id: json['id'] ?? '',
    userId: json['userId'] ?? '',
    message: json['message'] ?? '',
    response: json['response'] ?? '',
    timestamp: json['timestamp'] != null ? DateTime.parse(json['timestamp']) : DateTime.now(),
    isUser: json['isUser'] ?? false,
  );

  ChatMessage copyWith({
    String? id,
    String? userId,
    String? message,
    String? response,
    DateTime? timestamp,
    bool? isUser,
  }) => ChatMessage(
    id: id ?? this.id,
    userId: userId ?? this.userId,
    message: message ?? this.message,
    response: response ?? this.response,
    timestamp: timestamp ?? this.timestamp,
    isUser: isUser ?? this.isUser,
  );
}
