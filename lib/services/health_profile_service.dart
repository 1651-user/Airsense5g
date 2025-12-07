import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:airsense_5g/models/health_profile_model.dart';

class HealthProfileService {
  static final HealthProfileService _instance = HealthProfileService._internal();
  factory HealthProfileService() => _instance;
  HealthProfileService._internal();

  Future<Map<String, dynamic>> createProfile(HealthProfile profile) async {
    try {
      await Future.delayed(const Duration(milliseconds: 500));
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('health_profile_${profile.userId}', jsonEncode(profile.toJson()));
      
      debugPrint('✅ Health profile created for user: ${profile.userId}');
      
      return {'success': true, 'profile': profile.toJson()};
    } catch (e) {
      debugPrint('❌ Create profile error: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<HealthProfile?> getProfile(String userId) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final profileStr = prefs.getString('health_profile_$userId');
      
      if (profileStr != null) {
        return HealthProfile.fromJson(jsonDecode(profileStr));
      }
      return null;
    } catch (e) {
      debugPrint('❌ Get profile error: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>> updateProfile(HealthProfile profile) async {
    try {
      await Future.delayed(const Duration(milliseconds: 500));
      
      final updatedProfile = profile.copyWith(updatedAt: DateTime.now());
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('health_profile_${profile.userId}', jsonEncode(updatedProfile.toJson()));
      
      debugPrint('✅ Health profile updated for user: ${profile.userId}');
      
      return {'success': true, 'profile': updatedProfile.toJson()};
    } catch (e) {
      debugPrint('❌ Update profile error: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<bool> hasProfile(String userId) async {
    final profile = await getProfile(userId);
    return profile != null;
  }
}
