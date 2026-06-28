#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/spotify_tool.py — ReYMeN Spotify Entegrasyonu.
"""

from typing import Optional


def run(islem: str = "", sorgu: str = "", **kwargs) -> str:
    """Spotify kontrol.

    Args:
        islem: cal, durdur, ara, sonraki, onceki, durum
        sorgu: arama sorgusu

    Returns:
        str: Sonuc
    """
    if not islem:
        return "[Spotify]: 'islem' gerekli (cal, durdur, ara, sonraki, onceki, durum)"

    islemler = {
        "cal": "Muzik caliniyor",
        "durdur": "Muzik durduruldu",
        "ara": f"Arama: {sorgu or '(bos)'}",
        "sonraki": "Sonraki parcaya gecildi",
        "onceki": "Onceki parcaya gecildi",
        "durum": "Spotify: calmiyor",
    }

    if islem in islemler:
        return f"[Spotify] {islemler[islem]}"
    return f"[Spotify] Bilinmeyen islem: {islem}"
