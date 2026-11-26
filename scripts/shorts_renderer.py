
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess, shutil, json, random

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
FRAMES = OUT / "short_frames"
W, H, FPS = 540, 960, 15
TRANSITION = 0.45

OUT.mkdir(parents=True, exist_ok=True)
if FRAMES.exists():
    shutil.rmtree(FRAMES)
FRAMES.mkdir(parents=True)

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
    raise SystemExit("Hindi font missing")

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

COLORS = {
    "bunny": "#f1eeee", "mouse": "#d5a6ad",
    "panda": "#eeeeee", "parrot": "#48bd64",
    "cat": "#f5a35c", "squirrel": "#bd7849",
    "turtle": "#8bc26c"
}

def ellipse(d, box, fill, outline=None, width=2):
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

def detect_visual(scene):
    v = str(scene.get("visual", "intro")).lower()
    txt = str(scene.get("text", "")).lower()
    combined = v + " " + txt

    mapping = {
        "river": ["river", "water", "नदी", "पानी"],
        "village": ["village", "घर", "गांव", "गाँव"],
        "garden": ["garden", "flower", "फूल", "बगीचा"],
        "forest": ["forest", "tree", "जंगल", "पेड़"],
        "home": ["home", "house", "घर"],
        "rain": ["rain", "बारिश", "बादल"],
        "picnic": ["picnic", "पिकनिक"],
    }

    for kind, words in mapping.items():
        if any(w in combined for w in words):
            return kind
    return v

def draw_background(d, kind, t):
    palettes = {
        "forest": ("#91d9ff", "#62b86a"),
        "garden": ("#b7e5ff", "#71cb78"),
        "river": ("#9ce2ff", "#57b5c9"),
        "village": ("#ffd89b", "#c3b476"),
        "home": ("#ffdda8", "#8cc77a"),
        "rain": ("#a8b9d0", "#659c79"),
        "picnic": ("#a7e2ff", "#77c66d"),
        "hills": ("#b7b2ef", "#7ebd80")
    }

    sky, grass = palettes.get(kind, palettes["forest"])
    d.rectangle((0, 0, W, H), fill=sky)

    if kind == "rain":
        for x in range(0, W, 110):
            d.ellipse((x, 130, x+140, 210), fill="#788ca8")
        for k in range(24):
            x = (k*31 + int(t*80)) % W
            y = 180 + (k*37) % 400
            d.line((x, y, x-5, y+20), fill="#d8edff", width=2)

    # Layered hills
    for k in range(3):
        y = 390 + k*50
        d.ellipse((-120+k*70, y, W+120, y+250), fill=grass)

    # Ground
    d.rectangle((0, 760, W, H), fill=grass)

    # River
    if kind == "river":
        d.polygon([(0,650),(170,600),(320,680),
                   (540,590),(540,850),(0,850)],
                  fill="#4ab7e0")
        for x in range(40, 520, 85):
            y = 720 + int(math.sin(t*3+x)*12)
            d.arc((x,y,x+50,y+18),0,180,fill="white",width=3)

    # Village houses
    if kind == "village":
        for x in (55, 330):
            d.rectangle((x, 500, x+140, 700),
                        fill="#ffe0ad", outline="#8c6240", width=3)
            d.polygon([(x-15,500),(x+70,420),(x+155,500)],
                      fill="#c96c50")
            d.rectangle((x+55,590,x+90,700),fill="#875d43")
            d.rectangle((x+15,540,x+45,580),fill="#91d9f5")
            d.rectangle((x+100,540,x+125,580),fill="#91d9f5")

    # Home interior
    if kind == "home":
        d.rectangle((30, 280, 510, 760), fill="#f8dcb6")
        d.rectangle((0, 750, W, H), fill="#b68a61")
        d.rectangle((65, 420, 180, 560), fill="#a4d9f2")
        d.rectangle((330, 460, 460, 750), fill="#a46b47")
        d.rectangle((350, 500, 440, 570), fill="#ffda89")

    # Trees
    for tx, ty in [(75,520),(440,490),(280,570)]:
        d.rectangle((tx-12,ty,tx+12,ty+125),fill="#795438")
        ellipse(d,(tx-65,ty-80,tx+65,ty+45),"#34864c",width=0)
        ellipse(d,(tx-45,ty-125,tx+45,ty-35),"#4caa58",width=0)

    # Sun
    if kind != "rain":
        sx = 420 + int(math.sin(t*.3)*15)
        ellipse(d,(sx-38,65,sx+38,145),"#ffe66d",width=0)

    # Clouds
    for x,y in [(40,190),(260,150),(420,280)]:
        shift = int((t*10+x) % 600)-80
        ellipse(d,(shift,y,shift+90,y+35),"white",width=0)
        ellipse(d,(shift+20,y-15,shift+65,y+35),"white",width=0)

    # Animated grass flowers
    for k in range(15):
        x = (k*41 + int(t*10)) % W
        y = 820 + (k*13 % 100)
        ellipse(d,(x-4,y-4,x+4,y+4),
               "#fff3a5" if k%2 else "white",width=0)

