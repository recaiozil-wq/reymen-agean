# -*- coding: utf-8 -*-
"""tools/achievements.py — ReYMeN 8 Adım Achievement Sistemi.

Her rozet .reymen/achievements/<rozet_id>.json dosyasında saklanır.
Idempotent: aynı rozet iki kez verilmez.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
logger = logging.getLogger(__name__)

REYMEN_DIR = Path(__file__).parent.parent / ".reymen"
ACHIEVEMENTS_DIR = REYMEN_DIR / "achievements"
STATS_DIR = REYMEN_DIR / "stats"

# ── 8 rozet tanımı ──────────────────────────────────────────────

ROZET_TANIMLARI: List[Dict[str, str]] = [
    {"id": "novice_explorer",  "name": "Acemi Kaşif",   "emoji": "🥉"},
    {"id": "tool_master",      "name": "Alet Ustası",    "emoji": "🛠️"},
    {"id": "bug_hunter",       "name": "Hata Avcısı",    "emoji": "🐛"},
    {"id": "crystallizer",     "name": "Kristalci",     "emoji": "📜"},
    {"id": "memory_keeper",    "name": "Hafıza Bekçisi", "emoji": "🧠"},
    {"id": "bridge_builder",   "name": "Köprü Kurucu",   "emoji": "🌐"},
    {"id": "autonomous",       "name": "Otonom",         "emoji": "🤖"},
    {"id": "reymen_master",    "name": "ReYMeN Ustası",  "emoji": "🏆"},
]

ILK_7_ROZET = [r["id"] for r in ROZET_TANIMLARI[:-1]]


# ── Yardımcı Fonksiyonlar ────────────────────────────────────────


def _ver_rozet(rozet_id: str) -> Optional[Dict[str, Any]]:
    """Rozeti ver. Zaten varsa None döndür (idempotent)."""
    dosya = ACHIEVEMENTS_DIR / f"{rozet_id}.json"
    if dosya.exists():
        return None

    tanim = next((r for r in ROZET_TANIMLARI if r["id"] == rozet_id), None)
    if tanim is None:
        return None

    ACHIEVEMENTS_DIR.mkdir(parents=True, exist_ok=True)
    rozet = {
        "id": rozet_id,
        "name": tanim["name"],
        "emoji": tanim["emoji"],
        "earned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    dosya.write_text(json.dumps(rozet, indent=2, ensure_ascii=False), encoding="utf-8")
    return rozet


def _rozet_var_mi(rozet_id: str) -> bool:
    return (ACHIEVEMENTS_DIR / f"{rozet_id}.json").exists()


def _tum_rozetleri_listele() -> List[Dict[str, Any]]:
    """Kazanılmış tüm rozetleri döndür."""
    if not ACHIEVEMENTS_DIR.exists():
        return []
    rozetler = []
    for dosya in sorted(ACHIEVEMENTS_DIR.glob("*.json")):
        try:
            rozetler.append(json.loads(dosya.read_text(encoding="utf-8")))
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
    return rozetler


# ── Sayaç Fonksiyonları ──────────────────────────────────────────


def _sayac_artir(dosya_adi: str, anahtar: str = "count") -> int:
    """İstatistik sayacını 1 artır, yeni değeri döndür."""
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    dosya = STATS_DIR / dosya_adi
    veri: Dict[str, Any] = {"count": 0}
    if dosya.exists():
        veri = json.loads(dosya.read_text(encoding="utf-8"))
    veri[anahtar] = veri.get(anahtar, 0) + 1
    dosya.write_text(json.dumps(veri, indent=2), encoding="utf-8")
    return veri[anahtar]


def _listeye_ekle(dosya_adi: str, deger: str):
    """String listeye benzersiz ekleme yap."""
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    dosya = STATS_DIR / dosya_adi
    liste: List[str] = []
    if dosya.exists():
        liste = json.loads(dosya.read_text(encoding="utf-8"))
    if deger not in liste:
        liste.append(deger)
        dosya.write_text(json.dumps(liste, indent=2), encoding="utf-8")


# ── Okuma Fonksiyonları ──────────────────────────────────────────


def _kullanilan_araclar() -> List[str]:
    dosya = STATS_DIR / "tools_used.json"
    return json.loads(dosya.read_text(encoding="utf-8")) if dosya.exists() else []


def _hata_sayisi() -> int:
    dosya = STATS_DIR / "errors_fixed.json"
    return json.loads(dosya.read_text(encoding="utf-8")).get("count", 0) if dosya.exists() else 0


def _hafiza_sayisi() -> int:
    memory_dir = REYMEN_DIR / "memory"
    return len(list(memory_dir.glob("*.json"))) if memory_dir.exists() else 0


def _kanal_sayisi() -> int:
    dosya = STATS_DIR / "channels_used.json"
    return len(json.loads(dosya.read_text(encoding="utf-8"))) if dosya.exists() else 0


# ── Ana Kontrol Fonksiyonu ───────────────────────────────────────


def check_achievements(
    gorev_tamamlandi: bool = False,
    skill_olusturuldu: bool = False,
    kesintisiz_adim: int = 0,
) -> List[Dict[str, Any]]:
    """Tüm rozetleri kontrol et, yeni kazanılanları döndür.

    Args:
        gorev_tamamlandi: Bu turda bir görev tamamlandı mı?
        skill_olusturuldu: Bu turda yeni skill oluşturuldu mu?
        kesintisiz_adim: Bu görevdeki kesintisiz adım sayısı.

    Returns:
        Yeni kazanılan rozetlerin listesi.
    """
    yeni_rozetler: List[Dict[str, Any]] = []

    # 1 — Acemi Kaşif
    if gorev_tamamlandi:
        r = _ver_rozet("novice_explorer")
        if r:
            yeni_rozetler.append(r)

    # 2 — Alet Ustası
    if len(_kullanilan_araclar()) >= 3:
        r = _ver_rozet("tool_master")
        if r:
            yeni_rozetler.append(r)

    # 3 — Hata Avcısı
    if _hata_sayisi() >= 5:
        r = _ver_rozet("bug_hunter")
        if r:
            yeni_rozetler.append(r)

    # 4 — Kristalci
    if skill_olusturuldu:
        r = _ver_rozet("crystallizer")
        if r:
            yeni_rozetler.append(r)

    # 5 — Hafıza Bekçisi
    if _hafiza_sayisi() >= 20:
        r = _ver_rozet("memory_keeper")
        if r:
            yeni_rozetler.append(r)

    # 6 — Köprü Kurucu
    if _kanal_sayisi() >= 2:
        r = _ver_rozet("bridge_builder")
        if r:
            yeni_rozetler.append(r)

    # 7 — Otonom
    if kesintisiz_adim >= 5:
        r = _ver_rozet("autonomous")
        if r:
            yeni_rozetler.append(r)

    # 8 — ReYMeN Ustası (en son, tümü kontrol edilince)
    if all(_rozet_var_mi(r) for r in ILK_7_ROZET):
        r = _ver_rozet("reymen_master")
        if r:
            yeni_rozetler.append(r)

    return yeni_rozetler


def rozet_listele() -> str:
    """Kazanılmış rozetleri okunabilir metin olarak döndür."""
    rozetler = _tum_rozetleri_listele()
    if not rozetler:
        return "[Achievements] Henüz rozet kazanılmamış."

    satirlar = ["[Achievements]"]
    for r in rozetler:
        satirlar.append(f"  {r['emoji']} {r['name']} — {r['earned_at'][:10]}")
    return "\n".join(satirlar)


# ── Test Bloğu ────────────────────────────────────────────────────


if __name__ == "__main__":
    # Test 1: İlk rozet
    yeni = check_achievements(gorev_tamamlandi=True)
    print(f"Test 1 — İlk görev: {len(yeni)} yeni rozet")
    for r in yeni:
        print(f"  {r['emoji']} {r['name']}")

    # Test 2: Idempotent — tekrar çağır
    yeni2 = check_achievements(gorev_tamamlandi=True)
    print(f"Test 2 — Idempotent: {len(yeni2)} yeni rozet (0 olmalı)")

    # Test 3: Rozet listele
    print(f"\n{rozet_listele()}")
