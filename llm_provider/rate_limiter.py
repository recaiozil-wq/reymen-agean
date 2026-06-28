# -*- coding: utf-8 -*-
"""llm_provider/rate_limiter.py — Provider başına istek hız sınırlayıcı.

Token bucket algoritması; her provider için RPM (dakika başı istek)
sınırını thread-safe biçimde uygular. Limit aşılırsa çağrıyı bloke eder.
"""

import time
import threading
from dataclasses import dataclass, field

# Varsayılan dakika başı istek sınırları (ücretsiz/tier-1 değerleri)
_VARSAYILAN_RPM: dict[str, int] = {
    "openai":    500,
    "anthropic":  50,
    "groq":       30,
    "ollama":   9999,  # yerel — sınırsız sayılır
}


@dataclass
class _Kova:
    """Token bucket durumu (tek provider için)."""
    kapasite: int           # max jeton = RPM
    jetonlar: float         # mevcut jeton sayısı
    son_doldurma: float = field(default_factory=time.monotonic)
    kilit: threading.Lock = field(default_factory=threading.Lock)


class RateLimiter:
    """Provider başına RPM sınırı uygulayan token bucket rate limiter.

    Kullanım::

        rl = RateLimiter()
        rl.bekle("openai")   # Limit aşılmışsa bekler, aksi halde anında döner
        provider.chat(...)
    """

    def __init__(self, ozel_rpm: dict[str, int] | None = None):
        """
        Args:
            ozel_rpm: Varsayılan RPM değerlerini ezmek için {provider: rpm} dict'i.
        """
        rpm = {**_VARSAYILAN_RPM, **(ozel_rpm or {})}
        self._kovalar: dict[str, _Kova] = {
            p: _Kova(kapasite=r, jetonlar=float(r))
            for p, r in rpm.items()
        }

    def _kova_al(self, provider: str) -> _Kova:
        if provider not in self._kovalar:
            # Bilinmeyen provider → varsayılan 60 RPM
            self._kovalar[provider] = _Kova(kapasite=60, jetonlar=60.0)
        return self._kovalar[provider]

    def bekle(self, provider: str) -> float:
        """Bir istek hakkı talep et; gerekirse bloke et.

        Args:
            provider: 'openai' | 'anthropic' | 'groq' | 'ollama' vb.

        Returns:
            float: Beklenen süre (saniye). Beklemediyse 0.0.
        """
        kova = self._kova_al(provider)
        bekleme = 0.0

        with kova.kilit:
            simdi = time.monotonic()
            gecen = simdi - kova.son_doldurma
            kova.son_doldurma = simdi

            # Geçen süreye göre jeton yenile (1 dakika = kapasite kadar jeton)
            yeni_jeton = gecen * (kova.kapasite / 60.0)
            kova.jetonlar = min(kova.kapasite, kova.jetonlar + yeni_jeton)

            if kova.jetonlar >= 1.0:
                kova.jetonlar -= 1.0
            else:
                # Yeterli jeton yok — bir jeton dolana kadar bekle
                bekleme = (1.0 - kova.jetonlar) / (kova.kapasite / 60.0)
                kova.jetonlar = 0.0

        if bekleme > 0:
            print(f"\033[93m[RATE] '{provider}' sınırı → {bekleme:.2f}s bekleniyor\033[0m")
            time.sleep(bekleme)

        return bekleme

    def durum(self, provider: str) -> dict:
        """Provider'ın mevcut jeton durumunu döndür.

        Returns:
            dict: {'provider', 'jetonlar', 'kapasite', 'dolu_yuzde'}
        """
        kova = self._kova_al(provider)
        with kova.kilit:
            return {
                "provider": provider,
                "jetonlar": round(kova.jetonlar, 2),
                "kapasite": kova.kapasite,
                "dolu_yuzde": round(kova.jetonlar / kova.kapasite * 100, 1),
            }

    def tum_durum(self) -> list[dict]:
        """Tüm provider'ların jeton durumunu döndür."""
        return [self.durum(p) for p in self._kovalar]


# Modül düzeyi singleton
_limiter = RateLimiter()


def global_limiter() -> RateLimiter:
    """Global singleton RateLimiter döndür."""
    return _limiter