def draw_animal(d, kind, x, y, t, action, scale=1):
    s = scale
    c = COLORS.get(kind, "#e8c18c")

    walking = action in ("move","return","walk","search")
    jumping = action in ("play","celebrate","bloom","help","finish")

    bounce = abs(math.sin(t*5))*18 if jumping else math.sin(t*2)*5
    if walking:
        bounce = abs(math.sin(t*7))*10
    y -= bounce

    # Tail
    if kind in ("cat","squirrel"):
        d.arc((x+20*s,y+15*s,x+75*s,y+100*s),
              180,320,fill=c,width=max(3,int(9*s)))

    # Turtle shell
    if kind == "turtle":
        ellipse(d,(x-40*s,y+5*s,x+40*s,y+55*s),"#598d49")
        ellipse(d,(x-28*s,y-5*s,x+28*s,y+60*s),c)

    # Body
    ellipse(d,(x-36*s,y-65*s,x+36*s,y+10*s),c)

    # Ears
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
        ellipse(d,(x-43*s,y-65*s,x-10*s,y-28*s),"#222")
        ellipse(d,(x+10*s,y-65*s,x+43*s,y-28*s),"#222")

    elif kind == "squirrel":
        ellipse(d,(x+22*s,y-72*s,x+48*s,y-35*s),c)
        ellipse(d,(x-48*s,y-72*s,x-22*s,y-35*s),c)

    # Bow
    ac = {"bunny":"#ff72ad","mouse":"#a77bff",
          "panda":"#48b89a","parrot":"#ffcb45",
          "cat":"#49a6e8","squirrel":"#e67e43",
          "turtle":"#e4bd55"}.get(kind,"#ff72ad")
    d.polygon([(x-18*s,y+8*s),(x,y+23*s),(x+18*s,y+8*s)],fill=ac)

    # Eyes
    blink = int(t*3+x) % 19 == 0
    if blink:
        d.line((x-15*s,y-30*s,x-6*s,y-30*s),fill="#222",width=3)
        d.line((x+6*s,y-30*s,x+15*s,y-30*s),fill="#222",width=3)
    else:
        ellipse(d,(x-15*s,y-34*s,x-6*s,y-20*s),"#222",width=0)
        ellipse(d,(x+6*s,y-34*s,x+15*s,y-20*s),"#222",width=0)

    # Nose
    ellipse(d,(x-5*s,y-13*s,x+5*s,y-7*s),"#ec8c9f",width=0)

    # Mouth
    happy = action in ("celebrate","play","bloom","finish","picnic","home")
    if happy:
        d.arc((x-15*s,y-10*s,x+15*s,y+15*s),0,180,fill="#444",width=3)
    else:
        talk = abs(math.sin(t*12))
        ellipse(d,(x-7*s,y-4*s,x+7*s,y+4*s*talk+4),"#873e48",width=0)

    # Legs
    step = math.sin(t*7)*12 if walking else 0
    ellipse(d,(x-32*s,y+50*s+step,x-5*s,y+68*s+step),c)
    ellipse(d,(x+5*s,y+50*s-step,x+32*s,y+68*s-step),c)

    # Arms
    arm = math.sin(t*5)*22
    if happy:
        arm = math.sin(t*8)*35
    if walking:
        arm = math.sin(t*7)*30

    d.line((x-25*s,y+8*s,x-48*s,y+18*s+arm*s),
           fill="#4a4038",width=max(3,int(5*s)))
    d.line((x+25*s,y+8*s,x+48*s,y+18*s-arm*s),
           fill="#4a4038",width=max(3,int(5*s)))

