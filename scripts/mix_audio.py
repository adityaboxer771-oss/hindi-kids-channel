from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent

voice = ROOT / "output/kids/voice.mp3"
music = ROOT / "assets/music/cartoon_60s.mp3"
output = ROOT / "output/kids/final_audio.mp3"

output.parent.mkdir(parents=True, exist_ok=True)

if not voice.exists():
    raise FileNotFoundError("Voice file missing")

if not music.exists():
    raise FileNotFoundError("Background music missing")

cmd = [
    "ffmpeg", "-y",
    "-i", str(voice),
    "-i", str(music),
    "-filter_complex",
    "[0:a]volume=1.0[v];"
    "[1:a]volume=0.10[m];"
    "[v][m]amix=inputs=2:duration=first:dropout_transition=2[a]",
    "-map", "[a]",
    "-c:a", "libmp3lame",
    "-q:a", "4",
    str(output)
]

subprocess.run(cmd, check=True)
print("Final narration + background music ready.")
