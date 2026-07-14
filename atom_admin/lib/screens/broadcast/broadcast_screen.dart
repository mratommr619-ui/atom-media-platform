import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/broadcasts_provider.dart';
import 'package:atom_admin/core/widgets/app_error_view.dart';

class BroadcastScreen extends ConsumerWidget {
  const BroadcastScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final broadcastsAsync = ref.watch(broadcastListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Broadcasts'), actions: [IconButton(icon: const Icon(Icons.add), onPressed: () => _create(context, ref))]),
      body: broadcastsAsync.when(
        data: (list) => ListView.builder(
          itemCount: list.length,
          itemBuilder: (_, i) => ListTile(
            title: Text(list[i]['content']),
            subtitle: Text('Status: ${list[i]['status']}\nSent: ${list[i]['sent_count'] ?? 0}  Failed: ${list[i]['failed_count'] ?? 0}  Processed: ${(list[i]['sent_count'] ?? 0) + (list[i]['failed_count'] ?? 0)}'),
            trailing: IconButton(icon: const Icon(Icons.delete_outline), onPressed: () async { await ref.read(broadcastActionsProvider).delete((list[i]['id'] as num).toInt()); ref.invalidate(broadcastListProvider); }),
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppErrorView(error: e, onRetry: () => ref.invalidate(broadcastListProvider)),
      ),
    );
  }

  Future<void> _create(BuildContext context, WidgetRef ref) async {
    final content = TextEditingController();
    final media = TextEditingController();
    String type = 'text';
    final send = await showDialog<bool>(context: context, builder: (dialogContext) => StatefulBuilder(builder: (_, setDialogState) => AlertDialog(title: const Text('New broadcast'), content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [DropdownButtonFormField<String>(initialValue: type, decoration: const InputDecoration(labelText: 'Message type'), items: const [DropdownMenuItem(value: 'text', child: Text('Text')), DropdownMenuItem(value: 'photo', child: Text('Photo')), DropdownMenuItem(value: 'video', child: Text('Video'))], onChanged: (value) => setDialogState(() => type = value!)), const SizedBox(height: 10), TextField(controller: content, minLines: 3, maxLines: 6, decoration: const InputDecoration(labelText: 'Message / caption')), if (type != 'text') ...[const SizedBox(height: 10), TextField(controller: media, decoration: InputDecoration(labelText: type == 'photo' ? 'Photo URL or Telegram file ID' : 'Video URL or Telegram file ID'))]])), actions: [TextButton(onPressed: () => Navigator.pop(dialogContext, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, true), child: const Text('Send'))])));
    if (send == true && content.text.trim().isNotEmpty && (type == 'text' || media.text.trim().isNotEmpty)) { await ref.read(broadcastActionsProvider).create({'type': type, 'content': content.text.trim(), 'media_file_id': type == 'text' ? null : media.text.trim(), 'parse_mode': 'HTML', 'target_all': true}); ref.invalidate(broadcastListProvider); }
    content.dispose();
    media.dispose();
  }
}
