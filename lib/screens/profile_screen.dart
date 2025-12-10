import 'package:flutter/material.dart';
import 'package:airsense_5g/models/user_model.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/services/auth_service.dart';
import 'package:airsense_5g/services/health_profile_service.dart';
import 'package:airsense_5g/screens/login_screen.dart';
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
          title: Text('Profile',
              style: Theme.of(context)
                  .textTheme
                  .titleLarge
                  ?.copyWith(fontWeight: FontWeight.bold)),
          centerTitle: true),
      body: _isLoading
          ? Center(
              child: CircularProgressIndicator(
                  color: Theme.of(context).colorScheme.primary))
          : SingleChildScrollView(
              padding: AppSpacing.paddingLg,
              child: Column(
                children: [
                  GestureDetector(
                    onTap: () => _showImageSourceActionSheet(context),
                    child: Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primaryContainer,
                        shape: BoxShape.circle,
                        image: _profileImagePath != null
                            ? DecorationImage(
                                image: FileImage(File(_profileImagePath!)),
                                fit: BoxFit.cover,
                              )
                            : null,
                      ),
                      child: _profileImagePath == null
                          ? Icon(Icons.person,
                              size: 60,
                              color: Theme.of(context).colorScheme.primary)
                          : null,
                    ),
                  ),
                  if (_profileImagePath == null)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text('Tap to change',
                          style: Theme.of(context)
                              .textTheme
                              .bodySmall
                              ?.copyWith(
                                  color:
                                      Theme.of(context).colorScheme.primary)),
                    ),
                  const SizedBox(height: 16),
                  Text(_user?.name ?? 'User',
                      style: Theme.of(context)
                          .textTheme
                          .headlineSmall
                          ?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text(_user?.email ?? '',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color:
                              Theme.of(context).colorScheme.onSurfaceVariant)),
                  const SizedBox(height: 32),
                  if (_profile != null) ...[
                    Text('Health Profile',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    ProfileInfoCard(
                        label: 'Age', value: _profile!.age.toString()),
                    ProfileInfoCard(label: 'Gender', value: _profile!.gender),
                    ProfileInfoCard(
                        label: 'Activity Level',
                        value: _profile!.activityLevel),
                    ProfileInfoCard(
                        label: 'Pollution Sensitivity',
                        value: _profile!.pollutionSensitivity),
                    if (_profile!.conditions.isNotEmpty)
                      ProfileInfoCard(
                          label: 'Health Conditions',
                          value: _profile!.conditions.join(', ')),
                    const SizedBox(height: 24),
                  ],
                  Text('App Settings',
                      style: Theme.of(context)
                          .textTheme
                          .titleLarge
                          ?.copyWith(fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  SettingsCard(
                      icon: Icons.notifications,
                      label: 'Notifications',
                      onTap: () {}),
                  SettingsCard(
                      icon: Icons.location_on,
                      label: 'Location Settings',
                      onTap: () {}),
                  SettingsCard(
                      icon: Icons.security,
                      label: 'Privacy & Security',
                      onTap: () {}),
                  SettingsCard(
                      icon: Icons.help, label: 'Help & Support', onTap: () {}),
                  SettingsCard(
                      icon: Icons.info,
                      label: 'About AirSense 5G',
                      onTap: () {}),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: _logout,
                    style: ElevatedButton.styleFrom(
                      padding: AppSpacing.verticalMd,
                      backgroundColor: Theme.of(context).colorScheme.error,
                      foregroundColor: Theme.of(context).colorScheme.onError,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(AppRadius.md)),
                      elevation: 0,
                      minimumSize: const Size(double.infinity, 50),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.logout,
                            color: Theme.of(context).colorScheme.onError),
                        const SizedBox(width: 8),
                        Text('Logout',
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium
                                ?.copyWith(
                                    color:
                                        Theme.of(context).colorScheme.onError)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }
}

class ProfileInfoCard extends StatelessWidget {
  final String label;
  final String value;

  const ProfileInfoCard({super.key, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: AppSpacing.paddingMd,
      decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(AppRadius.md)),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant)),
          Flexible(
              child: Text(value,
                  style: Theme.of(context)
                      .textTheme
                      .bodyMedium
                      ?.copyWith(fontWeight: FontWeight.w600),
                  textAlign: TextAlign.end,
                  overflow: TextOverflow.ellipsis)),
        ],
      ),
    );
  }
}

class SettingsCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const SettingsCard(
      {super.key,
      required this.icon,
      required this.label,
      required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(AppRadius.md)),
      child: ListTile(
        leading: Icon(icon, color: Theme.of(context).colorScheme.primary),
        title: Text(label, style: Theme.of(context).textTheme.bodyMedium),
        trailing: Icon(Icons.chevron_right,
            color: Theme.of(context).colorScheme.onSurfaceVariant),
        onTap: onTap,
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppRadius.md)),
      ),
    );
  }
}
