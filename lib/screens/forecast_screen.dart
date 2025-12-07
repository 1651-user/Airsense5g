import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:airsense_5g/models/sensor_model.dart';
import 'package:airsense_5g/models/forecast_model.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/services/sensor_service.dart';
import 'package:airsense_5g/services/forecast_service.dart';
import 'package:airsense_5g/services/auth_service.dart';
import 'package:airsense_5g/services/health_profile_service.dart';
import 'package:airsense_5g/services/alert_service.dart';
import 'package:airsense_5g/theme.dart';
import 'package:intl/intl.dart';

class ForecastScreen extends StatefulWidget {
  const ForecastScreen({super.key});

  @override
  State<ForecastScreen> createState() => _ForecastScreenState();
}

class _ForecastScreenState extends State<ForecastScreen> {
  bool _isLoading = true;
  List<Sensor> _sensors = [];
  Forecast? _forecast;
  HealthProfile? _profile;
  Sensor? _selectedSensor;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    final sensors = await SensorService().getAllSensors();
    final user = await AuthService().getCurrentUser();
    HealthProfile? profile;

    if (user != null) {
      profile = await HealthProfileService().getProfile(user.id);
    }

    Forecast? forecast;
    Sensor? selectedSensor;

    if (sensors.isNotEmpty) {
      selectedSensor = sensors.first;
      forecast = await ForecastService().getForecast(selectedSensor.id, selectedSensor.currentData.aqi, selectedSensor.currentData.pm25);
    }

    if (mounted) {
      setState(() {
        _sensors = sensors;
        _selectedSensor = selectedSensor;
        _forecast = forecast;
        _profile = profile;
        _isLoading = false;
      });
    }
  }

  Future<void> _changeSensor(Sensor sensor) async {
    setState(() => _isLoading = true);
    
    final forecast = await ForecastService().getForecast(sensor.id, sensor.currentData.aqi, sensor.currentData.pm25);
    
    if (mounted) {
      setState(() {
        _selectedSensor = sensor;
        _forecast = forecast;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Forecast & Analytics', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)), centerTitle: true),
      body: _isLoading ? Center(child: CircularProgressIndicator(color: Theme.of(context).colorScheme.primary)) : SingleChildScrollView(
        padding: AppSpacing.paddingLg,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Select Location', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Container(
              padding: AppSpacing.paddingMd,
              decoration: BoxDecoration(color: Theme.of(context).colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(AppRadius.md)),
              child: DropdownButton<Sensor>(
                value: _selectedSensor,
                isExpanded: true,
                underline: const SizedBox.shrink(),
                items: _sensors.map((sensor) => DropdownMenuItem(value: sensor, child: Text(sensor.name))).toList(),
                onChanged: (sensor) {
                  if (sensor != null) _changeSensor(sensor);
                },
              ),
            ),
            if (_selectedSensor != null) ...[
              const SizedBox(height: 32),
              Text('24-Hour Forecast', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              SizedBox(height: 250, child: _forecast != null ? Hourly24Chart(forecast: _forecast!.hourly24) : const Center(child: Text('No forecast available'))),
              const SizedBox(height: 32),
              Text('Weekly Trend', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              SizedBox(height: 250, child: _forecast != null ? WeeklyChart(forecast: _forecast!.weekly) : const Center(child: Text('No forecast available'))),
              const SizedBox(height: 32),
              if (_profile != null && _forecast != null) ...[
                Text('What This Means for You', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                PersonalizedForecastAdvice(profile: _profile!, forecast: _forecast!),
              ],
            ],
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class Hourly24Chart extends StatelessWidget {
  final List<ForecastPoint> forecast;

  const Hourly24Chart({super.key, required this.forecast});

  @override
  Widget build(BuildContext context) {
    if (forecast.isEmpty) {
      return Center(child: Text('No data available', style: Theme.of(context).textTheme.bodyMedium));
    }

    final spots = forecast.asMap().entries.map((e) => FlSpot(e.key.toDouble(), e.value.aqi.toDouble())).toList();

    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true, drawVerticalLine: false, horizontalInterval: 50),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40, getTitlesWidget: (value, meta) => Text(value.toInt().toString(), style: Theme.of(context).textTheme.labelSmall))),
          bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, interval: 4, getTitlesWidget: (value, meta) {
            if (value.toInt() >= 0 && value.toInt() < forecast.length) {
              return Text(DateFormat('HH:mm').format(forecast[value.toInt()].timestamp), style: Theme.of(context).textTheme.labelSmall);
            }
            return const SizedBox.shrink();
          })),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: LightModeColors.lightPrimary,
            barWidth: 3,
            dotData: const FlDotData(show: true),
            belowBarData: BarAreaData(show: true, color: LightModeColors.lightPrimary.withValues(alpha: 0.2)),
          ),
        ],
      ),
    );
  }
}

