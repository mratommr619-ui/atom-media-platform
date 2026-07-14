import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/auth_provider.dart';

final seriesDetailProvider = FutureProvider.family<Map<String, dynamic>, int>((ref, id) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/series/$id');
  return response.data;
});

final seriesActionsProvider = Provider<SeriesActions>((ref) => SeriesActions(ref));

class SeriesActions {
  SeriesActions(this.ref);

  final Ref ref;

  Future<Map<String, dynamic>> create(Map<String, dynamic> data) async {
    final response = await ref.read(dioProvider).post('/series/', data: data);
    return (response.data as Map).cast<String, dynamic>();
  }

  Future<Map<String, dynamic>> update(int id, Map<String, dynamic> data) async {
    final response = await ref.read(dioProvider).put('/series/$id', data: data);
    return (response.data as Map).cast<String, dynamic>();
  }

  Future<Map<String, dynamic>> createEpisode(Map<String, dynamic> data) async {
    final response = await ref.read(dioProvider).post('/episodes/', data: data);
    return (response.data as Map).cast<String, dynamic>();
  }

  Future<Map<String, dynamic>> updateEpisode(int episodeId, Map<String, dynamic> data) async {
    final response = await ref.read(dioProvider).put('/episodes/$episodeId', data: data);
    return (response.data as Map).cast<String, dynamic>();
  }

  Future<void> deleteEpisode(int episodeId) async {
    await ref.read(dioProvider).delete('/episodes/$episodeId');
  }

  Future<void> delete(int id) async {
    await ref.read(dioProvider).delete('/series/$id');
  }

  Future<Map<String, dynamic>> importEpisodeVideo({
    required int episodeId,
    required String telegramLink,
    required String quality,
  }) async {
    final response = await ref.read(dioProvider).post('/import/telegram', data: {
      'episode_id': episodeId,
      'telegram_link': telegramLink,
      'quality': quality,
    });
    return (response.data as Map).cast<String, dynamic>();
  }
}
