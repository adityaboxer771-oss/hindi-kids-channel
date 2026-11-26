import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "config/clip_queue.json"

with open(QUEUE, encoding="utf-8") as f:
    data = json.load(f)

for item in data["clips"]:
    category = item.get("category")
    url = item.get("url")

    if category not in ("kids", "gaming"):
        print("Skipped: invalid category")
        continue

    if item.get("permission") is not True or not url:
        print("Skipped: permission or URL missing")
        continue

    folder = ROOT / "downloads" / category
    folder.mkdir(parents=True, exist_ok=True)

    command = [
        "yt-dlp",
        "--no-playlist",
        "-f", "bv*+ba/b",
        "--merge-output-format", "mp4",
        "-o", str(folder / "%(title).80s.%(ext)s"),
        url
    ]

    subprocess.run(command)

print("Download queue finished.")
