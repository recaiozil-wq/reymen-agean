#!/usr/bin/env python3
"""Iki Kita, Tek Bir Nefes — Istanbul belgesel video olusturucu.
Kullanim: .venv/Scripts/python.exe iki_kita.py
Ornek prompt:
  "Istanbul Bosphorus waterfront, sunny golden hour, holding simit in left hand
   and ayran in right hand, fishing with rod, seagulls flying, Bosphorus bridge
   and historic mosque, cinematic, photorealistic, 4K"

Her sahne icin Pexels API'den en yuksek cozunurluklu videolari bulur,
1080x1920'ye boyutlandirir, birlestirir. Ses eklemez (sessiz).
"""

import os, requests
from moviepy import VideoFileClip, concatenate_videoclips

PEXELS_KEY = "your-pexels-api-key"
BASE = r"MoneyPrinterTurbo"
CACHE = os.path.join(BASE, "storage", "cache_videos")
OUT = os.path.join(BASE, "storage", "tasks", "iki_kita")
os.makedirs(CACHE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# Sahne: (arama terimi, sure, aciklama)
SCENES = [
    ("Istanbul Bosphorus ferry sunrise", 5, "Bogaz vapor gun dogumu"),
    ("Hagia Sophia interior dome", 4, "Ayasofya kubbesi"),
    ("Sultanahmet Blue Mosque Istanbul", 3, "Sultanahmet Camii"),
    ("Grand Bazaar Istanbul spices", 4, "Kapalicarsi baharat"),
    ("Grand Bazaar shopkeeper Turkish", 4, "Kapalicarsi esnaf"),
    ("Galata Tower sunset Golden Horn", 4, "Galata gun batimi"),
    ("Golden Horn Istanbul sunset", 4, "Halic manzarasi"),
    ("Bosphorus bridge night lights", 4, "Bogaz kopru isiklar"),
    ("Istanbul ferry Bosphorus water wave", 3, "Vapur kopukleri"),
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
                best = {"link": f["link"], "h": h, "id": v["id"]}
                best_h = h
    return best

def download(url, fname):
    path = os.path.join(CACHE, fname)
    if not os.path.exists(path):
        print(f"  Indir: {fname}")
        with requests.get(url, timeout=120, stream=True) as r:
            with open(path, "wb") as f:
                for c in r.iter_content(8192): f.write(c)
    return path

def main():
    clips = []
    for i, (query, dur, desc) in enumerate(SCENES):
        print(f"\n[{i+1}] {desc} ({dur}s)")
        best = search_video(query)
        if not best:
            print("  Bulunamadi"); continue
        print(f"  {best['id']} ({best['h']}p)")
        path = download(best["link"], f"s{i:02d}_{best['id']}.mp4")
        c = VideoFileClip(path)
        c = c.resized(height=1920).cropped(x_center=c.w/2, width=1080)
        if c.duration < dur:
            c = concatenate_videoclips([c]*int(dur/c.duration+1))
        c = c.subclipped(0, dur).without_audio()
        clips.append(c)
        print(f"  OK {c.w}x{c.h} @ {c.duration:.1f}s")
    if not clips: return
    final = concatenate_videoclips(clips, method="compose")
    out = os.path.join(OUT, "final-iki-kita.mp4")
    final.write_videofile(out, codec="libx264", fps=24, threads=4, logger=None)
    print(f"\nOK! {out}  {final.duration:.1f}s")

if __name__ == "__main__": main()
