import 'dart:io';

import 'package:atom_admin/main.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hive/hive.dart';

void main() {
  setUpAll(() async {
    final tempDir = Directory.systemTemp.createTempSync('atom_admin_hive_test_');
    Hive.init(tempDir.path);
  });

  testWidgets('admin app shows login screen', (tester) async {
    await tester.pumpWidget(const ProviderScope(child: AtomAdminApp()));
    await tester.pump();

    expect(find.text('Atom Admin'), findsOneWidget);
    expect(find.text('Login'), findsOneWidget);
  });
}
