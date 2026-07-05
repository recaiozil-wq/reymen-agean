# -*- coding: utf-8 -*-
"""Iptal sinyali gonderme.

conversation_loop.py'den extract edilmistir.
Telegram bot, CLI veya web UI'dan conversation_loop'u durdurmak icin.
"""
from __future__ import annotations

import logging
from pathlib import Path

_PROJE_KOK = Path(__file__).resolve().parent.parent.parent
_STOP_SINYAL_DOSYASI = _PROJE_KOK / ".stop"
_STOP_SINYAL_ALTERNATIF = _PROJE_KOK / ".ReYMeN" / ".stop"

logger = logging.getLogger("conversation_loop")


def iptal_sinyali_gonder(mesaj: str = "stop") -> bool:
    """ConversationLoop'u durdurmak icin dosya tabanli sinyal gonder.

    Args:
        mesaj: Iptal sebebi (opsiyonel, .stop dosyasina yazilir)

    Returns:
        True = sinyal basariyla gonderildi
    """
    try:
        _STOP_SINYAL_DOSYASI.write_text(mesaj, encoding="utf-8")
        try:
            _STOP_SINYAL_ALTERNATIF.parent.mkdir(parents=True, exist_ok=True)
            _STOP_SINYAL_ALTERNATIF.write_text(mesaj, encoding="utf-8")
        except Exception:
            pass
        logger.warning("[IPTAL] Sinyal gonderildi: %s", mesaj)
        return True
    except Exception as e:
        logger.error("[IPTAL] Sinyal gonderilemedi: %s", e)
        return False
