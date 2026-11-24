"""render.py - 2D cartoon renderer for the Hindi kids channel.

Drop-in replacement for generator/generator/render.py.

Reads  output/story.json   (old format: scenes = list of strings
                            new format: scenes = list of dicts, see below)
Reads  output/audio/voice.mp3        (optional, one narration file)
Reads  output/audio/background.*     (optional, music; or assets/music/*)
Writes output/final_video.mp4

story.json (new format):
{
  "title": "...",
  "characters": ["bunny", "tota"],            # names from BUILTIN or config/characters.json
  "bg": "garden",                              # garden | night | rain | home
  "scenes": [
    {"who": "bunny", "line": "...", "action": "hop", "bg": "garden"},
    "plain string scenes also work"
  ]
}

Everything is drawn with Pillow (free, no image AI) and piped straight into
ffmpeg, so no frame files are written to disk.
"""
import argparse
import datetime
import json
import math
import random
import subprocess
import sys
from array import array
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont, features

OUTPUT = Path("output")
W, H = 1280, 720
FPS = 12                 # drawing fps, ffmpeg upsamples to 24
GROUND = 585             # y of the ground line
MIN_SECONDS = 120        # channel rule: every video >= 2 minutes

# ----------------------------------------------------------------- characters
BUILTIN = {
    "bunny":   {"kind": "bunny", "body": "#fdfdfd", "accent": "#f7b6c8",
                "accessories": ["bow", "none", "cap"]},
    "chuhiya": {"kind": "mouse", "body": "#b8c0c8", "accent": "#f4b6b6",
                "accessories": ["glasses", "bow", "none"]},
    "tota":    {"kind": "parrot", "body": "#33c46b", "accent": "#f5a623",
                "accessories": ["cap", "none"]},
    "billi":   {"kind": "cat", "body": "#f5a85a", "accent": "#fff1d6",
                "accessories": ["bow", "none"]},
    "panda":   {"kind": "panda", "body": "#ffffff", "accent": "#2b2b2b",
                "accessories": ["cap", "glasses", "none"]},
}


def rgb(c):
    return ImageColor.getrgb(c) if isinstance(c, str) else tuple(c)


def shade(c, k):
    r, g, b = rgb(c)
    return (int(r * k), int(g * k), int(b * k))


def resolve_specs(story, rng):
    """Turn story['characters'] into drawable specs, with per-video variety."""
    cfg = {}
    cfg_path = Path("config/characters.json")
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    names = story.get("characters") or ["bunny", "tota"]
    specs = {}
    for name in names:
        base = dict(BUILTIN.get(name, BUILTIN["bunny"]))
        over = cfg.get(name, {})
        for key in ("kind", "body", "accent"):
            if key in over:
                base[key] = over[key]
        if "beak" in over:
            base["accent"] = over["beak"]
        accs = over.get("accessory") or over.get("accessories") or base["accessories"]
        base["accessory"] = rng.choice(accs)
        specs[name] = base
    return names, specs


def ellipse(d, cx, cy, rx, ry, fill, outline=None, width=3):
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill,
              outline=outline, width=width)


