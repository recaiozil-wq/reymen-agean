# -*- coding: utf-8 -*-
"""Gemini Cloud Code adapter.

Hermes agent/gemini_cloudcode_adapter.py'den adapte.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class GeminiCloudCodeAdapter:
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
