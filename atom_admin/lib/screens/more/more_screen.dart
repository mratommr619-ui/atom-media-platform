import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class MoreScreen extends StatelessWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('More')),
    body: ListView(children: [
      ListTile(leading: const Icon(Icons.report_outlined), title: const Text('Reports'), onTap: () => context.go('/reports')),
      ListTile(leading: const Icon(Icons.campaign_outlined), title: const Text('Advertisements'), onTap: () => context.go('/advertisements')),
      ListTile(leading: const Icon(Icons.campaign), title: const Text('Broadcasts'), onTap: () => context.go('/broadcasts')),
      ListTile(leading: const Icon(Icons.poll_outlined), title: const Text('Polls'), onTap: () => context.go('/polls')),
      ListTile(leading: const Icon(Icons.devices_outlined), title: const Text('Admin devices'), onTap: () => context.go('/devices')),
    ]),
  );
}
