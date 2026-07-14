import 'package:atom_admin/core/widgets/app_error_view.dart';
import 'package:atom_admin/providers/series_detail_provider.dart';
import 'package:atom_admin/providers/series_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class SeriesDetailScreen extends ConsumerWidget {
  final int? id;
  const SeriesDetailScreen({super.key, this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (id == null) {
      return const _SeriesForm();
    }
    final seriesAsync = ref.watch(seriesDetailProvider(id!));
    return seriesAsync.when(
      data: (series) => _SeriesForm(id: id, initial: series),
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(
        appBar: AppBar(title: const Text('Edit Series')),
        body: AppErrorView(error: e, onRetry: () => ref.invalidate(seriesDetailProvider(id!))),
      ),
    );
  }
}

class _SeriesForm extends ConsumerStatefulWidget {
  const _SeriesForm({this.id, this.initial});

  final int? id;
  final Map<String, dynamic>? initial;

  @override
  ConsumerState<_SeriesForm> createState() => _SeriesFormState();
}

class _SeriesFormState extends ConsumerState<_SeriesForm> {
  final _formKey = GlobalKey<FormState>();
  final _title = TextEditingController();
  final _titleMm = TextEditingController();
  final _year = TextEditingController();
  final _country = TextEditingController();
  final _language = TextEditingController();
  final _poster = TextEditingController();
  final _episodeNumber = TextEditingController();
  final _episodeTitle = TextEditingController();
  final _episodeVideoLink = TextEditingController();
  final _episodeQuality = TextEditingController(text: 'HD');
  final _descriptionEn = TextEditingController();
  final _descriptionMm = TextEditingController();
  bool _published = true;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final series = widget.initial;
    if (series != null) {
      _title.text = series['title']?.toString() ?? '';
      _titleMm.text = series['title_mm']?.toString() ?? '';
      _year.text = series['year']?.toString() ?? '';
      _country.text = series['country']?.toString() ?? '';
      _language.text = series['language_original']?.toString() ?? '';
      _poster.text = series['poster']?.toString() ?? '';
      _descriptionEn.text = series['description_en']?.toString() ?? '';
      _descriptionMm.text = series['description_mm']?.toString() ?? '';
      _published = series['is_published'] == true;
    }
  }

  @override
  void dispose() {
    _title.dispose();
    _titleMm.dispose();
    _year.dispose();
    _country.dispose();
    _language.dispose();
    _poster.dispose();
    _episodeNumber.dispose();
    _episodeTitle.dispose();
    _episodeVideoLink.dispose();
    _episodeQuality.dispose();
    _descriptionEn.dispose();
    _descriptionMm.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final editing = widget.id != null;
    return Scaffold(
      appBar: AppBar(
        title: Text(editing ? 'Edit Series' : 'Add Series'),
        actions: [
          if (editing)
            IconButton(
              tooltip: 'Delete series',
              onPressed: _saving ? null : _delete,
              icon: const Icon(Icons.delete_outline),
            ),
          IconButton(
            tooltip: 'Save',
            onPressed: _saving ? null : _save,
            icon: _saving
                ? const SizedBox.square(dimension: 20, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.save),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _title,
              decoration: const InputDecoration(labelText: 'Title', border: OutlineInputBorder()),
              validator: (value) => value == null || value.trim().isEmpty ? 'Title is required' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(controller: _titleMm, decoration: const InputDecoration(labelText: 'Myanmar Title', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: TextFormField(controller: _year, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Year', border: OutlineInputBorder()))),
                const SizedBox(width: 12),
                Expanded(child: TextFormField(controller: _country, decoration: const InputDecoration(labelText: 'Country', border: OutlineInputBorder()))),
              ],
            ),
            const SizedBox(height: 12),
            TextFormField(controller: _language, decoration: const InputDecoration(labelText: 'Original Language', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            TextFormField(controller: _poster, decoration: const InputDecoration(labelText: 'Poster URL', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            TextFormField(controller: _descriptionEn, minLines: 3, maxLines: 5, decoration: const InputDecoration(labelText: 'English Description', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            TextFormField(controller: _descriptionMm, minLines: 3, maxLines: 5, decoration: const InputDecoration(labelText: 'Myanmar Description', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            Text('Episodes', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _episodeNumber,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Episode number', border: OutlineInputBorder()),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _episodeTitle,
                    decoration: const InputDecoration(labelText: 'Episode title', border: OutlineInputBorder()),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _episodeVideoLink,
              decoration: const InputDecoration(
                labelText: 'Episode Telegram video link',
                hintText: 'https://t.me/channel/123 or https://t.me/c/123456/123',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _episodeQuality,
              decoration: const InputDecoration(labelText: 'Episode video quality', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: editing && !_saving ? _addEpisode : null,
              icon: const Icon(Icons.add),
              label: Text(editing ? 'Add this episode' : 'Save series first, then add episodes'),
            ),
            if ((widget.initial?['episodes'] as List?)?.isNotEmpty == true) ...[
              const SizedBox(height: 8),
              Text('Saved episodes', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 6),
              for (final episode in (widget.initial!['episodes'] as List))
                ListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.tv),
                  title: Text('Episode ${episode['episode_number']}: ${episode['title'] ?? ''}'),
                  subtitle: Text('${(episode['videos'] as List?)?.length ?? 0} videos'),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      IconButton(icon: const Icon(Icons.edit_outlined), onPressed: () => _editEpisode((episode as Map).cast<String, dynamic>())),
                      IconButton(icon: const Icon(Icons.delete_outline), onPressed: () => _deleteEpisode((episode['id'] as num).toInt())),
                    ],
                  ),
                ),
            ],
            const SizedBox(height: 12),
            SwitchListTile(
              value: _published,
              onChanged: (value) => setState(() => _published = value),
              title: const Text('Published'),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: _saving ? null : _save,
              icon: const Icon(Icons.save),
              label: Text(editing ? 'Update Series' : 'Create Series'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    final data = {
      'title': _title.text.trim(),
      'title_mm': _emptyToNull(_titleMm.text),
      'year': _intOrNull(_year.text),
      'country': _emptyToNull(_country.text),
      'language_original': _emptyToNull(_language.text),
      'poster': _emptyToNull(_poster.text),
      'description_en': _emptyToNull(_descriptionEn.text),
      'description_mm': _emptyToNull(_descriptionMm.text),
      'is_published': _published,
      'is_archived': false,
    };
    try {
      late final Map<String, dynamic> saved;
      if (widget.id == null) {
        saved = await ref.read(seriesActionsProvider).create(data);
      } else {
        saved = await ref.read(seriesActionsProvider).update(widget.id!, data);
        ref.invalidate(seriesDetailProvider(widget.id!));
      }
      ref.invalidate(seriesListProvider);
      if (widget.id == null && mounted) context.go('/series/${saved['id']}');
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Save failed: $error')));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _addEpisode() async {
    final episodeNumber = _intOrNull(_episodeNumber.text);
    if (episodeNumber == null || widget.id == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter an episode number first.')));
      return;
    }
    setState(() => _saving = true);
    try {
      final episode = await ref.read(seriesActionsProvider).createEpisode({
        'series_id': widget.id,
        'episode_number': episodeNumber,
        'title': _emptyToNull(_episodeTitle.text),
        'description': null,
        'thumbnail': null,
        'is_published': _published,
      });
      final link = _episodeVideoLink.text.trim();
      if (link.isNotEmpty) {
        await ref.read(seriesActionsProvider).importEpisodeVideo(
          episodeId: (episode['id'] as num).toInt(),
          telegramLink: link,
          quality: _episodeQuality.text.trim().isEmpty ? 'HD' : _episodeQuality.text.trim(),
        );
      }
      _episodeNumber.clear();
      _episodeTitle.clear();
      _episodeVideoLink.clear();
      ref.invalidate(seriesDetailProvider(widget.id!));
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Episode save failed: $error')));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _editEpisode(Map<String, dynamic> episode) async {
    final number = TextEditingController(text: episode['episode_number'].toString());
    final title = TextEditingController(text: episode['title']?.toString() ?? '');
    final saved = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit episode'),
        content: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: number, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Episode number')),
          TextField(controller: title, decoration: const InputDecoration(labelText: 'Episode title')),
        ]),
        actions: [TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Save'))],
      ),
    );
    if (saved == true) {
      await ref.read(seriesActionsProvider).updateEpisode((episode['id'] as num).toInt(), {'episode_number': _intOrNull(number.text), 'title': _emptyToNull(title.text)});
      if (widget.id != null) ref.invalidate(seriesDetailProvider(widget.id!));
    }
    number.dispose();
    title.dispose();
  }

  Future<void> _deleteEpisode(int episodeId) async {
    await ref.read(seriesActionsProvider).deleteEpisode(episodeId);
    if (widget.id != null) ref.invalidate(seriesDetailProvider(widget.id!));
  }

  Future<void> _delete() async {
    if (widget.id == null) return;
    await ref.read(seriesActionsProvider).delete(widget.id!);
    ref.invalidate(seriesListProvider);
    if (mounted) context.go('/series');
  }

  String? _emptyToNull(String value) => value.trim().isEmpty ? null : value.trim();

  int? _intOrNull(String value) => int.tryParse(value.trim());
}