class WeeklyChart extends StatelessWidget {
  final List<ForecastPoint> forecast;

  const WeeklyChart({super.key, required this.forecast});

  @override
  Widget build(BuildContext context) {
    if (forecast.isEmpty) {
      return Center(child: Text('No data available', style: Theme.of(context).textTheme.bodyMedium));
    }

    final barGroups = forecast.asMap().entries.map((e) {
      final aqi = e.value.aqi;
      Color barColor;
      if (aqi <= 50) {
        barColor = LightModeColors.aqiGood;
      } else if (aqi <= 100) {
        barColor = LightModeColors.aqiModerate;
      } else if (aqi <= 150) {
        barColor = LightModeColors.aqiUnhealthy;
      } else {
        barColor = LightModeColors.aqiHazardous;
      }

      return BarChartGroupData(x: e.key, barRods: [BarChartRodData(toY: aqi.toDouble(), color: barColor, width: 24, borderRadius: const BorderRadius.vertical(top: Radius.circular(4)))]);
    }).toList();

    return BarChart(
      BarChartData(
        gridData: FlGridData(show: true, drawVerticalLine: false, horizontalInterval: 50),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40, getTitlesWidget: (value, meta) => Text(value.toInt().toString(), style: Theme.of(context).textTheme.labelSmall))),
          bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, getTitlesWidget: (value, meta) {
            if (value.toInt() >= 0 && value.toInt() < forecast.length) {
              return Text(DateFormat('EEE').format(forecast[value.toInt()].timestamp), style: Theme.of(context).textTheme.labelSmall);
            }
            return const SizedBox.shrink();
          })),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        borderData: FlBorderData(show: false),
        barGroups: barGroups,
      ),
    );
  }
}

class PersonalizedForecastAdvice extends StatelessWidget {
  final HealthProfile profile;
  final Forecast forecast;

  const PersonalizedForecastAdvice({super.key, required this.profile, required this.forecast});

  @override
  Widget build(BuildContext context) {
    final maxAQI = forecast.hourly24.map((f) => f.aqi).reduce((a, b) => a > b ? a : b);
    final maxPM25 = forecast.hourly24.map((f) => f.pm25).reduce((a, b) => a > b ? a : b);

    final advice = AlertService().getHealthAdvice(profile, maxAQI, maxPM25);

    return Container(
      padding: AppSpacing.paddingLg,
      decoration: BoxDecoration(color: Theme.of(context).colorScheme.primaryContainer, borderRadius: BorderRadius.circular(AppRadius.lg)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.lightbulb, color: Theme.of(context).colorScheme.primary, size: 28),
              const SizedBox(width: 12),
              Expanded(child: Text('Personalized Forecast Insight', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: Theme.of(context).colorScheme.onPrimaryContainer))),
            ],
          ),
          const SizedBox(height: 12),
          Text(advice, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onPrimaryContainer)),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Container(
                  padding: AppSpacing.paddingSm,
                  decoration: BoxDecoration(color: Theme.of(context).colorScheme.surface.withValues(alpha: 0.5), borderRadius: BorderRadius.circular(AppRadius.sm)),
                  child: Column(
                    children: [
                      Text('Peak AQI', style: Theme.of(context).textTheme.labelSmall),
                      const SizedBox(height: 4),
                      Text(maxAQI.toString(), style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Container(
                  padding: AppSpacing.paddingSm,
                  decoration: BoxDecoration(color: Theme.of(context).colorScheme.surface.withValues(alpha: 0.5), borderRadius: BorderRadius.circular(AppRadius.sm)),
                  child: Column(
                    children: [
                      Text('Peak PM2.5', style: Theme.of(context).textTheme.labelSmall),
                      const SizedBox(height: 4),
                      Text(maxPM25.toStringAsFixed(1), style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
