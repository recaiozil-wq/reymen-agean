# -*- coding: utf-8 -*-
"""Plugin LLM entegrasyonu.

Hermes agent/plugin_llm.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class PluginLLM:
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
