from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math
import subprocess
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
FRAMES = OUT / "short_frames"

W, H = 540, 960
FPS = 15
DURATION = 22
TOTAL = FPS * DURATION

OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

story = [
    "एक समय की बात है",
    "सुंदर जंगल में चिंटू नाम का",
    "एक प्यारा खरगोश रहता था",
    "उसे नए दोस्त बनाना पसंद था",
    "एक दिन उसे छोटा पंछी मिला",
    "जो रास्ता भटक गया था",
    "चिंटू ने उसकी मदद की",
    "और दोनों अच्छे दोस्त बन गए"
]

font_paths = [
    "/system/fonts/NotoSansDevanagari-VF.ttf",
    "/system/fonts/NotoSansDevanagariUI-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]

font_path = next((p for p in font_paths if Path(p).exists()), None)
if not font_path:
    raise SystemExit("Hindi font nahi mila. Screenshot bhejna.")

font = ImageFont.truetype(font_path, 27)
title_font = ImageFont.truetype(font_path, 34)

def draw_bunny(draw, x, y, t):
    bounce = int(math.sin(t * 5) * 9)
    y += bounce

    draw.ellipse((x-48, y-55, x+48, y+55), fill="#eeeeee")
    draw.ellipse((x-38, y-115, x-12, y-35), fill="#eeeeee")
    draw.ellipse((x+12, y-115, x+38, y-35), fill="#eeeeee")
    draw.ellipse((x-30, y-105, x-19, y-45), fill="#f4a6b8")
    draw.ellipse((x+19, y-105, x+30, y-45), fill="#f4a6b8")
    draw.ellipse((x-20, y-15, x-10, y-3), fill="black")
    draw.ellipse((x+10, y-15, x+20, y-3), fill="black")
    draw.ellipse((x-6, y+2, x+6, y+11), fill="#ed8ba0")
    draw.ellipse((x-65, y+35, x-25, y+75), fill="#eeeeee")
    draw.ellipse((x+25, y+35, x+65, y+75), fill="#eeeeee")

def draw_bird(draw, x, y, t):
    flap = int(math.sin(t * 10) * 10)
    draw.ellipse((x-35, y-25, x+35, y+25), fill="#ffcc33")
    draw.ellipse((x+10, y-48, x+52, y-5), fill="#ffcc33")
    draw.ellipse((x+30, y-35, x+38, y-27), fill="black")
    draw.polygon([(x+50,y-25),(x+75,y-15),(x+50,y-8)], fill="#ff8844")
    draw.ellipse((x-20, y-5-flap, x+12, y+15+flap), fill="#f5a623")

def make_frame(i):
    t = i / FPS
    img = Image.new("RGB", (W, H), "#87ceeb")
    d = ImageDraw.Draw(img)

    # Sky and clouds
    d.ellipse((40, 90, 150, 200), fill="#fff3a6")
    for x, y in [(80,260),(360,180),(300,350)]:
        d.ellipse((x,y,x+100,y+45), fill="white")
        d.ellipse((x+25,y-20,x+85,y+45), fill="white")

    # Forest hills and trees
    d.ellipse((-150, 530, 350, 1000), fill="#63bd65")
    d.ellipse((180, 520, 700, 1050), fill="#319b55")

    for x, y in [(60,560),(440,530),(420,700)]:
        d.rectangle((x-9,y,x+9,y+120), fill="#80552e")
        d.ellipse((x-55,y-75,x+55,y+35), fill="#238b45")

    # Ground
    d.rectangle((0,800,W,H), fill="#319b55")

    # Five animated story scenes
    scene = min(int(t / (DURATION / 5)), 4)
    bunny_x = [620, 420, 250, 250, 320][scene]
    bunny_y = [680, 680, 700, 680, 680][scene]
    draw_bunny(d, bunny_x, bunny_y, t + scene)
    bird_x = [620, 500, 350, 300, 390][scene] + int(math.sin(t*3)*35)
    bird_y = [300, 380, 470, 590, 500][scene] + int(math.sin(t*4)*18)
    if scene >= 2:
        draw_bird(d, bird_x, bird_y, t)

    # Story captions
    index = min(int(t / (DURATION / len(story))), len(story)-1)
    caption = story[index]

    d.rounded_rectangle((22, 90, W-22, 190), radius=24, fill="#ffffff")
    box = d.textbbox((0,0), "चिंटू की कहानी", font=title_font)
    tw = box[2] - box[0]
    d.text(((W-tw)//2, 118), "चिंटू की कहानी", font=title_font, fill="#174b32")

    d.rounded_rectangle((18, 825, W-18, 935), radius=25, fill="#ffffff")
    box = d.textbbox((0,0), caption, font=font)
    tw = box[2] - box[0]
    d.text(((W-tw)//2, 865), caption, font=font, fill="#202020")

    img.save(FRAMES / f"frame_{i:04d}.jpg", quality=88)

print("Making cartoon frames...")
for i in range(TOTAL):
    make_frame(i)

video = OUT / "short_video.mp4"
audio = OUT / "final_audio.mp3"
final = OUT / "short_final.mp4"

subprocess.run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", str(FRAMES / "frame_%04d.jpg"),
    "-vf", "scale=1080:1920",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    str(video)
], check=True)

if audio.exists():
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(audio),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac",
        "-shortest", str(final)
    ], check=True)
else:
    shutil.copy(video, final)

print("SHORT READY:", final)
import json
