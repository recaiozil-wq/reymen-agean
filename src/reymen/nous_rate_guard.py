# -*- coding: utf-8 -*-
"""Nous subscription rate limit koruyucusu.

Hermes agent/nous_rate_guard.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

class NousRateGuard:
    """Nous API rate limit kontrolu."""

    def __init__(self, max_req_per_min: int = 30):
        self.max_req_per_min = max_req_per_min
        self._zaman_damgalari: list = []

    def izin_ver(self) -> bool:
        simdi = time.time()
        self._zaman_damgalari = [t for t in self._zaman_damgalari if simdi - t < 60]
        if len(self._zaman_damgalari) >= self.max_req_per_min:
            return False
        self._zaman_damgalari.append(simdi)
        return True

    def bekleme_suresi(self) -> float:
        if not self._zaman_damgalari:
            return 0
        return max(0, 60 - (time.time() - self._zaman_damgalari[0]))
