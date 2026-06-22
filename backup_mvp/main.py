from moviepy import *
from pathlib import Path

WIDTH, HEIGHT = 1920, 1080
FPS = 30

BASE = Path(__file__).parent
IMAGES_DIR = BASE / "assets" / "images"
audio_files = list((BASE / "assets" / "audio").glob("*.*"))

if not audio_files:
    raise FileNotFoundError("Brak pliku audio")

AUDIO_PATH = audio_files[0]
OUTPUT_DIR = BASE / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

image_files = sorted(list(IMAGES_DIR.glob("*.png")) + list(IMAGES_DIR.glob("*.jpg")))

if not image_files:
    raise FileNotFoundError("Brak obrazków w assets/images")

if not AUDIO_PATH.exists():
    raise FileNotFoundError("Brak audio assets/audio/voice.wav")

audio = AudioFileClip(str(AUDIO_PATH))
total_duration = audio.duration
scene_duration = total_duration / len(image_files)

clips = []

for i, img_path in enumerate(image_files):
    clip = ImageClip(str(img_path), duration=scene_duration)

    clip = clip.resized(height=HEIGHT)

    if clip.w < WIDTH:
        clip = clip.resized(width=WIDTH)

    clip = clip.cropped(
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=WIDTH,
        height=HEIGHT
    )

    # prosty zoom, czyli bieda-animacja, ale działa
    clip = clip.resized(lambda t: 1 + 0.04 * t / scene_duration)

    clip = clip.cropped(
        x_center=WIDTH / 2,
        y_center=HEIGHT / 2,
        width=WIDTH,
        height=HEIGHT
    )

    clips.append(clip)

video = concatenate_videoclips(clips, method="compose")
video = video.with_audio(audio)

output_path = OUTPUT_DIR / "final.mp4"

video.write_videofile(
    str(output_path),
    fps=FPS,
    codec="libx264",
    audio_codec="aac",
    threads=8
)

print(f"Gotowe: {output_path}")