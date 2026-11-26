from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess, shutil, json, random

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
FRAMES = OUT / "short_frames"
W, H, FPS = 540, 960, 15
TRANSITION = 0.4

OUT.mkdir(parents=True, exist_ok=True)
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True, exist_ok=True)

data = json.loads((OUT / "story.json").read_text(encoding="utf-8"))
scenes = data.get("scenes", [])
title = data.get("title", "प्यारी कहानी")
chars = data.get("characters", [])
story = data.get("story", "")
bg_kind = data.get("background", "forest")

font_paths = [
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/system/fonts/NotoSansDevanagari-VF.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
]
fp = next((p for p in font_paths if Path(p).exists()), None)
if not fp:
    raise SystemExit("Hindi font nahi mila")

font = ImageFont.truetype(fp, 25)
small = ImageFont.truetype(fp, 19)
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
    for word in str(txt).split():
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

colors = {
    "bunny": "#f1eeee", "mouse": "#d5a6ad",
    "panda": "#eeeeee", "parrot": "#48bd64",
    "cat": "#f5a35c", "squirrel": "#bd7849",
    "turtle": "#8bc26c"
}

def ellipse(d, box, fill, outline="#4a4038", width=2):
    d.ellipse(tuple(int(v) for v in box), fill=fill,
              outline=outline, width=width)

def draw_animal(d, kind, x, y, t, action, scale=1):
    c = colors.get(kind, "#e8c18c")
    bounce = abs(math.sin(t * 4)) * 18 if action in (
        "play", "celebrate", "bloom", "help"
    ) else math.sin(t * 2) * 7
    y -= bounce
    s = scale

    if kind in ("cat", "squirrel"):
        d.arc((x+20*s, y+15*s, x+75*s, y+100*s),
              180, 320, fill=c, width=max(3, int(9*s)))

    if kind == "turtle":
        ellipse(d, (x-40*s, y+5*s, x+40*s, y+55*s), "#598d49")

    ellipse(d, (x-28*s, y-5*s, x+28*s, y+60*s), c)
    ellipse(d, (x-36*s, y-65*s, x+36*s, y+10*s), c)

    if kind == "bunny":
        ellipse(d, (x-23*s, y-120*s, x-5*s, y-45*s), c)
        ellipse(d, (x+5*s, y-120*s, x+23*s, y-45*s), c)
        ellipse(d, (x-17*s, y-105*s, x-10*s, y-55*s), "#eaa1b2")
        ellipse(d, (x+10*s, y-105*s, x+17*s, y-55*s), "#eaa1b2")

    elif kind == "mouse":
        ellipse(d, (x-50*s, y-70*s, x-12*s, y-30*s), "#dc91a6")
        ellipse(d, (x+12*s, y-70*s, x+50*s, y-30*s), "#dc91a6")

    elif kind == "cat":
        d.polygon([(x-30*s,y-40*s),(x-30*s,y-78*s),
                   (x-5*s,y-45*s)], fill=c, outline="#4a4038")
        d.polygon([(x+30*s,y-40*s),(x+30*s,y-78*s),
                   (x+5*s,y-45*s)], fill=c, outline="#4a4038")

    elif kind == "parrot":
        d.polygon([(x+20*s,y-45*s),(x+48*s,y-35*s),
                   (x+20*s,y-25*s)], fill="#ffb62d")
        d.polygon([(x-18*s,y+10*s),(x-45*s,y+38*s),
                   (x-12*s,y+30*s)], fill="#2988b7")

    elif kind == "panda":
        ellipse(d, (x-43*s,y-65*s,x-10*s,y-28*s), "#222222")
        ellipse(d, (x+10*s,y-65*s,x+43*s,y-28*s), "#222222")

    elif kind == "squirrel":
        ellipse(d, (x+22*s,y-72*s,x+48*s,y-35*s), c)
        ellipse(d, (x-48*s,y-72*s,x-22*s,y-35*s), c)

    elif kind == "turtle":
        ellipse(d, (x-35*s,y-5*s,x+35*s,y+45*s), "#578b46")

    blink = (int(t*3 + x) % 17 == 0)
    if blink:
        d.line((x-15*s,y-30*s,x-6*s,y-30*s), fill="#222222", width=3)
        d.line((x+6*s,y-30*s,x+15*s,y-30*s), fill="#222222", width=3)
    else:
        ellipse(d, (x-15*s,y-34*s,x-6*s,y-20*s), "#222222")
        ellipse(d, (x+6*s,y-34*s,x+15*s,y-20*s), "#222222")
        ellipse(d, (x-12*s,y-32*s,x-9*s,y-27*s), "white", width=0)
        ellipse(d, (x+9*s,y-32*s,x+12*s,y-27*s), "white", width=0)

    ellipse(d, (x-5*s,y-13*s,x+5*s,y-7*s), "#ec8c9f")
    d.arc((x-12*s,y-8*s,x+12*s,y+9*s), 0, 180,
          fill="#444444", width=2)

    ellipse(d, (x-32*s,y+50*s,x-5*s,y+68*s), c)
    ellipse(d, (x+5*s,y+50*s,x+32*s,y+68*s), c)

    arm = math.sin(t*5)*22
    d.line((x-25*s,y+8*s,x-48*s,y+18*s+arm*s),
           fill="#4a4038", width=max(3,int(5*s)))
    d.line((x+25*s,y+8*s,x+48*s,y+18*s-arm*s),
           fill="#4a4038", width=max(3,int(5*s)))

