import os

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# =========================
# CONFIG / CONSTANTS
# =========================

VIDEO_DIR = r"D:\SSD data\SC"
OUTPUT_DIR_NAME = "processed"

SUPPORTED_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi", ".webm")

# Logo width as percentage of video width
LOGO_WIDTH_PERCENT = {
    "landscape": 0.12,   # 12% of video width
    "portrait": 0.18    # larger for portrait videos
}

# Margins as percentage of video dimensions
MARGIN_PERCENT = {
    "x": 0.03,  # 3% horizontal margin
    "y": 0.03   # 3% vertical margin
}

OUTPUT_CODEC = "libx264"
OUTPUT_AUDIO_CODEC = "aac"

# =========================
# UTILS
# =========================

def get_script_logo_path():
    """Returns sc.png from the script's directory"""
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sc.png"
    )


def ensure_output_dir(video_dir):
    output_dir = os.path.join(video_dir, OUTPUT_DIR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_orientation(width, height):
    return "portrait" if height > width else "landscape"


def calculate_logo_width(video_width, orientation):
    return int(video_width * LOGO_WIDTH_PERCENT[orientation])


def calculate_position(video_w, video_h, logo_w, logo_h):
    margin_x = int(video_w * MARGIN_PERCENT["x"])
    margin_y = int(video_h * MARGIN_PERCENT["y"])

    x = video_w - logo_w - margin_x
    y = video_h - logo_h - margin_y

    return x, y


# =========================
# CORE PROCESSING
# =========================

def process_video(video_path, logo_path, output_dir):
    print(f"Processing: {os.path.basename(video_path)}")

    with VideoFileClip(video_path) as video:
        vw, vh = video.w, video.h
        orientation = get_orientation(vw, vh)

        # Load logo
        logo = ImageClip(logo_path, transparent=True)

        # Resize logo (MoviePy 2.x API)
        target_logo_width = calculate_logo_width(vw, orientation)
        logo = logo.resized(width=target_logo_width)

        # Position logo
        x, y = calculate_position(vw, vh, logo.w, logo.h)
        logo = logo.with_position((x, y)).with_duration(video.duration)

        # Composite
        final = CompositeVideoClip([video, logo])

        output_path = os.path.join(
            output_dir,
            os.path.basename(video_path)
        )

        final.write_videofile(
            output_path,
            codec=OUTPUT_CODEC,
            audio_codec=OUTPUT_AUDIO_CODEC,
            preset="medium",
            threads=4
        )


# =========================
# LIFECYCLE
# =========================

def main():
    logo_path = get_script_logo_path()
    if not os.path.exists(logo_path):
        raise FileNotFoundError("❌ sc.png not found in script directory")

    output_dir = ensure_output_dir(VIDEO_DIR)

    for file in os.listdir(VIDEO_DIR):
        if file.lower().endswith(SUPPORTED_EXTENSIONS):
            video_path = os.path.join(VIDEO_DIR, file)
            process_video(video_path, logo_path, output_dir)

    print("✅ All videos processed successfully.")


if __name__ == "__main__":
    main()
