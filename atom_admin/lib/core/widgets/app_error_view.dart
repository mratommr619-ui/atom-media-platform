import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hive_flutter/hive_flutter.dart';

class AppErrorView extends StatelessWidget {
  const AppErrorView({
    super.key,
    required this.error,
    this.onRetry,
  });

  final Object error;
  final VoidCallback? onRetry;

  @override
  Widget build(BuildContext context) {
    final expired = _isExpired(error);
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline, size: 42, color: Theme.of(context).colorScheme.error),
            const SizedBox(height: 12),
            Text(
              _message(error),
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            if (expired) ...[
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: () => _clearSession(context),
                icon: const Icon(Icons.login),
                label: const Text('Sign in again'),
              ),
            ] else if (onRetry != null) ...[
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ],
        ),
      ),
    );
  }

  bool _isExpired(Object error) {
    return error is DioException && error.response?.statusCode == 401;
  }

  Future<void> _clearSession(BuildContext context) async {
    final box = await Hive.openBox<dynamic>('auth');
    await box.delete('access_token');
    if (context.mounted) {
      context.go('/login');
    }
  }

  String _message(Object error) {
    if (error is DioException) {
      final status = error.response?.statusCode;
      if (status == 401) return 'Session expired. Please log out and sign in again.';
      if (status == 403) return 'This admin device is waiting for approval.';
      if (status != null && status >= 500) return 'Server error. Please restart/update the backend and try again.';
      if (error.type == DioExceptionType.connectionTimeout ||
          error.type == DioExceptionType.receiveTimeout ||
          error.type == DioExceptionType.sendTimeout ||
          error.type == DioExceptionType.connectionError) {
        return 'Cannot connect to the API. Check internet connection and API URL.';
      }
    }
    return 'Something went wrong. Please try again.';
  }
}
