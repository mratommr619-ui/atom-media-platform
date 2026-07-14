import 'package:atom_admin/providers/admin_devices_provider.dart';
import 'package:atom_admin/core/widgets/app_error_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AdminDevicesScreen extends ConsumerWidget {
  const AdminDevicesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final devicesAsync = ref.watch(adminDevicesProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Devices'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: () => ref.invalidate(adminDevicesProvider),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: devicesAsync.when(
        data: (devices) {
          if (devices.isEmpty) {
            return const Center(child: Text('No admin devices yet.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: devices.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final device = devices[index];
              final approved = device['approved'] == true;
              final deviceId = device['device_id'] as String;
              return Card(
                child: ListTile(
                  leading: Icon(approved ? Icons.verified_user : Icons.pending_actions),
                  title: Text(device['device_name']?.toString().isNotEmpty == true ? device['device_name'] : 'Unknown device'),
                  subtitle: Text(deviceId),
                  trailing: approved
                      ? const Chip(label: Text('Approved'))
                      : FilledButton.icon(
                          onPressed: () => ref.read(adminDeviceActionsProvider).approve(deviceId),
                          icon: const Icon(Icons.check),
                          label: const Text('Approve'),
                        ),
                ),
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => AppErrorView(error: error, onRetry: () => ref.invalidate(adminDevicesProvider)),
      ),
    );
  }
}
