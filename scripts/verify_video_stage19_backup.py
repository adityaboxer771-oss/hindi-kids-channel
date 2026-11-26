import json
import subprocess
from pathlib import Path

folder = Path("output/kids")
video = folder / "short_final.mp4"
thumbnail = folder / "thumbnail.png"
story = folder / "story.json"

errors = []

for f in (video, thumbnail, story):
    if not f.exists():
        errors.append(f"Missing: {f}")
    elif f.stat().st_size == 0:
        errors.append(f"Empty file: {f}")

if not errors:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-show_entries", "stream=codec_type",
             "-of", "json", str(video)],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        streams = data.get("streams", [])

        if duration < 10 or duration > 120:
            errors.append(f"Unexpected video duration: {duration:.2f}s")

        if not any(s.get("codec_type") == "video" for s in streams):
            errors.append("Video stream missing")

        if not any(s.get("codec_type") == "audio" for s in streams):
            errors.append("Audio stream missing")

        print(f"Video duration: {duration:.2f}s")
        print("Video and audio streams checked")

    except Exception as e:
        errors.append(f"Video verification failed: {e}")

if not errors:
    try:
        json.loads(story.read_text(encoding="utf-8"))
        print("Story JSON checked")
    except Exception as e:
        errors.append(f"Story JSON invalid: {e}")

if errors:
    print("\nVERIFICATION FAILED")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("\nVERIFICATION PASSED")
