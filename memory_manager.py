# -*- coding: utf-8 -*-
"""SHIM — agent/memory_manager.py yönlendirir + ReYMeN Türkçe API"""
from agent.memory_manager import *  # noqa: F401, F403
from agent.memory_manager import memory_manager  # noqa: F401

# Private name export — test patching için
import importlib as _imp_mm, sys as _sys_mm
_src_mm = _imp_mm.import_module('agent.memory_manager')
_sys_mm.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src_mm).items() if k.startswith('_') and not k.startswith('__')}
)


class MemoryManager:
    """ReYMeN bellek yöneticisi — kısa/uzun süreli bellek."""

    def __init__(self, max_kisa_bellek: int = 100, max_uzun_bellek: int = 1000):
        self._max_kisa = max_kisa_bellek
        self._max_uzun = max_uzun_bellek
        self._kisa_bellek: dict = {}
        self._uzun_bellek: dict = {}
        self._erisim_sayisi: dict = {}

    # Uyumluluk aliasları
    @property
    def _kisa(self):
        return self._kisa_bellek

    @property
    def _uzun(self):
        return self._uzun_bellek

    def hatirla(self, anahtar: str, deger, sure: str = "kisa") -> None:
        if sure == "uzun":
            self._uzun_bellek[anahtar] = deger
        else:
            self._kisa_bellek[anahtar] = deger

    def oku(self, anahtar: str):
        self._erisim_sayisi[anahtar] = self._erisim_sayisi.get(anahtar, 0) + 1
        return self._kisa_bellek.get(anahtar, self._uzun_bellek.get(anahtar))

    def ara(self, sorgu: str) -> list:
        sonuclar = []
        for d in (self._kisa_bellek, self._uzun_bellek):
            for k, v in d.items():
                if sorgu in k or (isinstance(v, str) and sorgu in v):
                    sonuclar.append((k, v))
        return sonuclar

    def unut(self, anahtar: str) -> None:
        self._kisa_bellek.pop(anahtar, None)
        self._uzun_bellek.pop(anahtar, None)

    def temizle(self, sure: str = "kisa") -> None:
        if sure == "uzun":
            self._uzun_bellek.clear()
        elif sure == "hepsi":
            self._kisa_bellek.clear()
            self._uzun_bellek.clear()
        else:
            self._kisa_bellek.clear()
