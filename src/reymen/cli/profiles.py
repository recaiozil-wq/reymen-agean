# -*- coding: utf-8 -*-
"""profiles.py — Profil yonetimi: JSON tabanli profil oku/yaz/kontrol."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Sabitler ────────────────────────────────────────────────

# Proje kokunu __file__ uzerinden tespit et (src/reymen/cli/ -> src/reymen/ -> src/ -> proje/)
_PROJE_KOKU = Path(__file__).resolve().parent.parent.parent.parent
_PROFIL_DIZINI = _PROJE_KOKU / ".ReYMeN" / "profiles"

_VARSAYILAN_PROFIL: dict[str, Any] = {
    "name": "default",
    "model": "deepseek-v4-flash",
    "provider": "deepseek",
    "gateway": "cli",
    "skills_dir": ".ReYMeN/skills",
}


# ═══════════════════════════════════════════════════════════════
# Profil JSON oku/yaz / listele
# ═══════════════════════════════════════════════════════════════


def _profil_yolu(profil_adi: str) -> Path:
    """Profil JSON dosyasinin tam yolunu doner."""
    return _PROFIL_DIZINI / f"{profil_adi}.json"


def profil_oku(profil_adi: str) -> dict[str, Any]:
    """Profil JSON dosyasini okur.

    Args:
        profil_adi: Profil adi (ornek: "default", "reymen")

    Returns:
        Profil sozlugu. Dosya yoksa varsayilan profil doner.
    """
    yol = _profil_yolu(profil_adi)
    if not yol.exists():
        logger.warning("[Profiles] Profil bulunamadi: %s, varsayilan kullaniliyor", yol)
        profil = dict(_VARSAYILAN_PROFIL)
        profil["name"] = profil_adi
        return profil

    try:
        with open(yol, "r", encoding="utf-8") as f:
            profil = json.load(f)
        # Eksik alanlari varsayilanla doldur
        for key, val in _VARSAYILAN_PROFIL.items():
            profil.setdefault(key, val)
        return profil
    except (json.JSONDecodeError, OSError) as e:
        logger.error("[Profiles] Profil okunamadi: %s - %s", yol, e)
        profil = dict(_VARSAYILAN_PROFIL)
        profil["name"] = profil_adi
        return profil


def profil_yaz(profil_adi: str, profil: dict[str, Any]) -> bool:
    """Profil JSON dosyasina yazar.

    Args:
        profil_adi: Profil adi
        profil: Profil sozlugu

    Returns:
        Basarili ise True
    """
    yol = _profil_yolu(profil_adi)
    try:
        _PROFIL_DIZINI.mkdir(parents=True, exist_ok=True)
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(profil, f, ensure_ascii=False, indent=2)
        logger.info("[Profiles] Profil kaydedildi: %s", yol)
        return True
    except OSError as e:
        logger.error("[Profiles] Profil yazilamadi: %s - %s", yol, e)
        return False


def list_profiles() -> list[str]:
    """Profil dizinindeki profil adlarini listeler.

    Returns:
        Profil adlari listesi (ornek: ["default", "reymen"])
    """
    if not _PROFIL_DIZINI.exists():
        logger.warning("[Profiles] Profil dizini yok: %s", _PROFIL_DIZINI)
        return ["default"]

    adlar: list[str] = []
    for entry in _PROFIL_DIZINI.iterdir():
        if entry.suffix == ".json" and entry.stem:
            adlar.append(entry.stem)

    # Her zaman en az "default" olsun
    if not adlar:
        adlar.append("default")

    return sorted(adlar)


def get_active_profile_name() -> str:
    """Aktif profil adini doner.

    Su an icin "reymen" profili oncelikli; yoksa "default".

    Returns:
        Profil adi
    """
    # Once reymen profilini dene
    if _profil_yolu("reymen").exists():
        return "reymen"
    # Varsayilan
    return "default"


def get_active_profile() -> dict[str, Any]:
    """Aktif profili tam sozluk olarak doner.

    Returns:
        Profil sozlugu (name, model, provider, gateway, skills_dir, ...)
    """
    ad = get_active_profile_name()
    return profil_oku(ad)


def profil_olustur(
    profil_adi: str,
    model: str = "deepseek-v4-flash",
    provider: str = "deepseek",
    gateway: str = "cli",
    skills_dir: str = ".ReYMeN/skills",
    extra: Optional[dict[str, Any]] = None,
) -> bool:
    """Yeni profil JSON dosyasi olusturur.

    Args:
        profil_adi: Profil adi (dosya adi olarak kullanilir)
        model: Varsayilan model
        provider: Varsayilan provider
        gateway: Varsayilan gateway
        skills_dir: Skills dizini yolu
        extra: Opsiyonel ek alanlar (description, vs.)

    Returns:
        Basarili ise True
    """
    profil: dict[str, Any] = {
        "name": profil_adi,
        "model": model,
        "provider": provider,
        "gateway": gateway,
        "skills_dir": skills_dir,
    }
    if extra:
        profil.update(extra)
    return profil_yaz(profil_adi, profil)


def profil_sil(profil_adi: str) -> bool:
    """Profil JSON dosyasini siler.

    Args:
        profil_adi: Profil adi

    Returns:
        Basarili ise True. "default" profili silinemez.
    """
    if profil_adi == "default":
        logger.warning("[Profiles] default profili silinemez")
        return False

    yol = _profil_yolu(profil_adi)
    if not yol.exists():
        logger.warning("[Profiles] Silinecek profil bulunamadi: %s", yol)
        return False

    try:
        yol.unlink()
        logger.info("[Profiles] Profil silindi: %s", yol)
        return True
    except OSError as e:
        logger.error("[Profiles] Profil silinemedi: %s - %s", yol, e)
        return False
