import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from core.paths import (
    CURRENT_PROJECT_FILE,
    PROJECTS_DIR,
    ProjectPaths,
    validate_project_id,
)


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def create_project(project_id: str, channel: str = "space") -> None:
    project_id = validate_project_id(project_id)
    paths = ProjectPaths(project_id)

    if paths.root.exists():
        raise FileExistsError(
            f"Projekt już istnieje: {paths.root}"
        )

    paths.ensure_structure()

    paths.topic.write_text("", encoding="utf-8")
    paths.channel.write_text(channel, encoding="utf-8")
    paths.script.write_text("", encoding="utf-8")

    write_json(paths.scenes, [])
    write_json(paths.video_plan, [])

    write_json(paths.characters, {"characters": []})
    write_json(paths.locations, {"locations": []})
    write_json(paths.objects, {"objects": []})
    write_json(paths.story, {})

    manifest = {
        "project_id": project_id,
        "channel": channel,
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "topic": "",
        "word_count": 0,
        "scene_count": 0,
        "output": str(paths.output_video.relative_to(paths.root)),
    }

    write_json(paths.manifest, manifest)

    print(f"Utworzono projekt: {paths.root}")


def use_project(project_id: str) -> None:
    project_id = validate_project_id(project_id)
    project_path = PROJECTS_DIR / project_id

    if not project_path.exists():
        raise FileNotFoundError(
            f"Projekt nie istnieje: {project_path}"
        )

    CURRENT_PROJECT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CURRENT_PROJECT_FILE.write_text(
        project_id,
        encoding="utf-8",
    )

    print(f"Aktywny projekt: {project_id}")


def list_projects() -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    projects = sorted(
        path.name
        for path in PROJECTS_DIR.iterdir()
        if path.is_dir()
    )

    if not projects:
        print("Brak projektów.")
        return

    current = None

    if CURRENT_PROJECT_FILE.exists():
        current = CURRENT_PROJECT_FILE.read_text(
            encoding="utf-8"
        ).strip()

    for project_id in projects:
        marker = " <- aktywny" if project_id == current else ""
        print(f"- {project_id}{marker}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Zarządzanie projektami AI Factory"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    create_parser = subparsers.add_parser(
        "create",
        help="Tworzy nowy projekt",
    )
    create_parser.add_argument("project_id")
    create_parser.add_argument(
        "--channel",
        default="space",
    )

    use_parser = subparsers.add_parser(
        "use",
        help="Ustawia aktywny projekt",
    )
    use_parser.add_argument("project_id")

    subparsers.add_parser(
        "list",
        help="Pokazuje projekty",
    )

    args = parser.parse_args()

    if args.command == "create":
        create_project(args.project_id, args.channel)

    elif args.command == "use":
        use_project(args.project_id)

    elif args.command == "list":
        list_projects()


if __name__ == "__main__":
    main()