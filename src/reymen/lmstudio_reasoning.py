# -*- coding: utf-8 -*-
"""LM Studio reasoning endpoint adapter.

Hermes agent/lmstudio_reasoning.py'den adapte.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class LMStudioReasoning:
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
