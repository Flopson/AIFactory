from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = ROOT / "projects"
CURRENT_PROJECT_FILE = ROOT / "config" / "current_project.txt"


def validate_project_id(project_id: str) -> str:
    project_id = project_id.strip()

    if not re.fullmatch(r"[a-zA-Z0-9_-]+", project_id):
        raise ValueError(
            "ID projektu może zawierać wyłącznie litery, cyfry, _ oraz -"
        )

    return project_id


@dataclass(frozen=True)
class ProjectPaths:
    project_id: str

    @property
    def root(self) -> Path:
        return PROJECTS_DIR / self.project_id

    @property
    def input_dir(self) -> Path:
        return self.root / "input"

    @property
    def memory_dir(self) -> Path:
        return self.root / "memory"

    @property
    def assets_dir(self) -> Path:
        return self.root / "assets"

    @property
    def audio_dir(self) -> Path:
        return self.assets_dir / "audio" / "scenes"

    @property
    def images_dir(self) -> Path:
        return self.assets_dir / "images"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def topic(self) -> Path:
        return self.input_dir / "topic.txt"

    @property
    def channel(self) -> Path:
        return self.input_dir / "channel.txt"

    @property
    def script(self) -> Path:
        return self.input_dir / "script.txt"

    @property
    def script_meta(self) -> Path:
        return self.input_dir / "script_meta.json"

    @property
    def scenes(self) -> Path:
        return self.input_dir / "scenes.json"

    @property
    def video_plan(self) -> Path:
        return self.input_dir / "video_plan.json"

    @property
    def characters(self) -> Path:
        return self.memory_dir / "characters.json"

    @property
    def locations(self) -> Path:
        return self.memory_dir / "locations.json"

    @property
    def objects(self) -> Path:
        return self.memory_dir / "objects.json"

    @property
    def story(self) -> Path:
        return self.memory_dir / "story.json"

    @property
    def manifest(self) -> Path:
        return self.root / "project.json"

    @property
    def output_video(self) -> Path:
        return self.output_dir / f"{self.project_id}.mp4"

    def ensure_structure(self) -> None:
        directories = [
            self.input_dir,
            self.memory_dir,
            self.audio_dir,
            self.images_dir,
            self.output_dir,
            self.logs_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


def get_current_project_id() -> str:
    if not CURRENT_PROJECT_FILE.exists():
        raise FileNotFoundError(
            "Brak config/current_project.txt. "
            "Najpierw utwórz albo wybierz projekt."
        )

    project_id = CURRENT_PROJECT_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not project_id:
        raise ValueError("config/current_project.txt jest pusty.")

    return validate_project_id(project_id)


def get_paths() -> ProjectPaths:
    paths = ProjectPaths(get_current_project_id())
    paths.ensure_structure()
    return paths


