import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/auth_provider.dart';

final userSearchProvider = StateProvider<String>((ref) => '');

final userListProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final dio = ref.read(dioProvider);
  final search = ref.watch(userSearchProvider);
  final response = await dio.get(
    '/users/',
    queryParameters: {
      if (search.trim().isNotEmpty) 'search': search.trim(),
    },
  );
  return (response.data as List).cast<Map<String, dynamic>>();
});

final userActionsProvider = Provider<UserActions>((ref) {
  return UserActions(ref);
});

class UserActions {
  UserActions(this.ref);

  final Ref ref;

  Future<void> ban(int userId) async => _post('/users/$userId/ban');

  Future<void> unban(int userId) async => _post('/users/$userId/unban');

  Future<void> setAdsDisabled(int userId, bool disabled) async {
    await _post('/users/$userId/ads/${disabled ? 'disable' : 'enable'}');
  }

  Future<void> _post(String path) async {
    await ref.read(dioProvider).post(path);
    ref.invalidate(userListProvider);
  }
}
