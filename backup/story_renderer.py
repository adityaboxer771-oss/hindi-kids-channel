from PIL import Image, ImageDraw
from pathlib import Path
import math, subprocess

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
FRAMES = OUT / "story_frames"
FRAMES.mkdir(parents=True, exist_ok=True)

W, H, FPS = 1280, 720, 15
SCENES = [
    "Ek sundar jungle",
    "Chintu khargosh",
    "Chhota panchi",
    "Dono ki dosti",
    "Khushi ka ant"
]

def draw_scene(scene, frame):
    im = Image.new("RGB", (W, H), "#8edcff")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 480, W, H), fill="#72c96b")
    d.ellipse((-150, 350, 600, 850), fill="#4eae62")
    d.ellipse((650, 350, 1450, 850), fill="#399b58")
    d.ellipse((1020, 60, 1150, 190), fill="#ffdf55")

    # Trees
    for x in [100, 1050, 1150]:
        d.rectangle((x+35, 340, x+65, 520), fill="#80552d")
        d.ellipse((x, 230, x+100, 390), fill="#23834c")

    # Bunny
    bounce = int(12 * abs(math.sin(frame * .16)))
    x = 480 + int(18 * math.sin(frame * .07))
    y = 270 - bounce
    d.ellipse((x+15, y-95, x+65, y+55), fill="#fff1dc", outline="#795548", width=4)
    d.ellipse((x+75, y-95, x+125, y+55), fill="#fff1dc", outline="#795548", width=4)
    d.ellipse((x, y, x+140, y+170), fill="#fff1dc", outline="#795548", width=4)
    d.ellipse((x+35, y+55, x+48, y+70), fill="#222")
    d.ellipse((x+92, y+55, x+105, y+70), fill="#222")
    d.ellipse((x+63, y+85, x+78, y+98), fill="#ff8b9c")

    # Bird
    bx = 760 + int(35 * math.sin(frame * .12))
    by = 310 + int(12 * math.sin(frame * .2))
    d.ellipse((bx, by, bx+90, by+65), fill="#ffca45", outline="#9b6722", width=3)
    d.ellipse((bx+60, by+5, bx+72, by+17), fill="#222")
    d.polygon([(bx+85, by+25), (bx+115, by+35), (bx+85, by+43)], fill="#ff813d")
    d.ellipse((bx+20, by+25, bx+60, by+55), fill="#f39b31")

    d.rounded_rectangle((250, 25, 1030, 95), radius=25, fill="white")
    d.text((350, 48), SCENES[scene], fill="#285b91")
    return im

for i in range(330):
    scene = min(i // 66, 4)
    draw_scene(scene, i).save(FRAMES / f"{i:04d}.png")

video = OUT / "story_animation.mp4"
subprocess.run([
    "ffmpeg", "-y", "-framerate", str(FPS),
    "-i", str(FRAMES / "%04d.png"),
    "-c:v", "libx264", "-pix_fmt", "yuv420p",
    str(video)
], check=True)

print("5-scene cartoon ready:", video)
