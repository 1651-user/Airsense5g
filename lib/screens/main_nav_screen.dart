import 'package:flutter/material.dart';
import 'package:airsense_5g/screens/dashboard_screen.dart';
import 'package:airsense_5g/screens/map_screen.dart';
import 'package:airsense_5g/screens/forecast_screen.dart';
import 'package:airsense_5g/screens/chat_screen.dart';
import 'package:airsense_5g/screens/profile_screen.dart';

class MainNavScreen extends StatefulWidget {
  const MainNavScreen({super.key});

  @override
  State<MainNavScreen> createState() => _MainNavScreenState();
}

class _MainNavScreenState extends State<MainNavScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const DashboardScreen(),
    const MapScreen(),
    const ForecastScreen(),
    const ChatScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        backgroundColor: Theme.of(context).colorScheme.surface,
        indicatorColor: Theme.of(context).colorScheme.primary.withValues(alpha: 0.15),
        height: 70,
        destinations: [
          NavigationDestination(icon: Icon(Icons.dashboard_outlined, color: Theme.of(context).colorScheme.onSurfaceVariant), selectedIcon: Icon(Icons.dashboard, color: Theme.of(context).colorScheme.primary), label: 'Dashboard'),
          NavigationDestination(icon: Icon(Icons.map_outlined, color: Theme.of(context).colorScheme.onSurfaceVariant), selectedIcon: Icon(Icons.map, color: Theme.of(context).colorScheme.primary), label: 'Map'),
          NavigationDestination(icon: Icon(Icons.auto_graph_outlined, color: Theme.of(context).colorScheme.onSurfaceVariant), selectedIcon: Icon(Icons.auto_graph, color: Theme.of(context).colorScheme.primary), label: 'Forecast'),
          NavigationDestination(icon: Icon(Icons.chat_outlined, color: Theme.of(context).colorScheme.onSurfaceVariant), selectedIcon: Icon(Icons.chat, color: Theme.of(context).colorScheme.primary), label: 'Chat'),
          NavigationDestination(icon: Icon(Icons.person_outline, color: Theme.of(context).colorScheme.onSurfaceVariant), selectedIcon: Icon(Icons.person, color: Theme.of(context).colorScheme.primary), label: 'Profile'),
        ],
      ),
    );
  }
}
