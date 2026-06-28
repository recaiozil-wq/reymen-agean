#!/usr/bin/env python3
"""Simit ve Ayran — Bosphorus custom video template.
8 scenes with specific Pexels queries for simit, ayran, and Bosphorus views.
Output: 42 seconds, 1080p, silent.
"""

import os, requests
from moviepy import VideoFileClip, concatenate_videoclips

PEXELS_KEY = "your-pexels-api-key"
BASE = r"MoneyPrinterTurbo"
CACHE = os.path.join(BASE, "storage", "cache_videos")
OUT = os.path.join(BASE, "storage", "tasks", "simit_ayran")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

SCENES = [
    ("Istanbul Bosphorus golden hour sunset", 6),
    ("person holding simit bagel Turkish food", 6),
    ("Istanbul Bosphorus bridge mosque view", 5),
    ("Turkish ayran drink glass", 5),
    ("person fishing Bosphorus Istanbul", 5),
    ("seagulls flying Bosphorus", 4),
    ("Istanbul Bosphorus waterfront sunny", 5),
    ("person eating simit drinking ayran", 6),
]

def search_video(query, min_h=1080):
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait"
    r = requests.get(url, headers={"Authorization": PEXELS_KEY}, timeout=15)
    if r.status_code != 200: return None
    best, best_h = None, 0
    for v in r.json().get("videos", []):
        for f in v.get("video_files", []):
            h, w = f.get("height", 0), f.get("width", 0)
            if h > w and h >= min_h and f.get("link") and h > best_h:
                best = {"link": f["link"], "id": v["id"]}
                best_h = h
    return best

def download(url, fname):
    path = os.path.join(CACHE, fname)
    if not os.path.exists(path):
        with requests.get(url, timeout=120, stream=True) as r:
            with open(path, "wb") as f:
                for c in r.iter_content(8192): f.write(c)
    return path

def main():
    clips = []
    for i, (query, dur) in enumerate(SCENES):
        best = search_video(query)
        if not best: continue
        path = download(best["link"], f"s{i:02d}_{best['id']}.mp4")
        c = VideoFileClip(path)
        c = c.resized(height=1920).cropped(x_center=c.w/2, width=1080)
        if c.duration < dur:
            c = concatenate_videoclips([c]*int(dur/c.duration+1))
        c = c.subclipped(0, dur).without_audio()
        clips.append(c)
    if not clips: return
    final = concatenate_videoclips(clips, method="compose")
    out = os.path.join(OUT, "final-simit-ayran.mp4")
    final.write_videofile(out, codec="libx264", fps=24, threads=4, logger=None)
    print(f"OK! {out}  {final.duration:.1f}s")

if __name__ == "__main__": main()
