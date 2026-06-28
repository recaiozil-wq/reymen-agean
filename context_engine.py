# -*- coding: utf-8 -*-
"""SHIM — agent/context_engine.py yönlendirir + ReYMeN ContextEngine"""
from agent.context_engine import *  # noqa: F401, F403

_ONEMLI_ANAHTAR = [
    "hedef", "hata", "api", "dosya", "proje", "görev", "key",
    "şifre", "url", "yol", "kisitlama", "not",
    "onemli", "dikkat", "uyari", "kritik", "zorunlu", "gerekli",
]

_OZETLE_ESIGI = 4       # Bu sayıdan fazla mesaj varsa özet yapılır
_SON_KORU = 3           # Son bu kadar mesaj özete dahil edilmez
_OZET_MAX_KISA = 80     # Her parça en fazla bu kadar karakter


class ContextEngine:
    """ReYMeN bağlam yöneticisi."""

    def __init__(self, max_token: int = 8000, **kwargs):
        self.max_token = max_token
        self.onemli_anahtarlar = _ONEMLI_ANAHTAR

    # ── token hesaplama ──────────────────────────────────────────────────────

    def _token_hesapla(self, gecmis: list, ek_metin: str = "") -> int:
        toplam = sum(
            len(str(g.get("icerik") or g.get("content") or ""))
            for g in gecmis
        )
        toplam += len(str(ek_metin))
        return toplam // 4

    def token_limit_asti_mi(self, gecmis: list, ek_metin: str = "") -> bool:
        return self._token_hesapla(gecmis, ek_metin) > self.max_token

    # ── özetleme ────────────────────────────────────────────────────────────

    def _ozetle(self, gecmis: list) -> str:
        if len(gecmis) <= _OZETLE_ESIGI:
            return ""
        # Son _SON_KORU mesajı koru, geri kalanı özetle
        eski = gecmis[:-_SON_KORU] if len(gecmis) > _SON_KORU else []
        if not eski:
            return ""
        parcalar = []
        for g in eski:
            icerik = str(g.get("icerik") or g.get("content") or "")
            parcalar.append(icerik[:_OZET_MAX_KISA])
        return " | ".join(parcalar)

    def ozetle(self, gecmis: list) -> str:
        return self._ozetle(gecmis)

    # ── önemli bilgi ayıklama ────────────────────────────────────────────────

    def _onemli_bilgileri_ayikla(self, gecmis: list) -> str:
        if not gecmis:
            return ""
        bulunanlar = []
        for g in gecmis:
            icerik = str(g.get("icerik") or g.get("content") or "").lower()
            for anahtar in _ONEMLI_ANAHTAR:
                if anahtar.lower() in icerik:
                    bulunanlar.append(icerik[:100])
                    break
        return " | ".join(bulunanlar)

    # ── bağlam hazırlama ─────────────────────────────────────────────────────

    def baglam_hazirla(self, gecmis: list, yeni_mesaj: str) -> dict:
        ozet = self._ozetle(gecmis)
        onemli = self._onemli_bilgileri_ayikla(gecmis)
        token_tahmini = self._token_hesapla(gecmis, yeni_mesaj)
        return {
            "ozet": ozet,
            "onemli": onemli,
            "yeni_mesaj": yeni_mesaj,
            "token_tahmini": token_tahmini,
        }
