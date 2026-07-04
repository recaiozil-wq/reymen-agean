# -*- coding: utf-8 -*-
"""
ortak_komut.py — 3 bot + ReYMeN Agent ortak yetki/komut merkezi.
Her degisiklikte otomatik guncellenir. Tum botlar burayi okur.
"""

import json
import os
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

PROJE_KOK = Path(__file__).resolve().parent.parent.parent
# WSL/Win uyumlu: once C:/Users/marko dene
if Path("/mnt/c/Users/marko").exists():
    HERMES_HOME = Path("/mnt/c/Users/marko") / ".hermes"
else:
    HERMES_HOME = Path.home() / ".hermes"

# ── Bot Profil Yapilari ────────────────────────────────────────────────

BOTLAR = {
    "pasa_38": {
        "profil": "default",
        "bot_adi": "@Pasa_38_bot",
        "gateway": "aktif",
        "yetki": "tam",
        "browser": "acik",
        "terminal": "acik",
        "web": "firecrawl",
        "soul_boyut": 0,
        "tools": "tum",
    },
    "reymen": {
        "profil": "reymen",
        "bot_adi": "@ReYMeN_ReYMeNbot",
        "gateway": "aktif",
        "yetki": "tam",
        "browser": "acik",
        "terminal": "acik",
        "web": "firecrawl",
        "soul_boyut": 0,
        "tools": "tum",
    },
    "kiral38": {
        "profil": "kiral38",
        "bot_adi": "@Kiral38bot",
        "gateway": "aktif",
        "yetki": "tam",
        "browser": "acik",
        "terminal": "acik",
        "web": "firecrawl",
        "soul_boyut": 0,
        "tools": "tum",
    },
}

# ── Ortak Komutlar ─────────────────────────────────────────────────────

ORTAK_KOMUTLAR = {
    "cevap_formati": "emoji+baslik+tablo+yorum",
    "dil": "Turkce",
    "cave_modu": True,
    "no_goblins": True,
    "side_quest": "sub_agent'a yonlendir",
    "durum_oku_zorunlu": True,
    "kendi_bilgisiyle_cevap_yasak": True,
    "kaynak": "durum.json TEK KAYNAK",
}

# ── Dosya Yollari ──────────────────────────────────────────────────────

SOUL_DOSYALARI = {
    "default": HERMES_HOME / "profiles" / "default" / "SOUL.md",
    "reymen": HERMES_HOME / "profiles" / "reymen" / "SOUL.md",
    "kiral38": HERMES_HOME / "profiles" / "kiral38" / "SOUL.md",
}

CONFIG_DOSYALARI = {
    "default": HERMES_HOME / "profiles" / "default" / "config.yaml",
    "reymen": HERMES_HOME / "profiles" / "reymen" / "config.yaml",
    "kiral38": HERMES_HOME / "profiles" / "kiral38" / "config.yaml",
}

DURUM_JSON = PROJE_KOK / "durum.json"


# ── Tarama Fonksiyonu ──────────────────────────────────────────────────

def tara_profil(profil: str) -> dict:
    """Bir profilin guncel durumunu tara."""
    sonuc = {"soul_boyut": 0, "browser": "?", "terminal_cwd": "?"}

    # SOUL.md boyutu
    soul_yol = SOUL_DOSYALARI.get(profil)
    if soul_yol and soul_yol.exists():
        sonuc["soul_boyut"] = soul_yol.stat().st_size

    # Config'den browser/terminal bilgisi
    config_yol = CONFIG_DOSYALARI.get(profil)
    if config_yol and config_yol.exists():
        icerik = config_yol.read_text(encoding="utf-8")
        # Browser durumu: disabled_toolsets listesinde "browser" var mi?
        import re as _re
        dt_match = _re.search(r'disabled_toolsets\s*:\s*\[(.*?)\]', icerik, _re.DOTALL)
        if dt_match:
            tools = [t.strip().strip("'\"") for t in dt_match.group(1).split(",") if t.strip()]
            sonuc["browser"] = "kapali" if "browser" in tools else "acik"
        else:
            sonuc["browser"] = "acik"
        # Terminal cwd
        for satir in icerik.split("\n"):
            if "cwd:" in satir:
                sonuc["terminal_cwd"] = satir.split("cwd:")[-1].strip().strip("'\"")
                break

    return sonuc


