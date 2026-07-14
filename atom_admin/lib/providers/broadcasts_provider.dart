import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/auth_provider.dart';

final broadcastListProvider = FutureProvider<List<dynamic>>((ref) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/broadcasts/');
  return response.data;
});

final broadcastActionsProvider = Provider((ref) => BroadcastActions(ref));
class BroadcastActions {
  BroadcastActions(this.ref); final Ref ref;
  Future<void> create(Map<String, dynamic> data) async => ref.read(dioProvider).post('/broadcasts/', data: data);
  Future<void> delete(int id) async => ref.read(dioProvider).delete('/broadcasts/$id');
}
