import subprocess
from pathlib import Path

BASE = Path(__file__).parent

SCRIPT = BASE / "input" / "script.txt"
OUTPUT = BASE / "assets" / "audio" / "voice.wav"

PIPER = BASE / "tools" / "piper" / "piper.exe"
MODEL = BASE / "models" / "en_US-lessac-medium.onnx"

text = SCRIPT.read_text(encoding="utf-8")

process = subprocess.run(
    [
        str(PIPER),
        "-m",
        str(MODEL),
        "-f",
        str(OUTPUT)
    ],
    input=text,
    text=True
)

print("Audio wygenerowane:", OUTPUT)