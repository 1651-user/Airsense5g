import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

class BytezService {
  final Dio _dio = Dio();

  // Backend server URL - change this to your computer's IP if testing on physical device
  // For emulator: http://10.0.2.2:5000 (Android) or http://localhost:5000 (iOS)
  // For physical device: http://YOUR_COMPUTER_IP:5000
  final String _baseUrl = kIsWeb
      ? 'http://localhost:5000/api'
      : 'http://10.0.2.2:5000/api'; // Android emulator default

  /// Send a message to the local LLaMA model via backend server
  ///
  /// [messages] - List of chat messages in OpenAI format
  /// [includeContext] - Whether to include air quality context (default: true)
  Future<String> sendMessage(
    List<Map<String, String>> messages, {
    bool includeContext = true,
  }) async {
    try {
      final url = '$_baseUrl/chat';

      debugPrint('Sending message to LLaMA via backend: $url');
      debugPrint('Message count: ${messages.length}');

      final response = await _dio.post(
        url,
        options: Options(
          headers: {
            'Content-Type': 'application/json',
          },
          receiveTimeout: const Duration(seconds: 60), // LLaMA can be slow
          sendTimeout: const Duration(seconds: 10),
        ),
        data: {
          'messages': messages,
          'include_context': includeContext,
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;

        if (data is Map && data['status'] == 'success') {
          final responseText =
              data['response']?.toString() ?? "No response content.";
          debugPrint(
              'LLaMA response received: ${responseText.substring(0, responseText.length > 50 ? 50 : responseText.length)}...');
          return responseText;
        }

        // Handle error responses from backend
        if (data is Map && data['error'] != null) {
          final errorMsg = data['error'].toString();
          final details = data['message'] ?? data['details'] ?? '';
          debugPrint('Backend error: $errorMsg - $details');

          if (errorMsg.contains('Cannot connect to LM Studio')) {
            return "⚠️ Cannot connect to LLaMA model. Please ensure LM Studio is running.\n\nDetails: $details";
          } else if (errorMsg.contains('timed out')) {
            return "⏱️ The AI model is taking too long to respond. Please try again with a shorter message.";
          }

          return "Sorry, there was an error: $errorMsg";
        }

        return "Received unexpected response format from server.";
      }

      // Handle HTTP errors
      if (response.statusCode == 503) {
        return "⚠️ LM Studio is not running or not accessible. Please start LM Studio and load a model.";
      } else if (response.statusCode == 504) {
        return "⏱️ Request timed out. The AI model took too long to respond.";
      }

      return "Sorry, I couldn't get a response from the server. (Status: ${response.statusCode})";
    } on DioException catch (e) {
      debugPrint('Dio Error: ${e.type} - ${e.message}');

      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        return "⏱️ Connection timed out. Please check if the backend server is running.";
      } else if (e.type == DioExceptionType.connectionError) {
        return "⚠️ Cannot connect to backend server. Please ensure:\n"
            "1. Backend server is running (python backend/server.py)\n"
            "2. LM Studio is running with a model loaded\n"
            "3. Network connectivity is available";
      }

      return "Error: Unable to connect to AI service. (${e.type})";
    } catch (e) {
      debugPrint('Unexpected error: $e');
      return "Error: An unexpected error occurred. ($e)";
    }
  }

  /// Test connection to backend server
  Future<bool> testConnection() async {
    try {
      final url = _baseUrl.replaceAll('/api', '/health');
      final response = await _dio.get(
        url,
        options: Options(
          receiveTimeout: const Duration(seconds: 5),
        ),
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Backend connection test failed: $e');
      return false;
    }
  }

  /// Test LLaMA model connection via backend
  Future<Map<String, dynamic>> testLLaMA() async {
    try {
      final url = '$_baseUrl/test-llm';
      final response = await _dio.get(url);

      if (response.statusCode == 200) {
        return {
          'connected': true,
          'data': response.data,
        };
      }

      return {
        'connected': false,
        'error': 'Status ${response.statusCode}',
      };
    } catch (e) {
      return {
        'connected': false,
        'error': e.toString(),
      };
    }
  }
}
