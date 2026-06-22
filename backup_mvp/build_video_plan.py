import json
import random
from pathlib import Path

BASE = Path(__file__).parent

SCENES_PATH = BASE / "input" / "scenes.json"
OUTPUT_PATH = BASE / "input" / "video_plan.json"

WORDS_PER_MINUTE = 145
SECONDS_PER_WORD = 60 / WORDS_PER_MINUTE

motions = [
    "zoom_in",
    "zoom_out",
    "pan_left",
    "pan_right"
]

scenes = json.loads(SCENES_PATH.read_text(encoding="utf-8"))

video_plan = []

for scene in scenes:
    text = scene["text"]
    word_count = len(text.split())

    duration = max(4, round(word_count * SECONDS_PER_WORD, 1))

    video_plan.append({
        "scene": scene["scene"],
        "narration": text,
        "duration": duration,
        "image_prompt": scene["image_prompt"],
        "image": f"scene_{scene['scene']}.png",
        "motion": random.choice(motions)
    })

OUTPUT_PATH.write_text(
    json.dumps(video_plan, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Wygenerowano video_plan.json: {OUTPUT_PATH}")