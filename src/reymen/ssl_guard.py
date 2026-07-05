# -*- coding: utf-8 -*-
"""SSL guvenlik denetimi.

Hermes agent/ssl_guard.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import ssl
logger = logging.getLogger(__name__)

def ssl_kontrol() -> bool:
    try:
        ctx = ssl.create_default_context()
        return True
    except Exception as e:
        logger.warning("SSL yapilandirma hatasi: %s", e)
        return False

def guvenli_url(url: str) -> bool:
    return url.startswith("https://")
