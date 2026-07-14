import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:atom_admin/screens/auth/login_screen.dart';
import 'package:atom_admin/screens/dashboard/dashboard_screen.dart';
import 'package:atom_admin/screens/movies/movie_list_screen.dart';
import 'package:atom_admin/screens/movies/movie_detail_screen.dart';
import 'package:atom_admin/screens/series/series_list_screen.dart';
import 'package:atom_admin/screens/series/series_detail_screen.dart';
import 'package:atom_admin/screens/users/user_list_screen.dart';
import 'package:atom_admin/screens/reports/report_list_screen.dart';
import 'package:atom_admin/screens/broadcast/broadcast_screen.dart';
import 'package:atom_admin/screens/polls/poll_list_screen.dart';
import 'package:atom_admin/screens/devices/admin_devices_screen.dart';
import 'package:atom_admin/screens/advertisements/advertisement_list_screen.dart';
import 'package:atom_admin/screens/more/more_screen.dart';

class AppRouter {
  static final router = GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      ShellRoute(
        builder: (_, __, child) => AdminScaffold(child: child),
        routes: [
          GoRoute(path: '/', builder: (_, __) => const DashboardScreen()),
          GoRoute(path: '/movies', builder: (_, __) => const MovieListScreen()),
          GoRoute(path: '/movies/new', builder: (_, __) => const MovieDetailScreen()),
          GoRoute(path: '/movies/:id', builder: (_, state) => MovieDetailScreen(id: int.parse(state.pathParameters['id']!))),
          GoRoute(path: '/series', builder: (_, __) => const SeriesListScreen()),
          GoRoute(path: '/series/new', builder: (_, __) => const SeriesDetailScreen()),
          GoRoute(path: '/series/:id', builder: (_, state) => SeriesDetailScreen(id: int.parse(state.pathParameters['id']!))),
          GoRoute(path: '/users', builder: (_, __) => const UserListScreen()),
          GoRoute(path: '/reports', builder: (_, __) => const ReportListScreen()),
          GoRoute(path: '/broadcasts', builder: (_, __) => const BroadcastScreen()),
          GoRoute(path: '/polls', builder: (_, __) => const PollListScreen()),
          GoRoute(path: '/devices', builder: (_, __) => const AdminDevicesScreen()),
          GoRoute(path: '/advertisements', builder: (_, __) => const AdvertisementListScreen()),
          GoRoute(path: '/more', builder: (_, __) => const MoreScreen()),
        ],
      ),
    ],
  );
}

class AdminScaffold extends StatelessWidget {
  final Widget child;
  const AdminScaffold({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 720;
    final selectedIndex = _selectedIndex(context);
    if (compact) {
      return Scaffold(
        body: child,
        bottomNavigationBar: NavigationBar(
          selectedIndex: selectedIndex > 4 ? 0 : selectedIndex,
          onDestinationSelected: (index) => _onTap(context, index),
          destinations: const [
            NavigationDestination(icon: Icon(Icons.dashboard), label: 'Dashboard'),
            NavigationDestination(icon: Icon(Icons.movie), label: 'Movies'),
            NavigationDestination(icon: Icon(Icons.tv), label: 'Series'),
            NavigationDestination(icon: Icon(Icons.people), label: 'Users'),
            NavigationDestination(icon: Icon(Icons.more_horiz), label: 'More'),
          ],
        ),
      );
    }
    return Scaffold(
      body: Row(
        children: [
          // Sidebar
          NavigationRail(
            selectedIndex: _selectedIndex(context),
            onDestinationSelected: (index) => _onTap(context, index),
            labelType: NavigationRailLabelType.all,
            destinations: const [
              NavigationRailDestination(icon: Icon(Icons.dashboard), label: Text('Dashboard')),
              NavigationRailDestination(icon: Icon(Icons.movie), label: Text('Movies')),
              NavigationRailDestination(icon: Icon(Icons.tv), label: Text('Series')),
              NavigationRailDestination(icon: Icon(Icons.people), label: Text('Users')),
              NavigationRailDestination(icon: Icon(Icons.report), label: Text('Reports')),
              NavigationRailDestination(icon: Icon(Icons.campaign), label: Text('Broadcasts')),
              NavigationRailDestination(icon: Icon(Icons.poll), label: Text('Polls')),
              NavigationRailDestination(icon: Icon(Icons.devices), label: Text('Devices')),
              NavigationRailDestination(icon: Icon(Icons.campaign_outlined), label: Text('Advertisements')),
            ],
          ),
          Expanded(child: child),
        ],
      ),
    );
  }

  int _selectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    if (location.startsWith('/movies')) return 1;
    if (location.startsWith('/series')) return 2;
    if (location.startsWith('/users')) return 3;
    if (location.startsWith('/reports')) return 4;
    if (location.startsWith('/broadcasts')) return 5;
    if (location.startsWith('/polls')) return 6;
    if (location.startsWith('/devices')) return 7;
    if (location.startsWith('/advertisements')) return 8;
    return 0;
  }

  void _onTap(BuildContext context, int index) {
    if (MediaQuery.sizeOf(context).width < 720 && index == 4) {
      context.go('/more');
      return;
    }
    switch (index) {
      case 0: context.go('/'); break;
      case 1: context.go('/movies'); break;
      case 2: context.go('/series'); break;
      case 3: context.go('/users'); break;
      case 4: context.go('/reports'); break;
      case 5: context.go('/broadcasts'); break;
      case 6: context.go('/polls'); break;
      case 7: context.go('/devices'); break;
      case 8: context.go('/advertisements'); break;
    }
  }
}
