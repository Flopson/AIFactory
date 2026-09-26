import json
import urllib.request
from core.paths import get_paths
from core.config_loader import load_settings

from core.memory import Memory

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def ask_ollama(prompt: str) -> str:
    payload = {
        "model": load_settings().get("ollama_model", "llama3.1:8b"),
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


def fallback_memory() -> dict:
    return {
        "characters": {"characters": []},
        "locations": {"locations": []},
        "objects": {"objects": []},
        "story": {
            "summary": "",
            "visual_continuity": "",
            "world_rules": [],
        },
    }


def analyse_script(script: str) -> dict:
    prompt = f"""
You are the continuity supervisor for an AI film production system.

Analyze the complete script and build a visual story bible.

Return ONLY valid JSON in exactly this structure:

{{
  "characters": {{
    "characters": [
      {{
        "name": "...",
        "type": "human / robot / creature / alien",
        "appearance": "...",
        "clothing": "...",
        "important_features": "...",
        "prompt_fragment": "..."
      }}
    ]
  }},
  "locations": {{
    "locations": [
      {{
        "name": "...",
        "appearance": "...",
        "lighting": "...",
        "color_palette": "...",
        "important_features": "...",
        "prompt_fragment": "..."
      }}
    ]
  }},
  "objects": {{
    "objects": [
      {{
        "name": "...",
        "appearance": "...",
        "important_features": "...",
        "prompt_fragment": "..."
      }}
    ]
  }},
  "story": {{
    "summary": "...",
    "visual_continuity": "...",
    "world_rules": [
      "..."
    ]
  }}
}}

Rules:
- Include only recurring or visually important entities.
- Descriptions must be visually specific and consistent.
- prompt_fragment must be concise and usable in Stable Diffusion.
- Do not invent unnecessary characters.
- Do not use markdown.
- Do not include explanations outside JSON.

SCRIPT:
{script}
"""

    try:
        raw_response = ask_ollama(prompt)
        result = json.loads(raw_response)

        required_keys = ["characters", "locations", "objects", "story"]

        for key in required_keys:
            if key not in result:
                raise ValueError(f"Brakuje klucza: {key}")

        return result

    except Exception as error:
        raise RuntimeError(f"Nie udało się przygotować pamięci projektu: {error}") from error


def main() -> None:
    paths = get_paths()
    if not paths.manifest.is_file():
        raise FileNotFoundError(f"Brak projektu: {paths.root}")
    script = paths.script.read_text(encoding="utf-8-sig").strip()
    if not script:
        raise ValueError(f"Scenariusz jest pusty: {paths.script}")
    story_bible = analyse_script(script)

    memory = Memory()
    memory.characters = story_bible["characters"]
    memory.locations = story_bible["locations"]
    memory.objects = story_bible["objects"]
    memory.story = story_bible["story"]
    memory.save()

    print(f"Pamięć projektu {paths.project_id}: {paths.memory_dir}")


if __name__ == "__main__":
    main()