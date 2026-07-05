# -*- coding: utf-8 -*-
"""Post-loop turn finalization for run_conversation.

ReYMeN versiyonu — Hermes agent/turn_finalizer.py'den adapte.
Hermes bagimliligi YOK, reymen'e ozgu.
"""
from __future__ import annotations

import logging

from reymen.cereyan.session_manager import session_kapat

logger = logging.getLogger("conversation_loop")


def finalize_turn(
    agent,  # ConversationLoop instance
    *,
    sonuc: dict,
    final_response,
    api_call_count,
    interrupted,
    failed,
    messages,
    effective_task_id,
    hedef,
    baslama,
):
    """Dongu sonu finalizasyonu ve sonuc dict'ini don.

    Args:
        agent: ConversationLoop instance'i
        sonuc: Mevcut sonuc dict'i (guncellenecek)
        final_response: Modelin son yaniti
        api_call_count: API cagrisi sayisi
        interrupted: Kullanici tarafindan durduruldu mu
        failed: Hata olustu mu
        messages: Mesaj listesi
        effective_task_id: Gorev ID
        hedef: Orijinal hedef
        baslama: Baslangic zaman damgasi

    Returns:
        Guncellenmis sonuc dict'i
    """
    # Budget exhaustion check
    if final_response is None and api_call_count >= agent.max_tur:
        sonuc["hata"] = "Budget exhausted"
        sonuc["basarili"] = False

    completed = (
        final_response is not None
        and api_call_count < agent.max_tur
        and not failed
    )

    # Build final result
    sonuc.update({
        "basarili": bool(final_response) and not failed,
        "yanit": final_response if not interrupted else None,
        "turlar": api_call_count,
        "sure": round(__import__("time").time() - baslama, 2),
        "tamamlandi": completed,
        "kesintiye_ugradi": interrupted,
        "hata": sonuc.get("hata"),
    })

    # Session kapat (session_manager'a devredildi)
    session_kapat(
        getattr(agent, "_storage", None),
        getattr(agent, "session_id", None),
        yanit=sonuc.get("yanit"),
        basarili=sonuc["basarili"],
    )

    # Diagnostics log
    _budget_used = getattr(agent, "_budget", None)
    _budget_str = f"{getattr(_budget_used, 'used', 0)}" if _budget_used else "N/A"
    _resp_len = len(final_response) if final_response else 0
    logger.info(
        "Turn ended: api_calls=%d/%d budget=%s response_len=%d basarili=%s",
        api_call_count, agent.max_tur, _budget_str, _resp_len, sonuc["basarili"],
    )

    # Clear interrupt state
    if interrupted:
        agent._iptal_istegi = False

    return sonuc
