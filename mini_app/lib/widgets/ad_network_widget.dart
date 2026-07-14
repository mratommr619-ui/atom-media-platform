// ignore_for_file: avoid_web_libraries_in_flutter, deprecated_member_use

import 'dart:html' as html;
import 'dart:ui_web' as ui_web;

import 'package:flutter/widgets.dart';

const _viewType = 'atom-media-ad-network';
bool _registered = false;

class AdNetworkWidget extends StatelessWidget {
  const AdNetworkWidget({super.key});

  static void _register() {
    if (_registered) return;
    _registered = true;
    // This is the configured banner network from ads.txt. It lives in an HTML
    // platform view so the ad provider's script can create its own iframe.
    ui_web.platformViewRegistry.registerViewFactory(_viewType, (int viewId) {
      final host = html.DivElement()
        ..id = 'atom-ad-$viewId'
        ..style.width = '320px'
        ..style.height = '50px'
        ..style.overflow = 'hidden';
      final script = html.ScriptElement()
        ..src = 'https://www.highperformanceformat.com/95529f8f0362e6ec8073e3385d7cba78/invoke.js'
        ..async = true;
      host.append(script);
      return host;
    });
  }

  @override
  Widget build(BuildContext context) {
    _register();
    return const SizedBox(width: 320, height: 50, child: HtmlElementView(viewType: _viewType));
  }
}
