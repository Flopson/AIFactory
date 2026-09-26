import json

from core.paths import ROOT, get_paths


CHANNELS_PATH = ROOT / "config" / "channels.json"
SETTINGS_PATH = ROOT / "config" / "settings.json"


def load_current_channel() -> dict:
    paths = get_paths()

    if not paths.manifest.is_file():
        raise FileNotFoundError(f"Brak projektu: {paths.root}")

    channels = json.loads(
        CHANNELS_PATH.read_text(encoding="utf-8-sig")
    )

    channel_id = paths.channel.read_text(
        encoding="utf-8-sig"
    ).strip()

    if channel_id not in channels:
        raise ValueError(f"Nieznany kanał: {channel_id}")

    return {
        **channels[channel_id],
        "id": channel_id,
    }


def load_settings() -> dict:
    return json.loads(
        SETTINGS_PATH.read_text(encoding="utf-8-sig")
    )