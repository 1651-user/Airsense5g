import 'dart:convert';
import 'package:dio/dio.dart';

class BytezService {
  final Dio _dio = Dio();
  final String _apiKey = '55d1337983ed4e97d81f98fe807c9cb5';
  final String _modelId = 'Qwen/Qwen3-4B-Instruct-2507';
  final String _baseUrl = 'https://api.bytez.com/models/v2';

  Future<String> sendMessage(List<Map<String, String>> messages) async {
    try {
      final url = '$_baseUrl/$_modelId';

      final response = await _dio.post(
        url,
        options: Options(
          headers: {
            'Authorization': 'Key $_apiKey',
            'Content-Type': 'application/json',
          },
        ),
        data: {
          'input': messages,
          'params': {
            'max_new_tokens': 1024,
            'temperature': 0.7,
          }
        },
      );

      if (response.statusCode == 200) {
        final data = response.data;
        if (data is Map && data.containsKey('output')) {
          // The output from Bytez usually comes as a generated string or list depending on model
          // For chat models receiving a list of messages, it typically returns the assistant's reply
          final output = data['output'];
          if (output is String) {
            return output;
          } else if (output is List && output.isNotEmpty) {
            // Check if the list contains maps (which matches the screenshot showing {role: ..., content: ...})
            final lastMessage = output.last;
            if (lastMessage is Map) {
              final content = lastMessage['content'];
              if (content != null) return content.toString();
            } else if (lastMessage is String) {
              // Initial approach fallback
              return lastMessage;
            }
            // Fallback: join if it's a list of strings
            return output.join('\n');
          }
          return output?.toString() ?? "No response";
        }
      }

      return "Sorry, I couldn't get a response from the server.";
    } catch (e) {
      print('Bytez API Error: $e');
      return "Error: Unable to connect to AI service.";
    }
  }
}
