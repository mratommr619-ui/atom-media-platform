import 'package:atom_admin/providers/users_provider.dart';
import 'package:atom_admin/core/widgets/app_error_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class UserListScreen extends ConsumerWidget {
  const UserListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersAsync = ref.watch(userListProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Users'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: () => ref.invalidate(userListProvider),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: usersAsync.when(
        data: (users) => Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              child: TextField(
                decoration: const InputDecoration(
                  hintText: 'Search name or username',
                  prefixIcon: Icon(Icons.search),
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) => ref.read(userSearchProvider.notifier).state = value,
              ),
            ),
            Expanded(
              child: users.isEmpty
                  ? const Center(child: Text('No users found'))
                  : ListView.separated(
                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                      itemCount: users.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (_, i) => _UserTile(user: users[i]),
                    ),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppErrorView(error: e, onRetry: () => ref.invalidate(userListProvider)),
      ),
    );
  }
}

class _UserTile extends ConsumerWidget {
  const _UserTile({required this.user});

  final Map<String, dynamic> user;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final status = user['status']?.toString() ?? 'active';
    final adsDisabled = user['ads_disabled'] == true;
    final fullName = '${user['first_name'] ?? ''} ${user['last_name'] ?? ''}'.trim();
    final username = user['username'] == null ? '' : '@${user['username']}';
    final userId = user['id'] as int;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            CircleAvatar(child: Text(_initial(fullName))),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    spacing: 8,
                    runSpacing: 6,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: [
                      Text(
                        fullName.isEmpty ? 'Unnamed user' : fullName,
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      Chip(label: Text(status), visualDensity: VisualDensity.compact),
                      if (adsDisabled) const Chip(label: Text('Ads off'), visualDensity: VisualDensity.compact),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text('Telegram ID: ${user['telegram_id']}  $username'),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Tooltip(
                  message: adsDisabled ? 'Enable ads for this user' : 'Disable ads for this user',
                  child: Switch(
                    value: adsDisabled,
                    onChanged: (value) => ref.read(userActionsProvider).setAdsDisabled(userId, value),
                  ),
                ),
                PopupMenuButton<String>(
                  tooltip: 'User actions',
                  itemBuilder: (_) => [
                    if (status != 'banned') const PopupMenuItem(value: 'ban', child: Text('Ban')),
                    if (status == 'banned') const PopupMenuItem(value: 'unban', child: Text('Unban')),
                  ],
                  onSelected: (action) {
                    final actions = ref.read(userActionsProvider);
                    if (action == 'ban') actions.ban(userId);
                    if (action == 'unban') actions.unban(userId);
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _initial(String value) {
    final trimmed = value.trim();
    return trimmed.isEmpty ? '?' : trimmed[0].toUpperCase();
  }
}
