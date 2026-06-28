# -*- coding: utf-8 -*-
"""SHIM — agent/chat_completion_helpers.py yönlendirir"""
from agent.chat_completion_helpers import *  # noqa: F401, F403


class ChatHelper:
    """Chat completion yardımcı sınıfı."""

    def __init__(self, model_adi: str = "varsayilan"):
        self._model_adi = model_adi
        self._istatistik = {"toplam_mesaj": 0, "toplam_token": 0}

    def mesaj_hazirla(self, rol: str, icerik: str) -> dict:
        token = self.token_say(icerik)
        self._istatistik["toplam_mesaj"] += 1
        self._istatistik["toplam_token"] += token
        return {"rol": rol, "icerik": icerik}

    def token_say(self, metin: str) -> int:
        return max(1, len(metin.split())) if metin else 0