def draw_props(d, action, t):
    if action in ("bloom","garden","care"):
        for x,y in [(90,680),(430,675),(155,735),(380,730)]:
            d.line((x,y,x,y+28),fill="#33874b",width=4)
            for dx,dy,c in [(0,-8,"#ff67aa"),(-8,0,"#ffcc45"),
                            (8,0,"#ff67aa"),(0,8,"#ffcc45")]:
                ellipse(d,(x+dx-6,y+dy-6,x+dx+6,y+dy+6),c,width=0)
            ellipse(d,(x-4,y-4,x+4,y+4),"#ffe66d",width=0)

    if action in ("picnic","play","celebrate"):
        d.rounded_rectangle((65,665,145,720),radius=12,
                           fill="#f4c65a",outline="#875b35",width=2)

    if action in ("water","river","rain"):
        d.ellipse((65,720,475,825),fill="#5bc9e8")

    if action in ("find","notice","search"):
        x,y=440,620
        d.rectangle((x-5,y,x+5,y+55),fill="#875b35")
        ellipse(d,(x-45,y-55,x+45,y+15),"#398c49",width=0)

    if action in ("clean","help"):
        d.rectangle((390,680,435,730),fill="#f4d15e")
        d.line((410,680,445,630),fill="#a7773f",width=5)

def make_scene_frame(i, si):
    t = i/FPS
    si = max(0,min(si,scene_count-1))
    scene = scenes[si] if scenes else {}
    visual = detect_visual(scene)

    img = Image.new("RGB",(W,H))
    d = ImageDraw.Draw(img)

    draw_background(d,visual,t)
    draw_props(d,visual,t)

    center = 270 + math.sin(t*1.4)*25
    positions = [center-100,center+100]

    for j,ch in enumerate(chars[:2]):
        kind = ch.get("animal","bunny")
        direction = -1 if j==0 else 1
        movement = math.sin(t*3)*20 if visual in ("walk","move","return","search") else 0
        x = max(70,min(W-70,positions[j]+movement*direction))
        y = 700 + int(math.sin(t*3+j)*10)
        draw_animal(d,kind,x,y,t+j,visual)

    # Title panel
    title_text = wrap(title,title_font,460)
    d.rounded_rectangle((15,40,W-15,150),radius=22,fill="white")
    d.multiline_text((W/2,95),title_text,font=title_font,
                     fill="#174b32",anchor="mm",align="center",spacing=5)

    # Story captions
    caption = wrap(scene.get("text",story),font,460)
    d.rounded_rectangle((15,790,W-15,945),radius=22,fill="white")
    d.multiline_text((W/2,865),caption,font=font,
                     fill="#202020",anchor="mm",align="center",spacing=8)

    # Scene label
    d.rounded_rectangle((205,165,335,205),radius=15,fill="white")
    d.text((270,185),f"Scene {si+1}/{scene_count}",
           fill="#174b32",font=small,anchor="mm")

    # Camera zoom
    zoom = 1.0 + 0.025*math.sin(t*1.6+si)
    nw,nh=int(W*zoom),int(H*zoom)
    img=img.resize((nw,nh),Image.Resampling.LANCZOS)
    left=max(0,min(nw-W,(nw-W)//2))
    top=max(0,min(nh-H,(nh-H)//2))
    img=img.crop((left,top,left+W,top+H))
    return img

def make_frame(i):
    t=i/FPS
    si=min(int(t/scene_seconds),scene_count-1) if scenes else 0

    if scenes:
        for boundary_idx in range(1,scene_count):
            boundary=boundary_idx*scene_seconds
            start=boundary-TRANSITION/2
            end=boundary+TRANSITION/2

            if start<=t<=end:
                alpha=max(0.0,min(1.0,(t-start)/TRANSITION))
                prev=make_scene_frame(i,boundary_idx-1)
                nxt=make_scene_frame(i,boundary_idx)
                img=Image.blend(prev,nxt,alpha)
                img.save(FRAMES/f"frame_{i:04d}.jpg",quality=88)
                return

    img=make_scene_frame(i,si)
    img.save(FRAMES/f"frame_{i:04d}.jpg",quality=88)

print("Rendering Cartoon Engine v2...")
for i in range(total):
    make_frame(i)

video=OUT/"short_video.mp4"
final=OUT/"short_final.mp4"

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

print("CARTOON ENGINE V2 READY:",final)

