# -*- coding: utf-8 -*-
"""reymen.plugin â€” Plugin sistemi (lifecycle hooks).

PluginBase:
    Tüm plugin'lerin türetmesi gereken temel sÄ±nÄ±f.
    Ä°steÄŸe baÄŸlÄ± hook metodlarÄ±:

        on_load()                     â€” plugin yüklendiÄŸinde
        on_unload()                   â€” plugin kaldÄ±rÄ±ldÄ±ÄŸÄ±nda
        on_session_start(session_id, user_id) â€” session baÅŸÄ±nda
        on_session_end(session_id, reason)    â€” session sonunda
        on_message(message, context)          â€” kullanÄ±cÄ± mesajÄ± geldiÄŸinde
        pre_llm_call(messages, context)       â€” LLM çaÄŸrÄ±sÄ± öncesi mesajlarÄ± deÄŸiÅŸtir
        post_llm_call(response, context)      â€” LLM yanÄ±tÄ± geldikten sonra iÅŸle
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PluginBase:
    """Tüm ReYMeN plugin'leri bu sÄ±nÄ±ftan türetilmelidir.

    Ã–zellikler:
        name (str):    Plugin adÄ± (zorunlu).
        version (str): Plugin versiyonu (zorunlu).

    Tüm hook metodlarÄ± *opsiyoneldir* â€” PluginBase varsayÄ±lan no-op
    implementasyon saÄŸlar, alt sÄ±nÄ±f sadece ihtiyacÄ± olanlarÄ± override eder.
    """

    name: str = "unnamed"
    version: str = "0.0.1"

    # â”€â”€ Lifecycle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def on_load(self) -> None:
        """Plugin yüklendiÄŸinde bir kere çaÄŸrÄ±lÄ±r."""
        pass

    def on_unload(self) -> None:
        """Plugin kaldÄ±rÄ±ldÄ±ÄŸÄ±nda bir kere çaÄŸrÄ±lÄ±r."""
        pass

    # â”€â”€ Session hooks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def on_session_start(self, session_id: str, user_id: str) -> None:
        """Yeni bir konuÅŸma oturumu baÅŸladÄ±ÄŸÄ±nda çaÄŸrÄ±lÄ±r."""
        pass

    def on_session_end(self, session_id: str, reason: str) -> None:
        """KonuÅŸma oturumu sonlandÄ±ÄŸÄ±nda çaÄŸrÄ±lÄ±r.

        Args:
            session_id: Oturum kimliÄŸi.
            reason:     Sonlanma sebebi (örn. "completed", "error", "cancelled").
        """
        pass

    # â”€â”€ Message hooks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def on_message(self, message: str, context: dict) -> str:
        """KullanÄ±cÄ± mesajÄ± iÅŸlenmeden hemen önce çaÄŸrÄ±lÄ±r.

        Dönen string mesajÄ±n yerine kullanÄ±lÄ±r. MesajÄ± deÄŸiÅŸtirmeden
        iletmek için orijinal *message* döndürülmelidir.
        """
        return message

    # â”€â”€ LLM hooks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def pre_llm_call(
        self, messages: List[dict], context: dict
    ) -> Tuple[List[dict], dict]:
        """LLM çaÄŸrÄ±sÄ±ndan hemen önce çaÄŸrÄ±lÄ±r.

        *messages* ve *context* üzerinde deÄŸiÅŸiklik yapÄ±p (messages, context)
        tuple'Ä± olarak döndürebilirsiniz.

        Args:
            messages: LLM'e gönderilecek mesaj listesi.
            context:  Plugin baÄŸlamÄ± (her plugin kendi anahtarÄ±nda saklanÄ±r).

        Returns:
            (messages, context) â€” deÄŸiÅŸtirilmiÅŸ veya orijinal halleri.
        """
        return messages, context

    def post_llm_call(self, response: dict, context: dict) -> Dict[str, Any]:
        """LLM yanÄ±tÄ± geldikten hemen sonra çaÄŸrÄ±lÄ±r.

        *response* dict'i üzerinde deÄŸiÅŸiklik yapÄ±p döndürebilirsiniz.

        Args:
            response: LLM'den gelen yanÄ±t dict'i.
            context:  Plugin baÄŸlamÄ±.

        Returns:
            DeÄŸiÅŸtirilmiÅŸ veya orijinal response dict'i.
        """
        return response


# â”€â”€ Re-export â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
__all__ = ["PluginBase"]
