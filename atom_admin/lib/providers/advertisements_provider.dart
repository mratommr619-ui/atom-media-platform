import 'package:atom_admin/providers/auth_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final advertisementsProvider = FutureProvider<List<dynamic>>((ref) async {
  final response = await ref.read(dioProvider).get('/advertisements/');
  return response.data as List<dynamic>;
});

class AdvertisementActions {
  AdvertisementActions(this.ref);
  final Ref ref;

  Future<void> create(Map<String, dynamic> data) async => ref.read(dioProvider).post('/advertisements/', data: data);
  Future<void> delete(int id) async => ref.read(dioProvider).delete('/advertisements/$id');
  Future<void> setActive(int id, bool isActive) async => ref.read(dioProvider).put('/advertisements/$id', data: {'is_active': isActive});
}

final advertisementActionsProvider = Provider((ref) => AdvertisementActions(ref));
