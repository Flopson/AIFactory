"""Explicit local pipeline: draft -> review -> approve -> produce."""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

from core.paths import ROOT, ProjectPaths, get_current_project_id
from core.review_gate import approval_path, fingerprint, now, require_approval, write_json


PRODUCTION_STEPS = (
    "core.script_splitter", "core.memory_builder", "core.scene_planner",
    "core.audio_generator", "core.image_generator", "core.video_builder",
)


def run_step(module, paths):
    env = os.environ.copy()
    env["AIFACTORY_PROJECT_ID"] = paths.project_id
    env["PYTHONIOENCODING"] = "utf-8"
    print(f"\nSTART: {module} | projekt: {paths.project_id}", flush=True)
    subprocess.run([sys.executable, "-m", module], cwd=ROOT, env=env, check=True)


def execute(args, paths):
    if args.command == "draft":
        if paths.script.is_file() and paths.script.read_text(encoding="utf-8-sig").strip():
            if not args.replace_script:
                raise ValueError("Scenariusz już istnieje. Do nowej generacji użyj --replace-script; powstanie kopia.")
            backup = paths.logs_dir / ("script-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".txt")
            shutil.copy2(paths.script, backup)
            print(f"Kopia poprzedniego tekstu: {backup}")
        approval_path(paths).unlink(missing_ok=True)
        run_step("core.writer", paths)
        fingerprint(paths)
        print("\nScenariusz gotowy do oceny. Następny krok: review. Produkcja nie została uruchomiona.")
    elif args.command == "review":
        token = fingerprint(paths)
        print(f"Projekt: {paths.project_id}\nTEMAT:\n{paths.topic.read_text(encoding='utf-8-sig')}")
        print(f"\nSCENARIUSZ:\n{paths.script.read_text(encoding='utf-8-sig')}")
        print("\nUSTAWIENIA:\n" + (ROOT / "config/settings.json").read_text(encoding="utf-8-sig"))
        channel_id = paths.channel.read_text(encoding="utf-8-sig").strip()
        channels = json.loads((ROOT / "config/channels.json").read_text(encoding="utf-8-sig"))
        print("\nKanał: " + channel_id)
        print(json.dumps(channels[channel_id], indent=2, ensure_ascii=False))
        if token != fingerprint(paths):
            raise ValueError("Pliki zmieniły się podczas przeglądu. Powtórz review.")
        write_json(paths.root / "script_review.json", {"fingerprint": token, "reviewed_at": now()})
        print("\nJeśli akceptujesz temat i tekst, wykonaj:")
        print(f"python run_pipeline.py approve --project {paths.project_id} --review {token}")
    elif args.command == "approve":
        review = json.loads((paths.root / "script_review.json").read_text(encoding="utf-8"))
        current = fingerprint(paths)
        if args.review != current or review.get("fingerprint") != current:
            raise ValueError("To nie jest wersja z przeglądu. Uruchom ponownie review.")
        write_json(approval_path(paths), {"fingerprint": current, "approved_at": now(), "project": paths.project_id})
        print("Temat i scenariusz zaakceptowane. Produkcję uruchamiasz osobną komendą produce.")
    elif args.command == "status":
        print(f"Projekt: {paths.project_id}\nScenariusz: {paths.script}")
        try:
            require_approval(paths)
            print("Akceptacja scenariusza: aktualna")
        except (ValueError, OSError) as exc:
            print(f"Akceptacja scenariusza: brak lub nieaktualna ({exc})")
        state = paths.root / "production_state.json"
        if state.is_file():
            print(state.read_text(encoding="utf-8"))
    elif args.command == "produce":
        receipt = require_approval(paths)
        state = {"status": "running", "started_at": now(), "fingerprint": receipt["fingerprint"]}
        state_path = paths.root / "production_state.json"
        write_json(state_path, state)
        try:
            for module in PRODUCTION_STEPS:
                require_approval(paths)
                state["stage"] = module
                write_json(state_path, state)
                run_step(module, paths)
                require_approval(paths)
            if not paths.output_video.is_file() or paths.output_video.stat().st_size == 0:
                raise ValueError("Montaż nie utworzył niepustego pliku MP4.")
            state.update(status="awaiting_video_review", finished_at=now(), output=str(paths.output_video))
            write_json(state_path, state)
        except BaseException as exc:
            state.update(status="failed", error=str(exc), finished_at=now())
            write_json(state_path, state)
            raise
        print(f"\nFilm do ręcznego obejrzenia: {paths.output_video}\nNic nie zostało opublikowane.")


def main():
    parser = argparse.ArgumentParser(description="Lokalna fabryka — jawne etapy i akceptacja scenariusza")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("draft", "review", "approve", "status", "produce"):
        child = sub.add_parser(command)
        child.add_argument("--project", help="ID projektu; domyślnie aktywny projekt")
        if command == "draft":
            child.add_argument("--replace-script", action="store_true")
        if command == "approve":
            child.add_argument("--review", required=True, help="Identyfikator pokazany przez review")
    args = parser.parse_args()
    paths = ProjectPaths(args.project or get_current_project_id())
    if not paths.manifest.is_file():
        parser.exit(1, f"Brak projektu: {paths.root}\n")
    paths.ensure_structure()
    lock = paths.root / ".pipeline.lock"
    try:
        lock.open("x").close()
    except FileExistsError:
        parser.exit(1, f"Projekt jest zajęty. Jeśli poprzedni proces został przerwany, sprawdź go przed usunięciem {lock}\n")
    try:
        execute(args, paths)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"BŁĄD: {exc}\n")
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
