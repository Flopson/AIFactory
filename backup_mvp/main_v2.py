import json
from pathlib import Path

from moviepy import *

BASE = Path(__file__).parent

VIDEO_PLAN = BASE / "input" / "video_plan.json"
AUDIO_PATH = BASE / "assets" / "audio" / "voice.wav"
OUTPUT_PATH = BASE / "output" / "final_v2.mp4"

WIDTH = 1920
HEIGHT = 1080
FPS = 30

with open(VIDEO_PLAN, "r", encoding="utf-8") as f:
    plan = json.load(f)

clips = []

for scene in plan:

    image_path = BASE / "assets" / "images" / scene["image"]

    duration = scene["duration"]
    motion = scene["motion"]

    print(f"Scena {scene['scene']} -> {image_path.name}")

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
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=WIDTH,
        height=HEIGHT
    )

    clips.append(clip)

video = concatenate_videoclips(clips, method="compose")

audio = AudioFileClip(str(AUDIO_PATH))

video = video.with_audio(audio)

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