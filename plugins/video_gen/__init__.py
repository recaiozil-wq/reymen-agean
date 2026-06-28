# -*- coding: utf-8 -*-
"""
plugins/video_gen/__init__.py — Video Uretim Plugin.

Araçlar: VIDEO_URET, VIDEO_OZETLE, VIDEO_INDIR
Provider: yt-dlp (indirme), fal.ai (uretim, FAL_KEY gerekir).

.env'de:
    FAL_KEY=... (fal.ai video uretimi icin)
"""

__all__ = ['kaydet', 'video_indir', 'video_ozetle', 'video_uret']
import json
import os
import re
import subprocess
import urllib.request

PLUGIN_ADI = "video_gen"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Video indirme ve AI video uretimi"


def _ytdlp_var() -> bool:
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True, timeout=5)
        return True
    except Exception:
        return False


def kaydet(motor):
    def video_indir(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        url = params[0] if params else ham.strip('"')
        cikti = params[1] if len(params) > 1 else "%(title)s.%(ext)s"
        if not _ytdlp_var():
            return "[VideoGen] yt-dlp yuklu degil. pip install yt-dlp"
        try:
            sonuc = subprocess.run(
                ["yt-dlp", "--no-playlist", "-o", cikti, url],
                capture_output=True, text=True, timeout=300,
            )
            if sonuc.returncode == 0:
                return f"[VideoGen] Indirildi: {url}"
            return f"[VideoGen] Hata: {sonuc.stderr[:200]}"
        except Exception as e:
            return f"[VideoGen] Hata: {e}"

    def video_ozetle(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        url = params[0] if params else ham.strip('"')
        if not _ytdlp_var():
            return "[VideoGen] yt-dlp yuklu degil."
        try:
            sonuc = subprocess.run(
                ["yt-dlp", "--dump-json", "--no-playlist", url],
                capture_output=True, text=True, timeout=30,
            )
            if sonuc.returncode != 0:
                return f"[VideoGen] Hata: {sonuc.stderr[:200]}"
            bilgi = json.loads(sonuc.stdout)
            return (
                f"[Video Bilgisi]\n"
                f"  Baslik  : {bilgi.get('title', '')}\n"
                f"  Kanal   : {bilgi.get('uploader', '')}\n"
                f"  Sure    : {bilgi.get('duration_string', '')}\n"
                f"  Goruntuleme: {bilgi.get('view_count', 0):,}\n"
                f"  Aciklama: {(bilgi.get('description') or '')[:200]}"
            )
        except Exception as e:
            return f"[VideoGen] Hata: {e}"

    def video_uret(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        prompt = params[0] if params else ham.strip('"')
        fal_key = os.environ.get("FAL_KEY", "")
        if not fal_key or fal_key.startswith("***"):
            return "[VideoGen] FAL_KEY eksik. .env'e FAL_KEY ekleyin."
        try:
            veri = json.dumps({
                "prompt": prompt, "duration": 5, "aspect_ratio": "16:9",
            }).encode()
            req = urllib.request.Request(
                "https://fal.run/fal-ai/kling-video/v1/standard/text-to-video",
                data=veri,
                headers={"Content-Type": "application/json",
                         "Authorization": f"Key {fal_key}"},
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                sonuc = json.loads(r.read())
            video_url = sonuc.get("video", {}).get("url", "")
            return f"[VideoGen] Video uretildi:\n{video_url}"
        except Exception as e:
            return f"[VideoGen] fal.ai hatasi: {e}"

    from plugins.kanban import _plugin_arac_kaydet
    _plugin_arac_kaydet(motor, "VIDEO_INDIR",  video_indir)
    _plugin_arac_kaydet(motor, "VIDEO_OZETLE", video_ozetle)
    _plugin_arac_kaydet(motor, "VIDEO_URET",   video_uret)
    print(f"[Plugin:{PLUGIN_ADI}] 3 arac kayit edildi.")
