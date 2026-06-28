# -*- coding: utf-8 -*-
"""memory_tool.py — Kalici bellek oku/yaz."""

import json
from pathlib import Path

# file her zaman güvenilir değil; resolve() ile sabitle
_ReYMeN_DIR = Path(__file__).resolve().parent.parent / ".ReYMeN" / "memories"


def _oku(dosya: str) -> str:
    p = _ReYMeN_DIR / dosya
    if p.exists():
        return p.read_text(encoding="utf-8")
    return "[Yok]"


def _yaz(dosya: str, icerik: str) -> str:
    _ReYMeN_DIR.mkdir(parents=True, exist_ok=True)
    p = _ReYMeN_DIR / dosya
    p.write_text(icerik, encoding="utf-8")
    return f"[Tamam] {dosya} kaydedildi ({len(icerik)} karakter)"


def run(eylem: str = "oku", kaynak: str = "MEMORY.md", icerik: str = "") -> str:
    eylem = eylem.strip().lower()
    if eylem == "oku":
        return _oku(kaynak)
    if eylem == "yaz":
        if not icerik:
            return "[Hata]: yaz eylemi icin icerik parametresi gerekli."
        return _yaz(kaynak, icerik)
    return f"[Hata]: eylem 'oku' veya 'yaz' olmali, alindi: '{eylem}'"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("MEMORY", run, "Bellek oku/yaz (MEMORY.md/USER.md)")
