# -*- coding: utf-8 -*-
"""Conversation setup — task_id, session acma, budget kurulum.

ReYMeN'e ozgu, Hermes bagimliligi YOK.
conversation_loop_v2.py'den extract edilmistir.
"""
from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("conversation_loop")


from reymen.cereyan.session_manager import session_ac


def setup_conversation(
    max_tur: int,
    hedef: str,
    provider: Optional[str] = None,
    baglam: Optional[dict] = None,
    *,
    session_active: bool = False,
    session_storage=None,
    beyin_model: Optional[str] = None,
    hook_oturum_baslat=None,
    plugin_hook_cagir=None,
    budget_olustur_fn=None,
    hook_tur_baslat=None,
    a2a_agent=None,
    cl_baslat=None,
) -> dict:
    """Konusma dongusu icin setup yap.

    Returns:
        dict: task_id, baslama, session_id, _storage, budget, sonuc, api_call_count
    """
    task_id = str(uuid.uuid4())[:8]
    if cl_baslat is not None:
        try:
            cl_baslat(task_id)
        except Exception:
            pass

    logger.info("[%s] run_conversation basladi: %.60s", task_id, hedef)
    baslama = time.time()

    sonuc: dict = {
        "task_id": task_id,
        "hedef": hedef,
        "basarili": False,
        "turlar": 0,
        "hata": None,
        "provider": provider,
        "yanit": None,
    }

    # Session ac (session_manager'a devredildi)
    _storage, session_id = session_ac(
        task_id, hedef, provider, baglam,
        session_storage_cls=session_storage if session_active else None,
        beyin_model=beyin_model,
        hook_oturum_baslat=hook_oturum_baslat,
        plugin_hook_cagir=plugin_hook_cagir,
    )
    if session_id:
        sonuc["session_id"] = session_id

    budget = budget_olustur_fn(hedef) if budget_olustur_fn else None

    if hook_tur_baslat is not None:
        try:
            hook_tur_baslat(tur=1, task_id=task_id, hedef=hedef[:100])
        except Exception:
            logger.warning("[hook] sessiz_except")

    # A2A mesaj kontrolu
    if a2a_agent is not None:
        try:
            a2a_msg = a2a_agent.receive(timeout=0.1)
            if a2a_msg is not None:
                logger.info(
                    "[%s] A2A mesaj alindi: sender=%s icerik=%.60s",
                    task_id, a2a_msg.sender, str(a2a_msg.content),
                )
        except Exception:
            pass

    return {
        "task_id": task_id,
        "baslama": baslama,
        "session_id": session_id,
        "_storage": _storage,
        "budget": budget,
        "sonuc": sonuc,
        "api_call_count": 0,
    }
