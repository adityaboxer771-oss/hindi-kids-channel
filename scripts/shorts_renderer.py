from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess, shutil, json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
FRAMES = OUT / "short_frames"
W, H, FPS = 540, 960, 15

OUT.mkdir(parents=True, exist_ok=True)
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True, exist_ok=True)

data = json.loads((OUT / "story.json").read_text(encoding="utf-8"))
scenes = data.get("scenes", [])
title = data.get("title", "प्यारी कहानी")
chars = data.get("characters", [])
story = data.get("story", "")

font_paths = [
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/system/fonts/NotoSansDevanagari-VF.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]
fp = next((p for p in font_paths if Path(p).exists()), None)
if not fp:
    raise SystemExit("Hindi font nahi mila")

font = ImageFont.truetype(fp, 25)
small = ImageFont.truetype(fp, 21)
title_font = ImageFont.truetype(fp, 30)

audio = OUT / "final_audio.mp3"
duration = 22
if audio.exists():
    try:
        p = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of",
             "default=noprint_wrappers=1:nokey=1", str(audio)],
            capture_output=True, text=True, check=True
        )
        duration = max(10, int(float(p.stdout.strip()) + 1))
    except Exception:
        pass

total = duration * FPS
scene_count = max(1, len(scenes))
scene_seconds = duration / scene_count

def wrap(txt, f, width):
    lines, line = [], ""
    for word in txt.split():
        test = (line + " " + word).strip()
        if f.getlength(test) <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return "\n".join(lines)

animal_colors = {
    "bunny": "#eeeeee", "mouse": "#c9a3a3",
    "panda": "#eeeeee", "parrot": "#40bb62",
    "cat": "#f4a45c", "squirrel": "#bc7848",
    "turtle": "#83b56b"
}

def draw_animal(d, kind, x, y, t, action, scale=1):
    c = animal_colors.get(kind, "#e8c18c")
    jump = abs(math.sin(t * 4)) * 14 if action in ("play", "celebrate", "bloom") else math.sin(t * 2) * 5
    y -= jump

    def el(box, fill, outline="#444444"):
        d.ellipse(tuple(int(v) for v in box), fill=fill, outline=outline, width=2)

    # Body and head
    el((x-28*scale,y-5*scale,x+28*scale,y+60*scale), c)
    el((x-32*scale,y-60*scale,x+32*scale,y+8*scale), c)

    if kind == "bunny":
        el((x-22*scale,y-115*scale,x-5*scale,y-45*scale),c)
        el((x+5*scale,y-115*scale,x+22*scale,y-45*scale),c)
        el((x-17*scale,y-100*scale,x-10*scale,y-52*scale),"#f3a5b7")
        el((x+10*scale,y-100*scale,x+17*scale,y-52*scale),"#f3a5b7")
    elif kind == "mouse":
        el((x-48*scale,y-65*scale,x-12*scale,y-28*scale),"#d98eaa")
        el((x+12*scale,y-65*scale,x+48*scale,y-28*scale),"#d98eaa")
    elif kind == "cat":
        d.polygon([(x-28*scale,y-38*scale),(x-25*scale,y-75*scale),(x-3*scale,y-45*scale)],fill=c,outline="#444444")
        d.polygon([(x+28*scale,y-38*scale),(x+25*scale,y-75*scale),(x+3*scale,y-45*scale)],fill=c,outline="#444444")
    elif kind == "parrot":
        d.polygon([(x+22*scale,y-45*scale),(x+48*scale,y-35*scale),(x+22*scale,y-25*scale)],fill="#ffae24")
        d.polygon([(x-20*scale,y+10*scale),(x-48*scale,y+25*scale),(x-18*scale,y+35*scale)],fill="#168cba")
    elif kind == "panda":
        el((x-43*scale,y-65*scale,x-10*scale,y-28*scale),"#222222")
        el((x+10*scale,y-65*scale,x+43*scale,y-28*scale),"#222222")
        el((x-18*scale,y-25*scale,x-5*scale,y-9*scale),"#222222")
        el((x+5*scale,y-25*scale,x+18*scale,y-9*scale),"#222222")
    elif kind == "squirrel":
        el((x+20*scale,y-65*scale,x+50*scale,y-25*scale),"#bc7848")
    elif kind == "turtle":
        el((x-35*scale,y-5*scale,x+35*scale,y+45*scale),"#588c48")

    # Face
    el((x-14*scale,y-30*scale,x-7*scale,y-20*scale),"#222222")
    el((x+7*scale,y-30*scale,x+14*scale,y-20*scale),"#222222")
    el((x-5*scale,y-14*scale,x+5*scale,y-7*scale),"#ed8ba0")
    d.arc((x-10*scale,y-8*scale,x+10*scale,y+5*scale),0,180,fill="#444444",width=2)

    # Feet
    el((x-32*scale,y+50*scale,x-5*scale,y+68*scale),c)
    el((x+5*scale,y+50*scale,x+32*scale,y+68*scale),c)

    # Animated arm
    arm = math.sin(t*5)*20
    d.line((x-25*scale,y+5*scale,x-48*scale,y+15*scale+arm),fill="#444444",width=4)
    d.line((x+25*scale,y+5*scale,x+48*scale,y+15*scale-arm),fill="#444444",width=4)

