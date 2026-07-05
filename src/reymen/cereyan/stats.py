# -*- coding: utf-8 -*-
"""ConversationLoop istatistik ve durum bilgisi.

conversation_loop.py'den extract edilmistir.
"""
from __future__ import annotations

from typing import Any


def loop_istatistik(
    durum: str,
    max_tur: int,
    tur_yoneticisi: Any = None,
) -> dict:
    """Dongu istatistiklerini dondur."""
    return {
        "durum": durum,
        "max_tur": max_tur,
        "tur_raporu": (
            tur_yoneticisi.genel_rapor() if tur_yoneticisi else {}
        ),
    }


def loop_durum(durum: str) -> str:
    """Dongu durumunu dondur."""
    return durum
