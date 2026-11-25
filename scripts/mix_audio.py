from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent

voice = ROOT / "output/kids/voice.mp3"
music = ROOT / "assets/music/cartoon_60s.mp3"
output = ROOT / "output/kids/final_audio.mp3"

cmd = [
    "ffmpeg", "-y",
    "-i", str(voice),
    "-i", str(music),
    "-filter_complex",
    "[0:a]volume=1.0[v];[1:a]volume=0.12[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2",
    "-c:a", "libmp3lame", "-q:a", "4",
    str(output)
]

subprocess.run(cmd, check=True)
print(f"Audio ready: {output}")
