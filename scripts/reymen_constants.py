"""ReYMeN constants — ReYMeN evrensel sabitleri ve yardımcıları."""

from __future__ import annotations

import os
from pathlib import Path


def get_reymen_home() -> Path:
    """Return the ReYMeN home directory (REYMEN_HOME env var or default)."""
    override = os.environ.get("REYMEN_HOME", "").strip()
    if override:
        return Path(override)
    # Windows: %LOCALAPPDATA%/reymen
    local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
    if local_appdata:
        return Path(local_appdata) / "reymen"
    return Path.home() / ".reymen"


def get_reymen_config_path() -> Path:
    return get_reymen_home() / "config.yaml"


def get_reymen_env_path() -> Path:
    return get_reymen_home() / ".env"


def display_reymen_home() -> str:
    """Return a human-readable ReYMeN home path string."""
    return str(get_reymen_home())
