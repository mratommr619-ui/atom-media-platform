import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/movies_provider.dart';
import 'package:atom_admin/core/widgets/app_error_view.dart';
import 'package:go_router/go_router.dart';

class MovieListScreen extends ConsumerWidget {
  const MovieListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final moviesAsync = ref.watch(movieListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Movies'), actions: [
        IconButton(onPressed: () => context.go('/movies/new'), icon: const Icon(Icons.add))
      ]),
      body: moviesAsync.when(
        data: (movies) => ListView.builder(
          itemCount: movies.length,
          itemBuilder: (_, i) {
            final movie = movies[i];
            return ListTile(
              title: Text(movie['title']),
              subtitle: Text(movie['year']?.toString() ?? ''),
              trailing: IconButton(
                icon: const Icon(Icons.edit),
                onPressed: () => context.go('/movies/${movie['id']}'),
              ),
            );
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppErrorView(error: e, onRetry: () => ref.invalidate(movieListProvider)),
      ),
    );
  }
}

void main() {
  runApp(const ProviderScope(child: MovieListScreen()));
}
