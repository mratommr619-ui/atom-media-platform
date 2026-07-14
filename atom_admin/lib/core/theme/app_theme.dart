import 'package:flutter/material.dart';

class AppTheme {
  static final lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    fontFamily: 'MyanmarText',
    colorSchemeSeed: Colors.indigo,
    appBarTheme: const AppBarTheme(centerTitle: true),
  );

  static final darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    fontFamily: 'MyanmarText',
    colorSchemeSeed: Colors.indigo,
    appBarTheme: const AppBarTheme(centerTitle: true),
  );
}
