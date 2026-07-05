# -*- coding: utf-8 -*-
"""Hava durumu sorgulama.

Hermes agent/weather.py'den adapte edilmistir.
"""
from __future__ import annotations
import json
import logging
import urllib.request
from typing import Optional

logger = logging.getLogger(__name__)

def hava_durumu(sehir: str = "Istanbul") -> Optional[str]:
    try:
        url = f"https://wttr.in/{sehir}?format=%C+%t"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode().strip()
    except Exception as e:
        logger.debug("Hava durumu hatasi: %s", e)
        return None
