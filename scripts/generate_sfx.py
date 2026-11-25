from pathlib import Path
import json, math, wave, struct, subprocess, random

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
story_file = OUT / "story.json"
audio = OUT / "final_audio.mp3"
sfx = OUT / "scene_sfx.wav"
temp = OUT / "audio_sfx_mix.mp3"

scenes = json.loads(story_file.read_text(encoding="utf-8")).get("scenes", [])

p = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
    capture_output=True, text=True, check=True
)
duration = float(p.stdout.strip())

rate = 22050
total_samples = int(duration * rate)
buffer = [0.0] * total_samples

effects = {
    "notice": (880, 1200),
    "find": (1000, 1400),
    "search": (550, 850),
    "help": (660, 880),
    "celebrate": (1100, 1500),
    "finish": (900, 1400),
    "bloom": (700, 1100),
    "play": (600, 1000),
    "picnic": (500, 850),
    "water": (500, 750),
    "rain": (350, 550),
    "worry": (420, 600),
    "think": (650, 900),
    "plan": (600, 900),
    "clean": (750, 1000),
    "practice": (700, 950),
    "home": (500, 700),
    "intro": (700, 1000),
    "lesson": (750, 1100),
    "teamwork": (800, 1200)
}

scene_duration = duration / max(1, len(scenes))

for i, scene in enumerate(scenes):
    action = str(scene.get("visual", "intro")).lower()
    freqs = effects.get(action, (600, 900))
    start = int((i * scene_duration + scene_duration * 0.5) * rate)
    length = int(0.22 * rate)

    for j in range(length):
        pos = start + j
        if pos >= total_samples:
            break

        t = j / rate
        fade = min(1.0, j / 500) * max(0, 1 - j / length)
        tone = (
            math.sin(2 * math.pi * freqs[0] * t) +
            0.5 * math.sin(2 * math.pi * freqs[1] * t)
        )
        buffer[pos] += tone * fade * 0.055

with wave.open(str(sfx), "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(rate)
    f.writeframes(b"".join(
        struct.pack("<h", max(-32767, min(32767, int(x * 32767))))
        for x in buffer
    ))

subprocess.run([
    "ffmpeg", "-y", "-i", str(audio), "-i", str(sfx),
    "-filter_complex", "[1:a]volume=0.35[s];[0:a][s]amix=inputs=2:duration=first:dropout_transition=1[a]",
    "-map", "[a]", "-c:a", "libmp3lame", "-q:a", "4", str(temp)
], check=True)

temp.replace(audio)
print("Scene sound effects mixed successfully.")
