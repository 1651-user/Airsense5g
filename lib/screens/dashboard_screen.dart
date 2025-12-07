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
    setState(() => _isLoading = true);

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
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadData,
          child: _isLoading ? Center(child: CircularProgressIndicator(color: Theme.of(context).colorScheme.primary)) : ListView(
            padding: AppSpacing.paddingLg,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Air Quality', style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text(DateFormat('EEEE, MMM d').format(DateTime.now()), style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
                    ],
                  ),
                  Icon(Icons.air, size: 40, color: Theme.of(context).colorScheme.primary),
                ],
              ),
              const SizedBox(height: 24),
              AQIOverviewCard(sensors: _sensors),
              const SizedBox(height: 20),
              HealthRiskCard(healthRisk: _healthRisk, profile: _profile),
              if (_alerts.isNotEmpty) ...[
                const SizedBox(height: 20),
                PersonalizedAlertCard(alert: _alerts.first),
              ],
              const SizedBox(height: 24),
              Text('Quick Stats', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              QuickStatsGrid(sensors: _sensors),
              const SizedBox(height: 24),
              Text('All Sensors', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              ..._sensors.map((sensor) => SensorListCard(sensor: sensor)),
            ],
          ),
        ),
      ),
    );
  }
}

class AQIOverviewCard extends StatelessWidget {
  final List<Sensor> sensors;

  const AQIOverviewCard({super.key, required this.sensors});

