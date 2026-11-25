from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
CATEGORY = sys.argv[1] if len(sys.argv) > 1 else "gaming"

if CATEGORY not in ("kids", "gaming"):
    raise SystemExit("Use: python scripts/editor.py kids OR gaming")

SOURCE = ROOT / "clips" / CATEGORY
OUTPUT = ROOT / "output" / CATEGORY / "final_video.mp4"

files = sorted(
    p for p in SOURCE.iterdir()
    if p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")
)

if not files:
    raise SystemExit(f"No clips found in {SOURCE}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
list_file = ROOT / "output" / "filelist.txt"

with list_file.open("w", encoding="utf-8") as f:
    for path in files:
        safe_path = str(path.resolve()).replace("'", "'\\''")
        f.write(f"file '{safe_path}'\n")

cmd = [
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", str(list_file),
    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30",
    "-c:v", "libx264", "-preset", "ultrafast",
    "-pix_fmt", "yuv420p", "-c:a", "aac",
    str(OUTPUT)
]

subprocess.run(cmd, check=True)
print(f"Video created: {OUTPUT}")
