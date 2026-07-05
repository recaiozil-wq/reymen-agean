# -*- coding: utf-8 -*-
"""Hesap kullanim istatistigi.

Hermes agent/account_usage.py'den adapte.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

def kullanim_al() -> dict:
    return {"soru": 0, "token": 0, "maliyet": 0.0}
