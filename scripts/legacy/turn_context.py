# -*- coding: utf-8 -*-
"""
turn_context.py — Per-turn context management for ReYMeN conversation loop.

Provides TurnContext, TurnKarari, and TurnYoneticisi for the turn lifecycle.
- TurnContext: holds per-turn state (kararlar, tur_id, etc.)
- TurnKarari: a single turn decision record
- TurnYoneticisi: manages multi-turn contexts (used by conversation_loop.py)

Stub module — reconciles conversation_loop.py and test_cozum.py APIs.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TurnKarari:
    """A single turn decision record."""

    adim: int = 0
    eylem: str = ""
    arac: Optional[str] = None
    tur: str = ""
    sonuc: Any = None
    basarili: Optional[bool] = None
    token_sayisi: int = 0
    icerik: str = ""


@dataclass
class TurnContext:
    """Per-turn context holding decisions, state, and results.

    Supports both conversation_loop.py API (used via TurnYoneticisi):
        ctx = tur_yoneticisi.yeni_tur()
        ctx.toplam_gereksinim_sayisi = 1
        ctx.karar_ekle(tur, arac)
        ctx.karar_bitir(basarili, sonuc)
        ctx.cozum_ozeti = "..."
        ctx.raporla()

    And test_cozum.py API:
        ctx = TurnContext(tur_id=1)
        ctx.karar_ekle("DOSYA_OKU", arac="DOSYA_OKU")
        ctx.karar_bitir(basarili=True, sonuc="Basarili")
    """

    # test_cozum.py API
    tur_id: int = 0
    kararlar: List[TurnKarari] = field(default_factory=list)

    # conversation_loop.py API
    toplam_gereksinim_sayisi: int = 0
    tamamlanan_gereksinim_sayisi: int = 0
    cozum_ozeti: str = ""
    user_message: str = ""
    original_user_message: Any = None
    messages: List[Dict[str, Any]] = field(default_factory=list)
    conversation_history: Optional[List[Dict[str, Any]]] = None
    active_system_prompt: Optional[str] = None
    effective_task_id: str = ""
    turn_id: str = ""
    current_turn_user_idx: int = 0
    should_review_memory: bool = False
    plugin_user_context: str = ""
    ext_prefetch_cache: str = ""

    _adim_sayaci: int = 0

    def karar_ekle(self, tur: str, arac: Optional[str] = None) -> TurnKarari:
        """Add a new decision record to this turn's context."""
        self._adim_sayaci += 1
        karar = TurnKarari(
            adim=self._adim_sayaci,
            eylem=tur,
            arac=arac,
            tur=tur,
        )
        self.kararlar.append(karar)
        return karar

    def karar_bitir(self, basarili: bool, sonuc: Any = None) -> None:
        """Mark the latest decision as completed."""
        if self.kararlar:
            self.kararlar[-1].basarili = basarili
            self.kararlar[-1].sonuc = sonuc
            if basarili:
                self.tamamlanan_gereksinim_sayisi += 1

    def raporla(self) -> dict:
        """Return a summary dict for this turn's results."""
        return {
            "turlar": len(self.kararlar),
            "tamamlanan": self.tamamlanan_gereksinim_sayisi,
            "toplam": self.toplam_gereksinim_sayisi,
            "cozum_ozeti": self.cozum_ozeti[:200] if self.cozum_ozeti else "",
        }


class TurnYoneticisi:
    """Manages turn contexts across conversation turns.

    Used by ConversationLoop to track per-turn state, decisions, and
    completion status.
    """

    def __init__(self, max_tur: int = 30):
        self.max_tur = max_tur
        self._contexts: List[TurnContext] = []
        self.toplam_gereksinim_sayisi = 0
        self.tamamlanan_gereksinim_sayisi = 0

    def yeni_tur(self) -> TurnContext:
        """Create and return a new TurnContext for a fresh turn."""
        ctx = TurnContext(
            tur_id=len(self._contexts) + 1,
            turn_id=str(uuid.uuid4())[:8],
        )
        ctx.toplam_gereksinim_sayisi = self.toplam_gereksinim_sayisi
        self._contexts.append(ctx)
        return ctx

    def tur_sayisi(self) -> int:
        """Return number of turns recorded so far."""
        return len(self._contexts)

    def karar_ekle(self, tur: str, arac: Optional[str] = None) -> Optional[TurnKarari]:
        """Add a decision to the latest turn context."""
        if self._contexts:
            return self._contexts[-1].karar_ekle(tur, arac)
        return None

    def karar_bitir(self, basarili: bool, sonuc: Any = None) -> None:
        """Mark the latest decision as completed across all contexts."""
        for ctx in reversed(self._contexts):
            if ctx.kararlar:
                ctx.karar_bitir(basarili, sonuc)
                break

    def raporla(self) -> dict:
        """Return a summary dict across all turns."""
        return {
            "turlar": self.tur_sayisi(),
            "tamamlanan": self.tamamlanan_gereksinim_sayisi,
            "toplam": self.toplam_gereksinim_sayisi,
        }
