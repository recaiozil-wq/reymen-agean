#!/usr/bin/env python3
"""
Storyboard Video Pipeline — Scene-by-scene video from Pexels + MoviePy 2.x.

Usage:
  python storyboard_video.py

Customize the SCENES list below for your own storyboard.
Each scene = (Pexels query, duration_seconds, description)
"""

import os, requests
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
import logging
logger = logging.getLogger(__name__)

# ─── CONFIG ────────────────────────────────────────────────────────
PEXELS_KEY = "your-pexels-api-key-here"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "storage", "cache_videos")
OUTPUT_DIR = os.path.join(BASE_DIR, "storage", "tasks", "storyboard_output")
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── SCENES: (query, duration, description) ───────────────────────
# Her sahne için Pexels'te aranacak sorgu, süre ve açıklama
SCENES = [
    ("Istanbul Bosphorus ferry sunrise", 5, "Boğaz vapur gün doğumu"),
    ("Hagia Sophia interior dome ceiling", 4, "Ayasofya kubbesi"),
    ("Sultanahmet Blue Mosque Istanbul", 3, "Sultanahmet Camii"),
    ("Grand Bazaar Istanbul spices color", 4, "Kapalıçarşı baharatlar"),
    ("Galata Tower sunset Golden Horn", 4, "Galata gün batımı"),
    ("Golden Horn Istanbul sunset", 4, "Haliç manzarası"),
    ("Bosphorus bridge night lights Istanbul", 4, "Boğaz köprüsü ışıklar"),
    ("Istanbul ferry Bosphorus water wave", 3, "Vapur köpükleri"),
]
# ───────────────────────────────────────────────────────────────────

def search_best_video(query, min_h=1080):
    """Pexels'te en yüksek çözünürlüklü dikey videoyu bul"""
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait"
    r = requests.get(url, headers={"Authorization": PEXELS_KEY}, timeout=15)
    if r.status_code != 200:
        return None
    best, best_h = None, 0
    for v in r.json().get("videos", []):
        for f in v.get("video_files", []):
            h, w = f.get("height", 0), f.get("width", 0)
            if h > w and h >= min_h and f.get("link") and h > best_h:
                best = {"link": f["link"], "h": h, "w": w, "id": v["id"]}
                best_h = h
    return best


def download(url, fname):
    path = os.path.join(CACHE_DIR, fname)
    if os.path.exists(path):
        return path
    print(f"  Downloading: {fname}")
    with requests.get(url, timeout=120, stream=True) as r:
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
    return path


def make_clip_9x16(path, target_duration):
    """Video dosyasını 1080x1920 (9:16) formatına getir ve hedef süreye kırp"""
    c = VideoFileClip(path)
    # Dikey (portrait) forma getir
    if c.w > c.h:  # yatay → dikey kırp
        c = c.resized(height=1920)
        c = c.cropped(x_center=c.w / 2, width=1080)
    else:
        c = c.resized(width=1080)
        c = c.cropped(y_center=c.h / 2, height=1920)
    # Süreyi hedefe ayarla (loop veya kırp)
    if c.duration < target_duration:
        loops = int(target_duration / c.duration) + 1
        c = concatenate_videoclips([c] * loops)
    c = c.subclipped(0, target_duration)
    c = c.without_audio()
    return c


def get_bg_music():
    """Arkaplan müziği indir (SoundHelix ücretsiz)"""
    path = os.path.join(CACHE_DIR, "bg_music.mp3")
    if not os.path.exists(path):
        try:
            r = requests.get(
                "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-14.mp3",
                timeout=30,
            )
            with open(path, "wb") as f:
                f.write(r.content)
            print("  Background music downloaded")
        except Exception as e:
            print(f"  Music download failed: {e}")
            return None
    return path


def main():
    print("=" * 50)
    print("STORYBOARD VIDEO PIPELINE")
    print("=" * 50)

    # 1. Her sahne için video bul ve indir
    clips = []
    for i, (query, dur, desc) in enumerate(SCENES):
        print(f"\n[{i + 1}/{len(SCENES)}] {desc} ({dur}s)")
        best = search_best_video(query)
        if not best:
            print(f"  SKIP: no video found for '{query}'")
            continue
        print(f"  Found: {best['id']} ({best['w']}x{best['h']})")
        path = download(best["link"], f"scene_{i:02d}_{best['id']}.mp4")
        try:
            clip = make_clip_9x16(path, dur)
            clips.append(clip)
            print(f"  OK: {clip.w}x{clip.h} @ {clip.duration:.1f}s")
        except Exception as e:
            print(f"  ERROR: {e}")

    if not clips:
        print("\nNo clips generated!")
        return

    # 2. Birleştir
    print(f"\nConcatenating {len(clips)} clips...")
    final = concatenate_videoclips(clips, method="compose")
    print(f"Total duration: {final.duration:.1f}s")

    # 3. Müzik ekle (opsiyonel, yorum satırını kaldır)
    # music_path = get_bg_music()
    # if music_path:
    #     try:
    #         audio = AudioFileClip(music_path).subclipped(0, final.duration)
    #         audio = audio.with_volume_scaled(0.2)
    #         final = final.with_audio(audio)
    #         print("Background music added")
    #     except Exception as e:
    #         print(f"Music error: {e}")

    # 4. Çıktı
    out = os.path.join(OUTPUT_DIR, "final-storyboard.mp4")
    print(f"\nRendering: {out}")
    final.write_videofile(
        out, codec="libx264", audio_codec="aac", fps=24, threads=4, logger=None
    )

    print(f"\n{'=' * 50}")
    print(f"DONE: {out}")
    print(f"Duration: {final.duration:.1f}s")
    print(f"Resolution: {final.w}x{final.h}")
    print(f"{'=' * 50}")

    for c in clips:
        c.close()
    final.close()


if __name__ == "__main__":
    main()