  @override
  Widget build(BuildContext context) {
    if (sensors.isEmpty) {
      return Container(
        padding: AppSpacing.paddingLg,
        decoration: BoxDecoration(color: Theme.of(context).colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(AppRadius.lg)),
        child: Center(child: Text('No sensor data available', style: Theme.of(context).textTheme.bodyMedium)),
      );
    }

    final avgAQI = (sensors.map((s) => s.currentData.aqi).reduce((a, b) => a + b) / sensors.length).round();
    final category = SensorService().getAQICategory(avgAQI);
    
    Color aqiColor;
    if (avgAQI <= 50) {
      aqiColor = LightModeColors.aqiGood;
    } else if (avgAQI <= 100) {
      aqiColor = LightModeColors.aqiModerate;
    } else if (avgAQI <= 150) {
      aqiColor = LightModeColors.aqiUnhealthy;
    } else {
      aqiColor = LightModeColors.aqiHazardous;
    }

    return Container(
      padding: AppSpacing.paddingLg,
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: [aqiColor, aqiColor.withValues(alpha: 0.7)], begin: Alignment.topLeft, end: Alignment.bottomRight),
        borderRadius: BorderRadius.circular(AppRadius.lg),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Current AQI', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.white, fontWeight: FontWeight.w600)),
              Icon(Icons.location_on, color: Colors.white, size: 20),
            ],
          ),
          const SizedBox(height: 20),
          Text(avgAQI.toString(), style: Theme.of(context).textTheme.displayLarge?.copyWith(color: Colors.white, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(category, style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.white)),
          const SizedBox(height: 16),
          Container(
            padding: AppSpacing.paddingSm,
            decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(AppRadius.sm)),
            child: Text('City Average', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}

class HealthRiskCard extends StatelessWidget {
  final String healthRisk;
  final HealthProfile? profile;

  const HealthRiskCard({super.key, required this.healthRisk, this.profile});

  @override
  Widget build(BuildContext context) {
    Color riskColor;
    IconData riskIcon;

    if (healthRisk.contains('High')) {
      riskColor = LightModeColors.aqiHazardous;
      riskIcon = Icons.warning;
    } else if (healthRisk.contains('Moderate')) {
      riskColor = LightModeColors.aqiModerate;
      riskIcon = Icons.info;
    } else {
      riskColor = LightModeColors.aqiGood;
      riskIcon = Icons.check_circle;
    }

    return Container(
      padding: AppSpacing.paddingLg,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: riskColor, width: 2),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: riskColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(AppRadius.md)),
            child: Icon(riskIcon, color: riskColor, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Your Health Risk Today', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
                const SizedBox(height: 4),
                Text(healthRisk, style: Theme.of(context).textTheme.titleLarge?.copyWith(color: riskColor, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class PersonalizedAlertCard extends StatelessWidget {
  final Alert alert;

  const PersonalizedAlertCard({super.key, required this.alert});

  @override
  Widget build(BuildContext context) {
    final isHighSeverity = alert.severity == 'high';
    final alertColor = isHighSeverity ? LightModeColors.aqiHazardous : LightModeColors.aqiModerate;

    return Container(
      padding: AppSpacing.paddingLg,
      decoration: BoxDecoration(color: alertColor.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(AppRadius.lg), border: Border.all(color: alertColor.withValues(alpha: 0.3))),
      child: Row(
        children: [
          Icon(Icons.health_and_safety, color: alertColor, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text('${alert.pollutant} Alert', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: alertColor)),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(color: alertColor, borderRadius: BorderRadius.circular(8)),
                      child: Text(alert.severity.toUpperCase(), style: Theme.of(context).textTheme.labelSmall?.copyWith(color: Colors.white)),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(alert.message, style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class QuickStatsGrid extends StatelessWidget {
  final List<Sensor> sensors;

  const QuickStatsGrid({super.key, required this.sensors});

  @override
  Widget build(BuildContext context) {
    if (sensors.isEmpty) return const SizedBox.shrink();

    final avgPM25 = sensors.map((s) => s.currentData.pm25).reduce((a, b) => a + b) / sensors.length;
    final avgPM10 = sensors.map((s) => s.currentData.pm10).reduce((a, b) => a + b) / sensors.length;
    final avgCO2 = sensors.map((s) => s.currentData.co2).reduce((a, b) => a + b) / sensors.length;

    return Row(
      children: [
        Expanded(child: QuickStatCard(label: 'PM2.5', value: avgPM25.toStringAsFixed(1), unit: 'µg/m³', icon: Icons.grain, color: LightModeColors.lightPrimary)),
        const SizedBox(width: 12),
        Expanded(child: QuickStatCard(label: 'PM10', value: avgPM10.toStringAsFixed(1), unit: 'µg/m³', icon: Icons.blur_on, color: LightModeColors.lightSecondary)),
        const SizedBox(width: 12),
        Expanded(child: QuickStatCard(label: 'CO₂', value: avgCO2.toStringAsFixed(0), unit: 'ppm', icon: Icons.cloud, color: LightModeColors.lightTertiary)),
      ],
    );
  }
}

class QuickStatCard extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final IconData icon;
  final Color color;

  const QuickStatCard({super.key, required this.label, required this.value, required this.unit, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: AppSpacing.paddingMd,
      decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(AppRadius.md)),
      child: Column(
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 8),
          Text(value, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold, color: color)),
          const SizedBox(height: 2),
          Text(unit, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
          const SizedBox(height: 4),
          Text(label, style: Theme.of(context).textTheme.labelSmall?.copyWith(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class SensorListCard extends StatelessWidget {
  final Sensor sensor;

  const SensorListCard({super.key, required this.sensor});

  @override
  Widget build(BuildContext context) {
    final aqi = sensor.currentData.aqi;
    Color aqiColor;
    if (aqi <= 50) {
      aqiColor = LightModeColors.aqiGood;
    } else if (aqi <= 100) {
      aqiColor = LightModeColors.aqiModerate;
    } else if (aqi <= 150) {
      aqiColor = LightModeColors.aqiUnhealthy;
    } else {
      aqiColor = LightModeColors.aqiHazardous;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: AppSpacing.paddingMd,
      decoration: BoxDecoration(color: Theme.of(context).colorScheme.surface, borderRadius: BorderRadius.circular(AppRadius.md), border: Border.all(color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.2))),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(color: aqiColor.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(AppRadius.sm)),
            child: Center(child: Text(aqi.toString(), style: Theme.of(context).textTheme.titleMedium?.copyWith(color: aqiColor, fontWeight: FontWeight.bold))),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(sensor.name, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 2),
                Text(sensor.location, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
              ],
            ),
          ),
          Icon(Icons.chevron_right, color: Theme.of(context).colorScheme.onSurfaceVariant),
        ],
      ),
    );
  }
}
