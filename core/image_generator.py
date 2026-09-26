import argparse
import json
from core.paths import get_paths


def run(paths):
    import copy
    import json
    import time
    import urllib.request
    import urllib.parse
    from pathlib import Path
    from core.config_loader import load_current_channel

    BASE = Path(__file__).resolve().parent.parent

    VIDEO_PLAN = paths.video_plan
    WORKFLOW = BASE / "workflows" / "story_image_workflow.json"

    COMFY_OUTPUT = BASE / "image_ai" / "ComfyUI" / "output"
    TARGET_IMAGES = paths.images_dir

    COMFY_URL = "http://127.0.0.1:8188"

    TARGET_IMAGES.mkdir(parents=True, exist_ok=True)

    base_workflow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    video_plan = json.loads(VIDEO_PLAN.read_text(encoding="utf-8"))
    channel = load_current_channel()

    def queue_prompt(workflow):
        data = json.dumps({"prompt": workflow}).encode("utf-8")
        req = urllib.request.Request(
            f"{COMFY_URL}/prompt",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        return json.loads(urllib.request.urlopen(req).read())


    def get_history(prompt_id):
        with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}") as response:
            return json.loads(response.read())


    def wait_for_image(prompt_id):
        while True:
            history = get_history(prompt_id)

            if prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})

                for node_output in outputs.values():
                    if "images" in node_output:
                        return node_output["images"][0]

            time.sleep(1)


    for scene in video_plan:
        scene_number = scene["scene"]
        prompt = scene["image_prompt"]

        workflow = copy.deepcopy(base_workflow)

        workflow["5"]["inputs"]["width"] = 1024
        workflow["5"]["inputs"]["height"] = 576

        workflow["6"]["inputs"]["text"] = (
            f"{channel['visual_style']}, "
            f"cinematic, ultra detailed, dramatic lighting, high quality, "
            f"{prompt}"
        )

        workflow["9"]["inputs"]["filename_prefix"] = f"{paths.project_id}/scene_{scene_number}"

        print(f"Generuję scenę {scene_number}: {prompt}")

        result = queue_prompt(workflow)
        prompt_id = result["prompt_id"]

        image_info = wait_for_image(prompt_id)

        generated_file = COMFY_OUTPUT / image_info.get("subfolder", "") / image_info["filename"]
        target_file = TARGET_IMAGES / f"scene_{scene_number}.png"

        time.sleep(0.5)

        if not generated_file.exists():
            raise FileNotFoundError(f"Nie znaleziono wygenerowanego pliku: {generated_file}")

        target_file.write_bytes(generated_file.read_bytes())

        print(f"OK: {target_file}")

    print("Wszystkie obrazki wygenerowane.")


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
            "images": str(paths.images_dir)
        }, indent=2, ensure_ascii=False))
        return
    print(f"Projekt: {paths.project_id}", flush=True)
    run(paths)


if __name__ == "__main__":
    main()