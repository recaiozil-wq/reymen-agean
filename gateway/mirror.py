# -*- coding: utf-8 -*-
"""gateway/mirror.py — Kanal Aynalama.

Bir kanala gelen mesaji diger kanallara otomatik yonlendirir.
"""

import threading


class Mirror:
    def __init__(self):
        self._kurallar: list[dict] = []
        self._kilit = threading.Lock()

    def ekle(self, kaynak: str, hedefler: list[str]):
        """Yeni aynalama kurali ekle.

        Args:
            kaynak: Kaynak platform adi
            hedefler: Yonlendirilecek hedef platformlar
        """
        with self._kilit:
            self._kurallar.append({"kaynak": kaynak, "hedefler": hedefler})

    def sil(self, kaynak: str):
        with self._kilit:
            self._kurallar = [k for k in self._kurallar if k["kaynak"] != kaynak]

    def yonlendir(self, kaynak: str, mesaj: str) -> list[str]:
        """Bir mesaji kurallara gore yonlendir.

        Args:
            kaynak: Mesajin geldigi platform
            mesaj: Mesaj icerigi

        Returns:
            Yonlendirme yapilan platformlar
        """
        with self._kilit:
            yonlendirilen = []
            for kural in self._kurallar:
                if kural["kaynak"] == kaynak:
                    yonlendirilen.extend(kural["hedefler"])
            return yonlendirilen

    def kurallar(self) -> list[dict]:
        with self._kilit:
            return list(self._kurallar)


# Global instance
aynalayici = Mirror()