def background(d, kind, t):
    palettes = {
        "forest": ("#87ceeb","#72c875"),
        "garden": ("#a8ddff","#69c987"),
        "river": ("#91d8ff","#65b8c4"),
        "village": ("#ffdc9c","#c7b777"),
        "hills": ("#b9a9ee","#83bb80")
    }
    sky, green = palettes.get(kind, palettes["forest"])
    d.rectangle((0,0,W,H),fill=sky)

    # Sun
    sx = 420 + int(math.sin(t*.3)*12)
    d.ellipse((sx-35,65,sx+35,135),fill="#ffe66d")

    # Clouds
    for x,y in [(40,200),(300,160),(180,300)]:
        shift = int(math.sin(t*.4+x)*12)
        d.ellipse((x+shift,y,x+shift+90,y+35),fill="white")
        d.ellipse((x+shift+20,y-18,x+shift+70,y+35),fill="white")

    d.ellipse((-100,490,330,900),fill=green)
    d.ellipse((200,510,650,920),fill="#399b58")

    for x,y in [(45,560),(465,540),(390,650)]:
        d.rectangle((x-8,y,x+8,y+120),fill="#80552e")
        d.ellipse((x-42,y-65,x+42,y+25),fill="#238b45")

    d.rectangle((0,760,W,H),fill="#319b55")

def make_frame(i):
    t = i/FPS
    si = min(int(t/scene_seconds), scene_count-1)
    scene = scenes[si]
    visual = scene.get("visual", "intro")

    img = Image.new("RGB",(W,H))
    d = ImageDraw.Draw(img)
    background(d, data.get("background","forest"),t)

    # Scene-specific movement
    center = 270 + math.sin(t*1.4)*30
    if visual in ("search","find","notice","worry"):
        center += math.sin(t*2)*20
    elif visual in ("play","celebrate","bloom"):
        center += math.sin(t*4)*35

    positions = [center-100, center+100]
    for j,ch in enumerate(chars[:2]):
        kind = ch.get("animal","bunny")
        x = max(65,min(W-65,positions[j]))
        draw_animal(d,kind,x,690+j*8,t+j,visual)

    # Title
    title_text = wrap(title,title_font,460)
    d.rounded_rectangle((15,45,W-15,150),radius=22,fill="white")
    d.multiline_text((W/2,98),title_text,font=title_font,
                     fill="#174b32",anchor="mm",align="center",spacing=5)

    # Captions
    caption = wrap(scene.get("text",story),font,460)
    d.rounded_rectangle((15,790,W-15,945),radius=22,fill="white")
    d.multiline_text((W/2,865),caption,font=font,
                     fill="#202020",anchor="mm",align="center",spacing=8)

    # Scene marker
    d.rounded_rectangle((215,165,325,205),radius=15,fill="white")
    d.text((270,185),f"Scene {si+1}/{scene_count}",fill="#174b32",anchor="mm")

    img.save(FRAMES/f"frame_{i:04d}.jpg",quality=88)

print("Rendering story-based cartoon...")
for i in range(total):
    make_frame(i)

video = OUT/"short_video.mp4"
final = OUT/"short_final.mp4"

subprocess.run([
    "ffmpeg","-y","-framerate",str(FPS),
    "-i",str(FRAMES/"frame_%04d.jpg"),
    "-vf","scale=1080:1920",
    "-c:v","libx264","-pix_fmt","yuv420p",
    str(video)
],check=True)

if audio.exists():
    subprocess.run([
        "ffmpeg","-y","-i",str(video),"-i",str(audio),
        "-map","0:v","-map","1:a",
        "-c:v","copy","-c:a","aac","-shortest",
        str(final)
    ],check=True)
else:
    shutil.copy(video,final)

print("SHORT READY:",final)