def draw_character(d, cx, cy, s, spec, mouth, t, action, speaking):
    """cx,cy = head centre, s = head radius, mouth 0..1."""
    body, accent = rgb(spec["body"]), rgb(spec["accent"])
    line = shade(body, 0.6) if sum(body) > 200 else shade(body, 1.6)
    line = tuple(min(255, v) for v in line)
    kind = spec["kind"]
    dx = dy = 0.0
    if action == "hop":
        dy = -abs(math.sin(t * 5)) * s * 0.55
    elif action == "dance":
        dy = -abs(math.sin(t * 4)) * s * 0.25
        dx = math.sin(t * 3) * s * 0.35
    else:
        dy = math.sin(t * 2) * s * 0.04
    if speaking:
        dy -= mouth * s * 0.05
    cx += dx
    cy += dy

    # shadow
    lift = min(1.0, abs(dy) / (s * 0.6 + 1))
    ellipse(d, cx, GROUND + 8, s * (1.0 - 0.3 * lift), s * 0.2, (60, 90, 50))

    # ears / tuft (behind head)
    if kind == "bunny":
        for sx in (-1, 1):
            ellipse(d, cx + sx * s * 0.45, cy - s * 1.45, s * 0.28, s * 0.85, body, line)
            ellipse(d, cx + sx * s * 0.45, cy - s * 1.45, s * 0.15, s * 0.65, accent)
    elif kind == "mouse":
        for sx in (-1, 1):
            ellipse(d, cx + sx * s * 0.8, cy - s * 0.75, s * 0.5, s * 0.5, body, line)
            ellipse(d, cx + sx * s * 0.8, cy - s * 0.75, s * 0.32, s * 0.32, accent)
    elif kind == "cat":
        for sx in (-1, 1):
            d.polygon([(cx + sx * s * 0.9, cy - s * 0.2),
                       (cx + sx * s * 0.75, cy - s * 1.3),
                       (cx + sx * s * 0.15, cy - s * 0.8)], fill=body, outline=line)
    elif kind == "panda":
        for sx in (-1, 1):
            ellipse(d, cx + sx * s * 0.8, cy - s * 0.75, s * 0.38, s * 0.38, accent)
    elif kind == "parrot":
        for i, a in enumerate((-0.35, 0.0, 0.35)):
            ellipse(d, cx + a * s, cy - s * (1.05 + 0.1 * (i % 2)), s * 0.14, s * 0.3,
                    shade(body, 0.8), line)

    # body, belly, feet
    by = cy + s * 1.35
    ellipse(d, cx, by, s * 0.85, s * 0.95, body, line)
    ellipse(d, cx, by + s * 0.1, s * 0.5, s * 0.6, accent if kind != "panda" else (255, 255, 255))
    for sx in (-1, 1):
        ellipse(d, cx + sx * s * 0.4, by + s * 0.95, s * 0.32, s * 0.16, accent, line)
    # arms
    wave = math.sin(t * 6) * s * 0.25 if action in ("dance", "hop") else 0
    for sx in (-1, 1):
        up = wave if sx == 1 else -wave
        ellipse(d, cx + sx * s * 0.95, by - s * 0.1 + up, s * 0.22, s * 0.22, body, line)

    # head
    ellipse(d, cx, cy, s, s * 0.95, body, line, 4)
    if kind == "panda":
        for sx in (-1, 1):
            ellipse(d, cx + sx * s * 0.38, cy - s * 0.1, s * 0.3, s * 0.34, accent)
    # eyes
    blink = (t % 3.2) < 0.14
    for sx in (-1, 1):
        ex, ey = cx + sx * s * 0.38, cy - s * 0.1
        if blink:
            d.line((ex - s * 0.17, ey, ex + s * 0.17, ey), fill=(30, 30, 30), width=5)
        else:
            ellipse(d, ex, ey, s * 0.2, s * 0.22, (255, 255, 255), (30, 30, 30), 2)
            ellipse(d, ex, ey + s * 0.02, s * 0.11, s * 0.13, (25, 25, 25))
            ellipse(d, ex - s * 0.04, ey - s * 0.04, s * 0.04, s * 0.04, (255, 255, 255))
    # cheeks
    for sx in (-1, 1):
        ellipse(d, cx + sx * s * 0.65, cy + s * 0.3, s * 0.15, s * 0.1, (255, 160, 170))
    # nose / beak
    if kind == "parrot":
        d.polygon([(cx - s * 0.2, cy + s * 0.05), (cx + s * 0.2, cy + s * 0.05),
                   (cx, cy + s * 0.42)], fill=accent, outline=line)
        my = cy + s * 0.46
    else:
        ellipse(d, cx, cy + s * 0.12, s * 0.09, s * 0.06, (190, 80, 100))
        my = cy + s * 0.36
    # mouth (opens with the voice)
    mh = s * 0.04 + s * 0.16 * mouth
    ellipse(d, cx, my + mh, s * 0.2, mh, (120, 30, 50))
    if mouth > 0.45:
        ellipse(d, cx, my + mh * 1.5, s * 0.11, mh * 0.45, (240, 120, 130))

    # accessory
    acc = spec.get("accessory", "none")
    if acc == "bow":
        px, py = cx + s * 0.7, cy - s * 0.8
        d.polygon([(px, py), (px - s * 0.32, py - s * 0.2), (px - s * 0.32, py + s * 0.2)],
                  fill=(255, 90, 140))
        d.polygon([(px, py), (px + s * 0.32, py - s * 0.2), (px + s * 0.32, py + s * 0.2)],
                  fill=(255, 90, 140))
        ellipse(d, px, py, s * 0.09, s * 0.09, (255, 200, 220))
    elif acc == "cap":
        d.pieslice((cx - s * 0.95, cy - s * 1.35, cx + s * 0.95, cy + s * 0.1),
                   180, 360, fill=(225, 70, 70), outline=(150, 30, 30), width=3)
        ellipse(d, cx + s * 0.35, cy - s * 0.62, s * 0.75, s * 0.1, (190, 40, 40))
    elif acc == "glasses":
        for sx in (-1, 1):
            ellipse(d, cx + sx * s * 0.38, cy - s * 0.1, s * 0.3, s * 0.3,
                    None, (40, 40, 40), 5)
        d.line((cx - s * 0.08, cy - s * 0.1, cx + s * 0.08, cy - s * 0.1),
               fill=(40, 40, 40), width=5)


