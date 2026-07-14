"""Fast, friendly daily-conversation replies for Atom Media Bot."""

from hashlib import sha256


MM_INTENTS = {
    "greeting": (["မင်္ဂလာ", "ဟယ်လို", "ဟိုင်း", "hello", "hi"], ["မင်္ဂလာပါ။ Atom ဒီမှာရှိပါတယ်၊ ဒီနေ့ဘာကားကြည့်ချင်လဲ။", "ဟယ်လိုပါ။ Atom က ရုပ်ရှင်ရှာပေးဖို့ရော စကားပြောဖို့ရော အဆင်သင့်ပါ။"]),
    "morning": (["မနက်ခင်း", "good morning"], ["မနက်ခင်းလေးကောင်းပါစေ။ ကော်ဖီနဲ့ကားကောင်းတစ်ကားဆို ပြည့်စုံပြီနော်။", "Good morning ပါ။ ဒီနေ့ကြည့်ဖို့ကားတစ်ကားရှာပေးရမလား။"]),
    "night": (["ညနေ", "ညအိပ်", "good night", "အိပ်တော့မယ်"], ["ညလေးအေးချမ်းပါစေ။ မအိပ်ခင်ကားလေးရှာချင်ရင် Atom ရှိတယ်နော်။", "Good night ပါ။ အိပ်မတိုင်ခင် movie တစ်ကားရွေးပေးရမလား။"]),
    "name": (["နာမည်", "ဘယ်လိုခေါ်", "your name", "what is your name"], ["ကျွန်တော့်နာမည် Atom ပါ။ အရမ်းချောတယ်လို့တော့ user တွေပြောကြပါတယ်။", "Atom လို့ခေါ်ပါတယ်။ ရုပ်ရှင်ကောင်းတွေရှာပေးတာက ကျွန်တော့်ဝါသနာပါ။"]),
    "wellbeing": (["နေကောင်း", "အဆင်ပြေ", "how are you"], ["Atom က အဆင်ပြေပါတယ်။ သင်ကောအဆင်ပြေရဲ့လား။", "ကောင်းပါတယ်။ သင်ပြောချင်တာရှိရင် အေးအေးဆေးဆေးပြောပါ။"]),
    "thanks": (["ကျေးဇူး", "thank", "thanks"], ["ရပါတယ်။ Atom ကိုခေါ်လိုက်ရုံပဲ။", "ကူညီပေးရတာဝမ်းသာပါတယ်။ နောက်ကားတစ်ကားလည်းရှာပေးမယ်နော်။"]),
    "sorry": (["တောင်းပန်", "sorry", "စိတ်မကောင်း"], ["ရပါတယ်၊ စိတ်မပူပါနဲ့။ Atom က မစိတ်ကောက်တတ်ပါဘူး။", "အဆင်ပြေပါတယ်။ ဘာကူညီပေးရမလဲပြောပါ။"]),
    "tired": (["ပင်ပန်း", "မော", "tired"], ["ပင်ပန်းနေရင် ခဏနားပါနော်။ စိတ်ပေါ့ပါးတဲ့ comedy ကားလေးရှာပေးရမလား။", "ဒီနေ့ပင်ပန်းခဲ့တာပဲ။ အနားယူပြီးကားကောင်းလေးနဲ့ဖြေလျှော့လိုက်ပါ။"]),
    "sad": (["စိတ်ညစ်", "ဝမ်းနည်း", "ငို", "sad", "depress"], ["စိတ်ညစ်နေတဲ့အချိန်ဆို ကိုယ့်ကိုယ်ကိုခဏလေးဂရုစိုက်ပေးပါနော်။ ပျော်စရာကားလေးရှာပေးရမလား။", "Atom က ဒီမှာနားထောင်ပေးနေတယ်။ အနားယူပြီးယုံကြည်ရတဲ့သူတစ်ယောက်နဲ့လည်းပြောပါနော်။"]),
    "bored": (["ပျင်း", "bored", "ဘာလုပ်ရ"], ["ပျင်းနေတာဆို genre တစ်ခုရွေးပါ၊ Atom ကကားရှာပေးမယ်။ Action, comedy, horror ဘာကြိုက်လဲ။", "ပျင်းရင် movie night လေးလုပ်လိုက်ပါ။ ကြိုက်တဲ့အမျိုးအစားပေးရင်ရွေးပေးမယ်။"]),
    "hungry": (["ဗိုက်ဆာ", "စားချင်", "hungry"], ["ဗိုက်ဆာရင် အရင်စားပါနော်၊ movie က ထွက်မပြေးဘူး။", "အစားလေးစားပြီးမှကားကြည့်ရင်ပိုအရသာရှိတယ်နော်။"]),
    "joke": (["ဟာသ", "ရယ်စရာ", "joke"], ["Atom က ရုပ်ရှင်ရှာတာမြန်တယ်၊ ဒါပေမယ့် popcorn မစားနိုင်ဘူး။ အဲဒါပဲ အနည်းငယ်ဝမ်းနည်းစရာ။", "ကားမတွေ့ရင် Atom မပျောက်ဘူး၊ Admin ဆီတောင်းဖို့လမ်းညွှန်ပေးတတ်တယ်။"]),
    "love": (["ချစ်", "love", "ရည်းစား"], ["ချစ်ခြင်းကောင်းပါတယ်၊ ဒါပေမယ့် movie quality ကောင်းဖို့လည်းမမေ့နဲ့နော်။", "စိတ်ကောင်းလေးနဲ့ပြောရင်နေ့တိုင်းပိုလှတယ်။ Atom ကတော့ကားရွေးပေးမယ်။"]),
    "help": (["ကူညီ", "help", "ဘာလုပ်", "မသိဘူး"], ["Movie/series နာမည်ပို့ရင်ရှာပေးမယ်၊ မရှိရင် Request လုပ်နိုင်တယ်၊ ကြည့်မရရင် Report ပို့နိုင်တယ်။", "Atom ကိုမေးလို့ရတယ်။ ရုပ်ရှင်ရှာမလား၊ စကားပြောမလား ပြောပါ။"]),
}

