# -*- coding: utf-8 -*-
"""SHIM — agent/credential_sources.py yönlendirir"""
from agent.credential_sources import *  # noqa: F401, F403
import os as _os


class CredentialSource:
    """Ortam değişkeni ve bellek tabanlı kimlik bilgisi kaynağı."""

    def __init__(self, kaynak_yolu: str = ""):
        self.kaynak_yolu = kaynak_yolu
        self._bellek_ortusu: dict = {}
        self._kaynak_istatistik: dict = {"env_alma": 0, "bellek_kayit": 0}

    def al(self, anahtar: str):
        self._kaynak_istatistik["env_alma"] = self._kaynak_istatistik.get("env_alma", 0) + 1
        return self._bellek_ortusu.get(anahtar, _os.environ.get(anahtar))

    def kaydet(self, anahtar: str, deger: str, kaynak: str = "bellek") -> None:
        self._bellek_ortusu[anahtar] = deger
        self._kaynak_istatistik["bellek_kayit"] = self._kaynak_istatistik.get("bellek_kayit", 0) + 1

    def kaynak_listele(self) -> dict:
        return {"kaynaklar": list(self._bellek_ortusu.keys()), "sayac": self._kaynak_istatistik}
