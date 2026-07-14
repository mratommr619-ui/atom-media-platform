import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/polls_provider.dart';
import 'package:atom_admin/core/widgets/app_error_view.dart';

class PollListScreen extends ConsumerWidget {
  const PollListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pollsAsync = ref.watch(pollListProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Polls'), actions: [IconButton(icon: const Icon(Icons.add), onPressed: () => _create(context, ref))]),
      body: pollsAsync.when(
        data: (polls) => ListView.builder(
          itemCount: polls.length,
          itemBuilder: (_, i) => ListTile(
            title: Text(polls[i]['question']),
            trailing: Text(polls[i]['is_closed'] ? 'Closed' : 'Open'),
            onLongPress: () async { await ref.read(pollActionsProvider).delete((polls[i]['id'] as num).toInt()); ref.invalidate(pollListProvider); },
          ),
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => AppErrorView(error: e, onRetry: () => ref.invalidate(pollListProvider)),
      ),
    );
  }

  Future<void> _create(BuildContext context, WidgetRef ref) async {
    final question = TextEditingController();
    final options = [TextEditingController(), TextEditingController()];
    final save = await showDialog<bool>(context: context, builder: (dialogContext) => StatefulBuilder(builder: (_, setDialogState) => AlertDialog(title: const Text('New poll'), content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [TextField(controller: question, decoration: const InputDecoration(labelText: 'Question')), const SizedBox(height: 10), for (var index = 0; index < options.length; index++) Row(children: [Expanded(child: TextField(controller: options[index], decoration: InputDecoration(labelText: 'Option ${index + 1}'))), if (options.length > 2) IconButton(icon: const Icon(Icons.remove_circle_outline), onPressed: () => setDialogState(() { options[index].dispose(); options.removeAt(index); }))]), Align(alignment: Alignment.centerLeft, child: TextButton.icon(onPressed: () => setDialogState(() => options.add(TextEditingController())), icon: const Icon(Icons.add), label: const Text('Add option')))])), actions: [TextButton(onPressed: () => Navigator.pop(dialogContext, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, true), child: const Text('Send poll'))])));
    final choices = options.map((item) => item.text.trim()).where((item) => item.isNotEmpty).toList();
    if (save == true && question.text.trim().isNotEmpty && choices.length >= 2) { await ref.read(pollActionsProvider).create({'question': question.text.trim(), 'is_anonymous': true, 'is_multiple_choice': false, 'is_closed': false, 'options': choices.map((text) => {'text': text}).toList()}); ref.invalidate(pollListProvider); }
    question.dispose(); for (final option in options) { option.dispose(); }
  }
}
