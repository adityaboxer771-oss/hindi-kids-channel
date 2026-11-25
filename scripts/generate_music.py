import math
import wave
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
folder = ROOT / "assets/music"
folder.mkdir(parents=True, exist_ok=True)

wavfile = folder / "original_music.wav"
mp3file = folder / "cartoon_60s.mp3"

sr = 22050
duration = 60
volume = 0.10

# Original soft cartoon chord progression
chords = [
    [261.63, 329.63, 392.00],
    [220.00, 261.63, 329.63],
    [174.61, 220.00, 261.63],
    [196.00, 246.94, 293.66],
]

samples = []

for i in range(sr * duration):
    t = i / sr
    chord = chords[int(t // 4) % len(chords)]
    local = t % 4

    fade = min(1.0, local / 0.4, (4 - local) / 0.4)
    fade = max(0.0, fade)

    sound = 0
    for f in chord:
        sound += math.sin(2 * math.pi * f * t)

    sound /= len(chord)
    sound *= fade * volume

    samples.append(int(max(-1, min(1, sound)) * 32767))

with wave.open(str(wavfile), "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(struct.pack("<" + "h" * len(samples), *samples))

subprocess.run([
    "ffmpeg", "-y", "-i", str(wavfile),
    "-codec:a", "libmp3lame", "-q:a", "5",
    str(mp3file)
], check=True)

wavfile.unlink(missing_ok=True)
print("Original background music generated.")
