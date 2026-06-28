# -*- coding: utf-8 -*-
"""context_tool.py — Token durumu ve context sıkıştırma."""

from __future__ import annotations
from typing import Any


_CTX: Any = None  # Lazy


def _get_ctx():
    global _CTX
    if _CTX is None:
        from context_manager import AdvancedContextCompressor
        _CTX = AdvancedContextCompressor()
    return _CTX


def run(eylem: str = "durum", agresif: bool = False) -> str:
    eylem = eylem.strip().lower()

    try:
        ctx = _get_ctx()
    except ImportError as e:
        return f"[Hata]: context_manager modülü yüklenemedi — {e}"

    # ── DURUM ────────────────────────────────────────
    if eylem == "durum":
        try:
            bilgi = "[Bilgi] Mesaj sayisi / token bilgisi bu surumde mevcut degil."
        except Exception as e:
            return f"[Hata]: Durum alınamadı — {e}"

        if isinstance(bilgi, dict):
            satirlar = ["[Token Durumu]"]
            for k, v in bilgi.items():
                satirlar.append(f"  {k}: {v}")
            return "\n".join(satirlar)
        return f"[Token Durumu]\n{bilgi}"

    # ── SIKISTIR ─────────────────────────────────────
    if eylem == "sikistir":
        try:
            sonuc = ctx.compress()
        except Exception as e:
            return f"[Hata]: Sıkıştırma başarısız — {e}"

        if isinstance(sonuc, dict):
            onceki = sonuc.get("onceki_token", "?")
            sonraki = sonuc.get("sonraki_token", "?")
            return (
                f"[Tamam] Context sıkıştırıldı.\n"
                f"  Önce : {onceki} token\n"
                f"  Sonra: {sonraki} token\n"
                f"  Kazanım: {sonuc.get('kazanim', '?')}"
            )
        return f"[Tamam] {sonuc}"

    return f"[Hata]: eylem 'durum' veya 'sikistir' olmalı, alındı: '{eylem}'"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet(
        "CONTEXT", run, "Token durumu göster / eski mesajları sıkıştır"
    )
