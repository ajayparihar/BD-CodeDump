import os
import threading
import subprocess
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from tkinterdnd2 import TkinterDnD, DND_FILES

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

# =========================
# CONSTANTS
# =========================

SUPPORTED_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi", ".webm")
OUTPUT_DIR_NAME = "processed"

PRESETS = {
    "Default": dict(size=12, margin=3, safe_bottom=0, safe_right=0),
    "Instagram Reels": dict(size=16, margin=4, safe_bottom=12, safe_right=6),
    "TikTok": dict(size=18, margin=4, safe_bottom=14, safe_right=8),
    "YouTube Shorts": dict(size=15, margin=4, safe_bottom=10, safe_right=0),
}

# =========================
# UTILS
# =========================

def get_logo_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "sc.png")


def find_videos(paths):
    videos = []
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            videos.append(p)
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.suffix.lower() in SUPPORTED_EXTENSIONS:
                    videos.append(f)
    return videos


def orientation(w, h):
    return "portrait" if h > w else "landscape"


# =========================
# PROCESSORS
# =========================

def process_moviepy(video, logo, settings, log):
    output_dir = video.parent / OUTPUT_DIR_NAME
    output_dir.mkdir(exist_ok=True)

    out = output_dir / video.name
    if out.exists():
        log(f"⏭ Skipped: {video.name}")
        return

    log(f"▶ Processing (MoviePy): {video.name}")

    with VideoFileClip(str(video)) as clip:
        vw, vh = clip.w, clip.h

        logo_clip = ImageClip(logo, transparent=True)

        logo_w = int(vw * settings["size"] / 100)
        logo_clip = logo_clip.resized(width=logo_w)

        mx = int(vw * settings["margin"] / 100)
        my = int(vh * settings["margin"] / 100)

        safe_b = int(vh * settings["safe_bottom"] / 100)
        safe_r = int(vw * settings["safe_right"] / 100)

        x = vw - logo_clip.w - mx - safe_r
        y = vh - logo_clip.h - my - safe_b

        logo_clip = logo_clip.with_position((x, y)).with_duration(clip.duration)

        final = CompositeVideoClip([clip, logo_clip])

        final.write_videofile(
            str(out),
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger=None
        )

    log(f"✅ Done: {video.name}")


def process_ffmpeg(video, logo, settings, log):
    output_dir = video.parent / OUTPUT_DIR_NAME
    output_dir.mkdir(exist_ok=True)

    out = output_dir / video.name
    if out.exists():
        log(f"⏭ Skipped: {video.name}")
        return

    log(f"⚡ Processing (ffmpeg): {video.name}")

    size = settings["size"] / 100
    margin = settings["margin"] / 100
    safe_b = settings["safe_bottom"] / 100
    safe_r = settings["safe_right"] / 100

    filter_complex = (
        f"[1][0]scale2ref=w=iw*{size}:h=ow/mdar[logo][vid];"
        f"[vid][logo]overlay="
        f"x=W-w-(W*{margin})-(W*{safe_r}):"
        f"y=H-h-(H*{margin})-(H*{safe_b})"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", logo,
        "-filter_complex", filter_complex,
        "-c:a", "copy",
        str(out)
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log(f"✅ Done: {video.name}")


# =========================
# GUI
# =========================

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Video Logo Tool PRO")
        self.geometry("820x600")

        self.logo = get_logo_path()
        self.videos = []

        self.size = tk.IntVar(value=12)
        self.margin = tk.IntVar(value=3)
        self.backend = tk.StringVar(value="MoviePy")
        self.preset = tk.StringVar(value="Default")

        self.build_ui()

    def build_ui(self):
        ttk.Label(self, text="Drag Videos / Folders", font=("Segoe UI", 12, "bold")).pack()

        self.listbox = tk.Listbox(self, height=8)
        self.listbox.pack(fill="both", expand=True, padx=10)
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind("<<Drop>>", self.on_drop)

        controls = ttk.Frame(self)
        controls.pack(fill="x", padx=10)

        ttk.Label(controls, text="Logo Size %").grid(row=0, column=0)
        ttk.Scale(controls, from_=5, to=30, variable=self.size, orient="horizontal").grid(row=0, column=1, sticky="ew")

        ttk.Label(controls, text="Margin %").grid(row=1, column=0)
        ttk.Scale(controls, from_=1, to=10, variable=self.margin, orient="horizontal").grid(row=1, column=1, sticky="ew")

        ttk.Label(controls, text="Preset").grid(row=0, column=2)
        ttk.OptionMenu(controls, self.preset, "Default", *PRESETS.keys(), command=self.apply_preset).grid(row=0, column=3)

        ttk.Label(controls, text="Backend").grid(row=1, column=2)
        ttk.OptionMenu(controls, self.backend, "MoviePy", "MoviePy", "ffmpeg").grid(row=1, column=3)

        ttk.Button(self, text="Start Processing", command=self.start).pack(pady=10)

        self.logbox = tk.Text(self, height=8)
        self.logbox.pack(fill="both", padx=10)

    def log(self, msg):
        self.logbox.insert("end", msg + "\n")
        self.logbox.see("end")

    def on_drop(self, e):
        paths = self.tk.splitlist(e.data)
        vids = find_videos(paths)
        for v in vids:
            if v not in self.videos:
                self.videos.append(v)
                self.listbox.insert("end", str(v))
        self.log(f"📁 Added {len(vids)} videos")

    def apply_preset(self, name):
        p = PRESETS[name]
        self.size.set(p["size"])
        self.margin.set(p["margin"])
        self.log(f"🎯 Preset applied: {name}")

    def start(self):
        if not self.videos:
            messagebox.showwarning("No videos", "Add videos first")
            return
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        preset = PRESETS[self.preset.get()]
        settings = {
            "size": self.size.get(),
            "margin": self.margin.get(),
            "safe_bottom": preset["safe_bottom"],
            "safe_right": preset["safe_right"],
        }

        for v in self.videos:
            try:
                if self.backend.get() == "ffmpeg":
                    process_ffmpeg(v, self.logo, settings, self.log)
                else:
                    process_moviepy(v, self.logo, settings, self.log)
            except Exception as e:
                self.log(f"❌ {v.name}: {e}")

        self.log("🎉 All done!")


if __name__ == "__main__":
    App().mainloop()
