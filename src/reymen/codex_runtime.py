# -*- coding: utf-8 -*-
"""Codex runtime adapter.

Hermes agent/codex_runtime.py'den adapte.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class CodexRuntime:
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
