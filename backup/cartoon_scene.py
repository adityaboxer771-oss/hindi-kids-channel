from PIL import Image, ImageDraw
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out = ROOT / "output/kids/scene.png"
out.parent.mkdir(parents=True, exist_ok=True)

im = Image.new("RGB", (1280, 720), "#8edcff")
d = ImageDraw.Draw(im)

# Sky and hills
d.rectangle((0, 480, 1280, 720), fill="#72c96b")
d.ellipse((-150, 350, 600, 850), fill="#4eae62")
d.ellipse((550, 350, 1450, 850), fill="#399b58")

# Sun
d.ellipse((1030, 65, 1160, 195), fill="#ffdf55")

# Clouds
for x, y in [(180, 130), (700, 100)]:
    d.ellipse((x, y, x+100, y+60), fill="white")
    d.ellipse((x+35, y-25, x+115, y+55), fill="white")
    d.ellipse((x+75, y, x+155, y+60), fill="white")

# Cute original bunny
d.ellipse((470, 270, 570, 480), fill="#fff4e6", outline="#795548", width=5)
d.ellipse((590, 270, 690, 480), fill="#fff4e6", outline="#795548", width=5)
d.ellipse((480, 320, 690, 540), fill="#fff4e6", outline="#795548", width=5)
d.ellipse((500, 350, 670, 515), fill="#fff4e6")
d.ellipse((525, 405, 545, 430), fill="#222222")
d.ellipse((625, 405, 645, 430), fill="#222222")
d.ellipse((575, 445, 595, 465), fill="#ff8b9c")
d.arc((550, 445, 585, 485), 0, 90, fill="#795548", width=4)
d.arc((585, 445, 620, 485), 90, 180, fill="#795548", width=4)

# Title
d.rounded_rectangle((300, 25, 980, 95), radius=25, fill="white")
d.text((390, 45), "Meri Pyari Jungle Kahani", fill="#285b91", stroke_width=1)

im.save(out)
print("Cartoon scene ready:", out)
