import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

SCRIPT_PATH = BASE / "input" / "script.txt"
OUTPUT_PATH = BASE / "input" / "scenes.json"

text = SCRIPT_PATH.read_text(encoding="utf-8").strip()

# 1 akapit = 1 scena
paragraphs = [
    p.strip()
    for p in text.split("\n\n")
    if p.strip()
]

scenes = []

for index, paragraph in enumerate(paragraphs, start=1):
    scenes.append({
        "scene": index,
        "text": paragraph,
        "image_prompt": f"cinematic detailed illustration of: {paragraph}",
        "duration": None
    })

OUTPUT_PATH.write_text(
    json.dumps(scenes, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Wygenerowano {len(scenes)} scen:")
print(OUTPUT_PATH)