import 'dart:math';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'package:atom_admin/core/config/app_config.dart';
import 'package:hive_flutter/hive_flutter.dart';

Future<Box<dynamic>> _authBox() => Hive.openBox<dynamic>('auth');

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      sendTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
    ),
  );
  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) async {
        final box = await _authBox();
        final token = box.get('access_token') as String?;
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
    ),
  );
  return dio;
});

final authProvider = StateNotifierProvider<AuthNotifier, AsyncValue<bool>>((ref) {
  return AuthNotifier(ref);
});

class AuthNotifier extends StateNotifier<AsyncValue<bool>> {
  final Ref ref;
  AuthNotifier(this.ref) : super(const AsyncValue.loading()) {
    _restoreSession();
  }

  Future<void> _restoreSession() async {
    final box = await _authBox();
    final token = box.get('access_token') as String?;
    if (token == null || token.isEmpty) {
      state = const AsyncValue.data(false);
      return;
    }
    try {
      await ref.read(dioProvider).get('/auth/me');
      state = const AsyncValue.data(true);
    } on DioException {
      await box.delete('access_token');
      state = const AsyncValue.data(false);
    }
  }

  Future<void> login(String password) async {
    state = const AsyncValue.loading();
    try {
      final box = await _authBox();
      final deviceId = await _deviceId(box);
      final response = await ref.read(dioProvider).post(
        '/auth/login',
        data: {
          'password': password,
          'device_id': deviceId,
          'device_name': 'Atom Admin Phone',
        },
      );
      await box.put('access_token', response.data['access_token'] as String);
      state = const AsyncValue.data(true);
    } on DioException catch (e) {
      state = AsyncValue.error(_loginErrorMessage(e), StackTrace.current);
    } catch (e) {
      state = AsyncValue.error(e.toString(), StackTrace.current);
    }
  }

  Future<void> logout() async {
    final box = await _authBox();
    await box.delete('access_token');
    state = const AsyncValue.data(false);
  }

  Future<String> _deviceId(Box<dynamic> box) async {
    final existing = box.get('device_id') as String?;
    if (existing != null && existing.isNotEmpty) return existing;
    final random = Random.secure();
    final parts = List.generate(4, (_) => random.nextInt(1 << 32).toRadixString(16).padLeft(8, '0'));
    final id = parts.join('-');
    await box.put('device_id', id);
    return id;
  }

  String _loginErrorMessage(DioException error) {
    final data = error.response?.data;
    if (data is Map && data['detail'] is String) {
      return data['detail'] as String;
    }
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.connectionError) {
      return 'Connection failed. API: ${AppConfig.apiBaseUrl}';
    }
    return 'Login failed';
  }
}
