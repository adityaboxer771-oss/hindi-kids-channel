from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess, shutil, json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
FRAMES = OUT / "short_frames"

W, H = 540, 960
FPS = 15
DURATION = 22
TOTAL = FPS * DURATION

OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

data = json.loads((OUT / "story.json").read_text(encoding="utf-8")) if (OUT / "story.json").exists() else {}
story_text = data.get("story", "एक समय की बात है। सभी दोस्त मिलकर खुश रहते थे।")
title = data.get("title", "प्यारी कहानी")

font_paths = [
    "/system/fonts/NotoSansDevanagari-VF.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]
font_path = next((p for p in font_paths if Path(p).exists()), None)
if not font_path:
    raise SystemExit("Hindi font nahi mila")

font = ImageFont.truetype(font_path, 25)
title_font = ImageFont.truetype(font_path, 30)

def wrap(text, f, max_width):
    lines, line = [], ""
    for word in text.split():
        test = (line + " " + word).strip()
        if f.getlength(test) <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return "\n".join(lines)

sentences = [s.strip() for s in story_text.replace("\n", " ").split("।") if s.strip()]
captions = []
for sentence in sentences:
    words = sentence.split()
    for i in range(0, len(words), 5):
        captions.append(" ".join(words[i:i+5]))
if not captions:
    captions = ["एक प्यारी कहानी"]

def animal(d, kind, x, y, t):
    bounce = int(math.sin(t * 5) * 7)
    y += bounce
    colors = {
        "bunny": "#eeeeee",
        "mouse": "#b9a0a0",
        "parrot": "#35bd65",
        "cat": "#f4a45c",
        "panda": "#eeeeee"
    }
    c = colors[kind]

    # Body and head
    d.ellipse((x-27,y-5,x+27,y+65), fill=c, outline="#444444", width=2)
    d.ellipse((x-29,y-48,x+29,y+12), fill=c, outline="#444444", width=2)

    if kind == "bunny":
        d.ellipse((x-22,y-95,x-5,y-38), fill=c, outline="#444444")
        d.ellipse((x+5,y-95,x+22,y-38), fill=c, outline="#444444")
        d.ellipse((x-15,y-88,x-9,y-45), fill="#f3a5b7")
        d.ellipse((x+9,y-88,x+15,y-45), fill="#f3a5b7")
        eye = "#111111"
    elif kind == "mouse":
        d.ellipse((x-48,y-60,x-12,y-25), fill="#d98eaa", outline="#444444")
        d.ellipse((x+12,y-60,x+48,y-25), fill="#d98eaa", outline="#444444")
        eye = "#111111"
    elif kind == "parrot":
        d.ellipse((x-20,y-65,x+28,y-20), fill="#35bd65")
        d.polygon([(x+25,y-48),(x+49,y-38),(x+25,y-30)], fill="#ffae24")
        d.polygon([(x-25,y+5),(x-52,y+25),(x-18,y+35)], fill="#168cba")
        eye = "#111111"
    elif kind == "cat":
        d.polygon([(x-27,y-38),(x-25,y-72),(x-2,y-45)], fill=c, outline="#444444")
        d.polygon([(x+2,y-45),(x+25,y-72),(x+27,y-38)], fill=c, outline="#444444")
        eye = "#111111"
    else:
        d.ellipse((x-45,y-65,x-10,y-30), fill="#222222")
        d.ellipse((x+10,y-65,x+45,y-30), fill="#222222")
        d.ellipse((x-17,y-25,x-5,y-9), fill="#222222")
        d.ellipse((x+5,y-25,x+17,y-9), fill="#222222")
        eye = "#ffffff"

    d.ellipse((x-14,y-28,x-7,y-20), fill=eye)
    d.ellipse((x+7,y-28,x+14,y-20), fill=eye)
    d.ellipse((x-5,y-14,x+5,y-7), fill="#ed8ba0")
    d.line((x-5,y-2,x+5,y-2), fill="#444444", width=2)

    # Feet
    d.ellipse((x-32,y+52,x-5,y+68), fill=c, outline="#444444")
    d.ellipse((x+5,y+52,x+32,y+68), fill=c, outline="#444444")

def make_frame(i):
    t = i / FPS
    scene = min(int(t / (DURATION / 5)), 4)

    backgrounds = ["#87ceeb", "#a8ddff", "#ffdc9c", "#a9e8c0", "#b9a9ee"]
    img = Image.new("RGB", (W,H), backgrounds[scene])
    d = ImageDraw.Draw(img)

    # Sun and clouds
    d.ellipse((410,65,490,145), fill="#ffe66d")
    for x,y in [(45,210),(300,170),(180,300)]:
        d.ellipse((x,y,x+90,y+35), fill="white")
        d.ellipse((x+20,y-18,x+70,y+35), fill="white")

    # Hills and trees
    d.ellipse((-100,490,330,900), fill="#72c875")
    d.ellipse((200,510,650,920), fill="#3b9e60")
    for x,y in [(45,560),(465,540),(390,650)]:
        d.rectangle((x-8,y,x+8,y+120), fill="#80552e")
        d.ellipse((x-42,y-65,x+42,y+25), fill="#238b45")

    d.rectangle((0,760,W,H), fill="#319b55")

    # Five friends
    positions = [65,168,270,372,475]
    kinds = ["bunny","mouse","parrot","cat","panda"]

    for j, (x,kind) in enumerate(zip(positions,kinds)):
        animal(d, kind, x, 690 + (j % 2)*5, t + j)

    # Story title
    title_text = wrap(title, title_font, 460)
    d.rounded_rectangle((15,45,W-15,150), radius=22, fill="white")
    tb = d.multiline_textbbox((0,0), title_text, font=title_font, spacing=5, align="center")
    th = tb[3]-tb[1]
    d.multiline_text((W/2,98-th/2), title_text, font=title_font, fill="#174b32", anchor="ma", align="center", spacing=5)

    # Story captions
    index = min(int(t / (DURATION / len(captions))), len(captions)-1)
    caption = wrap(captions[index], font, 460)
    d.rounded_rectangle((15,805,W-15,940), radius=22, fill="white")
    d.multiline_text((W/2,872), caption, font=font, fill="#202020", anchor="mm", align="center", spacing=8)

    img.save(FRAMES / f"frame_{i:04d}.jpg", quality=88)

print("Making five-character cartoon...")
for i in range(TOTAL):
    make_frame(i)

video = OUT / "short_video.mp4"
audio = OUT / "final_audio.mp3"
final = OUT / "short_final.mp4"

subprocess.run([
    "ffmpeg","-y",
    "-framerate",str(FPS),
    "-i",str(FRAMES / "frame_%04d.jpg"),
    "-vf","scale=1080:1920",
    "-c:v","libx264",
    "-pix_fmt","yuv420p",
    str(video)
], check=True)

if audio.exists():
    subprocess.run([
        "ffmpeg","-y",
        "-i",str(video),
        "-i",str(audio),
        "-map","0:v","-map","1:a",
        "-c:v","copy","-c:a","aac",
        "-shortest",str(final)
    ], check=True)
else:
    shutil.copy(video,final)

print("SHORT READY:",final)
