# -*- coding: utf-8 -*-
"""Codex Responses API adapter.

Hermes agent/codex_responses_adapter.py'den adapte.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class CodexResponsesAdapter:
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
