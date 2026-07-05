# -*- coding: utf-8 -*-
"""AWS Bedrock adapter.

Hermes agent/bedrock_adapter.py'den adapte.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class BedrockAdapter:
    """AWS Bedrock API'sine baglanir."""
    def __init__(self):
        self.aktif = False
    def is_available(self) -> bool:
        return self.aktif