def guncelle() -> dict:
    """Tum profilleri tara, BOTLAR'i guncelle, durum.json'a yaz.
    
    Dinamik olarak eklenen botlari (yeni kullanicinin kendi botu gibi)
    korur — sadece hardcoded BOTLAR'daki botlari degil, durum.json'da
    zaten kayitli olan tum botlari muhafaza eder.
    """
    # Mevcut durum.json'u oku (dinamik botlari korumak icin)
    mevcut_botlar = {}
    if DURUM_JSON.exists():
        try:
            mevcut = json.loads(DURUM_JSON.read_text(encoding="utf-8"))
            mevcut_botlar = mevcut.get("botlar", {})
        except Exception:
            mevcut_botlar = {}

    # Hardcoded BOTLAR'i guncelle (profil durumlarini tara)
    for ad, bot in BOTLAR.items():
        durum = tara_profil(bot["profil"])
        bot["soul_boyut"] = durum["soul_boyut"]
        bot["browser"] = durum["browser"]

    # Hardcoded ve dinamik botlari birlestir
    # Hardcoded botlar kendi ayarlarini korur
    # Dinamik botlar (hardcoded'da olmayan) oldugu gibi kalir
    birlesik_botlar = dict(BOTLAR)  # hardcoded'lar
    for anahtar, deger in mevcut_botlar.items():
        if anahtar not in birlesik_botlar:
            birlesik_botlar[anahtar] = deger  # dinamik botlari ekle

    # durum.json'u guncelle
    yeni_durum = {
        "proje": "ReYMeN Agent",
        "surum": "2026-06-30",
        "botlar": birlesik_botlar,
        "ortak_komutlar": ORTAK_KOMUTLAR,
        "esit_mi": _butun_botlar_esit_mi(),
    }

    DURUM_JSON.write_text(
        json.dumps(yeni_durum, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return yeni_durum


def _butun_botlar_esit_mi() -> dict:
    """Tum botlarin (hardcoded + dinamik) ayni yetkide olup olmadigini kontrol et.
    Sadece permission/settings alanlarini karsilastir (profil/bot_adi haric).
    soul_boyut: 50 byte'dan az fark esit sayilir (bot ismi uzunlugu)."""
    karsilastirilacak_alanlar = [
        "gateway", "yetki", "browser", "terminal",
        "web", "tools",
    ]
    # Mevcut durum.json'daki tum botlari al (hardcoded + dinamik)
    butun_botlar = dict(BOTLAR)
    if DURUM_JSON.exists():
        try:
            mevcut = json.loads(DURUM_JSON.read_text(encoding="utf-8"))
            for anahtar, deger in mevcut.get("botlar", {}).items():
                if anahtar not in butun_botlar:
                    butun_botlar[anahtar] = deger
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
    yetkiler = [
        [b.get(alan, "") for alan in karsilastirilacak_alanlar]
        for b in butun_botlar.values()
    ]
    if not yetkiler:
        return {"esit": True, "aciklama": "Henuz bot yok"}
    ilk = yetkiler[0]
    esit = all(y == ilk for y in yetkiler)
    # Ayrica soul_boyut farki 50 bayti gecmemeli
    boyutlar = [b.get("soul_boyut", 0) for b in butun_botlar.values()]
    if esit and boyutlar:
        min_boyut = min(boyutlar)
        max_boyut = max(boyutlar)
        if max_boyut - min_boyut > 50:
            esit = False
    return {
        "esit": esit,
        "aciklama": "Tum botlar esit" if esit else "Fark var! (soul_boyut farki > 50 bayt veya yetki farki)",
    }


# ── CLI ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "tara":
        for ad in BOTLAR:
            d = tara_profil(BOTLAR[ad]["profil"])
            print(f"{ad}: SOUL={d['soul_boyut']}b, Browser={d['browser']}, CWD={d['terminal_cwd']}")
    elif len(sys.argv) > 1 and sys.argv[1] == "guncelle":
        sonuc = guncelle()
        print(f"✅ durum.json guncellendi. Botlar esit mi: {sonuc['esit_mi']['esit']}")
    else:
        print("Kullanim: python ortak_komut.py [tara|guncelle]")
