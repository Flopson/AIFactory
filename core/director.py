import json
import urllib.request
from pathlib import Path
from core.memory import Memory

BASE = Path(__file__).resolve().parent.parent

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.1:8b"


def load_memory_context() -> str:
    memory = Memory()

    sections = []

    characters = memory.characters.get("characters", [])
    if characters:
        character_lines = []

        for character in characters:
            character_lines.append(
                (
                    f"Name: {character.get('name', 'Unknown')}\n"
                    f"Type: {character.get('type', '')}\n"
                    f"Appearance: {character.get('appearance', '')}\n"
                    f"Clothing: {character.get('clothing', '')}\n"
                    f"Important features: "
                    f"{character.get('important_features', '')}\n"
                    f"Prompt fragment: "
                    f"{character.get('prompt_fragment', '')}"
                )
            )

        sections.append(
            "CHARACTERS:\n" + "\n\n".join(character_lines)
        )

    locations = memory.locations.get("locations", [])
    if locations:
        location_lines = []

        for location in locations:
            location_lines.append(
                (
                    f"Name: {location.get('name', 'Unknown')}\n"
                    f"Appearance: {location.get('appearance', '')}\n"
                    f"Lighting: {location.get('lighting', '')}\n"
                    f"Color palette: {location.get('color_palette', '')}\n"
                    f"Important features: "
                    f"{location.get('important_features', '')}\n"
                    f"Prompt fragment: "
                    f"{location.get('prompt_fragment', '')}"
                )
            )

        sections.append(
            "LOCATIONS:\n" + "\n\n".join(location_lines)
        )

    objects = memory.objects.get("objects", [])
    if objects:
        object_lines = []

        for item in objects:
            object_lines.append(
                (
                    f"Name: {item.get('name', 'Unknown')}\n"
                    f"Appearance: {item.get('appearance', '')}\n"
                    f"Important features: "
                    f"{item.get('important_features', '')}\n"
                    f"Prompt fragment: "
                    f"{item.get('prompt_fragment', '')}"
                )
            )

        sections.append(
            "IMPORTANT OBJECTS:\n" + "\n\n".join(object_lines)
        )

    story = memory.story

    if story:
        rules = story.get("world_rules", [])
        formatted_rules = "\n".join(f"- {rule}" for rule in rules)

        sections.append(
            (
                "STORY:\n"
                f"Summary: {story.get('summary', '')}\n"
                f"Visual continuity: "
                f"{story.get('visual_continuity', '')}\n"
                f"World rules:\n{formatted_rules}"
            )
        )

    if not sections:
        return "No story memory has been defined."

    return "\n\n".join(sections)


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
    memory_context = load_memory_context()

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

STORY BIBLE:
{memory_context}

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