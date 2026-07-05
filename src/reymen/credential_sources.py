# -*- coding: utf-8 -*-
"""Kimlik bilgisi kaynaklari — env, .env, auth.json.

Hermes agent/credential_sources.py'den adapte edilmistir.
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Optional

def env_anahtar_al(anahtar: str) -> Optional[str]:
    return os.environ.get(anahtar)

def dotenv_anahtar_al(anahtar: str, env_yolu: Optional[Path] = None) -> Optional[str]:
    try:
        from dotenv import load_dotenv
        yol = env_yolu or Path.cwd() / ".env"
        if yol.exists():
            load_dotenv(yol)
            return os.environ.get(anahtar)
    except Exception:
        pass
    return None

def auth_json_anahtar_al(anahtar: str, auth_yolu: Optional[Path] = None) -> Optional[str]:
    try:
        yol = auth_yolu or Path.home() / "AppData/Local/hermes/auth.json"
        if yol.exists():
            data = json.loads(yol.read_text(encoding="utf-8"))
            return data.get(anahtar)
    except Exception:
        pass
    return None
