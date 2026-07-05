# -*- coding: utf-8 -*-
"""Gemini Native API adapter.

Hermes agent/gemini_native_adapter.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class GeminiNativeAdapter:
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
