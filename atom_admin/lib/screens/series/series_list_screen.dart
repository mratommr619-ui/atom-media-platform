import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/series_provider.dart';
import 'package:atom_admin/core/widgets/app_error_view.dart';
import 'package:go_router/go_router.dart';

class SeriesListScreen extends ConsumerWidget {
  const SeriesListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final seriesAsync = ref.watch(seriesListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Series'), actions: [IconButton(icon: const Icon(Icons.add), onPressed: () => context.go('/series/new'))]),
      body: seriesAsync.when(
        data: (series) => ListView.builder(
          itemCount: series.length,
          itemBuilder: (_, i) => ListTile(
            title: Text(series[i]['title']),
            trailing: IconButton(icon: const Icon(Icons.edit), onPressed: () => context.go('/series/${series[i]['id']}')),
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppErrorView(error: e, onRetry: () => ref.invalidate(seriesListProvider)),
      ),
    );
  }
}

void main() {
  runApp(const ProviderScope(child: SeriesListScreen()));
}
