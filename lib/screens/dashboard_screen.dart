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
        tvoc: _sensors.map((s) => s.currentData.tvoc).reduce((a, b) => a + b) /
            count,
        aqi: (_sensors.map((s) => s.currentData.aqi).reduce((a, b) => a + b) /
                count)
            .round(),
        temperature: _sensors
                .map((s) => s.currentData.temperature)
                .reduce((a, b) => a + b) /
            count,
        humidity: _sensors
                .map((s) => s.currentData.humidity)
                .reduce((a, b) => a + b) /
            count,
        pressure: _sensors
                .map((s) => s.currentData.pressure)
                .reduce((a, b) => a + b) /
            count,
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
                    if (_sensors.isNotEmpty) _buildMultiSensorAQI(),
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

  Widget _buildMultiSensorAQI() {
    return Column(
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          physics: const BouncingScrollPhysics(),
          child: Row(
            children: _sensors
                .map((sensor) => _buildCompactAQIGauge(sensor))
                .toList(),
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Last updated: Just now',
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
                fontSize: 14,
              ),
        ),
      ],
    );
  }

  Widget _buildCompactAQIGauge(Sensor sensor) {
    final data = sensor.currentData;
    final aqiColor = _getAQIColor(data.aqi);

    return Container(
      width: 180,
      margin: const EdgeInsets.only(right: 16),
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: Theme.of(context)
            .colorScheme
            .surfaceContainerHighest
            .withOpacity(0.3),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
            color: Theme.of(context).colorScheme.outline.withOpacity(0.1)),
      ),
      child: Column(
        children: [
          Text(
            sensor.name,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 140,
            width: 140,
            child: CustomPaint(
              painter: AQICirclePainter(
                  aqi: data.aqi,
                  isDark: Theme.of(context).brightness == Brightness.dark,
                  strokeWidth: 10.0),
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      _getAQIIcon(data.aqi),
                      size: 24,
                      color: aqiColor,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${data.aqi}',
                      style:
                          Theme.of(context).textTheme.headlineMedium?.copyWith(
                                color: aqiColor,
                                fontWeight: FontWeight.bold,
                                fontSize: 32,
                              ),
                    ),
                    Text(
                      SensorService().getAQICategory(data.aqi).toUpperCase(),
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            color: aqiColor,
                            fontSize: 9,
                            letterSpacing: 1,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
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
                'Pollutant Levels by Sensor',
                style: TextStyle(
                  color: colorScheme.onSurface,
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Display all available sensors with their real labels
          ..._sensors.map((sensor) {
            return _buildSensorSection(sensor);
          }),
        ],
      ),
    );
  }

  Widget _buildSensorSection(Sensor sensor) {
    final colorScheme = Theme.of(context).colorScheme;
    final data = sensor.currentData;

    // Extract the number from the name (e.g., "Sensor 3" -> "3")
    final displayId = sensor.name.replaceAll(RegExp(r'[^0-9]'), '');

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: colorScheme.outline.withOpacity(0.3)),
      ),
      child: Theme(
        data: Theme.of(context).copyWith(
          dividerColor: Colors.transparent,
        ),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          leading: Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: colorScheme.primaryContainer,
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                displayId.isNotEmpty ? displayId : '?',
                style: TextStyle(
                  color: colorScheme.primary,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          title: Text(
            sensor.name,
            style: TextStyle(
              color: colorScheme.onSurface,
              fontSize: 15,
              fontWeight: FontWeight.w600,
            ),
          ),
          subtitle: Text(
            'AQI: ${data.aqi} • ${SensorService().getAQICategory(data.aqi)}',
            style: TextStyle(
              color: _getAQIColor(data.aqi),
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
          children: [
            const SizedBox(height: 8),
            _buildPollutantRow(
                'PM2.5', data.pm25, 'avg', '15.0', 'µg/m³', Colors.red),
            _buildPollutantRow(
                'PM10', data.pm10, 'avg', '45.0', 'µg/m³', Colors.red),
            _buildPollutantRow(
                'TVOC', data.tvoc, 'avg', '100.0', 'ppb', Colors.green),
            _buildPollutantRow(
                'Temp', data.temperature, 'avg', '30.0', '°C', Colors.orange),
            _buildPollutantRow(
                'Humidity', data.humidity, 'avg', '60.0', '%', Colors.blue),
            _buildPollutantRow('Pressure', data.pressure, 'avg', '1013.2',
                'hPa', Colors.purple),
            _buildPollutantRow(
                'CO2', data.co2, 'avg', '400.0', 'ppm', Colors.orange),
          ],
        ),
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
  final double strokeWidth;

  AQICirclePainter({
    required this.aqi,
    required this.isDark,
    this.strokeWidth = 15.0,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;

    // Background Arc
    final bgPaint = Paint()
      ..color = isDark ? const Color(0xFF1F1A2E) : const Color(0xFFF0F0F0)
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
          const Color(0xFFFF2E63),
          const Color(0xFFC2185B),
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
    return oldDelegate.aqi != aqi ||
        oldDelegate.isDark != isDark ||
        oldDelegate.strokeWidth != strokeWidth;
  }
}
