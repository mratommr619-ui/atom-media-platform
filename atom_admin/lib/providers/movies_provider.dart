import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:atom_admin/providers/auth_provider.dart';

final movieListProvider = FutureProvider<List<dynamic>>((ref) async {
  final dio = ref.read(dioProvider);
  final response = await dio.get('/movies/');
  return response.data['items'];
});
