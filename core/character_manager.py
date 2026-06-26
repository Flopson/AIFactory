import json
import urllib.request
from pathlib import Path
from core.memory import Memory

BASE = Path(__file__).resolve().parent.parent

SCRIPT_PATH = BASE / "input" / "script.txt"

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.1:8b"


def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]


def fallback_characters() -> dict:
    return {
        "characters": []
    }


def extract_characters(script: str) -> dict:
    prompt = f"""
You are a character continuity assistant for an AI video production pipeline.

Analyze the script and extract recurring characters, creatures, robots, or named entities that should stay visually consistent across scenes.

Return ONLY valid JSON in this exact structure:

{{
  "characters": [
    {{
      "name": "Character name",
      "type": "human / robot / creature / alien / object / location",
      "appearance": "short but detailed visual description",
      "clothing": "consistent outfit or surface details",
      "important_features": "unique visual features that must remain consistent",
      "prompt_fragment": "compact Stable Diffusion prompt fragment for this character"
    }}
  ]
}}

Rules:
- If there are no recurring characters, return {{"characters": []}}.
- Do not include explanations.
- Do not include markdown.
- Keep prompt_fragment visual and concise.
- Avoid copyrighted character names.

SCRIPT:
{script}
"""

    try:
        raw = ask_ollama(prompt)
        data = json.loads(raw)

        if "characters" not in data:
            raise ValueError("Missing characters key")

        return data

    except Exception as error:
        print("Character Manager fallback:", error)
        return fallback_characters()


def main():
    script = SCRIPT_PATH.read_text(encoding="utf-8")
    characters = extract_characters(script)

    memory = Memory()
    memory.characters = characters
    memory.save()

    print("Zapisano characters.json do assets/memory/")


if __name__ == "__main__":
    main()