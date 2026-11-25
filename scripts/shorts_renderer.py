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

colors = {
    "bunny": "#f1eeee", "mouse": "#d5a6ad",
    "panda": "#eeeeee", "parrot": "#48bd64",
    "cat": "#f5a35c", "squirrel": "#bd7849",
    "turtle": "#8bc26c"
}

def ellipse(d, box, fill, outline="#4a4038", width=2):
    d.ellipse(tuple(int(v) for v in box),
              fill=fill, outline=outline, width=width)

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

def draw_props(d, action, t):
    if action in ("bloom", "garden", "care"):
        for x, y in [(90,680),(430,675),(155,735),(380,730)]:
            d.line((x,y,x,y+28),fill="#33874b",width=4)
            for dx,dy,c in [(0,-8,"#ff67aa"),(-8,0,"#ffcc45"),
                            (8,0,"#ff67aa"),(0,8,"#ffcc45")]:
                ellipse(d,(x+dx-6,y+dy-6,x+dx+6,y+dy+6),c,width=0)
            ellipse(d,(x-4,y-4,x+4,y+4),"#ffe66d",width=0)

    if action in ("picnic", "play", "celebrate"):
        d.rounded_rectangle((65,665,145,720),radius=12,
                           fill="#f4c65a",outline="#875b35",width=2)
        for x in (85,115):
            ellipse(d,(x-10,670,x+10,690),"#e75c51",width=0)
        d.line((70,720,140,720),fill="#875b35",width=4)

    if action in ("water", "river", "rain"):
        d.ellipse((65,720,475,825),fill="#5bc9e8")
        for k in range(5):
            x = 90+k*80
            yy = 755+math.sin(t*3+k)*7
            d.arc((x,yy,x+45,yy+20),0,180,fill="white",width=3)

    if action in ("find", "notice", "search"):
        x,y = 440,620
        d.rectangle((x-5,y,x+5,y+55),fill="#875b35")
        ellipse(d,(x-45,y-55,x+45,y+15),"#398c49",width=0)
        ellipse(d,(x-28,y-75,x+28,y-25),"#4da755",width=0)

    if action in ("home", "finish"):
        d.rectangle((405,570,495,670),fill="#f6d49b",outline="#80552e",width=3)
        d.polygon([(390,570),(450,520),(510,570)],fill="#c76547")
        d.rectangle((440,615,465,670),fill="#865635")
        d.rectangle((415,590,435,610),fill="#9ad9f3")

    if action in ("think", "plan"):
        x,y = 420,480
        ellipse(d,(x-25,y-25,x+25,y+25),"white",width=0)
        ellipse(d,(x-6,y+30,x+6,y+42),"white",width=0)
        ellipse(d,(x-2,y+45,x+6,y+53),"white",width=0)

    if action in ("clean", "help"):
        d.rectangle((390,680,435,730),fill="#f4d15e",outline="#775b32")
        d.line((410,680,445,630),fill="#a7773f",width=5)

