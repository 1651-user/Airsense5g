import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/services/health_profile_service.dart';
import 'package:airsense_5g/models/user_model.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal() {
    _seedDummyUser();
  }

  final _uuid = const Uuid();

  Future<void> _seedDummyUser() async {
    final prefs = await SharedPreferences.getInstance();
    final existingUsers = prefs.getStringList('users') ?? [];
    bool exists = false;

    for (final userStr in existingUsers) {
      final user = User.fromJson(jsonDecode(userStr));
      if (user.email == 'sravya@gmail.com') {
        exists = true;
        break;
      }
    }

    if (!exists) {
      final user = User(
        id: 'dummy_user_id',
        name: 'Sravya',
        email: 'sravya@gmail.com',
        createdAt: DateTime.now(),
      );
      existingUsers.add(jsonEncode(user.toJson()));
      await prefs.setStringList('users', existingUsers);
      await prefs.setString('password_sravya@gmail.com', 'HIi@123');
      debugPrint('✅ Dummy user seeded: sravya@gmail.com');

      // Seed dummy health profile
      final healthService = HealthProfileService();
      if (!await healthService.hasProfile(user.id)) {
        final profile = HealthProfile(
          userId: user.id,
          age: 25,
          gender: 'Female',
          activityLevel: 'Moderate',
          pollutionSensitivity: 'Medium',
          conditions: ['Asthma'],
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
        await healthService.createProfile(profile);
        debugPrint('✅ Dummy health profile seeded');
      }
    }
  }

  Future<Map<String, dynamic>> signup(
      String name, String email, String password) async {
    try {
      await Future.delayed(const Duration(milliseconds: 800));

      final normalizedEmail = email.toLowerCase().trim();
      final prefs = await SharedPreferences.getInstance();
      final existingUsers = prefs.getStringList('users') ?? [];

      for (final userStr in existingUsers) {
        final user = User.fromJson(jsonDecode(userStr));
        if (user.email == normalizedEmail) {
          throw Exception('Email already exists');
        }
      }

      final user = User(
        id: _uuid.v4(),
        name: name,
        email: normalizedEmail,
        createdAt: DateTime.now(),
      );

      existingUsers.add(jsonEncode(user.toJson()));
      await prefs.setStringList('users', existingUsers);

      await prefs.setString('password_${user.email}', password);

      final token = _uuid.v4();
      await prefs.setString('jwt_token', token);
      await prefs.setString('current_user_id', user.id);

      debugPrint('✅ User signed up: ${user.email}');

      return {'success': true, 'user': user.toJson(), 'token': token};
    } catch (e) {
      debugPrint('❌ Signup error: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      await Future.delayed(const Duration(milliseconds: 800));

      final normalizedEmail = email.toLowerCase().trim();
      final prefs = await SharedPreferences.getInstance();
      final existingUsers = prefs.getStringList('users') ?? [];

      for (final userStr in existingUsers) {
        final user = User.fromJson(jsonDecode(userStr));
        if (user.email == normalizedEmail) {
          final storedPassword = prefs.getString('password_${user.email}');
          if (storedPassword == password) {
            final token = _uuid.v4();
            await prefs.setString('jwt_token', token);
            await prefs.setString('current_user_id', user.id);

            debugPrint('✅ User logged in: ${user.email}');

            return {'success': true, 'user': user.toJson(), 'token': token};
          } else {
            throw Exception('Invalid password');
          }
        }
      }

      // If specific dummy user is not found, attempt to seed it on-the-fly and retry logic
      if (normalizedEmail == 'sravya@gmail.com' && password == 'HIi@123') {
        debugPrint('⚠️ Dummy user not found, forcing seed...');
        await _seedDummyUser();
        // Recursively call login or manually construct success response
        final seededUsers = prefs.getStringList('users') ?? [];
        for (final userStr in seededUsers) {
          final user = User.fromJson(jsonDecode(userStr));
          if (user.email == normalizedEmail) {
            final token = _uuid.v4();
            await prefs.setString('jwt_token', token);
            await prefs.setString('current_user_id', user.id);
            return {'success': true, 'user': user.toJson(), 'token': token};
          }
        }
      }

      throw Exception('User not found');
    } catch (e) {
      debugPrint('❌ Login error: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('jwt_token');
    return token != null;
  }

  Future<User?> getCurrentUser() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final userId = prefs.getString('current_user_id');
      if (userId == null) return null;

      final existingUsers = prefs.getStringList('users') ?? [];
      for (final userStr in existingUsers) {
        final user = User.fromJson(jsonDecode(userStr));
        if (user.id == userId) {
          return user;
        }
      }
      return null;
    } catch (e) {
      debugPrint('❌ Get current user error: $e');
      return null;
    }
  }

  Future<String?> getProfileImage(String userId) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('profile_image_$userId');
  }

  Future<void> saveProfileImage(String userId, String path) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('profile_image_$userId', path);
    debugPrint('✅ Profile image saved for $userId: $path');
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    await prefs.remove('current_user_id');
    debugPrint('✅ User logged out');
  }
}
