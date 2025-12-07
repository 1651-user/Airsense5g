import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import 'package:airsense_5g/models/user_model.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final _uuid = const Uuid();

  Future<Map<String, dynamic>> signup(String name, String email, String password) async {
    try {
      await Future.delayed(const Duration(milliseconds: 800));
      
      final prefs = await SharedPreferences.getInstance();
      final existingUsers = prefs.getStringList('users') ?? [];
      
      for (final userStr in existingUsers) {
        final user = User.fromJson(jsonDecode(userStr));
        if (user.email == email) {
          throw Exception('Email already exists');
        }
      }

      final user = User(
        id: _uuid.v4(),
        name: name,
        email: email,
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
      
      final prefs = await SharedPreferences.getInstance();
      final existingUsers = prefs.getStringList('users') ?? [];
      
      for (final userStr in existingUsers) {
        final user = User.fromJson(jsonDecode(userStr));
        if (user.email == email) {
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

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    await prefs.remove('current_user_id');
    debugPrint('✅ User logged out');
  }
}
