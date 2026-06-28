# -*- coding: utf-8 -*-
"""SHIM — agent/turn_context.py yönlendirir"""
from agent.turn_context import *  # noqa: F401, F403
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class TurnKarari:
    """Tur kararı veri sınıfı."""
    adim: int = 0
    eylem: str = ""
    arac: str = ""
    token_sayisi: int = 0
    basarili: Optional[bool] = None
    sonuc: str = ""


class TurnContext:
    """ReYMeN tur bağlamı."""

    def __init__(self, tur_id: int = 0, **kwargs):
        self.tur_id = tur_id
        self.kararlar: List[TurnKarari] = []
        self._adim = 0

    def karar_ekle(self, eylem: str, arac: str = "", **kwargs) -> TurnKarari:
        self._adim += 1
        karar = TurnKarari(adim=self._adim, eylem=eylem, arac=arac)
        self.kararlar.append(karar)
        return karar

    def karar_bitir(self, basarili: bool = True, sonuc: str = "") -> None:
        if self.kararlar:
            self.kararlar[-1].basarili = basarili
            self.kararlar[-1].sonuc = sonuc

    def raporla(self) -> dict:
        return {
            "tur_id": self.tur_id,
            "toplam_adim": len(self.kararlar),
            "kararlar": [{"adim": k.adim, "eylem": k.eylem, "basarili": k.basarili} for k in self.kararlar],
        }


class TurnYoneticisi:
    """Tur yöneticisi."""

    def __init__(self, max_tur: int = 10):
        self.max_tur = max_tur
        self._tur = 0

    def yeni_tur(self) -> TurnContext:
        self._tur += 1
        return TurnContext(tur_id=self._tur)

    def genel_rapor(self) -> dict:
        """Genel tur istatistiklerini donder."""
        return {"toplam_tur": self._tur, "max_tur": self.max_tur}
