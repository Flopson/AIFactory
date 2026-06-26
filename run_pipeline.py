import subprocess
from pathlib import Path

BASE = Path(__file__).parent

steps = [
    "core.script_splitter",
    "core.character_manager",
    "core.scene_planner",
    "core.audio_generator",
    "core.image_generator",
    "core.video_builder",
]

for step in steps:
    print(f"\n=== START: {step} ===")

    result = subprocess.run(
        ["python", "-m", step],
        cwd=BASE
    )

    if result.returncode != 0:
        print(f"\nBŁĄD W KROKU: {step}")
        raise SystemExit(result.returncode)

    print(f"=== OK: {step} ===")

print("\nGOTOWE. Film jest w output/final_v3.mp4")