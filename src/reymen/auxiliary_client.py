# -*- coding: utf-8 -*-
"""Yardimci API istemcisi.

Hermes agent/auxiliary_client.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import urllib.request
import json
from typing import Optional

logger = logging.getLogger(__name__)

def api_get(url: str, timeout: int = 10) -> Optional[dict]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ReYMeN-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.debug("API GET hatasi: %s", e)
        return None

def api_post(url: str, data: dict, timeout: int = 10) -> Optional[dict]:
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                      headers={"Content-Type": "application/json",
                                               "User-Agent": "ReYMeN-Agent/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        logger.debug("API POST hatasi: %s", e)
        return None
