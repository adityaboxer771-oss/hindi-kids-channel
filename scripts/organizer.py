from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent

for category in ("kids", "gaming"):
    source = ROOT / "downloads" / category
    target = ROOT / "clips" / category
    target.mkdir(parents=True, exist_ok=True)

    count = 0
    for file in source.iterdir():
        if file.is_file() and file.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm"):
            shutil.copy2(file, target / file.name)
            count += 1

    print(f"{category}: {count} clips organised")

print("Organisation complete!")
