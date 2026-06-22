import json
from pathlib import Path

from core.config_loader import load_current_channel

from core.director import direct_scene

BASE = Path(__file__).resolve().parent.parent

SCENES_PATH = BASE / "input" / "scenes.json"
OUTPUT_PATH = BASE / "input" / "video_plan.json"

WORDS_PER_MINUTE = 145
SECONDS_PER_WORD = 60 / WORDS_PER_MINUTE


def map_camera_motion(camera_motion: str) -> str:
    text = camera_motion.lower()

    if "zoom out" in text or "pull back" in text:
        return "zoom_out"

    if "pan left" in text:
        return "pan_left"

    if "pan right" in text:
        return "pan_right"

    return "zoom_in"


scenes = json.loads(SCENES_PATH.read_text(encoding="utf-8"))

channel = load_current_channel()

video_plan = []

for scene in scenes:
    text = scene["text"]
    word_count = len(text.split())
    duration = max(4, round(word_count * SECONDS_PER_WORD, 1))

    print(f"Reżyseruję scenę {scene['scene']}...")

    direction = direct_scene(
        scene_text=text,
        channel_style=channel["channel_style"]
    )

    motion = map_camera_motion(direction["camera_motion"])

    video_plan.append({
        "scene": scene["scene"],
        "narration": text,
        "duration": duration,
        "image_prompt": direction["image_prompt"],
        "image": f"scene_{scene['scene']}.png",
        "motion": motion,
        "shot": direction["shot"],
        "camera_motion": direction["camera_motion"],
        "lighting": direction["lighting"],
        "mood": direction["mood"],
        "color_palette": direction["color_palette"],
        "visual_style": direction["visual_style"]
    })

OUTPUT_PATH.write_text(
    json.dumps(video_plan, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(f"Wygenerowano video_plan.json: {OUTPUT_PATH}")