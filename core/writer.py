import json
import re
import urllib.request
from pathlib import Path

from core.config_loader import load_current_channel, load_settings

BASE = Path(__file__).resolve().parent.parent

TOPIC_PATH = BASE / "input" / "topic.txt"
SCRIPT_PATH = BASE / "input" / "script.txt"
META_PATH = BASE / "input" / "script_meta.json"

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def ask_ollama(
    prompt: str,
    model: str,
    temperature: float = 0.75,
) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": 8192,
            "num_predict": 4096,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request, timeout=600) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"].strip()


def clean_script(text: str) -> str:
    cleaned_lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("```"):
            continue

        # Usuwamy nagłówki typu "Scene 1" albo "Chapter 2"
        if re.fullmatch(
            r"(scene|scena|chapter|rozdział)\s+\d+\s*:?",
            stripped,
            flags=re.IGNORECASE,
        ):
            continue

        if stripped.startswith("#"):
            stripped = stripped.lstrip("#").strip()

        cleaned_lines.append(stripped)

    # Ograniczamy wielokrotne puste linie
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def generate_script(
    topic: str,
    channel: dict,
    settings: dict,
) -> str:
    language = settings.get("language", "English")
    target_minutes = int(settings.get("target_minutes", 10))
    words_per_minute = int(settings.get("words_per_minute", 145))
    words_per_scene = int(settings.get("words_per_scene", 110))
    model = settings.get("ollama_model", "llama3.1:8b")

    target_words = target_minutes * words_per_minute
    scene_count = max(5, round(target_words / words_per_scene))

    prompt = f"""
You are a professional YouTube documentary scriptwriter.

Write a highly engaging narration script based on the supplied topic.

CHANNEL:
Name: {channel.get("name", channel.get("id", "Unknown"))}
Style: {channel.get("channel_style", "")}
Visual style: {channel.get("visual_style", "")}

TOPIC:
{topic}

REQUIREMENTS:
- Language: {language}
- Target length: approximately {target_words} words
- Target duration: approximately {target_minutes} minutes
- Divide the script into approximately {scene_count} visual scenes
- Each scene must be one natural paragraph
- Separate every scene using exactly one blank line
- Each paragraph should contain approximately {words_per_scene} words
- Start with a powerful hook
- Maintain curiosity and forward momentum
- Avoid repeating the same information
- Use vivid, visual descriptions suitable for AI-generated images
- End with a satisfying conclusion
- Do not include headings
- Do not include scene numbers
- Do not include production instructions
- Do not include markdown
- Output only the final narration script
"""

    script = clean_script(
        ask_ollama(prompt, model=model)
    )

    current_words = len(script.split())

    # Jedna próba rozszerzenia, jeśli model zrobił podejrzanie krótki tekst
    if current_words < target_words * 0.7:
        print(
            f"Scenariusz jest za krótki "
            f"({current_words}/{target_words} słów). Rozszerzam..."
        )

        expansion_prompt = f"""
Rewrite and expand the following YouTube narration script.

TARGET:
- Language: {language}
- Approximately {target_words} words
- Approximately {scene_count} paragraphs
- One visual scene per paragraph
- Blank line between paragraphs
- Preserve the topic, narrative logic, tone, and existing facts
- Improve the hook, tension, transitions, and conclusion
- Do not add headings or scene numbers
- Do not use markdown
- Output only the complete rewritten narration script

SCRIPT:
{script}
"""

        script = clean_script(
            ask_ollama(
                expansion_prompt,
                model=model,
                temperature=0.65,
            )
        )

    return script


def main() -> None:
    settings = load_settings()
    mode = settings.get("script_mode", "manual").lower()

    if mode == "manual":
        if not SCRIPT_PATH.exists() or not SCRIPT_PATH.read_text(
            encoding="utf-8"
        ).strip():
            raise FileNotFoundError(
                "Tryb manualny jest aktywny, ale input/script.txt jest pusty."
            )

        print("Writer: tryb manualny — pozostawiam istniejący script.txt.")
        return

    if mode != "topic":
        raise ValueError(
            f"Nieznany script_mode: {mode}. "
            "Dozwolone wartości: topic albo manual."
        )

    if not TOPIC_PATH.exists():
        raise FileNotFoundError(
            f"Brak pliku z tematem: {TOPIC_PATH}"
        )

    topic = TOPIC_PATH.read_text(encoding="utf-8").strip()

    if not topic:
        raise ValueError("input/topic.txt jest pusty.")

    channel = load_current_channel()

    print(f"Writer: tworzę scenariusz dla tematu: {topic}")
    print(f"Kanał: {channel.get('name', channel['id'])}")

    script = generate_script(topic, channel, settings)

    SCRIPT_PATH.write_text(script, encoding="utf-8")

    word_count = len(script.split())

    metadata = {
        "topic": topic,
        "channel": channel["id"],
        "language": settings.get("language", "English"),
        "target_minutes": settings.get("target_minutes", 10),
        "word_count": word_count,
        "script_mode": mode,
    }

    META_PATH.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Writer: wygenerowano {word_count} słów.")
    print(f"Scenariusz zapisany: {SCRIPT_PATH}")


if __name__ == "__main__":
    main()