# -*- coding: utf-8 -*-
"""curator.py â€” ReYMeN Otomatik Bakim (Curator) Modulu.

Ne yapar:
  - Skill dosyalarinda bozuk/eksik frontmatter tespit ve duzeltme
  - Hafiza budama (MEMORY.md limit kontrolu)
  - Gereksiz __pycache__ temizligi
  - Trend raporu (self-improve verileriyle)
  - Dosya boyutu/node_modules temizligi (opsiyonel)

Kullanim:
    from reymen.sistem.curator import curator_calistir, curator_rapor
    sonuc = curator_calistir()
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "curator_calistir",
    "curator_rapor",
    "curator_temizlik_yap",
    "motor_kaydet",
]

# â”€â”€ Varsayilan yapilandirma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_DEFAULT_CONFIG: dict[str, Any] = {
    "skill_max_boyut_kb": 100,  # 100KB ustu skill uyarisi
    "memory_max_char": 50000,  # MEMORY.md max karakter
    "pycache_temizlik": True,  # __pycache__ temizligi
    "skill_frontmatter_kontrol": True,  # SKILL.md frontmatter kontrol
    "haftalik_trend_gun": 7,  # Trend raporu kapsami
}

# â”€â”€ Yardimcilar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _proje_kok() -> Path:
    """Proje kok dizinini bul."""
    return Path(__file__).resolve().parent.parent.parent.parent


def _dosya_boyutu_mb(yol: Path) -> float:
    """Dosya boyutunu MB cinsinden don."""
    try:
        return yol.stat().st_size / (1024 * 1024)
    except (OSError, PermissionError):
        return 0.0


# â”€â”€ 1. Skill bakimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _skill_kontrol(kok: Path) -> list[str]:
    """Skill dosyalarini tara, bozuk/eksik bul."""
    sorunlar: list[str] = []
    skill_dizinleri = [
        kok / "reymen" / "cereyan" / "skills",
        kok / "skills",
    ]
    for sd in skill_dizinleri:
        if not sd.exists():
            continue
        for f in sorted(sd.rglob("*.md")):
            if f.name == "README.md" or f.name == "PATHS.md":
                continue
            try:
                icerik = f.read_text(encoding="utf-8", errors="replace")
                # Frontmatter kontrolu
                if icerik.startswith("---"):
                    kapama = icerik.find("---", 3)
                    if kapama == -1:
                        sorunlar.append(f"Eksik frontmatter: {f.relative_to(kok)}")
                # Boyut kontrolu
                boyut_kb = _dosya_boyutu_mb(f) * 1024
                if boyut_kb > _DEFAULT_CONFIG["skill_max_boyut_kb"]:
                    sorunlar.append(
                        f"Buyuk skill ({boyut_kb:.0f}KB): {f.relative_to(kok)}"
                    )
            except Exception as e:
                sorunlar.append(f"Okunamayan skill: {f.relative_to(kok)} -> {e}")
    return sorunlar


# â”€â”€ 2. Hafiza budama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _hafiza_kontrol(kok: Path) -> list[str]:
    """MEMORY.md ve USER.md boyutunu kontrol et."""
    sorunlar: list[str] = []
    for dosya_adi in ("MEMORY.md", "USER.md"):
        aday_yollar = [
            kok / ".ReYMeN" / "memories" / dosya_adi,
            kok / ".ReYMeN" / dosya_adi,
            kok / "reymen" / "hafiza" / dosya_adi,
        ]
        for yol in aday_yollar:
            if yol.exists():
                boyut = len(yol.read_text(encoding="utf-8", errors="replace"))
                limit = _DEFAULT_CONFIG["memory_max_char"]
                if boyut > limit:
                    sorunlar.append(
                        f"{dosya_adi} asiri buyuk ({boyut}/{limit} char, "
                        f"%{boyut*100//limit})"
                    )
                break
    return sorunlar


# â”€â”€ 3. __pycache__ temizligi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _pycache_temizle(kok: Path, dry_run: bool = True) -> list[str]:
    """__pycache__ klasorlerini temizle (dry_run=True: sadece raporla)."""
    sonuc: list[str] = []
    toplam_boyut = 0
    toplam_dosya = 0
    EXCLUDE_DIRS = {".tbench-testing", ".git", "node_modules"}
    for kok_dizini, alt_dizinler, dosyalar in os.walk(kok):
        kok_yol = Path(kok_dizini)
        # Erisilemeyen/exclude dizinleri atla
        alt_dizinler[:] = [
            d for d in alt_dizinler if d not in EXCLUDE_DIRS and not d.startswith(".")
        ]
        if kok_yol.name != "__pycache__":
            continue
        for f in dosyalar:
            try:
                toplam_boyut += (kok_yol / f).stat().st_size
                toplam_dosya += 1
            except (OSError, PermissionError):
                continue
        if not dry_run:
            import shutil

            try:
                shutil.rmtree(kok_yol)
                sonuc.append(f"Temizlendi: {kok_yol.relative_to(kok)}")
            except Exception as e:
                sonuc.append(f"Hata: {kok_yol.relative_to(kok)} -> {e}")

    if dry_run:
        sonuc.append(
            f"__pycache__: {toplam_dosya} dosya, "
            f"{toplam_boyut / (1024*1024):.1f}MB (dry run)"
        )
    return sonuc


# â”€â”€ 4. Trend raporu (self-improve DB) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _trend_rapor(kok: Path) -> dict[str, Any]:
    """Self-improve DB'sinden trend verisi al."""
    db_yollari = [
        kok / "reymen" / "merkez_db" / "self_improve.db",
        kok / "src" / "reymen" / "merkez_db" / "self_improve.db",
    ]
    for db_yol in db_yollari:
        if db_yol.exists():
            try:
                conn = sqlite3.connect(str(db_yol))
                conn.row_factory = sqlite3.Row
                # Son 7 gun trend
                cutoff = time.time() - 7 * 86400
                rows = conn.execute(
                    "SELECT score, grade, success, step_name "
                    "FROM metrics WHERE timestamp >= ? ORDER BY timestamp DESC",
                    (cutoff,),
                ).fetchall()
                conn.close()
                if rows:
                    scores = [r["score"] for r in rows]
                    return {
                        "toplam_adim": len(rows),
                        "ortalama_skor": round(sum(scores) / len(scores), 3),
                        "gecen": sum(1 for r in rows if r["success"]),
                        "basarisiz": sum(1 for r in rows if not r["success"]),
                    }
                return {"toplam_adim": 0, "mesaj": "Son 7 gunde veri yok"}
            except Exception as e:
                return {"hata": str(e)}
    return {"mesaj": "self_improve.db bulunamadi"}


