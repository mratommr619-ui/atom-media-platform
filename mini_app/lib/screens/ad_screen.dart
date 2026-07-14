// ignore_for_file: deprecated_member_use

import 'dart:async';
// ignore: avoid_web_libraries_in_flutter
import 'dart:js' as js;
import 'package:flutter/material.dart';
import 'package:mini_app/services/api_service.dart';
import 'package:url_launcher/url_launcher.dart';

class AdScreen extends StatefulWidget {
  const AdScreen({super.key});

  @override
  State<AdScreen> createState() => _AdScreenState();
}

class _AdScreenState extends State<AdScreen> {
  int _countdown = 15;
  Timer? _timer;
  bool _adCompleted = false;
  bool _hasError = false;
  bool _loadingAd = true;
  Map<String, dynamic>? _ad;

  int get _adDuration => ( _ad?['duration'] as num?)?.toInt() ?? 15;

  @override
  void initState() {
    super.initState();
    _loadAd();
  }

  Future<void> _loadAd() async {
    final token = Uri.base.queryParameters['token'];
    if (token != null) {
      try {
        final ad = await ApiService.getAdvertisement(token);
        if (mounted) {
          setState(() {
            _ad = ad;
            _countdown = (ad['duration'] as num?)?.toInt() ?? 15;
            _loadingAd = false;
          });
        }
      } catch (_) {
        if (mounted) setState(() => _loadingAd = false);
      }
    } else if (mounted) {
      setState(() => _loadingAd = false);
    }
    _showIndexAds();
    if (mounted) _startCountdown();
  }

  void _startCountdown() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      final remaining = _countdown - 1;
      if (remaining <= 0) {
        timer.cancel();
        setState(() {
          _countdown = 0;
          _adCompleted = true;
        });
        _verifyAndClose();
      } else {
        setState(() => _countdown = remaining);
      }
    });
  }

  Future<void> _verifyAndClose() async {
    final uri = Uri.base;
    final token = uri.queryParameters['token'];
    if (token != null) {
      try {
        await ApiService.verifyAd(token);
      } catch (_) {
        if (mounted) {
          setState(() => _hasError = true);
        }
      }
    }
    // Closing must happen after the watch time even if delivery reports an
    // error; the user can use the new Watch button to obtain a fresh token.
    _closeTelegramMiniApp();
  }

  void _closeTelegramMiniApp() {
    try {
      _hideIndexAds();
      final telegram = js.context['Telegram'];
      final webApp = telegram?['WebApp'];
      webApp?.callMethod('close');
    } catch (_) {}
  }

  void _showIndexAds() { try { js.context['atomMediaAds']?.callMethod('show'); } catch (_) {} }
  void _hideIndexAds() { try { js.context['atomMediaAds']?.callMethod('hide'); } catch (_) {} }

  Future<void> _openAdLink() async {
    final link = _ad?['link']?.toString();
    if (link == null || link.isEmpty) return;
    await launchUrl(Uri.parse(link), mode: LaunchMode.externalApplication);
  }

  @override
  void dispose() {
    _hideIndexAds();
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (_loadingAd) const CircularProgressIndicator() else ...[
              if ((_ad?['media_url']?.toString() ?? '').isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(bottom: 20),
                  child: InkWell(
                    onTap: _openAdLink,
                    child: Image.network(
                      _ad!['media_url'].toString(),
                      height: 210,
                      width: 320,
                      fit: BoxFit.contain,
                      errorBuilder: (_, __, ___) => const SizedBox.shrink(),
                    ),
                  ),
                ),
            const Icon(Icons.play_circle_fill, size: 72),
            const SizedBox(height: 20),
            Text(_ad?['title']?.toString() ?? 'ကြော်ငြာ', style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w700), textAlign: TextAlign.center),
            const SizedBox(height: 4),
            const Text('Advertisement', style: TextStyle(fontSize: 16)),
            if (!_adCompleted) ...[
              const SizedBox(height: 20),
              Text('$_countdown စက္ကန့် စောင့်ပေးပါ', style: const TextStyle(fontSize: 18)),
              const SizedBox(height: 16),
              SizedBox(
                width: 280,
                child: LinearProgressIndicator(value: (_adDuration - _countdown) / _adDuration),
              ),
            ] else if (_hasError)
              const Padding(
                padding: EdgeInsets.all(24),
                child: Text('ကြော်ငြာမပြီးဆုံးသေးပါ။ ဗီဒီယိုကို ဖွင့်လို့မရသေးပါ။', textAlign: TextAlign.center),
              )
            else
              const Text('ကျေးဇူးတင်ပါတယ်။ ဗီဒီယိုကို Bot မှပို့ပေးပါမယ်။'),
            ],
          ],
        ),
      ),
    );
  }
}
