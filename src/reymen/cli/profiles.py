# -*- coding: utf-8 -*-
"""profiles.py â€” Profil yonetimi: bagimsiz ReYMeN profilleri + opsiyonel ReYMeN uyumlulugu."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_REYMEN_PROJE_KOKU = Path(__file__).resolve().parent.parent.parent.parent
_REYMEN_PROFIL_DIZINI = _REYMEN_PROJE_KOKU / ".ReYMeN" / "profiles"
_ESKI_PROFIL_DIZINI = Path.home() / ".reymen" / "profiles"

# ReYMeN yoksa baÄŸÄ±msÄ±z çalÄ±ÅŸ â€” kritik baÄŸÄ±mlÄ±lÄ±k kaldÄ±rma
_ESKI_PROFIL_MEVCUT = _ESKI_PROFIL_DIZINI.exists()

_VARSAYILAN_PROFIL: dict[str, Any] = {
    "name": "default",
    "model": "deepseek-v4-flash",
    "provider": "deepseek",
    "gateway": "cli",
    "skills_dir": ".ReYMeN/skills",
}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Profil JSON oku/yaz / listele (ReYMeN eski API â€” geri uyumlu)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _reymen_profil_yolu(profil_adi: str) -> Path:
    """ReYMeN profil JSON dosyasinin tam yolunu doner."""
    return _REYMEN_PROFIL_DIZINI / f"{profil_adi}.json"


def _hermes_profil_yolu(profil_adi: str) -> Optional[Path]:
    """Eski profil dizin yolunu doner (varsa)."""
    yol = _ESKI_PROFIL_DIZINI / profil_adi
    return yol if yol.is_dir() else None


def _profil_yolu(profil_adi: str) -> Path:
    """Profil yolunu doner: once ReYMeN, sonra ReYMeN (opsiyonel)."""
    # Once ReYMeN profili
    reymen_yol = _reymen_profil_yolu(profil_adi)
    if reymen_yol.exists():
        return reymen_yol

    # Sonra ReYMeN (eger installed ise)
    if _ESKI_PROFIL_MEVCUT:
        h = _hermes_profil_yolu(profil_adi)
        if h:
            return h / "config.yaml"

    return reymen_yol


def profil_oku(profil_adi: str) -> dict[str, Any]:
    """Profil JSON dosyasini okur.

    Args:
        profil_adi: Profil adi (ornek: "default", "reymen", "kiral38")

    Returns:
        Profil sozlugu. Dosya yoksa varsayilan profil doner.
        ReYMeN profili ise config.yaml + .env + mcp.json + SOUL.md bilgilerini ekler.
    """
    # Once ReYMeN profili olarak dene
    hermes_yol = _hermes_profil_yolu(profil_adi)
    if hermes_yol:
        return _hermes_profil_oku(profil_adi, hermes_yol)

    # Yoksa ReYMeN profili olarak dene
    yol = _reymen_profil_yolu(profil_adi)
    if not yol.exists():
        logger.warning("[Profiles] Profil bulunamadi: %s, varsayilan kullaniliyor", yol)
        profil = dict(_VARSAYILAN_PROFIL)
        profil["name"] = profil_adi
        return profil

    try:
        with open(yol, "r", encoding="utf-8") as f:
            profil = json.load(f)
        for key, val in _VARSAYILAN_PROFIL.items():
            profil.setdefault(key, val)
        return profil
    except (json.JSONDecodeError, OSError) as e:
        logger.error("[Profiles] Profil okunamadi: %s - %s", yol, e)
        profil = dict(_VARSAYILAN_PROFIL)
        profil["name"] = profil_adi
        return profil


def _hermes_profil_oku(profil_adi: str, hermes_yol: Path) -> dict[str, Any]:
    """ReYMeN profil dizinindeki tum dosyalari okuyarak profil sozlugu olusturur."""
    profil: dict[str, Any] = {
        "name": profil_adi,
        "kaynak": "reymen",
        "dizin": str(hermes_yol),
    }

    # config.yaml oku
    config_yaml = hermes_yol / "config.yaml"
    if config_yaml.exists():
        profil["config_yaml"] = str(config_yaml)
        profil["config_boyut"] = config_yaml.stat().st_size

    # .env kontrol
    env_dosya = hermes_yol / ".env"
    if env_dosya.exists():
        profil["env_var"] = True
        profil["env_boyut"] = env_dosya.stat().st_size
        # .env'deki anahtar isimlerini oku (degerleri gizle)
        try:
            with open(env_dosya, "r", encoding="utf-8") as f:
                env_keys = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key = line.split("=", 1)[0].strip()
                        env_keys.append(key)
            profil["env_anahtarlari"] = env_keys
        except OSError:
            profil["env_anahtarlari"] = []

    # mcp.json kontrol
    mcp_json = hermes_yol / "mcp.json"
    if mcp_json.exists():
        profil["mcp_json"] = str(mcp_json)
        try:
            with open(mcp_json, "r", encoding="utf-8") as f:
                mcp_data = json.load(f)
            profil["mcp_sunucu_sayisi"] = len(mcp_data.get("mcpServers", {}))
        except (json.JSONDecodeError, OSError):
            profil["mcp_sunucu_sayisi"] = 0

    # SOUL.md kontrol
    soul_md = hermes_yol / "SOUL.md"
    if soul_md.exists():
        profil["soul_md"] = str(soul_md)
        profil["soul_boyut"] = soul_md.stat().st_size

    return profil


def profil_yaz(profil_adi: str, profil: dict[str, Any]) -> bool:
    """Profil JSON dosyasina yazar. (Sadece ReYMeN profilleri icin)

    Args:
        profil_adi: Profil adi
        profil: Profil sozlugu

    Returns:
        Basarili ise True
    """
    yol = _reymen_profil_yolu(profil_adi)
    try:
        _REYMEN_PROFIL_DIZINI.mkdir(parents=True, exist_ok=True)
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(profil, f, ensure_ascii=False, indent=2)
        logger.info("[Profiles] Profil kaydedildi: %s", yol)
        return True
    except OSError as e:
        logger.error("[Profiles] Profil yazilamadi: %s - %s", yol, e)
        return False


def list_profiles() -> list[dict[str, Any]]:
    """Profil listesini doner: ReYMeN + ReYMeN profilleri birlikte.

    Returns:
        Profil bilgisi sozlukleri listesi (name, kaynak, dizin, vs.)
    """
    profiller: list[dict[str, Any]] = []

    # ReYMeN profilleri (opsiyonel)
    if _ESKI_PROFIL_MEVCUT:
        for entry in sorted(_ESKI_PROFIL_DIZINI.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                profiller.append(_hermes_profil_oku(entry.name, entry))

    # ReYMeN profilleri
    if _REYMEN_PROFIL_DIZINI.exists():
        for entry in sorted(_REYMEN_PROFIL_DIZINI.iterdir()):
            if entry.suffix == ".json" and entry.stem:
                # ReYMeN'te varsa ekleme
                if not any(p["name"] == entry.stem and p.get("kaynak") == "reymen" for p in profiller):
                    try:
                        with open(entry, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        data["kaynak"] = "reymen"
                        data["dizin"] = str(entry)
                        profiller.append(data)
                    except (json.JSONDecodeError, OSError):
                        profiller.append({
                            "name": entry.stem,
                            "kaynak": "reymen",
                            "dizin": str(entry),
                        })

    if not profiller:
        profiller.append({
            "name": "default",
            "kaynak": "reymen",
            "dizin": "varsayilan",
        })

    return profiller


def list_profile_names() -> list[str]:
    """Sadece profil adlarini listeler (eski API â€” geri uyumlu)."""
    return [p["name"] for p in list_profiles()]


def get_active_profile_name() -> str:
    """Aktif profil adini doner.

    Oncelik sirasi:
    1. REYMEN_PROFILE / HERMES_PROFILE ortam degiskeni
    2. ReYMeN profili (.ReYMeN/profiles/)
    3. ReYMeN profili (eger installed ise)
    4. default
    """
    # REYMEN_PROFILE env (once kendi env'miz)
    env_profil = os.environ.get("REYMEN_PROFILE") or os.environ.get("HERMES_PROFILE")
    if env_profil:
        return env_profil

    # ReYMeN profilleri (bagimsiz calisir)
    if _reymen_profil_yolu("reymen").exists():
        return "reymen"

    # ReYMeN profilleri (opsiyonel â€” sadece installed ise)
    if _ESKI_PROFIL_MEVCUT and _hermes_profil_yolu("kiral38"):
        return "kiral38"

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
        ReYMeN profilleri bu fonksiyonla silinemez (dizindir).
    """
    if profil_adi == "default":
        logger.warning("[Profiles] default profili silinemez")
        return False

    # ReYMeN profili mi? (sadece okunabilir)
    if _ESKI_PROFIL_MEVCUT and _hermes_profil_yolu(profil_adi):
        logger.warning("[Profiles] ReYMeN profilleri silinemez: %s", profil_adi)
        return False

    yol = _reymen_profil_yolu(profil_adi)
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Yeni: ReYMeN profil detaylari
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def profil_detay(profil_adi: str) -> dict[str, Any]:
    """Profilin tum dosyalarini ve meta bilgilerini doner."""
    profil = profil_oku(profil_adi)

    # ReYMeN profiliyse dosya listesi ekle
    hermes_yol = _hermes_profil_yolu(profil_adi)
    if hermes_yol:
        dosyalar = []
        for entry in sorted(hermes_yol.iterdir()):
            if entry.is_file() and not entry.name.startswith("."):
                dosyalar.append({
                    "ad": entry.name,
                    "boyut": entry.stat().st_size,
                    "son_guncelleme": entry.stat().st_mtime,
                })
        profil["dosyalar"] = dosyalar

    return profil


def profil_env_anahtarlari(profil_adi: str) -> list[dict[str, str]]:
    """Profil .env dosyasindaki anahtar bilgilerini doner (degerler gizli).

    Returns:
        [{"anahtar": "DEEPSEEK_API_KEY", "var": true, "deger": "***..."}, ...]
    """
    hermes_yol = _hermes_profil_yolu(profil_adi)
    if not hermes_yol:
        return []

    env_dosya = hermes_yol / ".env"
    if not env_dosya.exists():
        return []

    anahtarlar = []
    try:
        with open(env_dosya, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("\"'")
                gizli = val[:4] + "..." + val[-4:] if len(val) > 10 else "***"
                anahtarlar.append({
                    "anahtar": key,
                    "var": bool(val),
                    "deger": gizli if val else "(bos)",
                })
    except OSError:
        pass

    return anahtarlar
