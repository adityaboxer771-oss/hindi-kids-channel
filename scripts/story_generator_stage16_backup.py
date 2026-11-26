import random, json
from pathlib import Path

OUT = Path("output/kids")
OUT.mkdir(parents=True, exist_ok=True)

characters = [
    ("चिंटू खरगोश", "बहादुर", "bunny"),
    ("मिन्नी चूहिया", "समझदार", "mouse"),
    ("गोलू पांडा", "मददगार", "panda"),
    ("टोटो तोता", "बातूनी", "parrot"),
    ("बिल्लू बिल्ली", "जिज्ञासु", "cat"),
    ("पिंकू गिलहरी", "फुर्तीला", "squirrel"),
    ("मोती कछुआ", "धैर्यवान", "turtle"),
]

places = [
    ("हरे-भरे जंगल", "forest"),
    ("सुंदर फूलों वाले बगीचे", "garden"),
    ("नदी के किनारे", "river"),
    ("एक छोटे से गाँव", "village"),
    ("रंगीन पहाड़ियों", "hills"),
    ("आम के पेड़ों वाले बगीचे", "garden"),
    ("एक जादुई जंगल", "forest"),
]

events = [
    {
        "problem": "एक नन्हा पक्षी अपना रास्ता भूल गया था",
        "action": "दोस्तों ने उसे रास्ता पहचानने में मदद की",
        "dialogue": "पक्षी बोला, तुम सबका बहुत धन्यवाद!",
        "ending": "पक्षी खुशी से अपने घर पहुँच गया",
        "lesson": "दूसरों की मदद करना अच्छी बात है",
        "visual": ["intro", "search", "help", "home", "lesson"]
    },
    {
        "problem": "बगीचे में एक पौधा सूखने लगा था",
        "action": "दोस्तों ने मिलकर पौधे को पानी दिया और उसकी देखभाल की",
        "dialogue": "गोलू बोला, हम रोज इसकी देखभाल करेंगे!",
        "ending": "कुछ दिनों बाद पौधे पर सुंदर फूल खिल गए",
        "lesson": "पेड़-पौधों की देखभाल करनी चाहिए",
        "visual": ["intro", "notice", "water", "bloom", "lesson"]
    },
    {
        "problem": "उन्हें रास्ते में एक खोया हुआ खिलौना मिला",
        "action": "सबने मिलकर खिलौने के मालिक को ढूँढा",
        "dialogue": "मिन्नी बोली, किसी की चीज लौटाना हमारा काम है!",
        "ending": "खिलौने का मालिक खुशी से झूम उठा",
        "lesson": "ईमानदारी सबसे अच्छी आदत है",
        "visual": ["intro", "find", "search", "celebrate", "lesson"]
    },
    {
        "problem": "बारिश के कारण उनकी picnic की जगह गीली हो गई",
        "action": "दोस्तों ने पेड़ों के नीचे नई जगह तैयार की",
        "dialogue": "बिल्लू बोला, साथ हों तो हर जगह मजेदार है!",
        "ending": "सबने मिलकर मजेदार picnic मनाई",
        "lesson": "मुश्किल में मिलकर समाधान निकालना चाहिए",
        "visual": ["intro", "rain", "plan", "picnic", "lesson"]
    },
    {
        "problem": "एक छोटी गिलहरी को अपने घर का रास्ता नहीं मिल रहा था",
        "action": "दोस्तों ने आसपास के पेड़ों और रास्तों को ध्यान से देखा",
        "dialogue": "चिंटू बोला, चिंता मत करो, हम साथ हैं!",
        "ending": "गिलहरी अपने घर पहुँचकर खुश हो गई",
        "lesson": "दोस्ती और मदद बहुत महत्वपूर्ण हैं",
        "visual": ["intro", "search", "help", "home", "lesson"]
    },
    {
        "problem": "जंगल में सभी दोस्त एक नया खेल खेलना चाहते थे",
        "action": "उन्होंने सबकी पसंद का एक नया खेल बनाया",
        "dialogue": "टोटो बोला, यह तो सबसे मजेदार खेल है!",
        "ending": "सभी दोस्तों ने खुशी से खेल खेला",
        "lesson": "सबकी बात सुनना और मिलकर काम करना अच्छा है",
        "visual": ["intro", "think", "plan", "play", "lesson"]
    },
    {
        "problem": "नदी के किनारे उन्हें बहुत सारे कागज पड़े मिले",
        "action": "उन्होंने जगह साफ करने में सहयोग किया",
        "dialogue": "मोती बोला, प्रकृति को साफ रखना हमारी जिम्मेदारी है!",
        "ending": "नदी का किनारा फिर से सुंदर दिखने लगा",
        "lesson": "हमें अपने आसपास सफाई रखनी चाहिए",
        "visual": ["intro", "notice", "clean", "celebrate", "lesson"]
    },
    {
        "problem": "एक दोस्त अपनी चित्रकारी प्रतियोगिता को लेकर घबराया हुआ था",
        "action": "दोस्तों ने उसे अभ्यास करने और आत्मविश्वास रखने के लिए प्रोत्साहित किया",
        "dialogue": "मिन्नी बोली, कोशिश करना सबसे जरूरी है!",
        "ending": "उसने खुशी से अपनी सुंदर चित्रकारी पूरी की",
        "lesson": "लगातार कोशिश करने से आत्मविश्वास बढ़ता है",
        "visual": ["intro", "worry", "practice", "finish", "lesson"]
    },
    {
        "problem": "जंगल में तेज हवा से उनके खेल के सामान बिखर गए",
        "action": "दोस्तों ने मिलकर सामान इकट्ठा किया और खेल की जगह ठीक की",
        "dialogue": "पिंकू बोली, टीमवर्क से काम आसान हो जाता है!",
        "ending": "सभी ने फिर से मिलकर अपना खेल शुरू किया",
        "lesson": "मिलजुलकर काम करने से मुश्किलें आसान होती हैं",
        "visual": ["intro", "notice", "help", "play", "lesson"]
    },
    {
        "problem": "एक दोस्त ने पहली बार नया गाना सीखने की कोशिश की",
        "action": "दोस्तों ने उसे धैर्य से अभ्यास करने में मदद की",
        "dialogue": "टोटो बोला, धीरे-धीरे अभ्यास करो, तुम सीख जाओगे!",
        "ending": "सबने मिलकर खुशी से गाना गाया",
        "lesson": "धैर्य और अभ्यास से नई चीजें सीख सकते हैं",
        "visual": ["intro", "worry", "practice", "celebrate", "lesson"]
    }
]

