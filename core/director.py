import json
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.1:8b"

CHARACTERS_PATH = BASE / "assets" / "characters" / "characters.json"


def load_json(path: Path, fallback: dict) -> dict:
    if not path.exists():
        return fallback

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def load_character_context() -> str:
    data = load_json(CHARACTERS_PATH, {"characters": []})
    characters = data.get("characters", [])

    if not characters:
        return "No recurring characters defined."

    lines = []

    for character in characters:
        lines.append(
            f"""
Name: {character.get("name", "Unknown")}
Type: {character.get("type", "Unknown")}
Appearance: {character.get("appearance", "")}
Clothing: {character.get("clothing", "")}
Important features: {character.get("important_features", "")}
Prompt fragment: {character.get("prompt_fragment", "")}
""".strip()
        )

    return "\n\n".join(lines)


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


def fallback_director(scene_text: str) -> dict:
    return {
        "shot": "wide cinematic establishing shot",
        "camera_motion": "slow zoom in",
        "lighting": "dramatic volumetric lighting",
        "mood": "mysterious and cinematic",
        "color_palette": "blue, black, silver",
        "visual_style": "cinematic sci-fi concept art",
        "image_prompt": (
            "cinematic sci-fi concept art, wide establishing shot, "
            "dramatic volumetric lighting, mysterious atmosphere, "
            f"{scene_text}, highly detailed, no text, no watermark"
        )
    }


def direct_scene(scene_text: str, channel_style: str = "cinematic sci-fi") -> dict:
    character_context = load_character_context()

    prompt = f"""
SYSTEM:
You are an award-winning movie director, cinematographer, and Stable Diffusion prompt engineer.

ROLE:
Your job is to create visual direction for one scene of an AI-generated YouTube video.

CHANNEL STYLE:
{channel_style}

STORY CONTINUITY RULES:
All scenes belong to the same story.
Keep visual consistency.
If recurring characters exist, preserve their appearance exactly.
Do not randomly change age, hair, clothing, species, or important visual features.

CHARACTERS:
{character_context}

CURRENT SCENE:
{scene_text}

OUTPUT FORMAT:
Return ONLY valid JSON with exactly these keys:

{{
  "shot": "...",
  "camera_motion": "...",
  "lighting": "...",
  "mood": "...",
  "color_palette": "...",
  "visual_style": "...",
  "image_prompt": "..."
}}

RULES:
- image_prompt must be detailed and usable for Stable Diffusion.
- image_prompt must include character continuity if relevant.
- image_prompt must not contain dialogue.
- image_prompt must not contain text overlays.
- image_prompt must include: no text, no watermark, no logo.
- Keep it cinematic and visually coherent.
- Do not include markdown.
- Do not include explanations.
"""

    try:
        raw = ask_ollama(prompt)
        data = json.loads(raw)

        required = [
            "shot",
            "camera_motion",
            "lighting",
            "mood",
            "color_palette",
            "visual_style",
            "image_prompt"
        ]

        for key in required:
            if key not in data:
                raise ValueError(f"Missing key: {key}")

        return data

    except Exception as error:
        print("Director fallback:", error)
        return fallback_director(scene_text)