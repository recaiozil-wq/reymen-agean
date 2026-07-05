# -*- coding: utf-8 -*-
"""Kullanici geri bildirimi ile context compression.

Hermes agent/manual_compression_feedback.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CompressionFeedback:
    """Kullanicidan gelen compression geri bildirimini yonetir."""

    def __init__(self):
        self._feedback: dict = {"begenildi": 0, "sikayet": 0}

    def begendi(self) -> None:
        self._feedback["begenildi"] += 1

    def sikayet(self) -> None:
        self._feedback["sikayet"] += 1

    def oran(self) -> float:
        toplam = self._feedback["begenildi"] + self._feedback["sikayet"]
        if toplam == 0:
            return 0.5
        return self._feedback["begenildi"] / toplam
