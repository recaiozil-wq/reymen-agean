# -*- coding: utf-8 -*-
"""VarsayÄ±lan hook callback fonksiyonlarÄ± â€” motor ve dÃ¶ngÃ¼ olaylarÄ±nÄ± dinler.

Her fonksiyon ``hook_dispatcher.hook_kaydet()`` ile kaydedilir.
Ortak imza: fn(olay: str, **data) -> None
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)

# â”€â”€ Metrik toplama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_olay_sayaci: dict[str, int] = defaultdict(int)
_olay_suresi: dict[str, float] = defaultdict(float)
_son_olay_zamani: dict[str, float] = {}
_baslangic = time.time()


def _log_cb(olay: str, **data: Any) -> None:
    """TÃ¼m hook'larÄ± DEBUG seviyesinde logla. Hata ayÄ±klama iÃ§in."""
    logger.debug("[HOOK] %s -> %s", olay, {k: str(v)[:80] for k, v in data.items()})


def _metrik_cb(olay: str, **data: Any) -> None:
    """Hook olaylarÄ±nÄ± say ve sÃ¼re tut. Hata ayÄ±klama/metrik iÃ§in."""
    _olay_sayaci[olay] += 1
    _son_olay_zamani[olay] = time.time()


def _session_izleme_cb(olay: str, **data: Any) -> None:
    """Session baÅŸlangÄ±Ã§/bitiÅŸ olaylarÄ±nÄ± logla."""
    if olay == "on_session_start":
        session_id = data.get("session_id", "?")
        logger.info(
            "[HOOK] Session baÅŸladÄ±: %s (task=%s)", session_id, data.get("task_id", "?")
        )
    elif olay == "on_session_end":
        session_id = data.get("session_id", "?")
        basarili = data.get("basarili", False)
        logger.info(
            "[HOOK] Session bitti: %s | basarili=%s | tur=%s",
            session_id,
            basarili,
            data.get("tur_sayisi", "?"),
        )


def _hata_izleme_cb(olay: str, **data: Any) -> None:
    """Hata olaylarÄ±nÄ± WARNING seviyesinde logla. Kritik hatalarÄ± ayÄ±r."""
    if olay == "on_error":
        hata = data.get("hata", "?")
        baglam = data.get("olay_baglami", "")
        task_id = data.get("task_id", "?")
        logger.warning(
            "[HOOK] HATA task=%s | baglam=%s | hata=%s",
            task_id,
            baglam,
            str(hata)[:150],
        )


def _tool_izleme_cb(olay: str, **data: Any) -> None:
    """Tool Ã§aÄŸrÄ±larÄ±nÄ± izle. Hata durumunda uyar."""
    if olay == "on_tool_call":
        arac = data.get("arac_adi", "?")
        logger.debug("[HOOK] Tool Ã§aÄŸrÄ±sÄ±: %s", arac)
    elif olay == "on_tool_result":
        arac = data.get("arac_adi", "?")
        sure = data.get("sure_sn", 0)
        if sure > 10:
            logger.info("[HOOK] YavaÅŸ tool: %s (%.1fs)", arac, sure)


def _context_izleme_cb(olay: str, **data: Any) -> None:
    """Context sÄ±kÄ±ÅŸtÄ±rma olaylarÄ±nÄ± izle."""
    if olay == "on_context_compress":
        mesaj = data.get("mesaj_sayisi", "?")
        token = data.get("token_tahmini", "?")
        logger.info("[HOOK] Context sÄ±kÄ±ÅŸtÄ±rma: %s mesaj, ~%s token", mesaj, token)


# â”€â”€ TÃ¼m varsayÄ±lan callback'leri kaydet â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def varsayilan_hooklari_kaydet(hook_sistemi: Any = None) -> None:
    """TÃ¼m varsayÄ±lan hook callback'lerini kaydet.

    Args:
        hook_sistemi: Motor._hooks (AsynchronousHookDispatcher) veya None.
                      None ise cereyan.hook_dispatcher.hook_kaydet kullanÄ±lÄ±r.
    """
    from reymen.cereyan.hook_dispatcher import hook_kaydet as _kaydet_fonk

    callbacks = [
        ("on_session_start", _session_izleme_cb),
        ("on_session_start", _metrik_cb),
        ("on_session_end", _session_izleme_cb),
        ("on_session_end", _metrik_cb),
        ("on_turn_start", _metrik_cb),
        ("on_turn_end", _metrik_cb),
        ("on_tool_call", _tool_izleme_cb),
        ("on_tool_call", _metrik_cb),
        ("on_tool_result", _tool_izleme_cb),
        ("on_tool_result", _metrik_cb),
        ("on_error", _hata_izleme_cb),
        ("on_error", _metrik_cb),
        ("on_context_compress", _context_izleme_cb),
    ]

    kaydet = hook_sistemi.kaydet if hook_sistemi else _kaydet_fonk

    for olay, cb in callbacks:
        try:
            kaydet(olay, cb)
        except Exception as e:
            logger.warning("[HOOK] Kayit hatasi %s/%s: %s", olay, cb.__name__, e)

    logger.info("[HOOK] %d varsayÄ±lan hook callback kaydedildi", len(callbacks))


# â”€â”€ Metrik gÃ¶rÃ¼ntÃ¼leme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def metrik_raporu() -> dict:
    """Hook metriklerini dÃ¶ndÃ¼r: olay bazlÄ± sayÄ± ve sÃ¼re."""
    return {
        "olay_sayaci": dict(_olay_sayaci),
        "calisma_suresi": round(time.time() - _baslangic, 1),
        "toplam_olay": sum(_olay_sayaci.values()),
    }
