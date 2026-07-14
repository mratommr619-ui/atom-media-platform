import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/auth_provider.dart';

final pollListProvider = FutureProvider<List<dynamic>>((ref) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/polls/');
  return response.data;
});

final pollActionsProvider = Provider((ref) => PollActions(ref));
class PollActions {
  PollActions(this.ref); final Ref ref;
  Future<void> create(Map<String, dynamic> data) async => ref.read(dioProvider).post('/polls/', data: data);
  Future<void> delete(int id) async => ref.read(dioProvider).delete('/polls/$id');
}
