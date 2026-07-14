import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/reports_provider.dart';
import 'package:atom_admin/core/widgets/app_error_view.dart';

class ReportListScreen extends ConsumerWidget {
  const ReportListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final reportsAsync = ref.watch(reportListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Reports')),
      body: reportsAsync.when(
        data: (reports) => ListView.builder(
          itemCount: reports.length,
          itemBuilder: (_, i) => ListTile(
            title: Text(reports[i]['report_type']),
            subtitle: Text(reports[i]['description'] ?? 'No description'),
            trailing: Chip(label: Text(reports[i]['status'])),
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppErrorView(error: e, onRetry: () => ref.invalidate(reportListProvider)),
      ),
    );
  }
}