# ---------------------------------------------------------------- backgrounds
def gradient(top, bottom, h):
    img = Image.new("RGB", (W, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        k = y / max(1, h - 1)
        d.line((0, y, W, y), fill=tuple(int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)))
    return img


def make_bg(name, rng):
    if name == "night":
        img = gradient((15, 20, 60), (50, 60, 120), GROUND)
        full = Image.new("RGB", (W, H), (30, 80, 50))
        full.paste(img, (0, 0))
        d = ImageDraw.Draw(full)
        for _ in range(60):
            x, y = rng.randint(0, W), rng.randint(0, 330)
            d.ellipse((x, y, x + 4, y + 4), fill=(255, 255, 200))
        ellipse(d, 1090, 120, 55, 55, (255, 250, 215))
        ellipse(d, 1115, 108, 48, 48, (40, 45, 95))
        ellipse(d, 300, GROUND + 160, 700, 190, (25, 70, 45))
        return full
    if name == "home":
        full = Image.new("RGB", (W, H), (255, 236, 200))
        d = ImageDraw.Draw(full)
        d.rectangle((0, GROUND - 20, W, H), fill=(196, 146, 96))
        for x in range(0, W, 160):
            d.line((x, GROUND - 20, x - 60, H), fill=(170, 120, 75), width=3)
        d.rounded_rectangle((820, 90, 1140, 380), 20, fill=(170, 220, 250), outline=(140, 90, 50), width=12)
        d.line((980, 90, 980, 380), fill=(140, 90, 50), width=8)
        d.line((820, 235, 1140, 235), fill=(140, 90, 50), width=8)
        return full
    sky = ((90, 140, 160), (180, 195, 205)) if name == "rain" else ((110, 190, 245), (215, 240, 255))
    img = gradient(sky[0], sky[1], GROUND)
    full = Image.new("RGB", (W, H), (88, 190, 90))
    full.paste(img, (0, 0))
    d = ImageDraw.Draw(full)
    if name != "rain":
        ellipse(d, 1120, 110, 120, 120, (255, 240, 170))
        ellipse(d, 1120, 110, 70, 70, (255, 214, 70))
    ellipse(d, 250, GROUND + 120, 520, 190, (110, 205, 105))
    ellipse(d, 950, GROUND + 140, 560, 200, (96, 190, 92))
    d.rectangle((0, GROUND + 5, W, H), fill=(78, 176, 82))
    for _ in range(30):
        x, y = rng.randint(0, W), rng.randint(GROUND + 25, H - 15)
        c = rng.choice([(255, 90, 120), (255, 220, 60), (255, 255, 255), (190, 110, 240)])
        ellipse(d, x, y, 8, 8, c)
        ellipse(d, x, y, 3, 3, (255, 200, 40))
    return full


def draw_overlay(d, name, t):
    """Moving things on top of the cached background."""
    if name == "garden":
        for i, (bx, by) in enumerate(((150, 110), (560, 70), (860, 150))):
            x = (bx + t * (14 + 6 * i)) % (W + 260) - 130
            for ox, oy, r in ((0, 0, 40), (38, 8, 48), (82, 0, 38), (40, -24, 34)):
                ellipse(d, x + ox, by + oy, r, r * 0.75, (255, 255, 255))
    elif name == "rain":
        for i in range(70):
            x = (i * 97 + t * 90) % W
            y = (i * 53 + t * 520) % GROUND
            d.line((x, y, x - 8, y + 24), fill=(120, 160, 210), width=3)


# ------------------------------------------------------------------- text
FONT_PATHS = [
    "assets/fonts/NotoSansDevanagari-Bold.ttf",
    "assets/fonts/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Bold.ttf",
    "/system/fonts/NotoSansDevanagari-Regular.ttf",
    "/data/data/com.termux/files/usr/share/fonts/noto/NotoSansDevanagari-Regular.ttf",
]


def load_font(size):
    engine = ImageFont.Layout.RAQM if features.check("raqm") else ImageFont.Layout.BASIC
    paths = list(FONT_PATHS)
    for pat in ("/usr/share/fonts/**/NotoSansDevanagari*.ttf", "/system/fonts/*Devanagari*.ttf"):
        paths += [str(p) for p in Path("/").glob(pat.lstrip("/"))]
    for p in paths:
        try:
            return ImageFont.truetype(p, size, layout_engine=engine)
        except OSError:
            continue
    if not getattr(load_font, "warned", False):
        print("WARNING: Devanagari font not found, Hindi text will look wrong "
              "(put NotoSansDevanagari-Bold.ttf in assets/fonts/)")
        load_font.warned = True
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_caption(d, text, font):
    lines = wrap(d, text, font, W - 220)[:3]
    lh = 64
    box_h = lh * len(lines) + 30
    y0 = H - box_h - 25
    d.rounded_rectangle((90, y0, W - 90, H - 25), 28, fill=(255, 250, 235), outline=(90, 50, 110), width=5)
    for i, ln in enumerate(lines):
        d.text((W // 2, y0 + 15 + lh * i + lh // 2), ln, fill=(60, 30, 80), font=font, anchor="mm")


# ------------------------------------------------------------------ audio
def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def audio_duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return float(out.strip())


def load_envelope(voice):
    """Loudness per drawn frame (0..1) so the mouth follows the voice."""
    wav = OUTPUT / "audio" / "_env.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(voice), "-ac", "1",
         "-ar", "16000", "-f", "wav", str(wav)])
    raw = wav.read_bytes()[44:]
    samples = array("h")
    samples.frombytes(raw[: len(raw) // 2 * 2])
    win = 16000 // FPS
    env = [sum(abs(v) for v in samples[i:i + win]) / max(1, len(samples[i:i + win]))
           for i in range(0, len(samples), win)]
    ref = sorted(env)[int(len(env) * 0.95)] or 1
    env = [min(1.0, e / ref) for e in env]
    # light smoothing
    return [(env[max(0, i - 1)] + 2 * env[i] + env[min(len(env) - 1, i + 1)]) / 4
            for i in range(len(env))]


def find_music():
    for pat in ("output/audio/background.*", "assets/music/*.mp3", "assets/music/*.wav"):
        hits = sorted(Path(".").glob(pat))
        if hits:
            return hits[0]
    return None


# ------------------------------------------------------------------ main
def normalise_scenes(story, names):
    actions = ["hop", "dance", "idle"]
    scenes = []
    for i, sc in enumerate(story["scenes"]):
        if isinstance(sc, str):
            sc = {"line": sc}
        scenes.append({
            "line": sc.get("line", ""),
            "who": sc.get("who") if sc.get("who") in names else names[i % len(names)],
            "action": sc.get("action", actions[i % 3]),
            "bg": sc.get("bg", story.get("bg", "garden")),
        })
    return scenes


def render_video(story_path=OUTPUT / "story.json", min_seconds=MIN_SECONDS, seed=None):
    story = json.loads(Path(story_path).read_text(encoding="utf-8"))
    seed = seed if seed is not None else datetime.date.today().toordinal()
    rng = random.Random(seed)
    names, specs = resolve_specs(story, rng)
    scenes = normalise_scenes(story, names)

    voice = OUTPUT / "audio" / "voice.mp3"
    voice = voice if voice.exists() else None
    music = find_music()

    # scene timing: share the voice length by text length (or 6 s each)
    if voice:
        vdur = audio_duration(voice)
        env = load_envelope(voice)
        weights = [max(8, len(s["line"])) for s in scenes]
        durs = [vdur * w / sum(weights) for w in weights]
    else:
        vdur, env = None, None
        durs = [6.0] * len(scenes)
    loop_dur = sum(durs)
    loops = max(1, math.ceil(min_seconds / loop_dur))
    total = loop_dur * loops
    starts = [sum(durs[:i]) for i in range(len(durs))]
    print(f"story {loop_dur:.1f}s x {loops} loop(s) = {total:.1f}s, seed {seed}")

    bgs = {n: make_bg(n, random.Random(seed)) for n in {s["bg"] for s in scenes}}
    font = load_font(46)
    small = load_font(38)

    final = OUTPUT / "final_video.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    a_idx = 1
    chains = []
    if voice:
        cmd += ["-stream_loop", str(loops - 1), "-i", str(voice)]
        chains.append(f"[{a_idx}:a]volume=1.0[v]")
        a_idx += 1
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        chains.append(f"[{a_idx}:a]volume=0.2[m]")
    if voice and music:
        graph = ";".join(chains) + ";[v][m]amix=inputs=2:duration=first:dropout_transition=0,volume=2[a]"
        amap = ["-filter_complex", graph, "-map", "0:v", "-map", "[a]"]
    elif voice or music:
        graph = ";".join(chains).replace("[v]", "[a]").replace("[m]", "[a]")
        amap = ["-filter_complex", graph, "-map", "0:v", "-map", "[a]"]
    else:
        amap = ["-map", "0:v", "-an"]
    cmd += amap + ["-vf", "fps=24,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
                   "-crf", "23", "-c:a", "aac", "-t", f"{total:.2f}", str(final)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    n_frames = int(total * FPS)
    for f in range(n_frames):
        t = f / FPS
        tl = t % loop_dur
        idx = max(i for i in range(len(starts)) if starts[i] <= tl)
        sc = scenes[idx]
        img = bgs[sc["bg"]].copy()
        d = ImageDraw.Draw(img)
        draw_overlay(d, sc["bg"], t)

        if env:
            m = env[int(tl * FPS) % len(env)]
            mouth = min(1.0, m * 1.5)
        else:
            mouth = abs(math.sin(t * 9))
        n = len(names)
        for k, name in enumerate(names):
            cx = W // 2 if n == 1 else int(W * (0.3 + 0.4 * k / (n - 1)))
            talking = name == sc["who"]
            hs = 105 if talking else 88          # head radius
            draw_character(d, cx, GROUND - 2.5 * hs, hs,
                           specs[name], mouth if talking else 0.0, t,
                           sc["action"] if talking else "idle", talking)
        if t < 4:
            d.text((W // 2, 60), story.get("title", ""), fill=(255, 255, 255),
                   font=small, anchor="mm", stroke_width=4, stroke_fill=(60, 30, 90))
        draw_caption(d, sc["line"], font)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")
    dur = audio_duration(final)
    print(f"Video ready: {final} ({dur:.1f}s)")
    if dur < min_seconds - 1:
        sys.exit(f"Video shorter than {min_seconds}s")
    return final


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default=str(OUTPUT / "story.json"))
    ap.add_argument("--min-seconds", type=int, default=MIN_SECONDS)
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    OUTPUT.mkdir(exist_ok=True)
    render_video(a.story, a.min_seconds, a.seed)
