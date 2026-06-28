#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reymen_ajan.py — ReYMeN Bilgi Ajanı aracı.

ReYMeN motor.py üzerinden çağrılabilir.
Arama -> Çekme -> Filtreleme -> Özetleme -> Kaydetme
"""

import asyncio
import os
import sys
from pathlib import Path

# ReYMeN modül yolunu ekle
_REYMEN_DIR = Path(__file__).parent.parent / "ReYMeN_mirror"
if _REYMEN_DIR.exists():
    sys.path.insert(0, str(_REYMEN_DIR))

TOOL_META = {
    "aciklama": (
        "ReYMeN Bilgi Ajanı — web'den bilgi toplar, filtreler, özetler."
        " Kullanım: HERMES_ARA(sorgu='yapay zeka haberleri')"
    ),
    "kategori": "web",
    "parametreler": [
        {
            "ad": "sorgu",
            "tip": "str",
            "zorunlu": True,
            "aciklama": "Araştırma sorgusu (Türkçe veya İngilizce)",
        },
        {
            "ad": "max_kaynak",
            "tip": "int",
            "zorunlu": False,
            "varsayilan": 5,
            "aciklama": "Kullanılacak maksimum kaynak sayısı (1-10)",
        },
    ],
    "ornek": 'HERMES_ARA(sorgu="son yapay zeka gelişmeleri")',
}


def check_fn() -> bool:
    """ReYMeN ajan kullanılabilir mi?"""
    return _REYMEN_DIR.exists()


def run(sorgu: str, max_kaynak: int = 5) -> dict:
    """
    ReYMeN Bilgi Ajanı'nı çalıştır.

    Args:
        sorgu: Araştırma sorgusu
        max_kaynak: Kullanılacak maksimum kaynak (1-10)

    Returns:
        {"durum", "ozet", "kaynaklar", "kaynak_sayisi", "hata"}
    """
    try:
        from core.orchestrator import ReYMeNOrchestrator
    except ImportError:
        return {
            "durum": "hata",
            "hata": (
                "ReYMeN modülleri bulunamadı. "
                f"Beklenen dizin: {_REYMEN_DIR}"
            ),
        }

    async def _async_run() -> dict:
        orchestrator = ReYMeNOrchestrator(max_concurrent=5)

        # Pipeline'i çalıştır
        result = await orchestrator.process_query(sorgu)

        if not result:
            return {
                "durum": "basarisiz",
                "sorgu": sorgu,
                "ozet": "İçerik bulunamadı veya işlenemedi.",
                "kaynaklar": [],
                "kaynak_sayisi": 0,
            }

        return {
            "durum": "basarili",
            "sorgu": sorgu,
            "ozet": result.get("summary", ""),
            "kaynaklar": result.get("sources", []),
            "kaynak_sayisi": result.get("source_count", 0),
        }

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        sonuc = loop.run_until_complete(_async_run())
        loop.close()
        return sonuc
    except Exception as e:
        return {
            "durum": "hata",
            "sorgu": sorgu,
            "hata": str(e),
        }