def draw_animal(d, kind, x, y, t, action, scale=1):
    c = colors.get(kind, "#e8c18c")
    s = scale

    walking = action in ("move","return","walk","search")
    jumping = action in ("play","celebrate","bloom","help","finish")
    bounce = abs(math.sin(t*5))*22 if jumping else math.sin(t*2)*5

    if walking:
        bounce = abs(math.sin(t*7))*10
    y -= bounce

    if kind in ("cat","squirrel"):
        tail = math.sin(t*3)*20
        d.arc((x+20*s,y+15*s,x+75*s,y+100*s),
              180+tail,320+tail,fill=c,width=max(3,int(9*s)))

    if kind == "turtle":
        ellipse(d,(x-40*s,y+5*s,x+40*s,y+55*s),"#598d49")
        ellipse(d,(x-28*s,y-5*s,x+28*s,y+60*s),c)

    ellipse(d,(x-36*s,y-65*s,x+36*s,y+10*s),c)

    if kind == "bunny":
        ellipse(d,(x-23*s,y-120*s,x-5*s,y-45*s),c)
        ellipse(d,(x+5*s,y-120*s,x+23*s,y-45*s),c)
        ellipse(d,(x-17*s,y-105*s,x-10*s,y-55*s),"#eaa1b2")
        ellipse(d,(x+10*s,y-105*s,x+17*s,y-55*s),"#eaa1b2")

    elif kind == "mouse":
        ellipse(d,(x-50*s,y-70*s,x-12*s,y-30*s),"#dc91a6")
        ellipse(d,(x+12*s,y-70*s,x+50*s,y-30*s),"#dc91a6")

    elif kind == "cat":
        d.polygon([(x-30*s,y-40*s),(x-30*s,y-78*s),(x-5*s,y-45*s)],fill=c)
        d.polygon([(x+30*s,y-40*s),(x+30*s,y-78*s),(x+5*s,y-45*s)],fill=c)

    elif kind == "parrot":
        d.polygon([(x+20*s,y-45*s),(x+48*s,y-35*s),(x+20*s,y-25*s)],fill="#ffb62d")
        d.polygon([(x-18*s,y+10*s),(x-45*s,y+38*s),(x-12*s,y+30*s)],fill="#2988b7")

    elif kind == "panda":
        ellipse(d,(x-43*s,y-65*s,x-10*s,y-28*s),"#222222")
        ellipse(d,(x+10*s,y-65*s,x+43*s,y-28*s),"#222222")

    elif kind == "squirrel":
        ellipse(d,(x+22*s,y-72*s,x+48*s,y-35*s),c)
        ellipse(d,(x-48*s,y-72*s,x-22*s,y-35*s),c)

    accessory_colors = {
        "bunny": "#ff72ad",
        "mouse": "#a77bff",
        "panda": "#48b89a",
        "parrot": "#ffcb45",
        "cat": "#49a6e8",
        "squirrel": "#e67e43",
        "turtle": "#e4bd55"
    }
    ac = accessory_colors.get(kind, "#ff72ad")
    d.polygon([(x-18*s,y+8*s),(x,y+23*s),(x+18*s,y+8*s)],
              fill=ac)
    ellipse(d,(x-5*s,y+10*s,x+5*s,y+20*s), "#fff4d6",width=0)

    blink = int(t*3+x) % 19 == 0
    worried = action in ("worry","rain")
    happy = action in ("celebrate","play","bloom","finish","picnic","home")
    thinking = action in ("think","plan","notice")

    if blink:
        d.line((x-15*s,y-30*s,x-6*s,y-30*s),fill="#222",width=3)
        d.line((x+6*s,y-30*s,x+15*s,y-30*s),fill="#222",width=3)
    else:
        ellipse(d,(x-15*s,y-34*s,x-6*s,y-20*s),"#222",width=0)
        ellipse(d,(x+6*s,y-34*s,x+15*s,y-20*s),"#222",width=0)
        ellipse(d,(x-12*s,y-32*s,x-9*s,y-27*s),"white",width=0)
        ellipse(d,(x+9*s,y-32*s,x+12*s,y-27*s),"white",width=0)

    if worried:
        d.line((x-18*s,y-43*s,x-7*s,y-39*s),fill="#4a4038",width=3)
        d.line((x+7*s,y-39*s,x+18*s,y-43*s),fill="#4a4038",width=3)
    elif thinking:
        d.line((x-18*s,y-43*s,x-7*s,y-43*s),fill="#4a4038",width=2)
        d.line((x+7*s,y-47*s,x+18*s,y-43*s),fill="#4a4038",width=2)

    ellipse(d,(x-5*s,y-13*s,x+5*s,y-7*s),"#ec8c9f",width=0)
    talking = int(t*7) % 3 != 0

    if happy:
        d.arc((x-15*s,y-10*s,x+15*s,y+15*s),0,180,fill="#444",width=3)
    elif talking:
        ellipse(d,(x-6*s,y-5*s,x+6*s,y+9*s),"#873e48",width=0)
    else:
        d.line((x-6*s,y+2*s,x+6*s,y+2*s),fill="#444",width=2)

    step = math.sin(t*7)*12 if walking else 0
    ellipse(d,(x-32*s,y+50*s+step,x-5*s,y+68*s+step),c)
    ellipse(d,(x+5*s,y+50*s-step,x+32*s,y+68*s-step),c)

    arm = math.sin(t*5)*22
    if happy:
        arm = math.sin(t*8)*35
    if walking:
        arm = math.sin(t*7)*30

    d.line((x-25*s,y+8*s,x-48*s,y+18*s+arm*s),
           fill="#4a4038",width=max(3,int(5*s)))
    d.line((x+25*s,y+8*s,x+48*s,y+18*s-arm*s),
           fill="#4a4038",width=max(3,int(5*s)))

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

    sx = 420 + int(math.sin(t*.3)*18)
    ellipse(d,(sx-40,65,sx+40,145),"#ffe66d",width=0)

    for x,y in [(40,200),(300,160),(180,300)]:
        shift = int((t*12+x) % 600)-80
        ellipse(d,(shift,y,shift+90,y+35),"white",width=0)
        ellipse(d,(shift+20,y-18,shift+70,y+35),"white",width=0)

    d.ellipse((-100,490,330,900),fill=green)
    d.ellipse((200,510,650,920),fill="#399b58")

    for x,y in [(45,560),(465,540),(390,650)]:
        d.rectangle((x-8,y,x+8,y+120),fill="#80552e")
        ellipse(d,(x-42,y-65,x+42,y+25),"#238b45",width=0)

    d.rectangle((0,760,W,H),fill="#319b55")
    random.seed(7)
    for k in range(14):
        px = (k*41 + int(t*18)) % W
        py = 430 + (k*57 % 330) + math.sin(t+k)*8
        ellipse(d,(px-4,py-4,px+4,py+4),
               "#fff3a5" if k%2 else "#ffffff",width=0)

