import json
from pathlib import Path

OUT = Path(__file__).with_name("reply_database.jsonl")


EN_INTENTS = [
    ("greeting", ["hi", "hello", "hey", "good morning", "good evening"], "Hi. I can help you find movies and series, request missing titles, and report playback problems."),
    ("thanks", ["thanks", "thank you", "appreciate it"], "You are welcome. Tell me the movie or series name whenever you are ready."),
    ("search", ["search", "find", "look for", "movie name", "series name"], "Send the movie or series name. I will search Atom Media for you."),
    ("request", ["request movie", "add movie", "movie not found", "need this movie"], "Send the title or poster. I will forward your request to the admin team."),
    ("report", ["video not working", "broken video", "wrong subtitle", "wrong episode", "quality problem"], "Please tap Report and describe the problem. Admins will review it."),
    ("ads", ["ad", "advertisement", "watch ad", "unlock video"], "Please watch the advertisement once to unlock the protected video."),
    ("favorites", ["favorite", "save movie", "saved list", "my favorites"], "Open Favorites to see saved movies and series. You can add items from search results."),
    ("language", ["language", "change language", "myanmar", "english"], "Tap Language and choose Myanmar or English. I will reply in your selected language."),
    ("admin", ["contact admin", "talk to admin", "support", "help me"], "You can contact the admin directly here: https://t.me/mratom_619"),
    ("account", ["account", "ban", "premium", "ads disabled"], "For account changes, please contact the admin: https://t.me/mratom_619"),
]

MM_INTENTS = [
    ("greeting", ["မင်္ဂလာပါ", "ဟယ်လို", "hi", "hello", "နေကောင်းလား"], "မင်္ဂလာပါ။ ရုပ်ရှင်/ဇာတ်လမ်းတွဲ ရှာဖို့၊ တောင်းခံဖို့၊ Report ပို့ဖို့ ကူညီပေးနိုင်ပါတယ်။"),
    ("thanks", ["ကျေးဇူး", "thank you", "thanks", "ကျေးဇူးတင်ပါတယ်"], "ရပါတယ်။ ရှာချင်တဲ့ ရုပ်ရှင်/ဇာတ်လမ်းတွဲနာမည်ကို ပို့ပေးပါ။"),
    ("search", ["ရှာမယ်", "ရှာပေး", "ကားရှာ", "ဇာတ်လမ်းတွဲရှာ", "movie ရှာ"], "ရုပ်ရှင် သို့မဟုတ် ဇာတ်လမ်းတွဲနာမည်ကို ပို့ပါ။ Atom Media ထဲကနေရှာပေးပါမယ်။"),
    ("request", ["ကားတောင်း", "ထည့်ပေး", "မရှိသေးဘူး", "ဒီကားလိုချင်", "request"], "ရုပ်ရှင်နာမည် သို့မဟုတ် poster ပို့ပါ။ Admin ဆီတောင်းခံပေးပါမယ်။"),
    ("report", ["ကြည့်မရ", "video မရ", "စာတန်းမှား", "အပိုင်းမှား", "quality မကောင်း"], "Report ကိုနှိပ်ပြီး ပြဿနာကိုရေးပို့ပါ။ Admin ကစစ်ဆေးပေးပါမယ်။"),
    ("ads", ["ကြော်ငြာ", "ad", "unlock", "ဖွင့်မရ", "ကြည့်ခွင့်"], "ဗီဒီယိုဖွင့်ရန် ကြော်ငြာကို တစ်ကြိမ်ကြည့်ပေးပါ။ ပြီးရင် video unlock ဖြစ်ပါမယ်။"),
    ("favorites", ["ကြိုက်နှစ်သက်မှု", "သိမ်းမယ်", "favorite", "save", "စာရင်း"], "Favorites ထဲမှာ သိမ်းထားတဲ့ကားတွေကြည့်နိုင်ပါတယ်။ Search result ထဲကနေထည့်နိုင်ပါတယ်။"),
    ("language", ["ဘာသာစကား", "မြန်မာ", "english", "language ပြောင်း", "စာပြောင်း"], "Language ကိုနှိပ်ပြီး မြန်မာ/English ရွေးပါ။ ရွေးထားတဲ့ဘာသာစကားနဲ့ပြန်ဖြေပေးပါမယ်။"),
    ("admin", ["admin ဆက်သွယ်", "ဆက်သွယ်ချင်", "support", "အကူအညီ", "ပြောချင်"], "Admin ကိုဒီ link ကနေ တိုက်ရိုက်ဆက်သွယ်နိုင်ပါတယ်: https://t.me/mratom_619"),
    ("account", ["account", "ban", "premium", "ads ပိတ်", "အကောင့်"], "Account ပြင်ဆင်မှုအတွက် Admin ကိုဆက်သွယ်ပါ: https://t.me/mratom_619"),
]

EN_PREFIXES = ["", "please ", "can you ", "i want to ", "how to ", "help me ", "tell me about ", "where can i "]
EN_SUFFIXES = ["", " please", " now", " in atom", " on atom media", " for me", " today", " with the bot"]
MM_PREFIXES = ["", "ကျေးဇူးပြုပြီး ", "ဘယ်လို ", "ငါ ", "ကျွန်တော် ", "ကျွန်မ ", "အကူအညီ ", "atom မှာ "]
MM_SUFFIXES = ["", " ပေးပါ", " လုပ်ချင်တယ်", " ဘယ်လိုလုပ်ရမလဲ", " ရမလား", " အခု", " ဒီ bot မှာ", " atom media မှာ"]


def make_entry(lang: str, intent: str, query: str, answer: str, idx: int) -> dict:
    return {
        "id": f"{lang}-{idx:05d}",
        "lang": lang,
        "intent": intent,
        "queries": [query],
        "answer": answer,
    }


def generate_language(lang: str, intents, prefixes, suffixes, target: int) -> list[dict]:
    entries = []
    seen = set()
    idx = 0
    while len(entries) < target:
        for intent, phrases, answer in intents:
            for phrase in phrases:
                for prefix in prefixes:
                    for suffix in suffixes:
                        query = f"{prefix}{phrase}{suffix}".strip()
                        key = (lang, query)
                        if query and key not in seen:
                            seen.add(key)
                            entries.append(make_entry(lang, intent, query, answer, idx))
                            idx += 1
                            if len(entries) >= target:
                                return entries
        round_no = len(entries)
        for intent, phrases, answer in intents:
            for phrase in phrases:
                query = f"{phrase} {intent} {round_no}"
                key = (lang, query)
                if key not in seen:
                    seen.add(key)
                    entries.append(make_entry(lang, intent, query, answer, idx))
                    idx += 1
                    if len(entries) >= target:
                        return entries
    return entries


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    entries.extend(generate_language("en", EN_INTENTS, EN_PREFIXES, EN_SUFFIXES, 50_000))
    entries.extend(generate_language("mm", MM_INTENTS, MM_PREFIXES, MM_SUFFIXES, 50_000))
    with OUT.open("w", encoding="utf-8", newline="\n") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote {len(entries)} entries to {OUT}")


if __name__ == "__main__":
    main()
