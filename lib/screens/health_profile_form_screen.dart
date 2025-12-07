import 'package:flutter/material.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/services/health_profile_service.dart';
import 'package:airsense_5g/screens/main_nav_screen.dart';
import 'package:airsense_5g/theme.dart';

class HealthProfileFormScreen extends StatefulWidget {
  final String userId;

  const HealthProfileFormScreen({super.key, required this.userId});

  @override
  State<HealthProfileFormScreen> createState() => _HealthProfileFormScreenState();
}

class _HealthProfileFormScreenState extends State<HealthProfileFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _ageController = TextEditingController();
  
  String _selectedGender = 'Male';
  final List<String> _genders = ['Male', 'Female', 'Other'];
  
  final List<String> _selectedConditions = [];
  final List<String> _conditions = ['Asthma', 'Allergies', 'COPD', 'Heart disease', 'Weak immunity', 'Elderly (60+)'];
  
  String _selectedActivity = 'Indoor worker';
  final List<String> _activities = ['Student', 'Indoor worker', 'Outdoor worker', 'Athlete'];
  
  String _selectedSensitivity = 'Medium';
  final List<String> _sensitivities = ['Low', 'Medium', 'High'];
  
  bool _isLoading = false;

  @override
  void dispose() {
    _ageController.dispose();
    super.dispose();
  }

  Future<void> _submitProfile() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final profile = HealthProfile(
      userId: widget.userId,
      age: int.parse(_ageController.text),
      gender: _selectedGender,
      conditions: _selectedConditions,
      activityLevel: _selectedActivity,
      pollutionSensitivity: _selectedSensitivity,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );

    final profileService = HealthProfileService();
    final result = await profileService.createProfile(profile);

    if (!mounted) return;

    setState(() => _isLoading = false);

    if (result['success'] == true) {
      Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const MainNavScreen()));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(result['error'] ?? 'Failed to create profile'), backgroundColor: Theme.of(context).colorScheme.error));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Health Profile', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)), centerTitle: true, automaticallyImplyLeading: false),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: AppSpacing.paddingLg,
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Container(
                  padding: AppSpacing.paddingMd,
                  decoration: BoxDecoration(color: Theme.of(context).colorScheme.primaryContainer, borderRadius: BorderRadius.circular(AppRadius.md)),
                  child: Row(
                    children: [
                      Icon(Icons.info_outline, color: Theme.of(context).colorScheme.primary),
                      const SizedBox(width: 12),
                      Expanded(child: Text('Complete your health profile to receive personalized air quality alerts', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onPrimaryContainer))),
                    ],
                  ),
                ),
                const SizedBox(height: 32),
                Text('Basic Information', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _ageController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    labelText: 'Age',
                    prefixIcon: Icon(Icons.cake_outlined, color: Theme.of(context).colorScheme.primary),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(AppRadius.md)),
                    filled: true,
                    fillColor: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) return 'Please enter your age';
                    final age = int.tryParse(value);
                    if (age == null || age < 1 || age > 120) return 'Please enter a valid age';
                    return null;
                  },
                ),
                const SizedBox(height: 20),
                DropdownButtonFormField<String>(
                  value: _selectedGender,
                  decoration: InputDecoration(
                    labelText: 'Gender',
                    prefixIcon: Icon(Icons.person_outline, color: Theme.of(context).colorScheme.primary),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(AppRadius.md)),
                    filled: true,
                    fillColor: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
                  ),
                  items: _genders.map((gender) => DropdownMenuItem(value: gender, child: Text(gender))).toList(),
                  onChanged: (value) => setState(() => _selectedGender = value!),
                ),
                const SizedBox(height: 32),
                Text('Health Conditions', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text('Select all that apply', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _conditions.map((condition) {
                    final isSelected = _selectedConditions.contains(condition);
                    return FilterChip(
                      label: Text(condition, style: Theme.of(context).textTheme.bodySmall),
                      selected: isSelected,
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            _selectedConditions.add(condition);
                          } else {
                            _selectedConditions.remove(condition);
                          }
                        });
                      },
                      selectedColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.2),
                      checkmarkColor: Theme.of(context).colorScheme.primary,
                      backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                    );
                  }).toList(),
                ),
                const SizedBox(height: 32),
                Text('Activity Level', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _activities.map((activity) {
                    final isSelected = _selectedActivity == activity;
                    return ChoiceChip(
                      label: Text(activity, style: Theme.of(context).textTheme.bodySmall),
                      selected: isSelected,
                      onSelected: (selected) => setState(() => _selectedActivity = activity),
                      selectedColor: Theme.of(context).colorScheme.primary,
                      labelStyle: TextStyle(color: isSelected ? Theme.of(context).colorScheme.onPrimary : Theme.of(context).colorScheme.onSurface),
                      backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                    );
                  }).toList(),
                ),
                const SizedBox(height: 32),
                Text('Pollution Sensitivity', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: _sensitivities.map((sensitivity) {
                    final isSelected = _selectedSensitivity == sensitivity;
                    return ChoiceChip(
                      label: Text(sensitivity, style: Theme.of(context).textTheme.bodySmall),
                      selected: isSelected,
                      onSelected: (selected) => setState(() => _selectedSensitivity = sensitivity),
                      selectedColor: Theme.of(context).colorScheme.primary,
                      labelStyle: TextStyle(color: isSelected ? Theme.of(context).colorScheme.onPrimary : Theme.of(context).colorScheme.onSurface),
                      backgroundColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                    );
                  }).toList(),
                ),
                const SizedBox(height: 40),
                ElevatedButton(
                  onPressed: _isLoading ? null : _submitProfile,
                  style: ElevatedButton.styleFrom(
                    padding: AppSpacing.verticalMd,
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    foregroundColor: Theme.of(context).colorScheme.onPrimary,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.md)),
                    elevation: 0,
                  ),
                  child: _isLoading ? SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Theme.of(context).colorScheme.onPrimary)) : Text('Continue', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Theme.of(context).colorScheme.onPrimary)),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
