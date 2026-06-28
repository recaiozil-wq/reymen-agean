# -*- coding: utf-8 -*-
"""memory_providers/base.py — Bellek sağlayıcı interface."""

from __future__ import annotations          # 3.8 compat: list[dict] yerine
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BellekSaglayici(ABC):
    """Tüm bellek sağlayıcılar için interface."""

    @abstractmethod
    def kaydet(self, anahtar: str, deger: Any,
               namespace: str = "default") -> str: ...

    @abstractmethod
    def oku(self, anahtar: str,
            namespace: str = "default") -> Optional[Any]: ...

    @abstractmethod
    def ara(self, sorgu: str, limit: int = 5) -> List[Dict]: ...

    @abstractmethod
    def sil(self, anahtar: str, namespace: str = "default") -> str: ...

    @abstractmethod
    def durum(self) -> Dict: ...

    # ── Ortak yardımcı ────────────────────────────────────────
    @staticmethod
    def _sinirla(metin: str, limit: int = 200) -> str:
        """Cümle ortasında kesmez; son boşluğa snap eder."""
        if len(metin) <= limit:
            return metin
        kes = metin[:limit].rfind(" ")
        return metin[: kes if kes > 0 else limit] + "…"
