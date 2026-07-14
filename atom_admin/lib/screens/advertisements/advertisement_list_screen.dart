import 'package:atom_admin/providers/advertisements_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AdvertisementListScreen extends ConsumerWidget {
  const AdvertisementListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ads = ref.watch(advertisementsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Advertisements'), actions: [IconButton(icon: const Icon(Icons.add), onPressed: () => _create(context, ref))]),
      body: ads.when(
        data: (items) => ListView.builder(
          itemCount: items.length,
          itemBuilder: (_, index) {
            final ad = (items[index] as Map).cast<String, dynamic>();
            return ListTile(
              leading: ad['media_url']?.toString().isNotEmpty == true ? Image.network(ad['media_url'], width: 48, height: 48, fit: BoxFit.cover, errorBuilder: (_, __, ___) => const Icon(Icons.campaign)) : const Icon(Icons.campaign),
              title: Text(ad['title']?.toString() ?? 'Advertisement'),
              subtitle: Text('${ad['duration']} seconds'),
              trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                Switch(value: ad['is_active'] == true, onChanged: (value) async { await ref.read(advertisementActionsProvider).setActive((ad['id'] as num).toInt(), value); ref.invalidate(advertisementsProvider); }),
                IconButton(icon: const Icon(Icons.delete_outline), onPressed: () async { await ref.read(advertisementActionsProvider).delete((ad['id'] as num).toInt()); ref.invalidate(advertisementsProvider); }),
              ]),
            );
          },
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text('Could not load ads: $error')),
      ),
    );
  }

  Future<void> _create(BuildContext context, WidgetRef ref) async {
    final title = TextEditingController();
    final media = TextEditingController();
    final link = TextEditingController();
    final duration = TextEditingController(text: '15');
    final save = await showDialog<bool>(context: context, builder: (context) => AlertDialog(title: const Text('Add advertisement'), content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [TextField(controller: title, decoration: const InputDecoration(labelText: 'Title')), TextField(controller: media, decoration: const InputDecoration(labelText: 'Image URL')), TextField(controller: link, decoration: const InputDecoration(labelText: 'Click URL')), TextField(controller: duration, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Duration seconds'))])), actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Save'))]));
    if (save == true && title.text.trim().isNotEmpty) {
      await ref.read(advertisementActionsProvider).create({'title': title.text.trim(), 'media_url': media.text.trim().isEmpty ? null : media.text.trim(), 'link': link.text.trim().isEmpty ? null : link.text.trim(), 'duration': int.tryParse(duration.text) ?? 15, 'is_active': true});
      ref.invalidate(advertisementsProvider);
    }
    title.dispose(); media.dispose(); link.dispose(); duration.dispose();
  }
}
