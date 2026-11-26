import asyncio
import sys
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parent.parent

VOICES = {
    "kids": "hi-IN-SwaraNeural",
    "gaming": "hi-IN-MadhurNeural"
}

async def generate(text, category):
    voice = VOICES[category]
    output = ROOT / "output" / category / "voice.mp3"
    output.parent.mkdir(parents=True, exist_ok=True)

    tts = edge_tts.Communicate(text, voice)
    await tts.save(str(output))
    print(f"Voice saved: {output}")

if __name__ == "__main__":
    category = sys.argv[1]
    text = sys.argv[2]
    if category not in VOICES:
        raise SystemExit("Use kids or gaming")
    asyncio.run(generate(text, category))
