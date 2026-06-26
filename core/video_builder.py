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

    clip = clip.resized(1.12)

    if motion == "zoom_in":
        clip = clip.resized(
            lambda t: 1.0 + (0.08 * (t / duration))
        )

        clip = clip.cropped(
            x_center=clip.w / 2,
            y_center=clip.h / 2,
            width=WIDTH,
            height=HEIGHT
        )

    elif motion == "zoom_out":
        clip = clip.resized(
            lambda t: 1.08 - (0.08 * (t / duration))
        )

        clip = clip.cropped(
            x_center=clip.w / 2,
            y_center=clip.h / 2,
            width=WIDTH,
            height=HEIGHT
        )

    elif motion == "pan_left":
        horizontal_space = max(0, clip.w - WIDTH)
        vertical_space = max(0, clip.h - HEIGHT)

        def pan_left_position(t):
            progress = min(max(t / duration, 0), 1)

            return (
                -horizontal_space * progress,
                -vertical_space / 2,
            )

        clip = clip.with_position(pan_left_position)

        clip = CompositeVideoClip(
            [clip],
            size=(WIDTH, HEIGHT),
        ).with_duration(duration)

    elif motion == "pan_right":
        horizontal_space = max(0, clip.w - WIDTH)
        vertical_space = max(0, clip.h - HEIGHT)

        def pan_right_position(t):
            progress = min(max(t / duration, 0), 1)

            return (
                -horizontal_space * (1 - progress),
                -vertical_space / 2,
            )

        clip = clip.with_position(pan_right_position)

        clip = CompositeVideoClip(
            [clip],
            size=(WIDTH, HEIGHT),
        ).with_duration(duration)

    else:
        clip = clip.cropped(
            x_center=clip.w / 2,
            y_center=clip.h / 2,
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