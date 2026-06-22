import json
from pathlib import Path

BASE = Path(__file__).parent

VIDEO_PLAN_PATH = BASE / "input" / "video_plan.json"
PROMPTS_DIR = BASE / "input" / "prompts"

PROMPTS_DIR.mkdir(exist_ok=True)

video_plan = json.loads(VIDEO_PLAN_PATH.read_text(encoding="utf-8"))

for scene in video_plan:
    scene_number = scene["scene"]
    prompt = scene["image_prompt"]

    prompt_path = PROMPTS_DIR / f"scene_{scene_number}.txt"

    prompt_path.write_text(prompt, encoding="utf-8")

    print(f"SCENA {scene_number}")
    print(prompt)
    print("-" * 50)

print("Prompty zapisane w:", PROMPTS_DIR)