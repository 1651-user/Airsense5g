import 'package:firebase_auth/firebase_auth.dart' as firebase_auth;
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:airsense_5g/models/user_model.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:google_sign_in/google_sign_in.dart';

class AuthService {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  final firebase_auth.FirebaseAuth _auth = firebase_auth.FirebaseAuth.instance;
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Sign up with Email and Password
  Future<Map<String, dynamic>> signup(
      String name, String email, String password) async {
    try {
      final userCredential = await _auth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      final firebaseUser = userCredential.user;
      if (firebaseUser != null) {
        // Create our local User model
        final user = User(
          id: firebaseUser.uid,
          name: name,
          email: email,
          createdAt: DateTime.now(),
        );

        // Store user details in Firestore (Don't await this to prevent UI freezing if DB is slow)
        _firestore
            .collection('users')
            .doc(user.id)
            .set(user.toJson())
            .then((_) {
          debugPrint('✅ User metadata saved to Firestore');
        }).catchError((e) {
          debugPrint('⚠️ Firestore write failed (non-critical): $e');
        });

        // Cache locally
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('current_user_debug', user.id);

        debugPrint('✅ User signed up: ${user.email}');
        return {
          'success': true,
          'user': user.toJson(),
          'token': await firebaseUser.getIdToken()
        };
      }
      return {'success': false, 'error': 'User creation failed'};
    } on firebase_auth.FirebaseAuthException catch (e) {
      debugPrint('❌ Signup error: ${e.message}');
      return {'success': false, 'error': e.message ?? 'Signup failed'};
    } catch (e) {
      debugPrint('❌ Signup error: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  // Login with Email and Password
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final userCredential = await _auth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      final firebaseUser = userCredential.user;
      if (firebaseUser != null) {
        // Fetch user details from Firestore (assumes we saved name during signup)
        // Fetch user details from Firestore with timeout
        DocumentSnapshot<Map<String, dynamic>>? userDoc;
        try {
          userDoc = await _firestore
              .collection('users')
              .doc(firebaseUser.uid)
              .get()
              .timeout(const Duration(seconds: 5));
        } catch (e) {
          debugPrint('⚠️ Firestore read timed out/failed: $e');
          // userDoc remains null, triggering fallback below
        }

        Map<String, dynamic> userData;
        if (userDoc != null && userDoc.exists) {
          userData = userDoc.data()!;
        } else {
          // Fallback if no firestore doc exists
          userData = {
            'id': firebaseUser.uid,
            'name': firebaseUser.displayName ?? email.split('@')[0],
            'email': email,
            'createdAt': DateTime.now().toIso8601String(),
          };
        }

        debugPrint('✅ User logged in: ${firebaseUser.email}');
        return {
          'success': true,
          'user': userData,
          'token': await firebaseUser.getIdToken()
        };
      }
      return {'success': false, 'error': 'Login failed'};
    } on firebase_auth.FirebaseAuthException catch (e) {
      debugPrint('❌ Login error: ${e.message}');
      return {'success': false, 'error': e.message ?? 'Login failed'};
    } catch (e) {
      debugPrint('❌ Login error: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  // Google Sign-In
  Future<Map<String, dynamic>> signInWithGoogle() async {
    try {
      final GoogleSignIn googleSignIn = GoogleSignIn(
        clientId: kIsWeb
            ? '404670781078-8j9m0lg0957unch7ktsf1dkqe52cuth0.apps.googleusercontent.com'
            : null,
      );
      final GoogleSignInAccount? googleUser = await googleSignIn.signIn();
      if (googleUser == null) {
        return {'success': false, 'error': 'Google sign in cancelled'};
      }

      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;
      final firebase_auth.OAuthCredential credential =
          firebase_auth.GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      final firebase_auth.UserCredential userCredential =
          await _auth.signInWithCredential(credential);
      final firebaseUser = userCredential.user;

      if (firebaseUser != null) {
        // Fetch or create user in Firestore
        DocumentSnapshot<Map<String, dynamic>>? userDoc;
        try {
          userDoc = await _firestore
              .collection('users')
              .doc(firebaseUser.uid)
              .get()
              .timeout(const Duration(seconds: 3));
        } catch (e) {
          debugPrint('⚠️ Firestore read timed out/failed: $e');
        }

        if (userDoc == null || !userDoc.exists) {
          final user = User(
            id: firebaseUser.uid,
            name: firebaseUser.displayName ?? 'User',
            email: firebaseUser.email ?? '',
            createdAt: DateTime.now(),
          );

          // Fire and forget save
          _firestore
              .collection('users')
              .doc(user.id)
              .set(user.toJson())
              .onError((e, _) =>
                  debugPrint('⚠️ Firestore write failed (non-critical): $e'));
        }

        // Cache details
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('current_user_debug', firebaseUser.uid);

        return {
          'success': true,
          'user': {
            'id': firebaseUser.uid,
            'name': firebaseUser.displayName,
            'email': firebaseUser.email
          },
          'token': await firebaseUser.getIdToken()
        };
      }
      return {'success': false, 'error': 'Google sign in failed'};
    } catch (e) {
      debugPrint('❌ Google sign in error: $e');
      return {'success': false, 'error': e.toString()};
    }
  }

  // Check if logged in
  Future<bool> isLoggedIn() async {
    return _auth.currentUser != null;
  }

  // Get Current User
  Future<User?> getCurrentUser() async {
    final firebaseUser = _auth.currentUser;
    if (firebaseUser == null) return null;

    try {
      final userDoc = await _firestore
          .collection('users')
          .doc(firebaseUser.uid)
          .get()
          .timeout(const Duration(seconds: 3));
      if (userDoc.exists) {
        return User.fromJson(userDoc.data()!);
      }
      // Fallback
      return User(
        id: firebaseUser.uid,
        name: firebaseUser.displayName ??
            firebaseUser.email?.split('@')[0] ??
            'User',
        email: firebaseUser.email ?? '',
        createdAt: DateTime.now(), // Approximate
      );
    } catch (e) {
      debugPrint('❌ Get current user error: $e');
      return User(
        id: firebaseUser.uid,
        name: 'User',
        email: firebaseUser.email ?? '',
        createdAt: DateTime.now(),
      );
    }
  }

  // Logout
  Future<void> logout() async {
    await _auth.signOut();
    try {
      final GoogleSignIn googleSignIn = GoogleSignIn(
        clientId: kIsWeb
            ? '404670781078-8j9m0lg0957unch7ktsf1dkqe52cuth0.apps.googleusercontent.com'
            : null,
      );
      if (await googleSignIn.isSignedIn()) {
        await googleSignIn.signOut();
      }
    } catch (e) {
      debugPrint('⚠️ Google sign out failed/not needed: $e');
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
    debugPrint('✅ User logged out');
  }

  // --- Profile Image Helpers (Persisting to SharedPreferences for simplicity, or could use Storage) ---
  Future<String?> getProfileImage(String userId) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('profile_image_$userId');
  }

  Future<void> saveProfileImage(String userId, String path) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('profile_image_$userId', path);
  }
}
