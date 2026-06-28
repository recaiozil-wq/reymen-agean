# -*- coding: utf-8 -*-
"""
tools/session_search_tool.py — SESSION_ARA aracı.

Hermes'teki session_search aracının ReYMeN karşılığı: konuşma geçmişinde
(session_messages_fts) FTS5 tam metin arama yapar, sonuçları session
bazında gruplar ve LLM'in okuyabileceği bir özet metin döndürür.

motor.py._plugin_moduller_yukle() bu modülü otomatik import eder ve
modul seviyesindeki motor_kaydet(motor) fonksiyonunu çağırır.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from reymen.hafiza.session_db import get_storage
except ImportError:
    get_storage = None  # session_db henuz bu yola tasinmadiysa sessiz gec


def _limit_coz(limit) -> int:
    try:
        n = int(limit)
        return max(1, min(n, 50))
    except (TypeError, ValueError):
        return 10


def _formatla(sonuclar: list, sorgu: str) -> str:
    if not sonuclar:
        return f"[SESSION_ARA] '{sorgu}' için sonuç bulunamadı."

    parcalar = [f"[SESSION_ARA] '{sorgu}' için {len(sonuclar)} session bulundu:\n"]
    for i, s in enumerate(sonuclar, 1):
        parcalar.append(
            f"{i}. session_id={s['session_id']}  model={s.get('model') or '?'}  "
            f"eşleşen_mesaj={s['eslesen_mesaj_sayisi']}"
        )
        parcalar.append(f"   özet: {s['ozet']}")
        for m in s.get("ilgili_mesajlar", []):
            parcalar.append(f"   - [{m['rol']}] {m['icerik']}")
        parcalar.append("")
    return "\n".join(parcalar).rstrip()


def session_search(sorgu: str = "", limit: str = "10", tarih_araligi: str = "") -> str:
    """SESSION_ARA(sorgu, limit, tarih_araligi) — konuşma geçmişinde FTS5 arama.

    Args:
        sorgu:         Aranacak kelime/ifade (FTS5 MATCH sözdizimi geçerlidir).
        limit:         Döndürülecek maksimum session sayısı (varsayılan 10).
        tarih_araligi: Opsiyonel — "7g" (son 7 gün), "24s" (son 24 saat),
                       "bugun", veya "YYYY-MM-DD..YYYY-MM-DD".
    """
    if get_storage is None:
        return "[SESSION_ARA] Hata: reymen.hafiza.session_db modülü bulunamadı."
    if not sorgu or not sorgu.strip():
        return "[SESSION_ARA] Hata: 'sorgu' parametresi boş olamaz."

    try:
        storage = get_storage()
        sonuclar = storage.session_search(
            sorgu.strip(), limit=_limit_coz(limit), tarih_araligi=tarih_araligi or None
        )
        return _formatla(sonuclar, sorgu.strip())
    except Exception as e:
        logger.error("[SESSION_ARA] hata: %s", e)
        return f"[SESSION_ARA] Hata: {e}"


def motor_kaydet(motor) -> None:
    """motor._plugin_moduller_yukle() tarafından otomatik çağrılır."""
    motor._plugin_arac_kaydet(
        "SESSION_ARA",
        session_search,
        "Konuşma geçmişinde (FTS5) tam metin arama yap. "
        "Parametreler: sorgu, limit, tarih_araligi (örn. '7g', 'bugun', "
        "'2026-06-01..2026-06-27').",
    )
