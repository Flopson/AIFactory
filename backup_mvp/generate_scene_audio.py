import json
import subprocess
from pathlib import Path

BASE = Path(__file__).parent

VIDEO_PLAN = BASE / "input" / "video_plan.json"
OUTPUT_DIR = BASE / "assets" / "audio" / "scenes"

PIPER = BASE / "tools" / "piper" / "piper.exe"
MODEL = BASE / "models" / "en_US-lessac-medium.onnx"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plan = json.loads(VIDEO_PLAN.read_text(encoding="utf-8"))

for scene in plan:
    scene_number = scene["scene"]
    text = scene["narration"]

    output_file = OUTPUT_DIR / f"scene_{scene_number}.wav"

    print(f"Generuję audio dla sceny {scene_number}...")

    subprocess.run(
        [
            str(PIPER),
            "-m",
            str(MODEL),
            "-f",
            str(output_file)
        ],
        input=text,
        text=True,
        check=True
    )

    print(f"OK: {output_file}")

print("Gotowe. Audio scen zapisane w:", OUTPUT_DIR)