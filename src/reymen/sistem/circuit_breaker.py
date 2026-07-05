# -*- coding: utf-8 -*-
"""circuit_breaker.py â€” Circuit Breaker pattern (ReYMeN SOUL.md standardÄ±).

5 ardisik hata â†’ circuit OPEN (30sn bekle) â†’ HALF_OPEN â†’ basarili cagri â†’ CLOSED.

Kullanim:
    cb = CircuitBreaker()
    engel = cb.denetle()          # None = devam, str = circuit acik mesaji
    if engel:
        return engel              # cagriyi blokla
    try:
        sonuc = arac_calistir()
        cb.basari_kaydet()
    except Exception:
        mesaj = cb.hata_kaydet()  # 5. hatada mesaj doner
"""

import time
from typing import Optional


class CircuitBreakerState:
    CLOSED = "closed"  # Normal calisma
    OPEN = "open"  # Hata limiti asildi, bekleniyor
    HALF_OPEN = "half_open"  # Deneme suresi, sonraki basarili cagri kapatir


class CircuitBreaker:
    """Hata esigi asildiktan sonra sistemi gecici olarak devre disi birakir.

    Durum makinesi:
      CLOSED â†’ (5 hata) â†’ OPEN â†’ (30sn) â†’ HALF_OPEN â†’ (basari) â†’ CLOSED
                                                        â†’ (hata)  â†’ OPEN
    """

    ESIK: int = 5
    BEKLEME_SURESI: int = 30  # saniye

    def __init__(self) -> None:
        self.durum: str = CircuitBreakerState.CLOSED
        self.ardisik_hata: int = 0
        self.son_acilma: float = 0.0

    def denetle(self) -> Optional[str]:
        """Circuit aciksa engel mesaji doner, aksi halde None.

        OPEN durumunda BEKLEME_SURESI geçtiyse otomatik HALF_OPEN'a gecer.
        """
        if self.durum == CircuitBreakerState.OPEN:
            gecen = time.time() - self.son_acilma
            if gecen >= self.BEKLEME_SURESI:
                self.durum = CircuitBreakerState.HALF_OPEN
                return None
            kalan = int(self.BEKLEME_SURESI - gecen)
            return f"[CIRCUIT_BREAKER] Circuit open â€” {kalan}s kaldi"
        return None

    def hata_kaydet(self) -> Optional[str]:
        """Basarisiz islem bildir. ESIK asilinca OPEN'a gecer, mesaj doner."""
        self.ardisik_hata += 1
        if self.ardisik_hata >= self.ESIK:
            self.durum = CircuitBreakerState.OPEN
            self.son_acilma = time.time()
            return (
                f"[CIRCUIT_BREAKER] {self.ardisik_hata} ardisik hata â€” "
                f"circuit open ({self.BEKLEME_SURESI}sn)"
            )
        return None

    def basari_kaydet(self) -> None:
        """Basarili islem bildir. HALF_OPEN â†’ CLOSED, sayac sifirlanir."""
        if self.durum == CircuitBreakerState.HALF_OPEN:
            self.durum = CircuitBreakerState.CLOSED
        self.ardisik_hata = 0

    def sifirla(self) -> None:
        """Tam sifirla â€” test veya manuel mudahale icin."""
        self.durum = CircuitBreakerState.CLOSED
        self.ardisik_hata = 0
        self.son_acilma = 0.0

    def durum_bilgisi(self) -> dict:
        return {
            "durum": self.durum,
            "ardisik_hata": self.ardisik_hata,
            "son_acilma": self.son_acilma,
        }
