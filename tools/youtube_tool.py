#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
youtube_tool.py — YouTube video araçları.
Video transcript çekme, video bilgisi alma, web sayfasından özet çıkarma.
ReYMeN motor'una kaydedilir: YOUTUBE_TRANSCRIPT, YOUTUBE_VIDEO_ANALIZ
"""

import json
import re
import sys
import urllib.parse
import urllib.request
import urllib.error


def _video_id_cikar(url: str) -> str:
    """YouTube URL'sinden 11 karakterlik video ID'sini çıkar."""
    url = url.strip()
    patterns = [
        r'(?:v=|youtu\.be/|shorts/|embed/|live/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return url


def _zaman_damgasi(saniye: float) -> str:
    """Saniyeyi MM:SS veya HH:MM:SS formatına çevir."""
    toplam = int(saniye)
    h, kalan = divmod(toplam, 3600)
    m, s = divmod(kalan, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def transkript_getir(video_url: str, dil: str = "tr,en") -> str:
    """
    YouTube video transcript'ini çeker.

    Args:
        video_url: YouTube video URL'si veya video ID
        dil: Dil kodu (virgülle ayrılmış, örn: "tr,en")

    Returns:
        JSON string: video_id, segment_count, duration, full_text, (varsa) timestamped_text
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return json.dumps({
            "hata": "youtube-transcript-api kurulu değil. Şunu çalıştır: pip install youtube-transcript-api",
            "cozum": "pip install youtube-transcript-api"
        }, ensure_ascii=False)

    video_id = _video_id_cikar(video_url)
    diller = [d.strip() for d in dil.split(",")] if dil else None

    try:
        api = YouTubeTranscriptApi()
        if diller:
            segments = api.fetch(video_id, languages=diller)
        else:
            segments = api.fetch(video_id)

        # Normalize
        seg_list = [
            {"text": seg.text, "start": seg.start, "duration": seg.duration}
            for seg in segments
        ]

        if not seg_list:
            return json.dumps({"hata": "Transcript bulunamadı", "video_id": video_id}, ensure_ascii=False)

        tam_metin = " ".join(s["text"] for s in seg_list)
        zamanli_metin = "\n".join(
            f"{_zaman_damgasi(s['start'])} {s['text']}" for s in seg_list
        )
        sure = _zaman_damgasi(seg_list[-1]["start"] + seg_list[-1]["duration"])

        return json.dumps({
            "video_id": video_id,
            "segment_sayisi": len(seg_list),
            "sure": sure,
            "tam_metin": tam_metin,
            "zamanli_metin": zamanli_metin,
            "dil_kullanilan": diller or ["auto"],
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        hata = str(e)
        if "disabled" in hata.lower():
            return json.dumps({"hata": "Bu video için transcript devre dışı.", "video_id": video_id}, ensure_ascii=False)
        if "not found" in hata.lower() or "no transcript" in hata.lower():
            return json.dumps({
                "hata": f"Transcript bulunamadı. Farklı bir dil dene ({dil})",
                "video_id": video_id,
                "dil_denenen": diller
            }, ensure_ascii=False)
        return json.dumps({"hata": hata, "video_id": video_id}, ensure_ascii=False)


def video_bilgisi_al(url: str) -> str:
    """
    YouTube video sayfasından başlık, açıklama, meta bilgileri çeker.

    Args:
        url: YouTube video URL'si

    Returns:
        JSON string: başlık, açıklama, kanal, izlenme vb.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as yanit:
            html = yanit.read().decode('utf-8', errors='replace')

        # Başlık
        baslik = ""
        m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        if m:
            baslik = m.group(1).replace(" - YouTube", "").strip()

        # Açıklama (meta og:description)
        aciklama = ""
        m = re.search(r'<meta\s+[^>]*property="og:description"[^>]*content="([^"]*)"', html)
        if m:
            aciklama = m.group(1)
        if not aciklama:
            m = re.search(r'<meta\s+[^>]*name="description"[^>]*content="([^"]*)"', html)
            if m:
                aciklama = m.group(1)

        # Kanal
        kanal = ""
        m = re.search(r'"author"[^:]*:\s*"([^"]+)"', html)
        if m:
            kanal = m.group(1)
        if not kanal:
            m = re.search(r'<link\s+[^>]*itemprop="name"[^>]*content="([^"]+)"', html)
            if m:
                kanal = m.group(1)

        return json.dumps({
            "video_id": _video_id_cikar(url),
            "baslik": baslik or "Bulunamadı",
            "aciklama": aciklama[:500] if aciklama else "Bulunamadı",
            "kanal": kanal or "Bulunamadı",
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


def video_analiz_et(url: str, dil: str = "tr,en") -> str:
    """
    YouTube videosunu analiz et: başlık + açıklama + transcript + özet.
    Video içeriğini anlayıp kurulum/yapılandırma talimatlarını çıkarmak için kullanılır.

    Args:
        url: YouTube video URL'si
        dil: Transcript dili

    Returns:
        JSON string: video bilgisi + transcript + analiz
    """
    # Video bilgisini al
    bilgi = json.loads(video_bilgisi_al(url))
    if "hata" in bilgi:
        return json.dumps(bilgi, ensure_ascii=False)

    # Transcript al
    transkript_str = transkript_getir(url, dil)
    transkript = json.loads(transkript_str)

    sonuc = {
        "video": bilgi,
        "transkript_mevcut": "hata" not in transkript,
    }

    if "hata" not in transkript:
        sonuc["transkript_ozet"] = {
            "sure": transkript.get("sure", "?"),
            "kelime_sayisi": len(transkript.get("tam_metin", "").split()),
            "tam_metin": transkript.get("tam_metin", ""),
            "zamanli_metin": transkript.get("zamanli_metin", ""),
        }
    else:
        sonuc["transkript_hatasi"] = transkript["hata"]

    return json.dumps(sonuc, ensure_ascii=False, indent=2)


def motor_kaydet(motor) -> None:
    """
    ReYMeN motor'una YouTube araçlarını kaydeder.
    motor.py'deki _plugin_moduller_yukle tarafından otomatik bulunur.
    """
    if not hasattr(motor, '_plugin_arac_kaydet'):
        # Doğrudan motor_kaydet yöntemini dene
        if hasattr(motor, 'arac_kaydet'):
            motor.arac_kaydet("YOUTUBE_TRANSCRIPT", lambda url, dil="tr,en": transkript_getir(url, dil),
                            "YouTube videosundan transcript çeker. Kullanım: YOUTUBE_TRANSCRIPT(url, dil='tr,en')")
            motor.arac_kaydet("YOUTUBE_VIDEO_BILGI", lambda url: video_bilgisi_al(url),
                            "YouTube videosunun başlık/açıklama/kanal bilgisini alır")
            motor.arac_kaydet("YOUTUBE_VIDEO_ANALIZ", lambda url, dil="tr,en": video_analiz_et(url, dil),
                            "YouTube videosunu tam analiz eder: başlık + transcript + içerik özeti")
        return

    motor._plugin_arac_kaydet(
        "YOUTUBE_TRANSCRIPT",
        lambda url, dil="tr,en": transkript_getir(url, dil),
        "YouTube videosundan transcript/metin çeker. Kullanım: YOUTUBE_TRANSCRIPT(video_url, dil='tr,en')"
    )
    motor._plugin_arac_kaydet(
        "YOUTUBE_VIDEO_BILGI",
        lambda url: video_bilgisi_al(url),
        "YouTube videosunun başlık, açıklama, kanal bilgisini alır"
    )
    motor._plugin_arac_kaydet(
        "YOUTUBE_VIDEO_ANALIZ",
        lambda url, dil="tr,en": video_analiz_et(url, dil),
        "YouTube videosunu tam analiz eder: başlık + transcript + içerik özeti. "
        "Kurulum/yapılandırma videoları için kullan."
    )
