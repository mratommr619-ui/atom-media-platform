import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  static Future<void> verifyAd(String token) async {
    final verifyUrl = Uri.parse('$baseUrl/mini-app/verify?token=$token');
    final verifyResponse = await http.get(verifyUrl);
    if (verifyResponse.statusCode < 200 || verifyResponse.statusCode >= 300) {
      throw Exception('Advertisement verification failed');
    }

    final sendUrl = Uri.parse('$baseUrl/mini-app/send_video?token=$token');
    final sendResponse = await http.post(sendUrl);
    if (sendResponse.statusCode < 200 || sendResponse.statusCode >= 300) {
      throw Exception('Video delivery failed');
    }
  }

  static Future<Map<String, dynamic>> getAdvertisement(String token) async {
    final response = await http.get(Uri.parse('$baseUrl/mini-app/advertisement?token=$token'));
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Advertisement could not be loaded');
    }
    return (jsonDecode(response.body) as Map).cast<String, dynamic>();
  }
}
