import json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
OUT.mkdir(parents=True, exist_ok=True)
data = json.loads((OUT / "story.json").read_text(encoding="utf-8"))
title = data.get("title", "जंगल की प्यारी कहानी")
chars = data.get("characters", [])
bg = data.get("background", "forest")

palettes = {
    "forest": ("#83DFFF", "#6BCB77", "#FFE46B"),
    "garden": ("#B4E9FF", "#77D980", "#FFD56B"),
    "river": ("#8EDCFF", "#62C9A0", "#FFF0A0"),
    "village": ("#FFDBA6", "#83CE78", "#FFE16B"),
    "hills": ("#A6D9FF", "#76C978", "#FFD66B"),
}
sky, ground, sun = palettes.get(bg, palettes["forest"])

img = Image.new("RGB", (1280, 720), sky)
d = ImageDraw.Draw(img)

d.rectangle((0, 450, 1280, 720), fill=ground)
d.ellipse((930, 65, 1110, 245), fill=sun)

for x, y in [(100, 100), (500, 145), (850, 90)]:
    d.ellipse((x, y, x+110, y+55), fill="white")
    d.ellipse((x+40, y-20, x+140, y+55), fill="white")

for x in [80, 1120]:
    d.rectangle((x+35, 340, x+65, 540), fill="#8B5A2B")
    d.ellipse((x, 260, x+120, 410), fill="#299E58")

def animal(kind, x, y, s=1):
    outline = "#333333"
    if kind == "panda":
        body = "white"
        d.ellipse((x, y+90, x+150*s, y+230*s), fill=body, outline=outline, width=5)
        d.ellipse((x+15, y+10, x+135*s, y+135*s), fill=body, outline=outline, width=5)
        d.ellipse((x+15, y+20, x+55*s, y+65*s), fill="black")
        d.ellipse((x+95*s, y+20, x+135*s, y+65*s), fill="black")
        d.ellipse((x+35*s, y+50*s, x+65*s, y+85*s), fill="black")
        d.ellipse((x+85*s, y+50*s, x+115*s, y+85*s), fill="black")
        d.ellipse((x+50*s, y+65*s, x+100*s, y+90*s), fill="black")
    elif kind == "parrot":
        d.ellipse((x, y+60, x+140*s, y+210*s), fill="#39B96A", outline=outline, width=5)
        d.ellipse((x+20*s, y, x+120*s, y+110*s), fill="#38B96A", outline=outline, width=5)
        d.ellipse((x+35*s, y+35*s, x+55*s, y+55*s), fill="white")
        d.ellipse((x+85*s, y+35*s, x+105*s, y+55*s), fill="white")
        d.ellipse((x+43*s, y+42*s, x+50*s, y+50*s), fill="black")
        d.ellipse((x+93*s, y+42*s, x+100*s, y+50*s), fill="black")
        d.polygon([(x+65*s,y+55*s),(x+90*s,y+65*s),(x+65*s,y+85*s)], fill="#FFB52E")
    else:
        d.ellipse((x, y+90, x+150*s, y+230*s), fill="white", outline=outline, width=5)
        d.ellipse((x+20*s, y+10, x+130*s, y+130*s), fill="white", outline=outline, width=5)
        d.ellipse((x+20*s, y-65, x+55*s, y+55*s), fill="white", outline=outline, width=5)
        d.ellipse((x+95*s, y-65, x+130*s, y+55*s), fill="white", outline=outline, width=5)
        d.ellipse((x+45*s, y+55*s, x+60*s, y+70*s), fill="black")
        d.ellipse((x+90*s, y+55*s, x+105*s, y+70*s), fill="black")
        d.ellipse((x+65*s, y+80*s, x+85*s, y+95*s), fill="#FF8DA1")

# Characters selected from the generated story
animals = [c.get("animal", "bunny") for c in chars[:2]]
if not animals:
    animals = ["bunny", "panda"]

animal(animals[0], 220, 330)
animal(animals[1], 790, 330)

font_path = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
try:
    title_font = ImageFont.truetype(font_path, 62)
    small_font = ImageFont.truetype(font_path, 42)
except OSError:
    title_font = ImageFont.load_default()
    small_font = title_font

d.rounded_rectangle((100, 30, 1180, 240), radius=40, fill="#FFCF48", outline="white", width=8)

# Automatically shrink title to fit
while title_font.size > 30 and d.textbbox((0,0), title, font=title_font)[2] > 1000:
    title_font = ImageFont.truetype(font_path, title_font.size-2)

d.multiline_text((640, 135), title, font=title_font, fill="#3A245E",
                 anchor="mm", align="center", stroke_width=2, stroke_fill="white")

d.rounded_rectangle((350, 600, 930, 680), radius=30, fill="#FF6F91")
d.text((640, 640), "मजेदार हिंदी कहानी", font=small_font,
       fill="white", anchor="mm", stroke_width=2, stroke_fill="#B52D55")

img.save(OUT / "thumbnail.png")
print("Stage 18 thumbnail generated.")
