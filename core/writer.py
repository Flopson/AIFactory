import json
import re
import urllib.request
from core.paths import get_paths

from core.config_loader import load_current_channel, load_settings

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

def generate_outline(
    topic: str,
    channel: dict,
    language: str,
    scene_count: int,
    model: str,
) -> list[str]:
    prompt = f"""
Create an outline for a YouTube documentary.

CHANNEL:
{channel.get("channel_style", "")}

TOPIC:
{topic}

REQUIREMENTS:
- Language: {language}
- Exactly {scene_count} scenes
- One short sentence describing each scene
- Number the scenes from 1 to {scene_count}
- Begin with a strong hook
- Build curiosity and tension
- End with a satisfying conclusion
- Output only the numbered outline
"""

    raw_outline = ask_ollama(
        prompt,
        model=model,
        temperature=0.6,
    )

    outline = []

    for line in raw_outline.splitlines():
        cleaned = re.sub(
            r"^\s*(?:\d+[\.\):\-]|[-*])\s*",
            "",
            line,
        ).strip()

        if cleaned:
            outline.append(cleaned)

    if len(outline) < scene_count:
        raise ValueError(
            f"Ollama wygenerowała tylko {len(outline)} "
            f"punktów planu zamiast {scene_count}."
        )

    return outline[:scene_count]

def generate_script(
    topic: str,
    channel: dict,
    settings: dict,
) -> str:
    language = settings.get("language", "English")
    target_minutes = int(settings.get("target_minutes", 10))
    words_per_minute = int(settings.get("words_per_minute", 175))
    words_per_scene = int(settings.get("words_per_scene", 110))
    model = settings.get("ollama_model", "llama3.1:8b")

    target_words = target_minutes * words_per_minute
    scene_count = max(
        3,
        round(target_words / words_per_scene),
    )

    minimum_scene_words = int(words_per_scene * 0.9)
    maximum_scene_words = int(words_per_scene * 1.1)

    print(
        f"Writer: celuję w {scene_count} scen "
        f"po około {words_per_scene} słów."
    )

    outline = generate_outline(
        topic=topic,
        channel=channel,
        language=language,
        scene_count=scene_count,
        model=model,
    )

    paragraphs = []
    previous_scene = "This is the opening scene."

    for index, scene_outline in enumerate(outline, start=1):
        print(
            f"Writer: generuję scenę {index}/{scene_count}..."
        )

        scene_prompt = f"""
You are writing one scene of a YouTube documentary narration.

CHANNEL STYLE:
{channel.get("channel_style", "")}

FULL TOPIC:
{topic}

CURRENT SCENE:
Scene {index} of {scene_count}

SCENE PURPOSE:
{scene_outline}

PREVIOUS SCENE CONTEXT:
{previous_scene[-700:]}

REQUIREMENTS:
- Language: {language}
- Write between {minimum_scene_words} and {maximum_scene_words} words
- Write exactly one natural paragraph
- Continue the story logically
- Use vivid and visual descriptions
- Maintain curiosity and forward momentum
- Do not include a heading
- Do not include a scene number
- Do not include markdown
- Output only the narration paragraph
"""

        paragraph = clean_script(
            ask_ollama(
                scene_prompt,
                model=model,
                temperature=0.75,
            )
        )

        # Jedna scena musi być jednym akapitem
        paragraph = " ".join(paragraph.split())

        # Maksymalnie dwie poprawki konkretnej sceny
        for attempt in range(2):
            current_words = len(paragraph.split())

            if current_words >= minimum_scene_words:
                break

            print(
                f"Scena {index} jest za krótka "
                f"({current_words}/{minimum_scene_words}). "
                f"Rozszerzam — próba {attempt + 1}/2..."
            )

            expansion_prompt = f"""
Expand the following narration paragraph.

REQUIREMENTS:
- Language: {language}
- Between {minimum_scene_words} and {maximum_scene_words} words
- Preserve all existing information
- Add useful visual detail and narrative tension
- Keep it as exactly one paragraph
- Do not add headings or scene numbers
- Output only the expanded paragraph

PARAGRAPH:
{paragraph}
"""

            paragraph = clean_script(
                ask_ollama(
                    expansion_prompt,
                    model=model,
                    temperature=0.65,
                )
            )

            paragraph = " ".join(paragraph.split())

        paragraphs.append(paragraph)
        previous_scene = paragraph

    script = "\n\n".join(paragraphs)
    final_word_count = len(script.split())
    minimum_total = int(target_words * 0.9)

    print(
        f"Writer: wynik końcowy: "
        f"{final_word_count}/{target_words} słów."
    )

    if final_word_count < minimum_total:
        print(
            f"UWAGA: tekst jest krótszy niż 90% celu "
            f"({minimum_total} słów)."
        )

    return script

    


def main() -> None:
    paths = get_paths()
    if not paths.manifest.is_file():
        raise FileNotFoundError(f"Brak projektu: {paths.root}")

    print(f"Writer: projekt {paths.project_id}")
    settings = load_settings()
    mode = settings.get("script_mode", "manual").lower()

    if mode == "manual":
        if not paths.script.exists() or not paths.script.read_text(
            encoding="utf-8-sig"
        ).strip():
            raise FileNotFoundError(
                f"Tryb manualny: brak lub pusty scenariusz {paths.script}"
            )

        print("Writer: tryb manualny — pozostawiam istniejący script.txt.")
        return

    if mode != "topic":
        raise ValueError(
            f"Nieznany script_mode: {mode}. "
            "Dozwolone wartości: topic albo manual."
        )

    if not paths.topic.exists():
        raise FileNotFoundError(
            f"Brak pliku z tematem: {paths.topic}"
        )

    topic = paths.topic.read_text(encoding="utf-8-sig").strip()

    if not topic:
        raise ValueError(f"Plik tematu jest pusty: {paths.topic}")

    channel = load_current_channel()

    print(f"Writer: tworzę scenariusz dla tematu: {topic}")
    print(f"Kanał: {channel.get('name', channel['id'])}")

    script = generate_script(topic, channel, settings)

    paths.script.write_text(script, encoding="utf-8")

    word_count = len(script.split())

    metadata = {
        "project_id": paths.project_id,
        "topic": topic,
        "channel": channel["id"],
        "language": settings.get("language", "English"),
        "target_minutes": settings.get("target_minutes", 10),
        "word_count": word_count,
        "script_mode": mode,
    }

    paths.script_meta.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Writer: wygenerowano {word_count} słów.")
    print(f"Scenariusz zapisany: {paths.script}")


if __name__ == "__main__":
    main()