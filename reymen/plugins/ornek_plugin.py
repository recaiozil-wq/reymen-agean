# -*- coding: utf-8 -*-
"""Örnek ReYMeN Plugin — Tüm lifecycle hook'larını gösterir.

Kullanım:
    1. config.yaml'da plugins.enabled: true olduğundan emin ol
    2. Plugin otomatik yüklenir
    3. Her hook çağrıldığında log'a mesaj yazar
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

from reymen.plugin import PluginBase

logger = logging.getLogger(__name__)


class OrnekPlugin(PluginBase):
    """Tüm hook'ları gösteren örnek plugin.

    Her hook çağrıldığında log'da [Plugin:ornek] etiketiyle mesaj görünür.
    """

    name = "ornek_plugin"
    version = "1.0.0"

    # ── Lifecycle ──────────────────────────────────────────────────────

    def on_load(self) -> None:
        """Plugin yüklendiğinde çağrılır."""
        logger.info("[Plugin:ornek] on_load() — Plugin yuklendi. Hazirlik yapiliyor...")

    def on_unload(self) -> None:
        """Plugin kaldırıldığında çağrılır."""
        logger.info("[Plugin:ornek] on_unload() — Plugin kaldiriliyor, kaynaklar temizleniyor...")

    # ── Session hooks ──────────────────────────────────────────────────

    def on_session_start(self, session_id: str, user_id: str) -> None:
        """Yeni oturum başladığında çağrılır.

        Örnek: oturum başlangıcını loglama.
        """
        logger.info(
            "[Plugin:ornek] on_session_start() — session=%s, user=%s",
            session_id, user_id,
        )

    def on_session_end(self, session_id: str, reason: str) -> None:
        """Oturum sonlandığında çağrılır.

        Örnek: oturum istatistiklerini loglama.
        """
        logger.info(
            "[Plugin:ornek] on_session_end() — session=%s, reason=%s",
            session_id, reason,
        )

    # ── Message hooks ──────────────────────────────────────────────────

    def on_message(self, message: str, context: dict) -> str:
        """Kullanıcı mesajı işlenmeden hemen önce çağrılır.

        Örnek: mesaj loglama. Mesaj değiştirilmez.
        """
        logger.info(
            "[Plugin:ornek] on_message() — mesaj: %.80s, context_keys: %s",
            message, list(context.keys()),
        )
        # Mesajı değiştirmeden döndür
        return message

    # ── LLM hooks ──────────────────────────────────────────────────────

    def pre_llm_call(
        self, messages: List[dict], context: dict
    ) -> Tuple[List[dict], dict]:
        """LLM çağrısı öncesi mesajları değiştirme.

        Örnek: mesaj sayısını ve son mesajı logla.
        """
        logger.info(
            "[Plugin:ornek] pre_llm_call() — %d mesaj, son rol: %s",
            len(messages),
            messages[-1].get("role", "?") if messages else "?",
        )
        # Değişiklik yapmadan döndür
        return messages, context

    def post_llm_call(self, response: dict, context: dict) -> Dict[str, Any]:
        """LLM yanıtını işleme.

        Örnek: yanıt uzunluğunu logla.
        """
        icerik = response.get("content", "") or ""
        tool_calls = response.get("tool_calls", [])
        logger.info(
            "[Plugin:ornek] post_llm_call() — content=%d chars, tool_calls=%d",
            len(icerik), len(tool_calls),
        )
        # Yanıtı değiştirmeden döndür
        return response
