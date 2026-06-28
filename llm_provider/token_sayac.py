# -*- coding: utf-8 -*-
"""llm_provider/token_sayac.py — Token kullanımı ve maliyet takibi.

Her API çağrısından sonra token sayısını ve tahmini USD maliyetini kaydeder.
Thread-safe; birden fazla provider aynı anda kullanılabilir.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Optional

# $/1M token (Haziran 2025 tarifesi, yaklaşık)
_FIYAT: dict[str, dict[str, float]] = {
    "openai": {
        "gpt-4o":            {"giris": 2.50,  "cikis": 10.00},
        "gpt-4-turbo":       {"giris": 10.00, "cikis": 30.00},
        "gpt-4":             {"giris": 30.00, "cikis": 60.00},
        "gpt-3.5-turbo":     {"giris": 0.50,  "cikis": 1.50},
    },
    "anthropic": {
        "claude-sonnet-4-6":          {"giris": 3.00,  "cikis": 15.00},
        "claude-opus-4-8":            {"giris": 15.00, "cikis": 75.00},
        "claude-haiku-4-5-20251001":  {"giris": 0.25,  "cikis": 1.25},
        "claude-3-5-sonnet-20241022": {"giris": 3.00,  "cikis": 15.00},
    },
    "groq": {
        "llama-3.3-70b-versatile": {"giris": 0.59, "cikis": 0.79},
        "llama-3.1-8b-instant":    {"giris": 0.05, "cikis": 0.08},
        "mixtral-8x7b-32768":      {"giris": 0.24, "cikis": 0.24},
    },
    "ollama": {},  # yerel, ücretsiz
}


@dataclass
class TokenKayit:
    """Tek bir API çağrısına ait token/maliyet kaydı."""
    provider: str
    model: str
    giris_token: int
    cikis_token: int
    maliyet_usd: float
    zaman: float = field(default_factory=time.time)


class TokenSayac:
    """Oturum genelinde token tüketimini ve tahmini maliyeti izler."""

    def __init__(self):
        self._kayitlar: list[TokenKayit] = []
        self._kilit = threading.Lock()

    def kaydet(self, provider: str, model: str,
               giris_token: int, cikis_token: int) -> TokenKayit:
        """Yeni bir API çağrısını kaydet.

        Args:
            provider: 'openai' | 'anthropic' | 'groq' | 'ollama'
            model: Model adı.
            giris_token: Prompt/input token sayısı.
            cikis_token: Completion/output token sayısı.

        Returns:
            TokenKayit: Hesaplanan maliyet dahil kayıt.
        """
        maliyet = self._hesapla(provider, model, giris_token, cikis_token)
        kayit = TokenKayit(
            provider=provider,
            model=model,
            giris_token=giris_token,
            cikis_token=cikis_token,
            maliyet_usd=maliyet,
        )
        with self._kilit:
            self._kayitlar.append(kayit)
        return kayit

    def _hesapla(self, provider: str, model: str,
                 giris: int, cikis: int) -> float:
        """Tahmini USD maliyetini hesapla."""
        provider_fiyat = _FIYAT.get(provider, {})
        model_fiyat = provider_fiyat.get(model)

        if model_fiyat is None:
            # Model bulunamazsa provider ortalamasını kullan
            degerler = list(provider_fiyat.values())
            if not degerler:
                return 0.0
            model_fiyat = {
                "giris": sum(v["giris"] for v in degerler) / len(degerler),
                "cikis": sum(v["cikis"] for v in degerler) / len(degerler),
            }

        return (giris * model_fiyat["giris"] + cikis * model_fiyat["cikis"]) / 1_000_000

    def ozet(self) -> dict:
        """Oturum özeti: provider başına token + maliyet toplamları.

        Returns:
            dict: {
                'toplam_giris': int,
                'toplam_cikis': int,
                'toplam_usd': float,
                'provider_bazli': {provider: {giris, cikis, usd}},
                'cagri_sayisi': int,
            }
        """
        with self._kilit:
            kayitlar = list(self._kayitlar)

        provider_bazli: dict[str, dict] = {}
        for k in kayitlar:
            if k.provider not in provider_bazli:
                provider_bazli[k.provider] = {"giris": 0, "cikis": 0, "usd": 0.0, "cagri": 0}
            pb = provider_bazli[k.provider]
            pb["giris"] += k.giris_token
            pb["cikis"] += k.cikis_token
            pb["usd"] += k.maliyet_usd
            pb["cagri"] += 1

        toplam_giris = sum(k.giris_token for k in kayitlar)
        toplam_cikis = sum(k.cikis_token for k in kayitlar)
        toplam_usd = sum(k.maliyet_usd for k in kayitlar)

        return {
            "toplam_giris": toplam_giris,
            "toplam_cikis": toplam_cikis,
            "toplam_usd": round(toplam_usd, 6),
            "provider_bazli": provider_bazli,
            "cagri_sayisi": len(kayitlar),
        }

    def yazdir(self) -> None:
        """Özeti renkli olarak konsola yaz."""
        o = self.ozet()
        print(f"\033[94m{'-'*50}\033[0m")
        print(f"\033[94m[TOKEN] {o['cagri_sayisi']} cagri | "
              f"giris={o['toplam_giris']:,} | cikis={o['toplam_cikis']:,} | "
              f"\033[93m${o['toplam_usd']:.4f}\033[0m")
        for provider, pb in o["provider_bazli"].items():
            print(f"  \033[92m{provider:12}\033[0m "
                  f"in={pb['giris']:,} out={pb['cikis']:,}  ${pb['usd']:.4f}")
        print(f"\033[94m{'-'*50}\033[0m")

    def sifirla(self) -> None:
        """Oturum sayacını sıfırla."""
        with self._kilit:
            self._kayitlar.clear()


# Modül düzeyi singleton — tüm provider'lar paylaşır
_sayac = TokenSayac()


def global_sayac() -> TokenSayac:
    """Global singleton TokenSayac döndür."""
    return _sayac
