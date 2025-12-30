import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import 'package:airsense_5g/models/chat_message_model.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/services/api_client.dart';

class ChatService {
  static final ChatService _instance = ChatService._internal();
  factory ChatService() => _instance;
  ChatService._internal();

  final _uuid = const Uuid();
  final _apiClient = ApiClient();

  /// Send query to REAL Phi-2 AI backend with sensor context
  Future<ChatMessage> sendQuery(
      String userId, String query, HealthProfile? profile) async {
    try {
      debugPrint('🤖 Sending query to Phi-2 AI: $query');

      // Prepare messages array for the AI
      final messages = [
        {
          'role': 'user',
          'content': query,
        }
      ];

      // Add health profile context if available
      if (profile != null) {
        String profileContext = 'User health profile: ';
        if (profile.conditions.isNotEmpty) {
          profileContext += 'Conditions: ${profile.conditions.join(", ")}. ';
        }
        if (profile.activityLevel.isNotEmpty) {
          profileContext += 'Activity level: ${profile.activityLevel}. ';
        }

        messages.insert(0, {
          'role': 'system',
          'content': profileContext,
        });
      }

      // Call backend chat endpoint
      final response = await _apiClient.post(
        '/api/chat',
        data: {
          'messages': messages,
          'include_context': true, // Include sensor data context
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;

        if (data['status'] == 'success') {
          final aiResponse = data['response'] as String;

          final chatMessage = ChatMessage(
            id: _uuid.v4(),
            userId: userId,
            message: query,
            response: aiResponse,
            timestamp: DateTime.now(),
            isUser: false,
          );

          debugPrint('✅ Received response from Phi-2 AI');
          return chatMessage;
        }
      }

      throw Exception('Failed to get AI response: ${response.statusCode}');
    } catch (e) {
      debugPrint('❌ Chat service error: $e');

      // Fallback response if backend fails
      final fallbackMessage = ChatMessage(
        id: _uuid.v4(),
        userId: userId,
        message: query,
        response:
            'Sorry, I\'m having trouble connecting to the AI service right now. Please make sure the backend server is running at http://192.168.1.147:5000',
        timestamp: DateTime.now(),
        isUser: false,
      );

      return fallbackMessage;
    }
  }

  /// Get chat history (if backend supports it)
  Future<List<ChatMessage>> getChatHistory(String userId) async {
    try {
      // TODO: Implement backend endpoint for chat history
      // For now, return empty list
      return [];
    } catch (e) {
      debugPrint('❌ Get chat history error: $e');
      return [];
    }
  }
}
