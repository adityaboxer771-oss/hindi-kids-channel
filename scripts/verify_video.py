
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
data = {}
duration = 0

# Check files
for f in (video, thumbnail, story):
    if not f.exists() or f.stat().st_size == 0:
        errors.append(f"Missing or empty: {f}")

# Verify video
if not errors:
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-show_entries", "stream=codec_type,width,height,r_frame_rate",
                "-of", "json", str(video)
            ],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        streams = data.get("streams", [])

        vs = next(
            (s for s in streams if s.get("codec_type") == "video"),
            None
        )
        aus = next(
            (s for s in streams if s.get("codec_type") == "audio"),
            None
        )

        if 10 <= duration <= 120:
            checks.append("Duration OK")
        else:
            errors.append(f"Duration out of range: {duration:.2f}s")

        if vs:
            if (vs.get("width"), vs.get("height")) == (1080, 1920):
                checks.append("Resolution OK")
            else:
                errors.append(
                    f"Unexpected resolution: "
                    f"{vs.get('width')}x{vs.get('height')}"
                )

            fps = vs.get("r_frame_rate", "0/1")

            try:
                a, b = map(int, fps.split("/"))
                fps_value = a / b if b else 0

                if abs(fps_value - 15) <= 0.1:
                    checks.append("FPS OK")
                else:
                    errors.append(f"Unexpected FPS: {fps}")

            except Exception:
                errors.append("FPS could not be checked")

        else:
            errors.append("Video stream missing")

        if aus:
            checks.append("Audio stream OK")
        else:
            errors.append("Audio stream missing")

    except Exception as e:
        errors.append(f"Video verification failed: {e}")

# Verify story
try:
    sdata = json.loads(story.read_text(encoding="utf-8"))

    if isinstance(sdata.get("scenes"), list) and sdata["scenes"]:
        checks.append("Story structure OK")
    else:
        errors.append("Story scenes missing")

except Exception as e:
    errors.append(f"Story JSON invalid: {e}")

# Verify thumbnail
try:
    with Image.open(thumbnail) as im:
        if im.size == (1280, 720):
            checks.append("Thumbnail dimensions OK")
        else:
            errors.append(f"Thumbnail size unexpected: {im.size}")

except Exception as e:
    errors.append(f"Thumbnail verification failed: {e}")

# Save report
qc = {
    "status": "FAILED" if errors else "PASSED",
    "duration_seconds": round(duration, 2),
    "checks": checks,
    "errors": errors
}

report.write_text(
    json.dumps(qc, indent=2),
    encoding="utf-8"
)

print(json.dumps(qc, indent=2))

if errors:
    raise SystemExit(1)

print("VERIFICATION PASSED")