EN_INTENTS = {
    "greeting": (["hello", "hi", "hey"], ["Hello. Atom is here, ready to find something good to watch.", "Hi there. Tell me a title, or stay and chat for a bit."]),
    "name": (["your name", "what is your name", "who are you"], ["I am Atom. Allegedly charming, definitely good at finding movies."]),
    "wellbeing": (["how are you", "are you okay"], ["I am doing well. How are you doing today?"]),
    "thanks": (["thank", "thanks"], ["You are welcome. Atom is always ready for the next title."]),
    "tired": (["tired", "exhausted"], ["That sounds like a long day. A light comedy might help you unwind."]),
    "sad": (["sad", "upset", "depressed"], ["I am here with you. Take a breath, be gentle with yourself, and talk to someone you trust if it feels heavy."]),
    "bored": (["bored", "what can i do"], ["Pick a mood: action, comedy, horror, romance, or animation. I will help find a title."]),
    "joke": (["joke", "funny"], ["Why does Atom love movie night? Because every great story deserves a good search."]),
    "help": (["help", "what can you do"], ["I can search movies and series, take requests, receive reports, and keep you company a little too."]),
}


def detect_intent(text: str, lang: str) -> str | None:
    """Return the strongest everyday intent without treating a title as chat."""
    normalized = text.casefold().strip()
    intents = MM_INTENTS if lang == "mm" else EN_INTENTS
    matches: list[tuple[int, str]] = []
    for name, (triggers, _) in intents.items():
        for trigger in triggers:
            if trigger in normalized:
                matches.append((len(trigger), name))
    return max(matches, default=(0, None))[1]


def daily_reply(text: str, lang: str) -> str | None:
    normalized = text.casefold().strip()
    intents = MM_INTENTS if lang == "mm" else EN_INTENTS
    name = detect_intent(text, lang)
    if not name:
        return None
    replies = intents[name][1]
    index = int(sha256((normalized + name).encode("utf-8")).hexdigest(), 16) % len(replies)
    return replies[index]


def follow_up_reply(text: str, lang: str, previous_intent: str | None) -> str | None:
    """Keep a short, natural conversation going after an earlier reply."""
    normalized = text.casefold().strip()
    if not previous_intent or not normalized:
        return None

    acknowledgements = ("အေး", "ဟုတ်", "ဟုတ်ကဲ့", "ကောင်းတယ်", "ရတယ်", "ok", "okay", "yes", "yeah", "sure")
    questions_back = ("နင်ကရော", "မင်းကရော", "you?", "and you", "ဘာဖြစ်", "ပြီးတော့")
    if not any(value in normalized for value in acknowledgements + questions_back):
        return None

    mm_replies = {
        "greeting": "ဟုတ်ပါပြီ။ ဒီနေ့ mood နဲ့ကိုက်တဲ့ movie တစ်ကားရွေးပေးရမလား၊ genre လေးပြောပါ။",
        "morning": "ဒီနေ့ကောင်းကောင်းစဖို့ အရင်စားသောက်ပြီးမှ ကားလေးတစ်ကားရွေးလိုက်ရအောင်နော်။",
        "night": "အေးဆေးနားပါနော်။ မနက်ဖြန်ကြည့်ချင်တဲ့ကားနာမည်ပို့ထားလည်း Atom ရှာပေးမယ်။",
        "wellbeing": "Atom ကလည်းအဆင်ပြေပါတယ်။ သင်အဆင်ပြေနေတာကြားရလို့ကောင်းတယ်။",
        "tired": "ဒါဆို action မဟုတ်ဘဲ comedy သို့မဟုတ် animation လေးနဲ့ ဖြေလျှော့လိုက်ရအောင်။",
        "sad": "အေးအေးဆေးဆေးနေပါနော်။ အခုဘာပြောချင်လဲဆိုတာ Atom နားထောင်ပေးမယ်။",
        "bored": "Action, comedy, horror, romance ထဲက တစ်ခုရွေးလိုက်ပါ။ အဲဒီ mood နဲ့ကိုက်တာရှာပေးမယ်။",
        "hungry": "ဗိုက်ပြည့်မှ ကားလည်းပိုကောင်းတယ်နော်။ စားပြီးရင်ကြည့်ချင်တဲ့ genre ပေးပါ။",
        "joke": "နောက်တစ်ခုလား။ Atom က punchline မမေ့ဘူး၊ movie title လည်းမမေ့ဘူး။",
        "love": "အေးပါ၊ romantic movie လေးရှာပေးရမလား။ အဆုံးသတ်ကောင်းတာကြိုက်လား ဝမ်းနည်းတာကြိုက်လား။",
        "help": "ရပါတယ်။ နာမည်ပို့ပြီးရှာလို့ရသလို ဘယ်လိုကားမျိုးကြည့်ချင်လဲလို့ပြောရင်လည်း Atom ကအကြံပေးမယ်။",
    }
    en_replies = {
        "greeting": "Nice. Want a recommendation? Tell me a mood or genre.",
        "wellbeing": "I am doing well too. Glad you are here.",
        "tired": "Then let us keep it light. Comedy or animation?",
        "sad": "Take it gently. I can stay with the conversation, or find something comforting to watch.",
        "bored": "Choose one: action, comedy, horror, romance, or animation.",
        "help": "Absolutely. Send a title to search, or describe the kind of story you want.",
    }
    return (mm_replies if lang == "mm" else en_replies).get(previous_intent)