# â”€â”€ Ana fonksiyonlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def curator_calistir(
    kok: str | Path | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Curator bakimini calistir. Tum kontrolleri yap, rapor don.

    Args:
        kok: Proje kok dizini (None = otomatik algila)
        config: Yapilandirma (None = varsayilan)

    Returns:
        Bakim raporu (sozluk)
    """
    baslangic = time.time()
    if kok is None:
        kok = _proje_kok()
    else:
        kok = Path(kok) if isinstance(kok, str) else kok

    cfg = {**_DEFAULT_CONFIG, **(config or {})}

    sonuc: dict[str, Any] = {
        "tarih": datetime.now(timezone.utc).isoformat(),
        "kok": str(kok.resolve()),
        "sure_sn": 0,
        "skill_sorun": [],
        "hafiza_sorun": [],
        "pycache": [],
        "trend": {},
    }

    # 1. Skill kontrol
    sonuc["skill_sorun"] = _skill_kontrol(kok)

    # 2. Hafiza kontrol
    sonuc["hafiza_sorun"] = _hafiza_kontrol(kok)

    # 3. Pycache temizlik (dry run)
    if cfg["pycache_temizlik"]:
        sonuc["pycache"] = _pycache_temizle(kok, dry_run=True)

    # 4. Trend raporu
    sonuc["trend"] = _trend_rapor(kok)

    # 5. Genel metrikler
    sonuc["sure_sn"] = round(time.time() - baslangic, 2)

    return sonuc


def curator_temizlik_yap(
    kok: str | Path | None = None,
    pycache_sil: bool = True,
) -> list[str]:
    """Gerçek temizlik islemlerini yap (dry_run=False).

    Args:
        kok: Proje kok dizini
        pycache_sil: __pycache__ silinsin mi?

    Returns:
        Yapilan islem listesi
    """
    if kok is None:
        kok = _proje_kok()
    else:
        kok = Path(kok) if isinstance(kok, str) else kok

    islemler: list[str] = []

    if pycache_sil:
        islemler.extend(_pycache_temizle(kok, dry_run=False))

    if not islemler:
        islemler.append("Temizlik gerektiren durum yok.")
    return islemler


def curator_rapor(sonuc: dict[str, Any] | None = None) -> str:
    """Curator sonucunu insan-okunur metne cevir."""
    if sonuc is None:
        sonuc = curator_calistir()

    satirlar: list[str] = []
    satirlar.append(f"ğŸ“‹ Curator Raporu â€” {sonuc['tarih'][:19]}")
    satirlar.append(f"   Kok: {sonuc['kok']}")
    satirlar.append(f"   Sure: {sonuc['sure_sn']}sn")
    satirlar.append("")

    # Skill sorunlari
    skill = sonuc.get("skill_sorun", [])
    satirlar.append(f"ğŸ“„ Skill sorunu: {len(skill)}")
    for s in skill[:10]:
        satirlar.append(f"   âš ï¸  {s}")
    if len(skill) > 10:
        satirlar.append(f"   ... ve {len(skill) - 10} daha")

    # Hafiza sorunlari
    hafiza = sonuc.get("hafiza_sorun", [])
    satirlar.append(f"ğŸ’¾ Hafiza sorunu: {len(hafiza)}")
    for h in hafiza:
        satirlar.append(f"   âš ï¸  {h}")

    # Pycache
    pycache = sonuc.get("pycache", [])
    satirlar.append(f"ğŸ—‘ï¸  Pycache: {len(pycache)}")
    for p in pycache[:5]:
        satirlar.append(f"   {p}")

    # Trend
    trend = sonuc.get("trend", {})
    satirlar.append(f"ğŸ“Š Trend (son 7 gun):")
    if trend.get("toplam_adim", 0) > 0:
        satirlar.append(f"   Adim: {trend['toplam_adim']}")
        satirlar.append(f"   Skor: {trend.get('ortalama_skor', 'N/A')}")
        satirlar.append(f"   Basarili: {trend.get('gecen', 0)}")
        satirlar.append(f"   Basarisiz: {trend.get('basarisiz', 0)}")
    else:
        satirlar.append(f"   {trend.get('mesaj', 'Veri yok')}")

    return "\n".join(satirlar)


# â”€â”€ Motor kaydi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _tool_curator_calistir(**kw) -> str:
    """Curator bakimini calistir ve JSON rapor don."""
    sonuc = curator_calistir()
    return json.dumps(sonuc, indent=2, ensure_ascii=False)


def _tool_curator_rapor(**kw) -> str:
    """Curator raporunu insan-okunur metin olarak don."""
    return curator_rapor()


def _tool_curator_temizlik(**kw) -> str:
    """Dry-run olmayan gercek temizlik yap (pycache sil)."""
    islemler = curator_temizlik_yap()
    return "\n".join(islemler)


def motor_kaydet(motor) -> None:
    """Curator araclarini motor'a kaydet."""
    motor._plugin_arac_kaydet(
        "CURATOR_CALISTIR",
        _tool_curator_calistir,
        "Curator bakimini calistir. Skill/hafiza/pycache kontrolu + trend raporu.",
    )
    motor._plugin_arac_kaydet(
        "CURATOR_RAPOR",
        _tool_curator_rapor,
        "Curator raporunu insan-okunur metin olarak goster.",
    )
    motor._plugin_arac_kaydet(
        "CURATOR_TEMIZLIK",
        _tool_curator_temizlik,
        "Gerçek temizlik yap: __pycache__ sil.",
    )
    logger.info("[CURATOR] Motor'a 3 arac kaydedildi")


if __name__ == "__main__":
    # Dogrudan calistirma
    import sys

    dry_run = "--temizlik" not in sys.argv
    if dry_run:
        print(curator_rapor())
    else:
        islemler = curator_temizlik_yap()
        print("\n".join(islemler))
