# -*- coding: utf-8 -*-
"""reymen.plugin â€” Plugin sistemi (lifecycle hooks).

PluginBase:
    TÃ¼m plugin'lerin tÃ¼retmesi gereken temel sÄ±nÄ±f.
    Ä°steÄŸe baÄŸlÄ± hook metodlarÄ±:

        on_load()                     â€” plugin yÃ¼klendiÄŸinde
        on_unload()                   â€” plugin kaldÄ±rÄ±ldÄ±ÄŸÄ±nda
        on_session_start(session_id, user_id) â€” session baÅŸÄ±nda
        on_session_end(session_id, reason)    â€” session sonunda
        on_message(message, context)          â€” kullanÄ±cÄ± mesajÄ± geldiÄŸinde
        pre_llm_call(messages, context)       â€” LLM Ã§aÄŸrÄ±sÄ± Ã¶ncesi mesajlarÄ± deÄŸiÅŸtir
        post_llm_call(response, context)      â€” LLM yanÄ±tÄ± geldikten sonra iÅŸle
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PluginBase:
    """TÃ¼m ReYMeN plugin'leri bu sÄ±nÄ±ftan tÃ¼retilmelidir.

    Ã–zellikler:
        name (str):    Plugin adÄ± (zorunlu).
        version (str): Plugin versiyonu (zorunlu).

    TÃ¼m hook metodlarÄ± *opsiyoneldir* â€” PluginBase varsayÄ±lan no-op
    implementasyon saÄŸlar, alt sÄ±nÄ±f sadece ihtiyacÄ± olanlarÄ± override eder.
    """

    name: str = "unnamed"
    version: str = "0.0.1"

    # â”€â”€ Lifecycle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def on_load(self) -> None:
        """Plugin yÃ¼klendiÄŸinde bir kere Ã§aÄŸrÄ±lÄ±r."""
        pass

    def on_unload(self) -> None:
        """Plugin kaldÄ±rÄ±ldÄ±ÄŸÄ±nda bir kere Ã§aÄŸrÄ±lÄ±r."""
        pass

    # â”€â”€ Session hooks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def on_session_start(self, session_id: str, user_id: str) -> None:
        """Yeni bir konuÅŸma oturumu baÅŸladÄ±ÄŸÄ±nda Ã§aÄŸrÄ±lÄ±r."""
        pass

    def on_session_end(self, session_id: str, reason: str) -> None:
        """KonuÅŸma oturumu sonlandÄ±ÄŸÄ±nda Ã§aÄŸrÄ±lÄ±r.

        Args:
            session_id: Oturum kimliÄŸi.
            reason:     Sonlanma sebebi (Ã¶rn. "completed", "error", "cancelled").
        """
        pass

    # â”€â”€ Message hooks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def on_message(self, message: str, context: dict) -> str:
        """KullanÄ±cÄ± mesajÄ± iÅŸlenmeden hemen Ã¶nce Ã§aÄŸrÄ±lÄ±r.

        DÃ¶nen string mesajÄ±n yerine kullanÄ±lÄ±r. MesajÄ± deÄŸiÅŸtirmeden
        iletmek iÃ§in orijinal *message* dÃ¶ndÃ¼rÃ¼lmelidir.
        """
        return message

    # â”€â”€ LLM hooks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def pre_llm_call(
        self, messages: List[dict], context: dict
    ) -> Tuple[List[dict], dict]:
        """LLM Ã§aÄŸrÄ±sÄ±ndan hemen Ã¶nce Ã§aÄŸrÄ±lÄ±r.

        *messages* ve *context* Ã¼zerinde deÄŸiÅŸiklik yapÄ±p (messages, context)
        tuple'Ä± olarak dÃ¶ndÃ¼rebilirsiniz.

        Args:
            messages: LLM'e gÃ¶nderilecek mesaj listesi.
            context:  Plugin baÄŸlamÄ± (her plugin kendi anahtarÄ±nda saklanÄ±r).

        Returns:
            (messages, context) â€” deÄŸiÅŸtirilmiÅŸ veya orijinal halleri.
        """
        return messages, context

    def post_llm_call(self, response: dict, context: dict) -> Dict[str, Any]:
        """LLM yanÄ±tÄ± geldikten hemen sonra Ã§aÄŸrÄ±lÄ±r.

        *response* dict'i Ã¼zerinde deÄŸiÅŸiklik yapÄ±p dÃ¶ndÃ¼rebilirsiniz.

        Args:
            response: LLM'den gelen yanÄ±t dict'i.
            context:  Plugin baÄŸlamÄ±.

        Returns:
            DeÄŸiÅŸtirilmiÅŸ veya orijinal response dict'i.
        """
        return response


# â”€â”€ Re-export â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
__all__ = ["PluginBase"]
