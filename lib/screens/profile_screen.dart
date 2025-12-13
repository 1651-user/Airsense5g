import 'package:flutter/material.dart';
import 'package:airsense_5g/models/user_model.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/services/auth_service.dart';
import 'package:airsense_5g/services/health_profile_service.dart';
import 'package:airsense_5g/screens/login_screen.dart';
import 'package:airsense_5g/screens/health_profile_form_screen.dart'; // Import form screen
import 'package:airsense_5g/theme.dart';
import 'package:image_picker/image_picker.dart';
import 'package:image_cropper/image_cropper.dart';
import 'dart:io';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _isLoading = true;
  User? _user;
  HealthProfile? _profile;
  String? _profileImagePath;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    final user = await AuthService().getCurrentUser();
    HealthProfile? profile;
    String? imagePath;

    if (user != null) {
      profile = await HealthProfileService().getProfile(user.id);
      imagePath = await AuthService().getProfileImage(user.id);
    }

    if (mounted) {
      setState(() {
        _user = user;
        _profile = profile;
        _profileImagePath = imagePath;
        _isLoading = false;
      });
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    if (_user == null) return;

    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source);

    if (pickedFile != null) {
      _cropImage(pickedFile.path);
    }
  }

  Future<void> _cropImage(String filePath) async {
    if (_user == null) return;

    final croppedFile = await ImageCropper().cropImage(
      sourcePath: filePath,
      uiSettings: [
        AndroidUiSettings(
          toolbarTitle: 'Edit Profile Picture',
          toolbarColor: Theme.of(context).colorScheme.primary,
          toolbarWidgetColor: Theme.of(context).colorScheme.onPrimary,
          initAspectRatio: CropAspectRatioPreset.square,
          lockAspectRatio: true,
        ),
        IOSUiSettings(
          title: 'Edit Profile Picture',
        ),
      ],
    );

    if (croppedFile != null) {
      final path = croppedFile.path;
      await AuthService().saveProfileImage(_user!.id, path);
      setState(() {
        _profileImagePath = path;
      });
    }
  }

  void _showImageSourceActionSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: Icon(Icons.photo_library,
                  color: Theme.of(context).colorScheme.primary),
              title: const Text('Photo Gallery'),
              onTap: () {
                Navigator.of(context).pop();
                _pickImage(ImageSource.gallery);
              },
            ),
            ListTile(
              leading: Icon(Icons.photo_camera,
                  color: Theme.of(context).colorScheme.primary),
              title: const Text('Camera'),
              onTap: () {
                Navigator.of(context).pop();
                _pickImage(ImageSource.camera);
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _logout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Logout',
            style: Theme.of(context)
                .textTheme
                .titleLarge
                ?.copyWith(fontWeight: FontWeight.bold)),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: Text('Cancel',
                  style: TextStyle(
                      color: Theme.of(context).colorScheme.onSurface))),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: Text('Logout',
                style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await AuthService().logout();
      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
            MaterialPageRoute(builder: (_) => const LoginScreen()),
            (route) => false);
      }
    }
  }

  void _navigateToEditProfile() async {
    if (_user == null) return;

    // Navigate to HealthProfileFormScreen, passing existing profile if any
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => HealthProfileFormScreen(
          userId: _user!.id,
          existingProfile: _profile,
        ),
      ),
    );
    // Reload data when returning
    _loadData();
  }

  @override
  Widget build(BuildContext context) {
    // Determine screen width for responsiveness if needed
    // final screenSize = MediaQuery.of(context).size;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Profile',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontFamily: 'Caveat',
              fontSize: 28), // Using Caveat if available or fallback
          // Note: If Caveat is not loaded, ensure it is added to pubspec or use 'Cursive' fallback
        ),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () {
              // Settings action
            },
          ),
        ],
      ),
      body: _isLoading
          ? Center(
              child: CircularProgressIndicator(
                  color: Theme.of(context).colorScheme.primary))
          : SingleChildScrollView(
              padding: AppSpacing.paddingLg,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Profile Card
                  Container(
                    padding: const EdgeInsets.symmetric(
                        vertical: 32, horizontal: 16),
                    decoration: BoxDecoration(
                      color: const Color(
                          0xFF1E1E2C), // Dark card background like mockup
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.white10),
                    ),
                    child: Column(
                      children: [
                        GestureDetector(
                          onTap: () => _showImageSourceActionSheet(context),
                          child: Stack(
                            children: [
                              Container(
                                width: 100,
                                height: 100,
                                decoration: BoxDecoration(
                                  color: Colors.purple.shade400,
                                  shape: BoxShape.circle,
                                  image: _profileImagePath != null
                                      ? DecorationImage(
                                          image: FileImage(
                                              File(_profileImagePath!)),
                                          fit: BoxFit.cover,
                                        )
                                      : null,
                                ),
                                child: _profileImagePath == null
                                    ? Center(
                                        child: Text(
                                          _user?.name.isNotEmpty == true
                                              ? _user!.name[0].toUpperCase()
                                              : 'A',
                                          style: const TextStyle(
                                            fontSize: 40,
                                            color: Colors.white,
                                            fontWeight: FontWeight.w300,
                                          ),
                                        ),
                                      )
                                    : null,
                              ),
                              Positioned(
                                bottom: 0,
                                right: 0,
                                child: Container(
                                  padding: const EdgeInsets.all(6),
                                  decoration: const BoxDecoration(
                                    color: Color(0xFF2E2E3E), // Darker circle
                                    shape: BoxShape.circle,
                                  ),
                                  child: const Icon(Icons.camera_alt_outlined,
                                      size: 16, color: Colors.white),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          _user?.name ?? 'User',
                          style: Theme.of(context)
                              .textTheme
                              .headlineSmall
                              ?.copyWith(
                                color: Colors.white,
                                fontWeight: FontWeight.w300,
                                fontFamily:
                                    'Caveat', // Trying to match the font style if possible
                                fontSize: 28,
                              ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _user?.email ?? '',
                          style:
                              Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    color: Colors.white54,
                                  ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Health Profile Section
                  Text(
                    'Health Profile',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Colors.grey,
                          fontWeight: FontWeight.w400,
                        ),
                  ),
                  const SizedBox(height: 12),

                  Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E1E2C),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.white10),
                    ),
                    child: Column(
                      children: [
                        _buildProfileRow(
                          context,
                          icon: Icons.cake,
                          label: 'Age',
                          value: _profile != null
                              ? '${_profile!.age} years'
                              : '--',
                          iconColor: Colors.purple.shade300,
                        ),
                        const Divider(
                            height: 1,
                            color: Colors.white10,
                            indent: 16,
                            endIndent: 16),
                        _buildProfileRow(
                          context,
                          icon: Icons.wc, // Gender icon
                          label: 'Gender',
                          value: _profile?.gender ?? '--',
                          iconColor: Colors.purple.shade300,
                        ),
                        const Divider(
                            height: 1,
                            color: Colors.white10,
                            indent: 16,
                            endIndent: 16),
                        _buildProfileRow(
                          context,
                          icon: Icons.favorite,
                          label: 'Activity Level',
                          value: _profile?.activityLevel ?? '--',
                          iconColor: Colors.purple.shade300,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Edit Health Profile Button
                  ElevatedButton.icon(
                    onPressed: _navigateToEditProfile,
                    icon: const Icon(Icons.edit, size: 18),
                    label: const Text('Edit Health Profile'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor:
                          const Color(0xFF8B5CF6), // Example Custom Purple
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      elevation: 0,
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Logout Button
                  OutlinedButton.icon(
                    onPressed: _logout,
                    icon: const Icon(Icons.logout, size: 18),
                    label: const Text('Logout'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red.shade400, // Text color
                      side: BorderSide(color: Colors.white10), // Border color
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(16),
                      ),
                      backgroundColor: const Color(0xFF1E1E2C), // Dark bg
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildProfileRow(BuildContext context,
      {required IconData icon,
      required String label,
      required String value,
      required Color iconColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      child: Row(
        children: [
          Icon(icon, color: iconColor, size: 24),
          const SizedBox(width: 16),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w400,
              ),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 16,
              fontWeight: FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }
}
