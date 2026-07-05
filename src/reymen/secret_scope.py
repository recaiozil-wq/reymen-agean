# -*- coding: utf-8 -*-
"""API key guvenlik scope'u — hangi key'lerin hangi ortamda kullanilacagini belirler.

Hermes agent/secret_scope.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class SecretScope:
    """API key'lerin kapsamini belirler ve guvenli erisim saglar."""

    ORTAMLAR = {"local", "gateway", "cron", "test"}

    def __init__(self, ortam: str = "local"):
        self.ortam = ortam if ortam in self.ORTAMLAR else "local"

    def key_al(self, anahtar: str) -> Optional[str]:
        """Guvenli API key erisimi."""
        deger = os.environ.get(anahtar)
        if deger:
            return deger
        # Fallback: .env dosyasindan oku
        try:
            from dotenv import load_dotenv
            env_yolu = Path.cwd() / ".env"
            if env_yolu.exists():
                load_dotenv(env_yolu)
                return os.environ.get(anahtar)
        except Exception:
            pass
        return None

    def key_var_mi(self, anahtar: str) -> bool:
        return self.key_al(anahtar) is not None
