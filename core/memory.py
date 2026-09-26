import json
from core.paths import ROOT, get_paths


class Memory:

    def __init__(self):

        paths = get_paths()
        if not paths.manifest.is_file():
            raise FileNotFoundError(f"Brak projektu: {paths.root}")

        self.base = ROOT
        self.memory_dir = paths.memory_dir

        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.characters = self._load("characters.json", {"characters": []})

        self.locations = self._load("locations.json", {"locations": []})

        self.objects = self._load("objects.json", {"objects": []})

        self.story = self._load("story.json", {})


    def _load(self, filename, default):

        path = self.memory_dir / filename

        if not path.exists():
            path.write_text(
                json.dumps(default, indent=2),
                encoding="utf-8"
            )
            return default

        return json.loads(path.read_text(encoding="utf-8"))


    def save(self):

        (self.memory_dir / "characters.json").write_text(
            json.dumps(self.characters, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        (self.memory_dir / "locations.json").write_text(
            json.dumps(self.locations, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        (self.memory_dir / "objects.json").write_text(
            json.dumps(self.objects, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        (self.memory_dir / "story.json").write_text(
            json.dumps(self.story, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )