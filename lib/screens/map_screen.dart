import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:airsense_5g/models/sensor_model.dart';
import 'package:airsense_5g/services/sensor_service.dart';
import 'package:airsense_5g/screens/sensor_detail_screen.dart';
import 'package:airsense_5g/theme.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  GoogleMapController? _mapController;
  bool _isLoading = true;
  List<Sensor> _sensors = [];
  Set<Marker> _markers = {};

  static const CameraPosition _initialPosition = CameraPosition(target: LatLng(37.7749, -122.4194), zoom: 11);

  @override
  void initState() {
    super.initState();
    _loadSensors();
  }

  Future<void> _loadSensors() async {
    setState(() => _isLoading = true);

    final sensors = await SensorService().getAllSensors();
    final markers = <Marker>{};

    for (final sensor in sensors) {
      final aqi = sensor.currentData.aqi;
      BitmapDescriptor markerColor;

      if (aqi <= 50) {
        markerColor = BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen);
      } else if (aqi <= 100) {
        markerColor = BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueOrange);
      } else if (aqi <= 150) {
        markerColor = BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueYellow);
      } else {
        markerColor = BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed);
      }

      markers.add(Marker(
        markerId: MarkerId(sensor.id),
        position: LatLng(sensor.latitude, sensor.longitude),
        icon: markerColor,
        infoWindow: InfoWindow(title: sensor.name, snippet: 'AQI: $aqi - ${SensorService().getAQICategory(aqi)}'),
        onTap: () => _onMarkerTapped(sensor),
      ));
    }

    if (mounted) {
      setState(() {
        _sensors = sensors;
        _markers = markers;
        _isLoading = false;
      });
    }
  }

  void _onMarkerTapped(Sensor sensor) {
    Navigator.of(context).push(MaterialPageRoute(builder: (_) => SensorDetailScreen(sensor: sensor)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: _initialPosition,
            markers: _markers,
            onMapCreated: (controller) => _mapController = controller,
            myLocationButtonEnabled: true,
            zoomControlsEnabled: false,
            mapToolbarEnabled: false,
          ),
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: Container(
                margin: AppSpacing.paddingMd,
                padding: AppSpacing.paddingMd,
                decoration: BoxDecoration(color: Theme.of(context).colorScheme.surface, borderRadius: BorderRadius.circular(AppRadius.lg), boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.1), blurRadius: 10, offset: const Offset(0, 4))]),
                child: Row(
                  children: [
                    Icon(Icons.map, color: Theme.of(context).colorScheme.primary),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Sensor Locations', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                          Text('${_sensors.length} sensors active', style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant)),
                        ],
                      ),
                    ),
                    if (_isLoading) SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Theme.of(context).colorScheme.primary)),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: Container(
                margin: AppSpacing.paddingMd,
                padding: AppSpacing.paddingMd,
                decoration: BoxDecoration(color: Theme.of(context).colorScheme.surface, borderRadius: BorderRadius.circular(AppRadius.lg), boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.1), blurRadius: 10, offset: const Offset(0, -4))]),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text('AQI Legend', style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        LegendItem(color: LightModeColors.aqiGood, label: 'Good'),
                        LegendItem(color: LightModeColors.aqiModerate, label: 'Moderate'),
                        LegendItem(color: LightModeColors.aqiUnhealthy, label: 'Unhealthy'),
                        LegendItem(color: LightModeColors.aqiHazardous, label: 'Hazardous'),
                      ],
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
}

class LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const LegendItem({super.key, required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(width: 16, height: 16, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
        const SizedBox(height: 4),
        Text(label, style: Theme.of(context).textTheme.labelSmall),
      ],
    );
  }
}
