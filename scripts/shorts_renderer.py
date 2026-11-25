from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, subprocess, shutil, json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
FRAMES = OUT / "short_frames"
W, H, FPS = 540, 960, 15
audio_probe = OUT / "final_audio.mp3"
DURATION = 22
if audio_probe.exists():
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
             str(audio_probe)], capture_output=True, text=True, check=True
        )
        DURATION = max(10, int(float(probe.stdout.strip()) + 1))
    except Exception:
        DURATION = 22
TOTAL = FPS * DURATION
TOTAL = FPS * DURATION

OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)

data = json.loads((OUT / "story.json").read_text(encoding="utf-8")) if (OUT / "story.json").exists() else {}
story = data.get("story", "एक समय की बात है। सभी दोस्त मिलकर खुश रहते थे।")
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

def wrap(text, f, width):
    lines, line = [], ""
    for word in text.split():
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

sentences = [s.strip() for s in story.replace("\n", " ").split("।") if s.strip()]
captions = []
for sentence in sentences:
    words = sentence.split()
    for i in range(0, len(words), 5):
        captions.append(" ".join(words[i:i+5]))
if not captions:
    captions = ["एक प्यारी कहानी"]

animals = ["bunny", "mouse", "parrot", "cat", "panda"]
colors = {
    "bunny": "#eeeeee", "mouse": "#b9a0a0",
    "parrot": "#35bd65", "cat": "#f4a45c",
    "panda": "#eeeeee"
}

def animal(d, kind, x, y, t, scale=1):
    bounce = math.sin(t*4.5)*10
    y += bounce
    c = colors[kind]

    def box(a,b,e,f):
        return (int(x+a*scale), int(y+b*scale),
                int(x+e*scale), int(y+f*scale))

    def ellipse(a,b,e,f,fill,outline="#444444",width=2):
        d.ellipse(box(a,b,e,f),fill=fill,outline=outline,width=max(1,int(width*scale)))

    # Body
    ellipse(-25, -5, 25, 65, c)
    ellipse(-30, -52, 30, 10, c)

    if kind == "bunny":
        ellipse(-22,-105,-5,-40,c)
        ellipse(5,-105,22,-40,c)
        ellipse(-15,-98,-9,-47,"#f3a5b7",None)
        ellipse(9,-98,15,-47,"#f3a5b7",None)
    elif kind == "mouse":
        ellipse(-48,-65,-12,-28,"#d98eaa")
        ellipse(12,-65,48,-28,"#d98eaa")
    elif kind == "parrot":
        ellipse(-20,-65,28,-20,c)
        d.polygon([(x+25*scale,y-48*scale),
                   (x+49*scale,y-38*scale),
                   (x+25*scale,y-30*scale)],fill="#ffae24")
        d.polygon([(x-25*scale,y+5*scale),
                   (x-52*scale,y+25*scale),
                   (x-18*scale,y+35*scale)],fill="#168cba")
    elif kind == "cat":
        d.polygon([(x-27*scale,y-38*scale),
                   (x-25*scale,y-72*scale),
                   (x-2*scale,y-45*scale)],fill=c,outline="#444444")
        d.polygon([(x+2*scale,y-45*scale),
                   (x+25*scale,y-72*scale),
                   (x+27*scale,y-38*scale)],fill=c,outline="#444444")
    else:
        ellipse(-45,-65,-10,-30,"#222222")
        ellipse(10,-65,45,-30,"#222222")
        ellipse(-17,-25,-5,-9,"#222222")
        ellipse(5,-25,17,-9,"#222222")

    eye = "#ffffff" if kind == "panda" else "#111111"
    ellipse(-14,-29,-7,-20,eye,None)
    ellipse(7,-29,14,-20,eye,None)
    ellipse(-5,-14,5,-7,"#ed8ba0",None)
    d.line(box(-5,-2,5,-2),fill="#444444",width=2)

    # Feet
    ellipse(-32,52,-5,68,c)
    ellipse(5,52,32,68,c)

def background(d, scene, t):
    skies = ["#87ceeb", "#a8ddff", "#ffdc9c", "#a9e8c0", "#b9a9ee"]
    greens = ["#72c875", "#58bd72", "#63b36a", "#69c987", "#83bb80"]
    d.rectangle((0,0,W,H),fill=skies[scene])

    # Sun
    sunx = 420 + int(math.sin(t*.3)*12)
    d.ellipse((sunx-35,65,sunx+35,135),fill="#ffe66d")

    # Clouds
    for x,y in [(40,200),(300,160),(180,300)]:
        shift = int(math.sin(t*.4+x)*12)
        d.ellipse((x+shift,y,x+shift+90,y+35),fill="white")
        d.ellipse((x+shift+20,y-18,x+shift+70,y+35),fill="white")

    # Hills
    d.ellipse((-100,490,330,900),fill=greens[scene])
    d.ellipse((200,510,650,920),fill="#399b58")

    # Trees
    for x,y in [(45,560),(465,540),(390,650)]:
        d.rectangle((x-8,y,x+8,y+120),fill="#80552e")
        d.ellipse((x-42,y-65,x+42,y+25),fill="#238b45")

    d.rectangle((0,760,W,H),fill="#319b55")

def make_frame(i):
    t = i/FPS
    scene = min(int(t/(DURATION/5)),4)
    img = Image.new("RGB",(W,H))
    d = ImageDraw.Draw(img)

    background(d,scene,t)

    # Scene movement
    center = 270 + math.sin(t*1.4)*45
    positions = [
        center-190+math.sin(t*2)*15,
        center-95+math.sin(t*2.3+1)*18,
        center+math.sin(t*2.8+2)*35,
        center+95+math.sin(t*2.1+3)*15,
        center+190+math.sin(t*2.5+4)*18
    ]

    # Characters enter / move according to scene
    for j,kind in enumerate(animals):
        x = positions[j]
        x = max(55,min(W-55,x))
        animal(d,kind,x,690+(j%2)*5,t+j)

    # Story title
    title_text = wrap(title,title_font,460)
    d.rounded_rectangle((15,45,W-15,150),radius=22,fill="white")
    d.multiline_text((W/2,98),title_text,font=title_font,
                     fill="#174b32",anchor="mm",align="center",spacing=5)

    # Captions
    index = min(int(t/(DURATION/len(captions))),len(captions)-1)
    caption = wrap(captions[index],font,460)
    d.rounded_rectangle((15,805,W-15,940),radius=22,fill="white")
    d.multiline_text((W/2,872),caption,font=font,
                     fill="#202020",anchor="mm",align="center",spacing=8)

    # Scene indicator
    d.rounded_rectangle((215,165,325,205),radius=15,fill="white")
    d.text((270,185),f"Scene {scene+1}",fill="#174b32",anchor="mm")

    img.save(FRAMES/f"frame_{i:04d}.jpg",quality=88)

print("Creating animated cartoon scenes...")
for i in range(TOTAL):
    make_frame(i)

video = OUT/"short_video.mp4"
audio = OUT/"final_audio.mp3"
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
