import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/auth_provider.dart';

final movieDetailProvider = FutureProvider.family<Map<String, dynamic>, int>((ref, id) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/movies/$id');
  return response.data;
});

final movieActionsProvider = Provider<MovieActions>((ref) => MovieActions(ref));

class MovieActions {
  MovieActions(this.ref);

  final Ref ref;

  Future<Map<String, dynamic>> create(Map<String, dynamic> data) async {
    final response = await ref.read(dioProvider).post('/movies/', data: data);
    return (response.data as Map).cast<String, dynamic>();
  }

  Future<Map<String, dynamic>> update(int id, Map<String, dynamic> data) async {
    final response = await ref.read(dioProvider).put('/movies/$id', data: data);
    return (response.data as Map).cast<String, dynamic>();
  }

  Future<void> delete(int id) async {
    await ref.read(dioProvider).delete('/movies/$id');
  }

  Future<Map<String, dynamic>> importVideo({
    required int movieId,
    required String telegramLink,
    required String quality,
  }) async {
    final response = await ref.read(dioProvider).post('/import/telegram', data: {
      'movie_id': movieId,
      'telegram_link': telegramLink,
      'quality': quality,
    });
    return (response.data as Map).cast<String, dynamic>();
  }
}
