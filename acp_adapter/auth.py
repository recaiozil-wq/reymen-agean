# -*- coding: utf-8 -*-
"""acp_adapter/auth.py — ACP Kimlik Dogrulama.

ACP baglantilari icin basit token tabanli kimlik dogrulama.
"""

import hashlib
import hmac
import os
import time


class ACPAuth:
    """ACP kimlik dogrulama (HMAC + timestamp)."""

    def __init__(self, token: str = ""):
        self.token = token or os.environ.get("ACP_TOKEN", "ReYMeN-acp-default")
        self._suresi = 300  # 5 dakika gecerli

    def imzala(self, mesaj: str = "") -> str:
        """Bir mesaji HMAC ile imzala."""
        timestamp = str(int(time.time()))
        data = f"{timestamp}:{mesaj}"
        imza = hmac.new(
            self.token.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()[:16]
        return f"{timestamp}:{imza}"

    def dogrula(self, imzali_mesaj: str, mesaj: str = "") -> bool:
        """Imzali mesaji dogrula."""
        try:
            timestamp, imza = imzali_mesaj.split(":", 1)
            # Sure kontrolu
            if int(time.time()) - int(timestamp) > self._suresi:
                return False
            # Imza kontrolu
            beklenen = self.imzala(mesaj).split(":", 1)[1]
            return hmac.compare_digest(imza, beklenen)
        except Exception:
            return False


# — Test/ACP API exports (Hermes reference uyumu) —

TERMINAL_SETUP_AUTH_METHOD_ID = "terminal_setup"


def build_auth_methods(config):
    """Mevcut ACPAuth'tan method listesi üret."""
    return [ACPAuth(config)]


def has_provider(name):
    """Provider var mı kontrol et."""
    return name in ["hmac", "terminal_setup"]


def detect_provider(request):
    """Request'ten provider tipini tespit et."""
    if hasattr(request, "headers") and "x-hmac-signature" in request.headers:
        return "hmac"
    return "terminal_setup"
