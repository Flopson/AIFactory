import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

CHANNELS_PATH = BASE / "config" / "channels.json"
CURRENT_CHANNEL_PATH = BASE / "input" / "channel.txt"
SETTINGS_PATH = BASE / "config" / "settings.json"


def load_current_channel() -> dict:
    channels = json.loads(CHANNELS_PATH.read_text(encoding="utf-8"))
    channel_id = CURRENT_CHANNEL_PATH.read_text(encoding="utf-8").strip()

    if channel_id not in channels:
        raise ValueError(f"Nieznany kanał: {channel_id}")

    return {
        "id": channel_id,
        **channels[channel_id]
    }


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        raise FileNotFoundError(
            f"Brak pliku ustawień: {SETTINGS_PATH}"
        )

    return json.loads(
        SETTINGS_PATH.read_text(encoding="utf-8")
    )