HISTORY = OUT / "story_history.json"
history = []
if HISTORY.exists():
    try:
        history = json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:
        history = []

used_events = [x.get("event_index") for x in history[-10:]]
available_events = [i for i in range(len(events)) if i not in used_events]
if not available_events:
    available_events = list(range(len(events)))
event_index = random.choice(available_events)
event = events[event_index]

used_pairs = [x.get("character_pair") for x in history[-5:]]
available_pairs = [
    pair for pair in [
        (i, j) for i in range(len(characters))
        for j in range(i+1, len(characters))
    ] if str(pair) not in used_pairs
]
if not available_pairs:
    available_pairs = [
        (i, j) for i in range(len(characters))
        for j in range(i+1, len(characters))
    ]
pair = random.choice(available_pairs)
a, b = characters[pair[0]], characters[pair[1]]
place, bg = random.choice(places)

title = f"{a[0]} और {b[0]} की कहानी"

scenes = [
    {
        "text": f"एक समय की बात है। {place} में {a[0]} रहता था। वह बहुत {a[1]} था। उसका दोस्त {b[0]} भी बहुत {b[1]} था।",
        "visual": event["visual"][0],
        "beat": "introduction"
    },
    {
        "text": f"एक दिन {place} में {event['problem']}।",
        "visual": event["visual"][1],
        "beat": "problem"
    },
    {
        "text": f"{a[0]} ने {b[0]} को बुलाया। दोनों ने मिलकर काम करने का फैसला किया। {event['action']}।",
        "visual": event["visual"][2],
        "beat": "teamwork"
    },
    {
        "text": f"{event['dialogue']} {event['ending']}। दोनों दोस्तों ने खुशी-खुशी दिन बिताया।",
        "visual": event["visual"][3],
        "beat": "resolution"
    },
    {
        "text": f"इस कहानी से हमें सीख मिलती है कि {event['lesson']}।",
        "visual": event["visual"][4],
        "beat": "moral"
    }
]

story = " ".join(scene["text"] for scene in scenes)

data = {
    "title": title,
    "story": story,
    "characters": [
        {"name": a[0], "animal": a[2]},
        {"name": b[0], "animal": b[2]}
    ],
    "background": bg,
    "scenes": scenes,
    "story_structure": ["introduction", "problem", "teamwork", "resolution", "moral"],
    "version": 9
}

(OUT / "story.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

entry = {
    "title": title,
    "event_index": event_index,
    "character_pair": str(pair),
    "background": bg
}
history.append(entry)
HISTORY.write_text(json.dumps(history[-30:], ensure_ascii=False, indent=2), encoding="utf-8")

print("STAGE 9 STORY GENERATED")
print("History saved:", len(history[-30:]))
print(title)
print(story)
