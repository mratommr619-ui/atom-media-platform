import 'package:flutter/material.dart';
import 'package:mini_app/screens/ad_screen.dart';

void main() {
  runApp(const AtomMiniApp());
}

class AtomMiniApp extends StatelessWidget {
  const AtomMiniApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Atom Media',
      themeMode: ThemeMode.system,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        fontFamily: 'MyanmarText',
        colorSchemeSeed: Colors.deepPurple,
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        fontFamily: 'MyanmarText',
        colorSchemeSeed: Colors.deepPurple,
      ),
      home: const AdScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
