import argparse
import json
from core.paths import get_paths


def run(paths):
    import json
    import subprocess
    from pathlib import Path

    BASE = Path(__file__).resolve().parent.parent

    VIDEO_PLAN = paths.video_plan
    OUTPUT_DIR = paths.audio_dir

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
            encoding="utf-8",
            check=True
        )

        print(f"OK: {output_file}")

    print("Gotowe. Audio scen zapisane w:", OUTPUT_DIR)


def main():
    parser = argparse.ArgumentParser(description="Etap produkcji aktywnego projektu")
    parser.add_argument("--check-paths", action="store_true", help="Pokaż ścieżki bez generowania")
    args = parser.parse_args()
    paths = get_paths()
    if not paths.manifest.is_file():
        raise FileNotFoundError(f"Brak projektu: {paths.root}")
    if args.check_paths:
        print(json.dumps({
            "project": paths.project_id,
            "video_plan": str(paths.video_plan),
            "audio": str(paths.audio_dir)
        }, indent=2, ensure_ascii=False))
        return
    print(f"Projekt: {paths.project_id}", flush=True)
    run(paths)


if __name__ == "__main__":
    main()