def background(d, kind, t):
    palettes = {
        "forest": ("#87ceeb","#72c875"),
        "garden": ("#a8ddff","#69c987"),
        "river": ("#91d8ff","#65b8c4"),
        "village": ("#ffdc9c","#c7b777"),
        "hills": ("#b9a9ee","#83bb80")
    }
    sky, green = palettes.get(kind, palettes["forest"])
    d.rectangle((0,0,W,H), fill=sky)

    sx = 420 + int(math.sin(t*.3)*18)
    ellipse(d, (sx-40,65,sx+40,145), "#ffe66d", width=0)

    for x,y in [(40,200),(300,160),(180,300)]:
        shift = int((t*12+x) % 600)-80
        ellipse(d, (shift,y,shift+90,y+35), "white", width=0)
        ellipse(d, (shift+20,y-18,shift+70,y+35), "white", width=0)

    d.ellipse((-100,490,330,900), fill=green)
    d.ellipse((200,510,650,920), fill="#399b58")

    for x,y in [(45,560),(465,540),(390,650)]:
        d.rectangle((x-8,y,x+8,y+120), fill="#80552e")
        ellipse(d, (x-42,y-65,x+42,y+25), "#238b45", width=0)

    d.rectangle((0,760,W,H), fill="#319b55")

    random.seed(7)
    for k in range(14):
        px = (k*41 + int(t*18)) % W
        py = 430 + (k*57 % 330) + math.sin(t+k)*8
        ellipse(d, (px-4,py-4,px+4,py+4),
               "#fff3a5" if k%2 else "#ffffff", width=0)

def make_scene_frame(i, si):
    t = i/FPS
    si = max(0, min(si, scene_count-1))
    scene = scenes[si] if scenes else {}
    visual = scene.get("visual", "intro")

    img = Image.new("RGB", (W,H))
    d = ImageDraw.Draw(img)
    background(d, bg_kind, t)

    center = 270 + math.sin(t*1.4)*35
    if visual in ("search","find","notice","worry"):
        center += math.sin(t*2)*22
    elif visual in ("play","celebrate","bloom","help"):
        center += math.sin(t*4)*38

    positions = [center-100, center+100]
    for j,ch in enumerate(chars[:2]):
        kind = ch.get("animal", "bunny")
        x = max(70,min(W-70,positions[j]))
        draw_animal(d, kind, x, 700+j*8, t+j, visual)

    title_text = wrap(title, title_font, 460)
    d.rounded_rectangle((15,40,W-15,150),radius=22,fill="#ffffff")
    d.multiline_text((W/2,95),title_text,font=title_font,
                     fill="#174b32",anchor="mm",align="center",spacing=5)

    caption = wrap(scene.get("text",story),font,460)
    d.rounded_rectangle((15,790,W-15,945),radius=22,fill="#ffffff")
    d.multiline_text((W/2,865),caption,font=font,
                     fill="#202020",anchor="mm",align="center",spacing=8)

    d.rounded_rectangle((205,165,335,205),radius=15,fill="white")
    d.text((270,185),f"Scene {si+1}/{scene_count}",
           fill="#174b32",font=small,anchor="mm")

    return img

def make_frame(i):
    t = i/FPS
    si = min(int(t/scene_seconds), scene_count-1) if scenes else 0

    # Crossfade between neighboring scenes around each boundary
    if scenes:
        for boundary_idx in range(1, scene_count):
            boundary = boundary_idx * scene_seconds
            start = boundary - TRANSITION/2
            end = boundary + TRANSITION/2

            if start <= t <= end:
                alpha = max(0.0, min(1.0, (t-start)/TRANSITION))
                prev_img = make_scene_frame(i, boundary_idx-1)
                next_img = make_scene_frame(i, boundary_idx)
                img = Image.blend(prev_img, next_img, alpha)
                img.save(FRAMES/f"frame_{i:04d}.jpg", quality=88)
                return

    img = make_scene_frame(i, si)
    img.save(FRAMES/f"frame_{i:04d}.jpg", quality=88)

print("Rendering cartoon with transitions...")
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
