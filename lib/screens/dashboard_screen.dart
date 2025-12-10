import 'package:flutter/material.dart';
import 'package:airsense_5g/models/sensor_model.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/models/alert_model.dart';
import 'package:airsense_5g/services/auth_service.dart';
import 'package:airsense_5g/services/sensor_service.dart';
import 'package:airsense_5g/services/health_profile_service.dart';
import 'package:airsense_5g/services/alert_service.dart';
import 'package:airsense_5g/theme.dart';
import 'package:intl/intl.dart';
import 'dart:math' as math;

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isLoading = true;
  List<Sensor> _sensors = [];
  HealthProfile? _profile;
  List<Alert> _alerts = [];
  String _healthRisk = 'Loading...';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    if (!mounted) return;
    setState(() => _isLoading = true);

    try {
      final user = await AuthService().getCurrentUser();
      if (user == null) return;

      final sensors = await SensorService().getAllSensors();
      final profile = await HealthProfileService().getProfile(user.id);

      List<Alert> alerts = [];
      String healthRisk = 'Unknown';

      if (profile != null) {
        alerts = await AlertService().generateAlerts(user.id, profile, sensors);
        healthRisk = AlertService().getHealthRiskLevel(profile, sensors);
      }

      if (mounted) {
        setState(() {
          _sensors = sensors;
          _profile = profile;
          _alerts = alerts;
          _healthRisk = healthRisk;
          _isLoading = false;
        });
      }
    } catch (e) {
      debugPrint('Error loading dashboard data: $e');
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    // Calculate average sensor data for display (Same logic)
    SensorData? avgData;
    if (_sensors.isNotEmpty) {
      final count = _sensors.length;
      avgData = SensorData(
        pm25: _sensors.map((s) => s.currentData.pm25).reduce((a, b) => a + b) /
            count,
        pm10: _sensors.map((s) => s.currentData.pm10).reduce((a, b) => a + b) /
            count,
        co2: _sensors.map((s) => s.currentData.co2).reduce((a, b) => a + b) /
            count,
        no2: _sensors.map((s) => s.currentData.no2).reduce((a, b) => a + b) /
            count,
        so2: _sensors.map((s) => s.currentData.so2).reduce((a, b) => a + b) /
            count,
        o3: _sensors.map((s) => s.currentData.o3).reduce((a, b) => a + b) /
            count,
        aqi: (_sensors.map((s) => s.currentData.aqi).reduce((a, b) => a + b) /
                count)
            .round(),
        timestamp: DateTime.now(),
      );
    }

    // Access current theme colors
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: colorScheme.surface,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadData,
          color: colorScheme.primary,
          backgroundColor: colorScheme.surfaceContainerHighest,
          child: _isLoading
              ? Center(
                  child: CircularProgressIndicator(color: colorScheme.primary))
              : ListView(
                  padding: AppSpacing.paddingLg,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Air Quality',
                                style: textTheme.headlineMedium
                                    ?.copyWith(fontWeight: FontWeight.bold)),
                            const SizedBox(height: 4),
                            Text(
                              DateFormat('EEEE, MMM d').format(DateTime.now()),
                              style: textTheme.bodyMedium?.copyWith(
                                  color: colorScheme.onSurfaceVariant),
                            ),
                          ],
                        ),
                        Icon(Icons.air, size: 40, color: colorScheme.primary),
                      ],
                    ),
                    const SizedBox(height: 32),
                    if (avgData != null) _buildAQIGauge(avgData),
                    const SizedBox(height: 32),
                    _buildRiskLevelCard(),
                    const SizedBox(height: 20),
                    _buildHealthRecommendations(),
                    const SizedBox(height: 20),
                    if (avgData != null) _buildPollutantLevels(avgData),
                    const SizedBox(height: 20),
                  ],
                ),
        ),
      ),
    );
  }

  Widget _buildAQIGauge(SensorData data) {
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      children: [
        SizedBox(
          height: 250,
          width: 250,
          child: CustomPaint(
            painter: AQICirclePainter(
                aqi: data.aqi,
                isDark: Theme.of(context).brightness == Brightness.dark),
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    _getAQIIcon(data.aqi),
                    size: 48,
                    color: _getAQIColor(data.aqi),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${data.aqi}',
                    style: Theme.of(context).textTheme.displayLarge?.copyWith(
                          color: _getAQIColor(data.aqi),
                          fontSize: 64,
                          fontWeight: FontWeight.w300,
                          fontFamily: 'Roboto',
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    SensorService().getAQICategory(data.aqi).toUpperCase(),
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: _getAQIColor(data.aqi),
                          letterSpacing: 2,
                          fontWeight: FontWeight.w500,
                        ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Last updated: Just now',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: colorScheme.onSurfaceVariant,
                fontSize: 14,
              ),
        ),
      ],
    );
  }

  Widget _buildRiskLevelCard() {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: colorScheme.outline.withOpacity(0.5)),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.shield_outlined, color: colorScheme.primary, size: 20),
              const SizedBox(width: 8),
              Text(
                'Your Risk Level',
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: colorScheme
                  .errorContainer, // Use error container for high risk logic (simplified for now)
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: colorScheme.error.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(Icons.error_outline, color: colorScheme.error, size: 40),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'HIGH',
                        style: TextStyle(
                          color: colorScheme.error,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Based on your asthma condition and current AQI levels',
                        style: TextStyle(
                          color: colorScheme.onSurface
                              .withOpacity(0.8), // Better contrast on dark bg
                          fontSize: 13,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthRecommendations() {
    final colorScheme = Theme.of(context).colorScheme;
    final recommendations = [
      'Avoid outdoor activities.',
      'Wear N95 mask if you must go outside.',
      'Keep windows closed and use air purifier.',
      'Monitor health symptoms closely.',
    ];

    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: colorScheme.outline.withOpacity(0.5)),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb_outline,
                  color: colorScheme.primary, size: 20),
              const SizedBox(width: 8),
              Text(
                'Health Recommendations',
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ...recommendations.asMap().entries.map((entry) {
            final index = entry.key + 1;
            final text = entry.value;
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Row(
                children: [
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: colorScheme.primaryContainer,
                      shape: BoxShape.circle,
                    ),
                    alignment: Alignment.center,
                    child: Text(
                      '$index',
                      style: TextStyle(
                        color: colorScheme.primary,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      text,
                      style: TextStyle(
                        color: colorScheme.onSurfaceVariant,
                        fontSize: 14,
                      ),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildPollutantLevels(SensorData data) {
    final colorScheme = Theme.of(context).colorScheme;

    return Container(
      decoration: BoxDecoration(
        color: colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: colorScheme.outline.withOpacity(0.5)),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.bar_chart, color: colorScheme.primary, size: 20),
              const SizedBox(width: 8),
              Text(
                'Pollutant Levels',
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          _buildPollutantRow(
              'PM2.5', data.pm25, 'avg', '15.0', 'µg/m³', Colors.red),
          _buildPollutantRow(
              'PM10', data.pm10, 'avg', '45.0', 'µg/m³', Colors.red),
          _buildPollutantRow(
              'O3', data.o3, 'avg', '100.0', 'ppb', Colors.green),
          _buildPollutantRow(
              'NO2', data.no2, 'avg', '40.0', 'ppb', Colors.green),
          _buildPollutantRow(
              'SO2', data.so2, 'avg', '40.0', 'ppb', Colors.green),
          _buildPollutantRow('CO', 2.5, 'avg', '4.0', 'ppm', Colors.green),
        ],
      ),
    );
  }

  Widget _buildPollutantRow(String name, double value, String type,
      String limit, String unit, Color color) {
    final colorScheme = Theme.of(context).colorScheme;
    double progress =
        (value / (double.tryParse(limit) ?? 100.0)).clamp(0.0, 1.0);

    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                name,
                style: TextStyle(
                  color: colorScheme.onSurfaceVariant,
                  fontSize: 14,
                ),
              ),
              Text(
                '${value.toStringAsFixed(1)} $unit',
                style: TextStyle(
                  color: color.withOpacity(0.8),
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            height: 8,
            decoration: BoxDecoration(
              color: colorScheme.surfaceContainerHighest
                  .withOpacity(0.5), // Lighter bg for bar
              borderRadius: BorderRadius.circular(4),
            ),
            child: Row(
              children: [
                Expanded(
                  flex: (progress * 100).toInt(),
                  child: Container(
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ),
                Expanded(
                  flex: 100 - (progress * 100).toInt(),
                  child: const SizedBox(),
                ),
              ],
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'WHO Guideline: $limit $unit',
            style: TextStyle(
              color: colorScheme.onSurfaceVariant.withOpacity(0.5),
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  Color _getAQIColor(int aqi) {
    if (aqi <= 50) return const Color(0xFF4CAF50); // Good
    if (aqi <= 100) return const Color(0xFFFFC107); // Moderate
    if (aqi <= 150) return const Color(0xFFFF9800); // Unhealthy for Sensitive
    return const Color(0xFFFF2E63); // Unhealthy/Hazardous (Red/Pink)
  }

  IconData _getAQIIcon(int aqi) {
    if (aqi <= 50) return Icons.sentiment_satisfied_alt;
    if (aqi <= 100) return Icons.sentiment_neutral;
    if (aqi <= 150) return Icons.sentiment_dissatisfied;
    return Icons.sentiment_very_dissatisfied;
  }
}

class AQICirclePainter extends CustomPainter {
  final int aqi;
  final bool isDark;

  AQICirclePainter({required this.aqi, required this.isDark});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;
    const strokeWidth = 15.0;

    // Background Arc
    final bgPaint = Paint()
      ..color = isDark
          ? const Color(0xFF1F1A2E)
          : const Color(0xFFF0F0F0) // Matches card color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius - strokeWidth / 2),
      math.pi * 0.8,
      math.pi * 1.4,
      false,
      bgPaint,
    );

    // Progress Arc (Gradient)
    final progressPaint = Paint()
      ..shader = LinearGradient(
        colors: [
          const Color(0xFFFF2E63), // Red/Pink Accent
          const Color(0xFFC2185B), // Darker Pink/Red
        ],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ).createShader(Rect.fromCircle(center: center, radius: radius))
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final double percentage = (aqi / 300.0).clamp(0.0, 1.0);
    final double sweepAngle = (math.pi * 1.4) * percentage;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius - strokeWidth / 2),
      math.pi * 0.8,
      sweepAngle,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(covariant AQICirclePainter oldDelegate) {
    return oldDelegate.aqi != aqi || oldDelegate.isDark != isDark;
  }
}
