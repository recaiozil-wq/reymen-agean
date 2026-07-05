# -*- coding: utf-8 -*-
"""Memory provider ABC.

Hermes agent/memory_provider.py'den adapte.
"""
from __future__ import annotations
import abc
from typing import Any

class MemoryProvider(abc.ABC):
    @abc.abstractmethod
    def read(self, anahtar: str) -> Any: ...
    @abc.abstractmethod
    def write(self, anahtar: str, deger: Any) -> None: ...

class OnceHafizaProvider(MemoryProvider):
    def read(self, anahtar):
        try:
            from reymen.sistem.once_hafiza import hafizada_ara
            return hafizada_ara(anahtar)
        except Exception:
            return None
    def write(self, anahtar, deger):
        try:
            from reymen.sistem.once_hafiza import kaydet
            kaydet(hedef=anahtar, cozum=str(deger), kategori="genel", kaynak="memory_provider")
        except Exception:
            pass
