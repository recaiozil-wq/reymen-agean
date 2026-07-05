# -*- coding: utf-8 -*-
"""Session lifecycle yonetimi — acma, kapatma, kaydetme.

conversation_setup.py (session acma) + turn_finalizer.py (session kapatma)
arasindaki ortak mantigi tek dosyada toplar.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("conversation_loop")


def session_ac(
    task_id: str,
    hedef: str,
    provider: Optional[str] = None,
    baglam: Optional[dict] = None,
    *,
    session_storage_cls=None,
    beyin_model: Optional[str] = None,
    hook_oturum_baslat=None,
    plugin_hook_cagir=None,
) -> tuple[Optional[Any], Optional[str]]:
    """Session ac.

    Args:
        task_id: Gorev ID.
        hedef: Kullanici hedefi.
        provider: Provider adi.
        baglam: Opsiyonel baglam dicti.
        session_storage_cls: AdvancedSessionStorage sinifi (None = session devre disi).
        beyin_model: Model adi.
        hook_oturum_baslat: Hook callback (opsiyonel).
        plugin_hook_cagir: Plugin hook callback (opsiyonel).

    Returns:
        (_storage, session_id) ikilisi. Session yoksa (None, None).
    """
    if not session_storage_cls:
        return None, None

    try:
        db_yol = str(
            Path(__file__).resolve().parent.parent.parent.parent / "merkez_db" / "session.db"
        )
        storage = session_storage_cls(db_yol)
        session_id = storage.session_baslat(
            source="run_conversation",
            model=beyin_model,
            system_prompt=hedef[:500] if hedef else None,
            billing_provider=provider,
        )
        logger.info("[%s] Session acildi: %s", task_id, session_id)

        if hook_oturum_baslat is not None:
            try:
                hook_oturum_baslat(
                    session_id=session_id, task_id=task_id, agent_adi="reymen"
                )
            except Exception:
                logger.warning("[hook] oturum_baslat sessiz_except")

        if plugin_hook_cagir is not None:
            try:
                plugin_hook_cagir(
                    "on_session_start",
                    session_id=session_id or task_id,
                    user_id=baglam.get("user_id", "unknown") if baglam else "unknown",
                )
            except Exception:
                logger.warning("[plugin] on_session_start sessiz_except")

        return storage, session_id

    except Exception as se:
        logger.warning("[%s] Session baslatma hatasi: %s", task_id, se)
        return None, None


def session_kapat(
    storage: Any,
    session_id: Optional[str],
    yanit: Optional[str] = None,
    basarili: bool = False,
) -> bool:
    """Session kapat.

    Args:
        storage: AdvancedSessionStorage instance (None ise sessizce gecer).
        session_id: Session ID (None ise sessizce gecer).
        yanit: Son yanit metni (opsiyonel).
        basarili: Basarili durumu.

    Returns:
        True basarili, False hata veya session yok.
    """
    if not storage or not session_id:
        return False

    try:
        storage.session_bitir(
            session_id,
            yanit[:500] if yanit else None,
            basarili=basarili,
        )
        return True
    except Exception as e:
        logger.warning("Session bitirme hatasi: %s", e)
        return False
