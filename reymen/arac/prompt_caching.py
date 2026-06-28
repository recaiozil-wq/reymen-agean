# -*- coding: utf-8 -*-
"""prompt_caching.py — Prompt Onbellekleme.

Ayni prompt'lari LLM'e tekrar gondermemek icin hash tabanli
onbellek. TTL ve LRU ile bellek yonetimi.
"""

import hashlib
import json
import time
from collections import OrderedDict
from typing import Optional


class PromptCache:
    """Prompt onbellegi (LRU + TTL)."""

    def __init__(self, max_boyut: int = 100, ttl_saniye: int = 300):
        self._max_boyut = max_boyut
        self._ttl = ttl_saniye
        self._cache: OrderedDict[str, tuple[float, str]] = OrderedDict()
        self._hit = 0
        self._miss = 0

    def _hash(self, prompt: str, mesajlar: list) -> str:
        """Prompt + mesajlardan hash uret."""
        veri = prompt + "|" + json.dumps(mesajlar, sort_keys=True)
        return hashlib.md5(veri.encode("utf-8"), usedforsecurity=False).hexdigest()

    def al(self, prompt: str, mesajlar: list) -> Optional[str]:
        """Onbellekten yanit al.

        Returns:
            Yanit metni veya None (onbellekte yok/sure dolmus)
        """
        anahtar = self._hash(prompt, mesajlar)
        if anahtar not in self._cache:
            self._miss += 1
            return None

        zaman, yanit = self._cache[anahtar]
        if time.time() - zaman > self._ttl:
            del self._cache[anahtar]
            self._miss += 1
            return None

        # LRU: son kullanima tasi
        self._cache.move_to_end(anahtar)
        self._hit += 1
        return yanit

    def ekle(self, prompt: str, mesajlar: list, yanit: str):
        """Onbellege yanit ekle."""
        anahtar = self._hash(prompt, mesajlar)
        self._cache[anahtar] = (time.time(), yanit)

        # LRU eviction
        while len(self._cache) > self._max_boyut:
            self._cache.popitem(last=False)

    def istatistik(self) -> dict:
        toplam = self._hit + self._miss
        return {
            "boyut": len(self._cache),
            "hit": self._hit,
            "miss": self._miss,
            "hit_orani": round(self._hit / toplam * 100, 1) if toplam > 0 else 0,
        }

    def sifirla(self):
        self._cache.clear()
        self._hit = 0
        self._miss = 0


# Global cache instance
_ONBELLEK = PromptCache()


def cache_ile_uret(prompt: str, mesajlar: list, uret_fonksiyonu) -> str:
    """Onbellek kontrolu ile LLM cagrisi yap.

    Args:
        prompt: Sistem prompt'u
        mesajlar: Konusma mesajlari
        uret_fonksiyonu: Onbellekte yoksa cagrilacak fonksiyon

    Returns:
        Yanit metni
    """
    yanit = _ONBELLEK.al(prompt, mesajlar)
    if yanit is not None:
        return yanit

    yanit = uret_fonksiyonu(prompt, mesajlar)
    _ONBELLEK.ekle(prompt, mesajlar, yanit)
    return yanit


if __name__ == "__main__":
    c = PromptCache(max_boyut=5, ttl_saniye=10)
    c.ekle("test", [{"role": "user", "content": "merhaba"}], "merhaba")
    print("Hit:", c.al("test", [{"role": "user", "content": "merhaba"}]))
    print("Miss:", c.al("test", [{"role": "user", "content": "nasilsin"}]))
    print("Istatistik:", c.istatistik())
