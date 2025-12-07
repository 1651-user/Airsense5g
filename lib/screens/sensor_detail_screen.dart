import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:airsense_5g/models/sensor_model.dart';
import 'package:airsense_5g/models/sensor_reading_model.dart';
import 'package:airsense_5g/models/forecast_model.dart';
import 'package:airsense_5g/models/health_profile_model.dart';
import 'package:airsense_5g/services/sensor_service.dart';
import 'package:airsense_5g/services/forecast_service.dart';
import 'package:airsense_5g/services/auth_service.dart';
import 'package:airsense_5g/services/health_profile_service.dart';
import 'package:airsense_5g/services/alert_service.dart';
import 'package:airsense_5g/theme.dart';
import 'package:intl/intl.dart';

class SensorDetailScreen extends StatefulWidget {
  final Sensor sensor;

  const SensorDetailScreen({super.key, required this.sensor});

  @override
  State<SensorDetailScreen> createState() => _SensorDetailScreenState();
}

class _SensorDetailScreenState extends State<SensorDetailScreen> {
  bool _isLoading = true;
  List<SensorReading> _history = [];
  Forecast? _forecast;
  HealthProfile? _profile;
  String _advice = '';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    final history = await SensorService().getSensorHistory(widget.sensor.id);
    final forecast = await ForecastService().getForecast(widget.sensor.id, widget.sensor.currentData.aqi, widget.sensor.currentData.pm25);
    
    final user = await AuthService().getCurrentUser();
    HealthProfile? profile;
    String advice = 'Check your health profile for personalized advice.';

    if (user != null) {
      profile = await HealthProfileService().getProfile(user.id);
      if (profile != null) {
        advice = AlertService().getHealthAdvice(profile, widget.sensor.currentData.aqi, widget.sensor.currentData.pm25);
      }
    }

    if (mounted) {
      setState(() {
        _history = history;
        _forecast = forecast;
        _profile = profile;
        _advice = advice;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final aqi = widget.sensor.currentData.aqi;
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

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.sensor.name, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
        leading: IconButton(icon: Icon(Icons.arrow_back, color: Theme.of(context).colorScheme.onSurface), onPressed: () => Navigator.of(context).pop()),
      ),
      body: _isLoading ? Center(child: CircularProgressIndicator(color: Theme.of(context).colorScheme.primary)) : SingleChildScrollView(
        padding: AppSpacing.paddingLg,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: AppSpacing.paddingLg,
              decoration: BoxDecoration(color: aqiColor.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(AppRadius.lg), border: Border.all(color: aqiColor)),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Current AQI', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
                          const SizedBox(height: 4),
                          Text(aqi.toString(), style: Theme.of(context).textTheme.displayMedium?.copyWith(color: aqiColor, fontWeight: FontWeight.bold)),
                          Text(SensorService().getAQICategory(aqi), style: Theme.of(context).textTheme.titleMedium?.copyWith(color: aqiColor)),
                        ],
                      ),
                      Icon(Icons.location_on, color: aqiColor, size: 48),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(widget.sensor.location, style: Theme.of(context).textTheme.bodyMedium),
                ],
              ),
            ),
            const SizedBox(height: 24),
            Text('Real-time Values', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: PollutantCard(label: 'PM2.5', value: widget.sensor.currentData.pm25.toStringAsFixed(1), unit: 'µg/m³')),
                const SizedBox(width: 12),
                Expanded(child: PollutantCard(label: 'PM10', value: widget.sensor.currentData.pm10.toStringAsFixed(1), unit: 'µg/m³')),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: PollutantCard(label: 'CO₂', value: widget.sensor.currentData.co2.toStringAsFixed(0), unit: 'ppm')),
                const SizedBox(width: 12),
                Expanded(child: PollutantCard(label: 'O₃', value: widget.sensor.currentData.o3.toStringAsFixed(1), unit: 'ppb')),
              ],
            ),
            const SizedBox(height: 24),
            Text('24-Hour History', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            SizedBox(height: 200, child: HistoryChart(readings: _history)),
            const SizedBox(height: 24),
            if (_forecast != null) ...[
              Text('24-Hour Forecast', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              SizedBox(height: 200, child: ForecastChart(forecast: _forecast!.hourly24)),
              const SizedBox(height: 24),
            ],
            if (_profile != null) ...[
              Text('Personalized Advice', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              Container(
                padding: AppSpacing.paddingMd,
                decoration: BoxDecoration(color: Theme.of(context).colorScheme.primaryContainer, borderRadius: BorderRadius.circular(AppRadius.md)),
                child: Row(
                  children: [
                    Icon(Icons.health_and_safety, color: Theme.of(context).colorScheme.primary),
                    const SizedBox(width: 12),
                    Expanded(child: Text(_advice, style: Theme.of(context).textTheme.bodyMedium)),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class PollutantCard extends StatelessWidget {
  final String label;
  final String value;
  final String unit;

  const PollutantCard({super.key, required this.label, required this.value, required this.unit});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: AppSpacing.paddingMd,
      decoration: BoxDecoration(color: Theme.of(context).colorScheme.surfaceContainerHighest, borderRadius: BorderRadius.circular(AppRadius.md)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.labelMedium?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
          const SizedBox(height: 8),
          Text(value, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
          Text(unit, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
        ],
      ),
    );
  }
}

class HistoryChart extends StatelessWidget {
  final List<SensorReading> readings;

  const HistoryChart({super.key, required this.readings});

  @override
  Widget build(BuildContext context) {
    if (readings.isEmpty) {
      return Center(child: Text('No data available', style: Theme.of(context).textTheme.bodyMedium));
    }

    final spots = readings.asMap().entries.map((e) => FlSpot(e.key.toDouble(), e.value.aqi.toDouble())).toList();

    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true, drawVerticalLine: false, horizontalInterval: 50),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40, getTitlesWidget: (value, meta) => Text(value.toInt().toString(), style: Theme.of(context).textTheme.labelSmall))),
          bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, interval: 6, getTitlesWidget: (value, meta) {
            if (value.toInt() >= 0 && value.toInt() < readings.length) {
              return Text(DateFormat('HH:mm').format(readings[value.toInt()].timestamp), style: Theme.of(context).textTheme.labelSmall);
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
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(show: true, color: LightModeColors.lightPrimary.withValues(alpha: 0.2)),
          ),
        ],
      ),
    );
  }
}

class ForecastChart extends StatelessWidget {
  final List<ForecastPoint> forecast;

  const ForecastChart({super.key, required this.forecast});

  @override
  Widget build(BuildContext context) {
    if (forecast.isEmpty) {
      return Center(child: Text('No forecast available', style: Theme.of(context).textTheme.bodyMedium));
    }

    final spots = forecast.asMap().entries.map((e) => FlSpot(e.key.toDouble(), e.value.aqi.toDouble())).toList();

    return LineChart(
      LineChartData(
        gridData: FlGridData(show: true, drawVerticalLine: false, horizontalInterval: 50),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40, getTitlesWidget: (value, meta) => Text(value.toInt().toString(), style: Theme.of(context).textTheme.labelSmall))),
          bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, interval: 6, getTitlesWidget: (value, meta) {
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
            color: LightModeColors.lightSecondary,
            barWidth: 3,
            dashArray: [5, 5],
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(show: true, color: LightModeColors.lightSecondary.withValues(alpha: 0.2)),
          ),
        ],
      ),
    );
  }
}
