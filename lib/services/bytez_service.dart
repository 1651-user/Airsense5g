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
            String processed = output.trim();

            // Loop up to 10 times to peel off layers of {role: ..., content: ...}
            // using strictly index-based string manipulation for reliability.
            int loops = 0;
            while (loops < 10) {
              bool changed = false;

              // Check for the known wrapper format: starts with { and contains role: assistant
              // We check substring(0, 50) to avoid false positives deep in the text if possible,
              // but purely contains matches usage seen.
              if (processed.startsWith('{') &&
                  processed.contains('role: assistant')) {
                // Try to find "content:"
                int contentIndex = processed.indexOf('content:');
                if (contentIndex != -1) {
                  // Extract content after "content:" (8 chars)
                  String candidate =
                      processed.substring(contentIndex + 8).trim();

                  // If the candidate ends with '}', and we started with '{',
                  // it's highly likely this } closes the outer {.
                  if (candidate.endsWith('}')) {
                    candidate =
                        candidate.substring(0, candidate.length - 1).trim();
                  }

                  processed = candidate;
                  changed = true;
                }
              }

              // Also strip surrounding quotes if they exist (residual from JSON)
              if (processed.startsWith('"') &&
                  processed.endsWith('"') &&
                  processed.length > 1) {
                processed = processed.substring(1, processed.length - 1);
                changed = true;
              } else if (processed.startsWith("'") &&
                  processed.endsWith("'") &&
                  processed.length > 1) {
                processed = processed.substring(1, processed.length - 1);
                changed = true;
              }

              if (!changed) break;
              loops++;
            }

            // Final fallback: if "content:" still remains at the very start (e.g. malformed wrapper), try to strip it
            if (processed.startsWith('content:')) {
              processed = processed.substring(8).trim();
            }

            return processed;
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
