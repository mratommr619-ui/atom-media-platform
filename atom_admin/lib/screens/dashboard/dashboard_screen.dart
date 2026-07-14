import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/dashboard_provider.dart';
import 'package:atom_admin/core/widgets/app_error_view.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardAsync = ref.watch(dashboardProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: dashboardAsync.when(
        data: (data) => GridView.count(
          crossAxisCount: 4,
          children: [
            _StatCard(label: 'Total Users', value: data['total_users'].toString()),
            _StatCard(label: 'Today Users', value: data['today_users'].toString()),
            _StatCard(label: 'Movies', value: data['total_movies'].toString()),
            _StatCard(label: 'Series', value: data['total_series'].toString()),
            _StatCard(label: 'Episodes', value: data['total_episodes'].toString()),
            _StatCard(label: 'Videos', value: data['total_videos'].toString()),
            _StatCard(label: 'Open Reports', value: data['open_reports'].toString()),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppErrorView(error: e, onRetry: () => ref.invalidate(dashboardProvider)),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  const _StatCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(value, style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text(label, style: Theme.of(context).textTheme.titleSmall),
          ],
        ),
      ),
    );
  }
}

void main() {
  runApp(const ProviderScope(child: DashboardScreen()));
}
