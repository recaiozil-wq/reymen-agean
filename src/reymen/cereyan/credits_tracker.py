# -*- coding: utf-8 -*-
"""Credit/budget tracker — kredi takibi ve limit yonetimi.

ReYMeN'e ozgu, Hermes bagimliligi YOK.
conversation_loop_v2.py'den extract edilmistir.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

logger = logging.getLogger("conversation_loop")


class CreditsTracker:
    """Kredi/bakiye takibi.

    Her API cagrisinda token tuketimini kaydeder,
    limit asiminda uyari verir.
    """

    def __init__(self, max_budget: float = 0.0):
        self.max_budget = max_budget  # 0 = limitsiz
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_call_count = 0
        self._warning_threshold = 0.8  # %80 uyari
        self._critical_threshold = 0.95  # %95 kritik
        self._start_time = time.time()

    def kaydet(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        model: Optional[str] = None,
    ) -> None:
        """API cagrisi sonucu token/kredi kaydet."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
        self.api_call_count += 1

        if self.max_budget > 0:
            oran = self.total_cost / self.max_budget
            if oran >= self._critical_threshold:
                logger.warning(
                    "Kritik: butce %d%% tukendi (%.4f/%.4f USD, model=%s)",
                    int(oran * 100), self.total_cost, self.max_budget, model or "?",
                )
            elif oran >= self._warning_threshold:
                logger.info(
                    "Uyari: butce %d%% tukendi (%.4f/%.4f USD)",
                    int(oran * 100), self.total_cost, self.max_budget,
                )

    def durum(self) -> dict:
        """Mevcut durum raporu."""
        return {
            "api_calls": self.api_call_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost": round(self.total_cost, 6),
            "max_budget": self.max_budget,
            "calisma_suresi": round(time.time() - self._start_time, 2),
            "butce_kullanimi": f"{self.total_cost / self.max_budget * 100:.1f}%"
            if self.max_budget > 0
            else "limitsiz",
        }

    def limit_asildi_mi(self) -> bool:
        """Butce limiti asildi mi?"""
        return self.max_budget > 0 and self.total_cost >= self.max_budget


class SimpleBudget:
    """Basit iterasyon budget — iteration_budget modulu yoksa kullanilir."""

    def __init__(self, max_tur: int):
        self.max_tur = max_tur
        self.tur = 0
        self._bitti = False

    def devam_etmeli_mi(self) -> bool:
        return self.tur < self.max_tur and not self._bitti

    def tur_basla(self) -> None:
        self.tur += 1

    def tur_bitir(self, basarili: bool = True, **_: Any) -> None:
        self._bitti = basarili

    def gorev_tamamla(self) -> None:
        self._bitti = True

    gorev_tamami = gorev_tamamla

    def eylem_kaydet(self, _: Any) -> None:
        pass

    def ozet_dict(self) -> dict:
        return {"tur": self.tur, "max_tur": self.max_tur}


def budget_olustur(hedef: str, max_tur: int = 30) -> Any:
    """IterationBudget olustur; modul yoksa basit sayac doner."""
    try:
        from reymen.cereyan.iteration_budget import standart_budget

        b = standart_budget(hedef)
        b.max_tur = max(b.max_tur, max_tur)
        return b
    except ImportError:
        return SimpleBudget(max_tur)
