import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

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
          var output = data['output'];

          // Helper to extract content from a dynamic object
          String? extractContent(dynamic item) {
            if (item is Map) {
              return item['content']?.toString() ??
                  item['response']?.toString();
            }
            return null;
          }

          // 1. Handle List
          if (output is List && output.isNotEmpty) {
            // Try to find the last meaningful message
            var lastItem = output.last;
            // Try to extract from Map directly
            var content = extractContent(lastItem);
            if (content != null) return content;

            // If not a map, treats as string
            if (lastItem is String) {
              output = lastItem;
            } else {
              // convert to string and try to parse
              output = lastItem.toString();
            }
          }

          // 2. Handle String (or converted String)
          if (output is String) {
            var trimmed = output.trim();

            // Recursively strip the {role: assistant, content: ...} wrapper
            // The model seems to output nested structures or hallucinations of this format
            // containing nested braces like {role: ... offset by {role: ...
            // We loop to peel off every layer.
            int safetyLoop = 0;
            while (trimmed.startsWith('{') &&
                trimmed.contains('role: assistant') &&
                safetyLoop < 5) {
              final contentIndex = trimmed.indexOf('content:');
              if (contentIndex != -1) {
                // Extract everything after 'content:'
                // We add 8 for 'content:'.length
                var extracted = trimmed.substring(contentIndex + 8).trim();

                // Remove the trailing '}' if it matches the opening '{' for this wrapper
                if (extracted.endsWith('}')) {
                  extracted =
                      extracted.substring(0, extracted.length - 1).trim();
                }
                trimmed = extracted;
              } else {
                // If we see the wrapper start but no content field, break to avoid infinite loop
                break;
              }
              safetyLoop++;
            }

            // Aggressive Regex fallback if plain stripping didn't clean it (e.g. JSON style quotes)
            final jsonMatch =
                RegExp(r'"content":\s*"(.*?)"').firstMatch(trimmed);
            if (jsonMatch != null) {
              return jsonMatch.group(1) ?? trimmed;
            }

            // Fallback for Python-style dicts if they happen to use quotes
            final simpleMatch =
                RegExp(r"content:\s*['\u0022]?(.*?)['\u0022]?(?:,|})")
                    .firstMatch(trimmed);
            if (simpleMatch != null) {
              return simpleMatch.group(1)?.trim() ?? trimmed;
            }

            // If it looks like code/JSON but regex failed, allow it to pass through
            // rather than saying "I don't show", so we can at least see it.
            return trimmed;
          }

          return output?.toString() ?? "Received empty response.";
        }
      }

      return "Sorry, I couldn't get a response from the server. (Status: ${response.statusCode})";
    } catch (e) {
      debugPrint('Bytez API Error: $e');
      return "Error: Unable to connect to AI service. ($e)";
    }
  }
}
