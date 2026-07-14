import 'package:flutter_test/flutter_test.dart';
import 'package:mini_app/main.dart';

void main() {
  testWidgets('mini app shows advertisement screen', (tester) async {
    await tester.pumpWidget(const AtomMiniApp());

    expect(find.text('ကြော်ငြာ'), findsOneWidget);
    expect(find.text('Advertisement'), findsOneWidget);
    expect(find.textContaining('စက္ကန့် စောင့်ပေးပါ'), findsOneWidget);
  });
}
