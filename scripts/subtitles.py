from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output/kids/subtitles.srt"

text = " ".join(sys.argv[1:]).strip()
if not text:
    raise SystemExit('Usage: python scripts/subtitles.py "Hindi story"')

words = text.split()
chunks = [" ".join(words[i:i+5]) for i in range(0, len(words), 5)]

def stamp(seconds):
    ms = int(seconds * 1000)
    return f"{ms//3600000:02}:{(ms//60000)%60:02}:{(ms//1000)%60:02},{ms%1000:03}"

duration = 22
step = duration / len(chunks)

with OUTPUT.open("w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks):
        start = i * step
        end = min((i+1) * step, duration)
        f.write(f"{i+1}\n{stamp(start)} --> {stamp(end)}\n{chunk}\n\n")

print("Subtitles ready:", OUTPUT)
