# -*- coding: utf-8 -*-
"""
reymen_home.py â€” ~/.reymen/ dizin yapÄ±sÄ±nÄ± yÃ¶netir.

ReYMeN'in ~/.reymen/ yerine ReYMeN'in kendi ev dizini.
TÃ¼m config, session, state, cache bu altÄ±nda toplanÄ±r.
"""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Optional

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Sabitler
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

_REYMEN_HOME_OVERRIDE: Optional[Path] = None

# Alt dizinler
SUBDIRS = {
    "profiles": "Profiller (config.yaml, .env, mcp.json)",
    "sessions": "Oturum veritabanlarÄ± (state.db)",
    "cache": "GeÃ§ici dosyalar (image, audio, video)",
    "cache/images": "GÃ¶rsel Ã¶nbellek",
    "cache/audio": "Ses Ã¶nbellek",
    "cache/videos": "Video Ã¶nbellek",
    "cache/documents": "DokÃ¼man Ã¶nbellek",
    "skills": "Skill dosyalarÄ±",
    "logs": "Log dosyalarÄ±",
    "state": "KalÄ±cÄ± durum verileri",
}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ana Fonksiyonlar
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def get_reymen_home() -> Path:
    """~/.reymen/ yolunu dÃ¶ndÃ¼r.

    Ã–ncelik sÄ±rasÄ±:
    1. REYMEN_HOME ortam deÄŸiÅŸkeni
    2. ProgramlÄ± override (set_reymen_home)
    3. ~/.reymen/
    """
    # 1. Env var
    env_home = os.environ.get("REYMEN_HOME")
    if env_home:
        return Path(env_home)

    # 2. Override
    if _REYMEN_HOME_OVERRIDE:
        return _REYMEN_HOME_OVERRIDE

    # 3. Default
    return Path.home() / ".reymen"


def set_reymen_home(path: Path | str) -> None:
    """ReYMeN home dizinini programlÄ± olarak ayarla."""
    global _REYMEN_HOME_OVERRIDE
    _REYMEN_HOME_OVERRIDE = Path(path)


def ensure_reymen_home() -> Path:
    """~/.reymen/ ve tÃ¼m alt dizinlerini oluÅŸturur."""
    home = get_reymen_home()
    home.mkdir(parents=True, exist_ok=True)

    for subdir in SUBDIRS:
        (home / subdir).mkdir(parents=True, exist_ok=True)

    return home


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Yol YardÄ±mcÄ±larÄ±
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def profiles_dir() -> Path:
    """Profil dizini: ~/.reymen/profiles/"""
    return get_reymen_home() / "profiles"


def sessions_dir() -> Path:
    """Session dizini: ~/.reymen/sessions/"""
    return get_reymen_home() / "sessions"


def cache_dir(subdir: str = "images") -> Path:
    """Cache dizini: ~/.reymen/cache/<subdir>/"""
    d = get_reymen_home() / "cache" / subdir
    d.mkdir(parents=True, exist_ok=True)
    return d


def skills_dir() -> Path:
    """Skills dizini: ~/.reymen/skills/"""
    d = get_reymen_home() / "skills"
    d.mkdir(parents=True, exist_ok=True)
    return d


def logs_dir() -> Path:
    """Log dizini: ~/.reymen/logs/"""
    d = get_reymen_home() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def state_dir() -> Path:
    """State dizini: ~/.reymen/state/"""
    d = get_reymen_home() / "state"
    d.mkdir(parents=True, exist_ok=True)
    return d


def env_path() -> Path:
    """Env dosyasÄ±: ~/.reymen/.env"""
    return get_reymen_home() / ".env"


def config_path() -> Path:
    """Config dosyasÄ±: ~/.reymen/config.yaml"""
    return get_reymen_home() / "config.yaml"


def state_db_path() -> Path:
    """Session DB: ~/.reymen/sessions/state.db"""
    return sessions_dir() / "state.db"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ReYMeN Geriye Uyumluluk
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def hermes_to_reymen_path(hermes_path: str | Path) -> Path:
    """ReYMeN yolunu ReYMeN yoluna Ã§evir.

    ~/.reymen/xxx -> ~/.reymen/xxx
    """
    p = Path(hermes_path)
    if ".reymen" in p.parts:
        parts = list(p.parts)
        idx = parts.index(".reymen")
        parts[idx] = ".reymen"
        return Path(*parts)
    return p


def migrate_hermes_data() -> dict:
    """ReYMeN verilerini ~/.reymen/'e taÅŸÄ± (opsiyonel).

    Returns:
        {"migrated": [...], "skipped": [...], "errors": [...]}
    """
    hermes_home = Path.home() / ".reymen"
    reymen_home = get_reymen_home()
    result = {"migrated": [], "skipped": [], "errors": []}

    if not hermes_home.exists():
        return result

    import shutil

    # TaÅŸÄ±nacak dizinler
    migrate_dirs = ["profiles", "skills"]
    for d in migrate_dirs:
        src = hermes_home / d
        dst = reymen_home / d
        if src.exists() and not dst.exists():
            try:
                shutil.copytree(str(src), str(dst))
                result["migrated"].append(d)
            except Exception as e:
                result["errors"].append(f"{d}: {e}")
        else:
            result["skipped"].append(d)

    # .env dosyasÄ±
    hermes_env = hermes_home / ".env"
    reymen_env = reymen_home / ".env"
    if hermes_env.exists() and not reymen_env.exists():
        try:
            shutil.copy2(str(hermes_env), str(reymen_env))
            result["migrated"].append(".env")
        except Exception as e:
            result["errors"].append(f".env: {e}")

    return result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Bilgi
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def reymen_home_info() -> dict:
    """~/.reymen/ durum bilgisi."""
    home = get_reymen_home()
    info = {
        "path": str(home),
        "exists": home.exists(),
        "platform": platform.system(),
    }

    if home.exists():
        info["subdirs"] = {}
        for subdir in SUBDIRS:
            d = home / subdir
            info["subdirs"][subdir] = {
                "exists": d.exists(),
                "files": len(list(d.glob("*"))) if d.exists() else 0,
            }

    return info
