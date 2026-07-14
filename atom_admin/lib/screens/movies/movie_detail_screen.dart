import 'package:atom_admin/core/widgets/app_error_view.dart';
import 'package:atom_admin/providers/movie_detail_provider.dart';
import 'package:atom_admin/providers/movies_provider.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

class MovieDetailScreen extends ConsumerWidget {
  final int? id;
  const MovieDetailScreen({super.key, this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (id == null) {
      return const _MovieForm();
    }
    final movieAsync = ref.watch(movieDetailProvider(id!));
    return movieAsync.when(
      data: (movie) => _MovieForm(id: id, initial: movie),
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(
        appBar: AppBar(title: const Text('Edit Movie')),
        body: AppErrorView(error: e, onRetry: () => ref.invalidate(movieDetailProvider(id!))),
      ),
    );
  }
}

class _MovieForm extends ConsumerStatefulWidget {
  const _MovieForm({this.id, this.initial});

  final int? id;
  final Map<String, dynamic>? initial;

  @override
  ConsumerState<_MovieForm> createState() => _MovieFormState();
}

class _MovieFormState extends ConsumerState<_MovieForm> {
  final _formKey = GlobalKey<FormState>();
  final _title = TextEditingController();
  final _titleMm = TextEditingController();
  final _year = TextEditingController();
  final _country = TextEditingController();
  final _language = TextEditingController();
  final _duration = TextEditingController();
  final _thumbnail = TextEditingController();
  final _videoLink = TextEditingController();
  final _videoQuality = TextEditingController(text: 'HD');
  final _descriptionEn = TextEditingController();
  final _descriptionMm = TextEditingController();
  bool _published = true;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final movie = widget.initial;
    if (movie != null) {
      _title.text = movie['title']?.toString() ?? '';
      _titleMm.text = movie['title_mm']?.toString() ?? '';
      _year.text = movie['year']?.toString() ?? '';
      _country.text = movie['country']?.toString() ?? '';
      _language.text = movie['language_original']?.toString() ?? '';
      _duration.text = movie['duration']?.toString() ?? '';
      _thumbnail.text = movie['thumbnail']?.toString() ?? '';
      _descriptionEn.text = movie['description_en']?.toString() ?? '';
      _descriptionMm.text = movie['description_mm']?.toString() ?? '';
      _published = movie['is_published'] == true;
    }
  }

  @override
  void dispose() {
    _title.dispose();
    _titleMm.dispose();
    _year.dispose();
    _country.dispose();
    _language.dispose();
    _duration.dispose();
    _thumbnail.dispose();
    _videoLink.dispose();
    _videoQuality.dispose();
    _descriptionEn.dispose();
    _descriptionMm.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final editing = widget.id != null;
    return Scaffold(
      appBar: AppBar(
        title: Text(editing ? 'Edit Movie' : 'Add Movie'),
        actions: [
          if (editing)
            IconButton(
              tooltip: 'Delete movie',
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
                Expanded(child: TextFormField(controller: _duration, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Duration minutes', border: OutlineInputBorder()))),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: TextFormField(controller: _country, decoration: const InputDecoration(labelText: 'Country', border: OutlineInputBorder()))),
                const SizedBox(width: 12),
                Expanded(child: TextFormField(controller: _language, decoration: const InputDecoration(labelText: 'Original Language', border: OutlineInputBorder()))),
              ],
            ),
            const SizedBox(height: 12),
            TextFormField(controller: _thumbnail, decoration: const InputDecoration(labelText: 'Thumbnail URL', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            TextFormField(
              controller: _videoLink,
              decoration: const InputDecoration(
                labelText: 'Telegram video link',
                hintText: 'https://t.me/channel/123 or https://t.me/c/123456/123',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _videoQuality,
              decoration: const InputDecoration(labelText: 'Video quality', border: OutlineInputBorder()),
            ),
            if ((widget.initial?['videos'] as List?)?.isNotEmpty == true) ...[
              const SizedBox(height: 8),
              Text('Saved videos', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 6),
              for (final video in (widget.initial!['videos'] as List))
                ListTile(
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.movie),
                  title: Text(video['quality']?.toString() ?? 'Video'),
                  subtitle: Text('Telegram message ${video['message_id'] ?? ''}'),
                ),
            ],
            const SizedBox(height: 12),
            TextFormField(controller: _descriptionEn, minLines: 3, maxLines: 5, decoration: const InputDecoration(labelText: 'English Description', border: OutlineInputBorder())),
            const SizedBox(height: 12),
            TextFormField(controller: _descriptionMm, minLines: 3, maxLines: 5, decoration: const InputDecoration(labelText: 'Myanmar Description', border: OutlineInputBorder())),
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
              label: Text(editing ? 'Update Movie' : 'Create Movie'),
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
      'duration': _intOrNull(_duration.text),
      'thumbnail': _emptyToNull(_thumbnail.text),
      'description_en': _emptyToNull(_descriptionEn.text),
      'description_mm': _emptyToNull(_descriptionMm.text),
      'is_published': _published,
      'is_archived': false,
    };
    try {
      late final Map<String, dynamic> saved;
      if (widget.id == null) {
        saved = await ref.read(movieActionsProvider).create(data);
      } else {
        saved = await ref.read(movieActionsProvider).update(widget.id!, data);
        ref.invalidate(movieDetailProvider(widget.id!));
      }
      final link = _videoLink.text.trim();
      if (link.isNotEmpty) {
        await ref.read(movieActionsProvider).importVideo(
              movieId: (saved['id'] as num).toInt(),
              telegramLink: link,
              quality: _videoQuality.text.trim().isEmpty ? 'HD' : _videoQuality.text.trim(),
            );
      }
      ref.invalidate(movieListProvider);
      if (mounted) context.go('/movies');
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Save failed: $error')));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _delete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete movie?'),
        content: const Text('This also removes its saved video links.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancel')),
          FilledButton(onPressed: () => Navigator.pop(context, true), child: const Text('Delete')),
        ],
      ),
    );
    if (confirmed != true || widget.id == null) return;
    setState(() => _saving = true);
    try {
      await ref.read(movieActionsProvider).delete(widget.id!);
      ref.invalidate(movieListProvider);
      if (mounted) context.go('/movies');
    } catch (error) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Delete failed: $error')));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  String? _emptyToNull(String value) => value.trim().isEmpty ? null : value.trim();

  int? _intOrNull(String value) => int.tryParse(value.trim());
}
