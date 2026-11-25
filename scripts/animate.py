from PIL import Image
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
scene = Image.open(ROOT / "output/kids/scene.png").convert("RGB")
frames = ROOT / "output/kids/frames"
frames.mkdir(parents=True, exist_ok=True)

for i in range(60):
    frame = scene.copy()
    bunny = scene.crop((460, 260, 700, 550))
    y = int(12 * abs(__import__("math").sin(i * 0.22)))
    frame.paste(scene.crop((0, 260, 1280, 550)), (0, 260))
    frame.paste(bunny, (460, 260-y))
    frame.save(frames / f"{i:03}.png")

subprocess.run([
    "ffmpeg", "-y", "-framerate", "15",
    "-i", str(frames / "%03d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    str(ROOT / "output/kids/animation.mp4")
], check=True)

print("Bunny animation ready!")
