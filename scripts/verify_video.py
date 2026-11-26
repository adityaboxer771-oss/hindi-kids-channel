import json
import subprocess
from pathlib import Path
from PIL import Image

folder = Path("output/kids")
video = folder / "short_final.mp4"
thumbnail = folder / "thumbnail.png"
story = folder / "story.json"
report = folder / "qc_report.json"
errors = []
checks = []

for f in (video, thumbnail, story):
    if not f.exists() or f.stat().st_size == 0:
        errors.append(f"Missing or empty: {f}")

data = {}
duration = 0

if not errors:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-show_entries",
             "stream=codec_type,width,height,r_frame_rate",
             "-of", "json", str(video)],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        streams = data.get("streams", [])
        vs = next((s for s in streams if s.get("codec_type") == "video"), None)
        aus = next((s for s in streams if s.get("codec_type") == "audio"), None)

        if duration < 10 or duration > 120:
            errors.append(f"Duration out of range: {duration:.2f}s")
        else:
            checks.append("Duration OK")

        if not vs:
            errors.append("Video stream missing")
        else:
            
if (vs.get("width"), vs.get("height")) != (1080, 1920):

                errors.append(f"Unexpected resolution: {vs.get('width')}x{vs.get('height')}")
            else:
                checks.append("Resolution OK")

            fps = vs.get("r_frame_rate", "0/1")
            try:
                a, b = map(int, fps.split("/"))
                fps_value = a / b if b else 0
                if abs(fps_value - 15) > 0.1:
                    errors.append(f"Unexpected FPS: {fps}")
                else:
                    checks.append("FPS OK")
            except Exception:
                errors.append("FPS could not be checked")

        if not aus:
            errors.append("Audio stream missing")
        else:
            checks.append("Audio stream OK")

    except Exception as e:
        errors.append(f"Video verification failed: {e}")

try:
    sdata = json.loads(story.read_text(encoding="utf-8"))
    if not isinstance(sdata.get("scenes"), list) or not sdata["scenes"]:
        errors.append("Story scenes missing")
    else:
        checks.append("Story structure OK")
except Exception as e:
    errors.append(f"Story JSON invalid: {e}")

try:
    with Image.open(thumbnail) as im:
        if im.size != (1280, 720):
            errors.append(f"Thumbnail size unexpected: {im.size}")
        else:
            checks.append("Thumbnail dimensions OK")
except Exception as e:
    errors.append(f"Thumbnail verification failed: {e}")

qc = {
    "status": "FAILED" if errors else "PASSED",
    "duration_seconds": round(duration, 2),
    "checks": checks,
    "errors": errors
}
report.write_text(json.dumps(qc, indent=2), encoding="utf-8")

print(json.dumps(qc, indent=2))
if errors:
    raise SystemExit(1)

print("VERIFICATION PASSED")
