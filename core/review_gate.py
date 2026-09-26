"""Local review receipt for the main pipeline; no external services."""
import hashlib
import json
from datetime import datetime, timezone

from core.paths import ROOT


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


def fingerprint(paths):
    topic = paths.topic.read_text(encoding="utf-8-sig").strip()
    script = paths.script.read_text(encoding="utf-8-sig").strip()
    if not topic or not script:
        raise ValueError("Temat i scenariusz muszą być niepuste.")
    channel_id = paths.channel.read_text(encoding="utf-8-sig").strip()
    channels = json.loads((ROOT / "config/channels.json").read_text(encoding="utf-8-sig"))
    if channel_id not in channels:
        raise ValueError(f"Nieznany kanał: {channel_id}")
    # Hash exact text bytes as well as the effective channel/settings configuration.
    data = {
        "project": paths.project_id,
        "topic": hashlib.sha256(paths.topic.read_bytes()).hexdigest(),
        "script": hashlib.sha256(paths.script.read_bytes()).hexdigest(),
        "channel_id": channel_id,
        "channel": channels[channel_id],
        "settings": json.loads((ROOT / "config/settings.json").read_text(encoding="utf-8-sig")),
    }
    encoded = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def approval_path(paths):
    return paths.root / "script_approval.json"


def require_approval(paths):
    path = approval_path(paths)
    if not path.is_file():
        raise ValueError("Brak akceptacji. Uruchom review, przeczytaj tekst i wykonaj approve.")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if receipt.get("fingerprint") != fingerprint(paths):
        raise ValueError("Treść lub ustawienia zmieniły się. Wymagana ponowna ocena i akceptacja.")
    return receipt
