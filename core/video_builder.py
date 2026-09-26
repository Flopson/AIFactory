import argparse
import json
from core.paths import get_paths


def run(paths):
    import json
    from pathlib import Path

    from moviepy import AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips

    BASE = Path(__file__).resolve().parent.parent

    VIDEO_PLAN = paths.video_plan
    IMAGES_DIR = paths.images_dir
    AUDIO_DIR = paths.audio_dir

    OUTPUT_PATH = paths.output_video

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
                lambda t, duration=duration: 1.0 + (0.08 * (t / duration))
            )

            clip = clip.cropped(
                x_center=clip.w / 2,
                y_center=clip.h / 2,
                width=WIDTH,
                height=HEIGHT
            )

        elif motion == "zoom_out":
            clip = clip.resized(
                lambda t, duration=duration: 1.08 - (0.08 * (t / duration))
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

            def pan_left_position(t, duration=duration, horizontal_space=horizontal_space, vertical_space=vertical_space):
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

            def pan_right_position(t, duration=duration, horizontal_space=horizontal_space, vertical_space=vertical_space):
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
        temp_audiofile=str(paths.output_dir / "render-audio.m4a"),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        ffmpeg_params=[
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart"
        ]
    )

    print(f"\nGotowe: {OUTPUT_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Etap produkcji aktywnego projektu")
    parser.add_argument("--check-paths", action="store_true", help="Pokaż ścieżki bez generowania")
    args = parser.parse_args()
    paths = get_paths()
    if not paths.manifest.is_file():
        raise FileNotFoundError(f"Brak projektu: {paths.root}")
    if args.check_paths:
        print(json.dumps({
            "project": paths.project_id,
            "video_plan": str(paths.video_plan),
            "images": str(paths.images_dir),
            "audio": str(paths.audio_dir),
            "video": str(paths.output_video)
        }, indent=2, ensure_ascii=False))
        return
    print(f"Projekt: {paths.project_id}", flush=True)
    run(paths)


if __name__ == "__main__":
    main()
