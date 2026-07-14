import 'package:atom_admin/providers/auth_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final adminDevicesProvider = FutureProvider<List<Map<String, dynamic>>>((ref) async {
  final response = await ref.read(dioProvider).get('/auth/admin-devices');
  return (response.data as List).cast<Map<String, dynamic>>();
});

final adminDeviceActionsProvider = Provider<AdminDeviceActions>((ref) {
  return AdminDeviceActions(ref);
});

class AdminDeviceActions {
  AdminDeviceActions(this.ref);

  final Ref ref;

  Future<void> approve(String deviceId) async {
    await ref.read(dioProvider).post('/auth/admin-devices/$deviceId/approve');
    ref.invalidate(adminDevicesProvider);
  }
}
