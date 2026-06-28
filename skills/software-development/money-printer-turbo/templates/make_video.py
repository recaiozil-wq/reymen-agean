#!/usr/bin/env python3
"""
Custom video generator using Pexels API + MoviePy 2.x.
Scene-by-scene control beyond MoneyPrinterTurbo's capabilities.

Usage:
  .venv/Scripts/python.exe make_video.py

Features:
  - Scene-by-scene Pexels search and download
  - 4K output (2160x3840)
  - Optional no-audio mode
  - Background music (SoundHelix)

Dependencies: requests, moviepy (both in MoneyPrinterTurbo's .venv)

MoviePy 2.x API notes:
  - clip.subclip(t1, t2) → clip.subclipped(t1, t2)
  - from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
  - TextClip on Windows: font="C:/Windows/Fonts/arial.ttf" (full path required)
"""
import os, requests
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
import logging
logger = logging.getLogger(__name__)

# Read Pexels key from MoneyPrinterTurbo config
# Or hardcode: PEXELS_KEY = "your-key"
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app.config import config as mpt_config
    PEXELS_KEY = mpt_config.app.get("pexels_api_keys", [""])[0]
except Exception:
    PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "storage", "cache_videos")
OUTPUT_DIR = os.path.join(BASE_DIR, "storage", "tasks", "custom_video")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Each scene: (pexels_search_query, duration_seconds, description)
# Pexels automatically finds portrait (9:16) videos
SCENES = [
    ("Istanbul Bosphorus boat cruise", 10, "Boğazda gemi"),
    ("Galata Tower aerial drone view", 8, "Galata kulesi drone"),
    ("Camlica hill sunrise Istanbul", 8, "Çamlıca gün doğumu"),
    ("blonde woman smiling happy outdoor", 6, "Sarışın kızlar"),
    ("seagulls flying sea ocean waves", 5, "Martılar"),
    ("dolphin jumping ocean sea", 5, "Yunuslar"),
]

# Target resolution (4K portrait = 2160x3840)
TARGET_W, TARGET_H = 2160, 3840
NO_AUDIO = True  # Set False to allow background music

def search_pexels(query):
    """Find the highest-resolution portrait video from Pexels."""
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=10&orientation=portrait"
    resp = requests.get(url, headers={"Authorization": PEXELS_KEY}, timeout=15)
    if resp.status_code != 200:
        return []
    best, best_h = None, 0
    for v in resp.json().get("videos", []):
        for f in v.get("video_files", []):
            h, w = f.get("height", 0), f.get("width", 0)
            if h > w and h > best_h and f.get("link"):
                best, best_h = {"link": f["link"], "id": v["id"], "h": h, "w": w}, h
    return [best] if best else []

def download(url, fname):
    path = os.path.join(CACHE_DIR, fname)
    if os.path.exists(path):
        return path
    with requests.get(url, timeout=120, stream=True) as r:
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
    return path

def resize_to_target(clip):
    """Resize and crop to target 4K 9:16 portrait."""
    if clip.w > clip.h:  # landscape → crop portrait center
        clip = clip.resized(height=TARGET_H)
        clip = clip.cropped(x_center=clip.w/2, width=TARGET_W)
    else:
        clip = clip.resized(width=TARGET_W)
        clip = clip.cropped(y_center=clip.h/2, height=TARGET_H)
    return clip

def main():
    downloaded = []
    for i, (query, dur, desc) in enumerate(SCENES):
        results = search_pexels(query)
        if not results:
            alt_query = query.split(" ")[0]
            results = search_pexels(alt_query)
        if results:
            fname = f"s{i:02d}_{results[0]['id']}.mp4"
            path = download(results[0]["link"], fname)
            downloaded.append({"path": path, "dur": dur, "desc": desc})
            print(f"  [{i+1}] {desc}: ✓ {results[0]['id']} ({results[0]['w']}x{results[0]['h']})")
        else:
            print(f"  [{i+1}] {desc}: ✗ No video found")

    clips = []
    for d in downloaded:
        c = VideoFileClip(d["path"])
        c = resize_to_target(c)
        if c.duration < d["dur"]:
            c = concatenate_videoclips([c] * (int(d["dur"] / c.duration) + 1))
        c = c.subclipped(0, d["dur"])
        clips.append(c)

    final = concatenate_videoclips(clips, method="compose")

    # Optional: background music (disabled by default for clean output)
    if not NO_AUDIO:
        music_path = os.path.join(CACHE_DIR, "bg.mp3")
        if not os.path.exists(music_path):
            try:
                r = requests.get(
                    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                    timeout=30
                )
                with open(music_path, "wb") as f:
                    f.write(r.content)
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")
        if os.path.exists(music_path):
            audio = AudioFileClip(music_path).subclipped(0, final.duration)
            audio = audio.with_volume_scaled(0.25)
            final = final.with_audio(audio)
    else:
        final = final.without_audio()

    out = os.path.join(OUTPUT_DIR, "final-video.mp4")
    final.write_videofile(out, codec="libx264", audio_codec="aac", fps=24,
                          threads=max(1, os.cpu_count() or 4))
    final.close()
    for c in clips:
        c.close()

    print(f"\n✅ Video ready: {out}")
    print(f"   Resolution: {final.w}x{final.h}")
    print(f"   Duration: {final.duration:.1f}s")

if __name__ == "__main__":
    main()
