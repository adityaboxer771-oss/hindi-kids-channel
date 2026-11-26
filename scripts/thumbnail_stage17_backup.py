import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output/kids"
OUT.mkdir(parents=True, exist_ok=True)

data = json.loads((OUT / "story.json").read_text(encoding="utf-8"))
title = data.get("title", "जंगल की प्यारी कहानी")

img = Image.new("RGB", (1280, 720), "#8BE0FF")
draw = ImageDraw.Draw(img)

# Background
draw.rectangle((0, 460, 1280, 720), fill="#71CE72")
draw.ellipse((930, 60, 1110, 240), fill="#FFE66D")

# Clouds
for x, y in [(100, 100), (500, 150), (850, 90)]:
    draw.ellipse((x, y, x+100, y+50), fill="white")
    draw.ellipse((x+40, y-20, x+130, y+50), fill="white")

# Trees
for x in [100, 1120]:
    draw.rectangle((x+35, 340, x+65, 520), fill="#8B5A2B")
    draw.ellipse((x, 270, x+110, 390), fill="#38B96A")

# Cartoon bunny
draw.ellipse((270, 380, 430, 540), fill="white", outline="#333333", width=5)
draw.ellipse((290, 270, 350, 410), fill="white", outline="#333333", width=5)
draw.ellipse((350, 270, 410, 410), fill="white", outline="#333333", width=5)
draw.ellipse((300, 420, 400, 500), fill="white", outline="#333333", width=4)
draw.ellipse((320, 445, 335, 460), fill="black")
draw.ellipse((365, 445, 380, 460), fill="black")
draw.ellipse((342, 465, 358, 480), fill="#FF8DA1")

# Cartoon panda
draw.ellipse((770, 380, 930, 540), fill="white", outline="#333333", width=5)
draw.ellipse((770, 300, 830, 360), fill="black")
draw.ellipse((870, 300, 930, 360), fill="black")
draw.ellipse((790, 400, 850, 460), fill="black")
draw.ellipse((850, 400, 910, 460), fill="black")
draw.ellipse((810, 420, 830, 440), fill="white")
draw.ellipse((870, 420, 890, 440), fill="white")
draw.ellipse((835, 455, 865, 475), fill="black")

# Title
font_path = "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
try:
    title_font = ImageFont.truetype(font_path, 62)
    small_font = ImageFont.truetype(font_path, 42)
except OSError:
    title_font = ImageFont.load_default()
    small_font = title_font

draw.rounded_rectangle((170, 35, 1110, 235), radius=35, fill="#FFCF48", outline="#FFFFFF", width=8)

# Keep title readable
title = title[:45]
draw.text((640, 130), title, font=title_font, fill="#3A245E",
          anchor="mm", stroke_width=2, stroke_fill="white")

draw.rounded_rectangle((390, 600, 890, 680), radius=30, fill="#FF6F91")
draw.text((640, 640), "मजेदार हिंदी कहानी", font=small_font,
          fill="white", anchor="mm", stroke_width=2, stroke_fill="#B52D55")

img.save(OUT / "thumbnail.png")
print("Thumbnail saved:", OUT / "thumbnail.png")