def draw_action_effect(d, visual, t, x, y):
    phase = abs(math.sin(t*4))
    if visual in ("notice", "find", "search"):
        r = 22 + int(phase*8)
        d.ellipse((x-r,y-r,x+r,y+r),outline="#f4b942",width=5)
        d.ellipse((x-5,y-5,x+5,y+5),fill="#f4b942")
    elif visual in ("help", "teamwork"):
        r = 16 + int(phase*5)
        d.ellipse((x-r,y-r,x+r,y+r),fill="#ffcf70")
    elif visual in ("celebrate", "finish", "bloom"):
        for a in range(0,360,60):
            rad = math.radians(a+t*20)
            sx = x + int(math.cos(rad)*35)
            sy = y + int(math.sin(rad)*35)
            d.ellipse((sx-7,sy-7,sx+7,sy+7),fill="#ffd95c")
    elif visual in ("worry", "problem"):
        d.ellipse((x-18,y-18,x+18,y+18),fill="#b7d9ff")
    elif visual in ("play", "picnic"):
        r = 15 + int(phase*7)
        d.ellipse((x-r,y-r,x+r,y+r),fill="#a7e8a1")


def make_scene_frame(i, si):
    t = i/FPS
    si = max(0,min(si,scene_count-1))
    scene = scenes[si] if scenes else {}
    visual = scene.get("visual","intro")

    img = Image.new("RGB",(W,H))
    d = ImageDraw.Draw(img)
    background(d,bg_kind,t)
    draw_props(d,visual,t)

    center = 270 + math.sin(t*1.4)*35
    if visual in ("search","find","notice","worry"):
        center += math.sin(t*2)*22
    elif visual in ("play","celebrate","bloom","help","finish","picnic"):
        center += math.sin(t*4)*38

    positions = [center-100,center+100]
    action_offsets = {
        "walk": -45, "move": 45, "return": 70,
        "search": -35, "find": 35, "help": 0,
        "celebrate": 0, "finish": 0, "play": 0,
        "picnic": 0, "bloom": 0, "notice": 0,
        "worry": 0, "think": 0, "plan": 0
    }
    offset = action_offsets.get(visual, 0)
    movement = math.sin(t*3)*18 if visual in ("walk","move","return","search") else 0

    for j,ch in enumerate(chars[:2]):
        kind = ch.get("animal","bunny")
        direction = -1 if j == 0 else 1
        x = max(70,min(W-70,positions[j] + direction*offset + movement*direction))
        y = 700 + int(math.sin(t*3+j)*12)

        draw_animal(d,kind,x,y,t+j,visual)

        if visual in ("notice","find","search","help","celebrate",
                      "finish","play","bloom","picnic","worry"):
            draw_action_effect(d,visual,t,x,y-180)

    title_text = wrap(title,title_font,460)
    d.rounded_rectangle((15,40,W-15,150),radius=22,fill="white")
    d.multiline_text((W/2,95),title_text,font=title_font,
                     fill="#174b32",anchor="mm",align="center",spacing=5)

    caption = wrap(scene.get("text",story),font,460)
    d.rounded_rectangle((15,790,W-15,945),radius=22,fill="white")
    d.multiline_text((W/2,865),caption,font=font,
                     fill="#202020",anchor="mm",align="center",spacing=8)

    d.rounded_rectangle((205,165,335,205),radius=15,fill="white")
    d.text((270,185),f"Scene {si+1}/{scene_count}",
           fill="#174b32",font=small,anchor="mm")

    zoom = 1.0 + 0.035*math.sin(t*1.6+si)
    nw, nh = int(W*zoom), int(H*zoom)
    img = img.resize((nw,nh),Image.Resampling.LANCZOS)

    pan_x = int(math.sin(t*1.2+si)*8)
    pan_y = int(math.sin(t*.8+si)*6)
    left = max(0,min(nw-W,(nw-W)//2+pan_x))
    top = max(0,min(nh-H,(nh-H)//2+pan_y))
    img = img.crop((left,top,left+W,top+H))
    return img

def make_frame(i):
    t = i/FPS
    si = min(int(t/scene_seconds),scene_count-1) if scenes else 0

    if scenes:
        for boundary_idx in range(1,scene_count):
            boundary = boundary_idx*scene_seconds
            start = boundary-TRANSITION/2
            end = boundary+TRANSITION/2

            if start <= t <= end:
                alpha = max(0.0,min(1.0,(t-start)/TRANSITION))
                prev_img = make_scene_frame(i,boundary_idx-1)
                next_img = make_scene_frame(i,boundary_idx)
                img = Image.blend(prev_img,next_img,alpha)
                img.save(FRAMES/f"frame_{i:04d}.jpg",quality=88)
                return

    img = make_scene_frame(i,si)
    img.save(FRAMES/f"frame_{i:04d}.jpg",quality=88)

print("Rendering Stage 8 cartoon...")
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

print("STAGE 8 SHORT READY:",final)
