import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config/settings.json"

def load_settings():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)

def show_sources():
    settings = load_settings()
    print("=== CONTENT SOURCE MANAGER ===")
    for source, enabled in settings["sources"].items():
        print(f"{source}: {'ON' if enabled else 'OFF'}")

if __name__ == "__main__":
    show_sources()
