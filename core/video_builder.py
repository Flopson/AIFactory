import json
from pathlib import Path

from moviepy import *

BASE = Path(__file__).resolve().parent.parent

VIDEO_PLAN = BASE / "input" / "video_plan.json"
IMAGES_DIR = BASE / "assets" / "images"
AUDIO_DIR = BASE / "assets" / "audio" / "scenes"

OUTPUT_PATH = BASE / "output" / "final_v3.mp4"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

plan = json.loads(VIDEO_PLAN.read_text(encoding="utf-8"))

video_clips = []
audio_clips = []

for scene in plan:

    scene_number = scene["scene"]

    image_path = IMAGES_DIR / scene["image"]
    audio_path = AUDIO_DIR / f"scene_{scene_number}.wav"

    print(f"Scena {scene_number}")

    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    motion = scene["motion"]

    clip = ImageClip(str(image_path), duration=duration)

    clip = clip.resized(height=HEIGHT)

    if clip.w < WIDTH:
        clip = clip.resized(width=WIDTH)

    clip = clip.cropped(
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=WIDTH,
        height=HEIGHT
    )

    if motion == "zoom_in":

        clip = clip.resized(
            lambda t: 1 + (0.08 * (t / duration))
        )

    elif motion == "zoom_out":

        clip = clip.resized(
            lambda t: 1.08 - (0.08 * (t / duration))
        )

    else:

        clip = clip.resized(
            lambda t: 1 + (0.04 * (t / duration))
        )

    clip = clip.cropped(
        x_center=WIDTH / 2,
        y_center=HEIGHT / 2,
        width=WIDTH,
        height=HEIGHT
    )

    clip = clip.with_audio(audio)

    video_clips.append(clip)
    audio_clips.append(audio)

video = concatenate_videoclips(
    video_clips,
    method="compose"
)

video.write_videofile(
    str(OUTPUT_PATH),
    fps=FPS,
    codec="libx264",
    audio_codec="aac",
    ffmpeg_params=[
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart"
    ]
)

print(f"\nGotowe: {OUTPUT_PATH}")