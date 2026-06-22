import json
import urllib.request


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

    with urllib.request.urlopen(req, timeout=120) as response:
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
    prompt = f"""
You are an expert movie director and AI image prompt engineer.

Create visual direction for this narration scene.

Channel style:
{channel_style}

Scene narration:
{scene_text}

Return ONLY valid JSON with these exact keys:
{{
  "shot": "...",
  "camera_motion": "...",
  "lighting": "...",
  "mood": "...",
  "color_palette": "...",
  "visual_style": "...",
  "image_prompt": "..."
}}

Rules:
- image_prompt must be detailed and usable for Stable Diffusion.
- no text, no watermark, no logo.
- keep it cinematic.
- do not include explanations.
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