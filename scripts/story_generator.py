import random
import json
from pathlib import Path

OUT = Path("output/kids")
OUT.mkdir(parents=True, exist_ok=True)

characters = [
    ("चिंटू खरगोश", "बहादुर और दयालु"),
    ("मिन्नी चूहिया", "होशियार और प्यारी"),
    ("गोलू पांडा", "मजेदार और मददगार"),
    ("टोटो तोता", "रंगीन और बातूनी"),
    ("बिल्लू बिल्ली", "जिज्ञासु और दोस्ताना"),
]

places = [
    "हरे-भरे जंगल",
    "रंगीन फूलों वाले बगीचे",
    "नदी के किनारे",
    "एक सुंदर गाँव",
    "जादुई पेड़ों वाले जंगल",
]

problems = [
    "एक छोटा दोस्त रास्ता भूल गया था",
    "सबको एक खोया हुआ खिलौना मिला",
    "एक नन्हा पक्षी पानी ढूँढ रहा था",
    "दो दोस्तों को मिलकर एक पौधा बचाना था",
    "एक छोटी गिलहरी अपना घर ढूँढ रही थी",
]

lessons = [
    "मिलकर काम करने से मुश्किल आसान हो जाती है",
    "दूसरों की मदद करना अच्छी बात है",
    "सच्ची दोस्ती सबसे प्यारी होती है",
    "पेड़-पौधों और जानवरों का ख्याल रखना चाहिए",
    "हमें हमेशा सच बोलना चाहिए",
]

character, nature = random.choice(characters)
place = random.choice(places)
problem = random.choice(problems)
lesson = random.choice(lessons)

story = f"""
एक समय की बात है। {place} में {character} रहता था।
वह {nature} था।

एक दिन {place} में {problem}।
{character} ने उसकी मदद करने का फैसला किया।

दोनों ने मिलकर खुशी-खुशी समस्या हल कर ली।
सब बहुत खुश हुए और अच्छे दोस्त बन गए।

इस कहानी से हमें सीख मिलती है कि {lesson}।
"""

data = {
    "title": f"{character} की प्यारी कहानी",
    "story": story.strip()
}

with open(OUT / "story.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(data["title"])
print(data["story"])