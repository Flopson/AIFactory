import json
import re

from core.paths import get_paths


def main() -> None:
    paths = get_paths()

    if not paths.manifest.is_file():
        raise FileNotFoundError(f"Brak projektu: {paths.root}")

    text = paths.script.read_text(
        encoding="utf-8-sig"
    ).strip()

    if not text:
        raise ValueError(
            f"Scenariusz jest pusty: {paths.script}"
        )

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    scenes = [
        {
            "scene": index,
            "text": paragraph,
            "image_prompt": (
                f"cinematic detailed illustration of: {paragraph}"
            ),
            "duration": None,
        }
        for index, paragraph in enumerate(paragraphs, start=1)
    ]

    paths.scenes.write_text(
        json.dumps(scenes, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Projekt: {paths.project_id}")
    print(
        f"Wygenerowano {len(scenes)} scen: {paths.scenes}"
    )


if __name__ == "__main__":
    main()