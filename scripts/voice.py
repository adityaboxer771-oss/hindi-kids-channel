import asyncio
import sys
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output/kids/voice.mp3"
VOICE = "hi-IN-SwaraNeural"

async def generate(text):
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate="-5%",
        pitch="+5Hz"
    )
    await communicate.save(str(OUTPUT))
    print(f"Story voice saved: {OUTPUT}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python scripts/voice.py "Hindi story"')
    asyncio.run(generate(" ".join(sys.argv[1:])))
