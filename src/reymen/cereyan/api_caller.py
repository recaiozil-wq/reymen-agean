# -*- coding: utf-8 -*-
"""API cagrisi wrapper — retry + timeout + stream handling + fallback.

ReYMeN'e ozgu, Hermes bagimliligi YOK.
conversation_loop_v2.py'den extract edilmistir.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

logger = logging.getLogger("conversation_loop")


def api_cagrisi_yap(
    provider_fn: Any,
    api_kwargs: dict,
    *,
    max_retry: int = 3,
    base_delay: float = 2.0,
    stream: bool = False,
) -> dict:
    """OpenAI-uyumlu API cagrisi yap, retry + timeout ile.

    Args:
        provider_fn: OpenAI-compatible chat.completions.create benzeri fonksiyon.
        api_kwargs: API parametreleri (model, messages, tools, vs.)
        max_retry: Maksimum retry denemesi.
        base_delay: Retry arasi taban bekleme (exponential backoff).
        stream: Streaming aktif mi.

    Returns:
        {"basarili": bool, "yanit": Any, "hata": Optional[str], "deneme": int}
    """
    from reymen.cereyan.retry_utils import jittered_backoff

    for deneme in range(1, max_retry + 1):
        try:
            baslama = time.time()
            if stream:
                yanit = provider_fn(**api_kwargs)
            else:
                yanit = provider_fn(**api_kwargs)
            sure = time.time() - baslama
            logger.debug("API cagrisi basarili (%d. deneme, %.2fs)", deneme, sure)
            return {"basarili": True, "yanit": yanit, "hata": None, "deneme": deneme}
        except Exception as e:
            hata_str = str(e)
            logger.warning("API cagrisi hatasi (%d/%d): %s", deneme, max_retry, hata_str[:100])

            # 401/402/403 -> retry yapma, direkt hata
            if any(k in hata_str for k in ("401", "402", "403", "Unauthorized", "Forbidden")):
                return {"basarili": False, "yanit": None, "hata": hata_str, "deneme": deneme}

            # Son denemeyse bekleme
            if deneme < max_retry:
                bekle = jittered_backoff(deneme, base_delay=base_delay)
                logger.debug("Retry bekleniyor: %.2fs", bekle)
                time.sleep(bekle)

    return {"basarili": False, "yanit": None, "hata": "Max retry asildi", "deneme": max_retry}


def direct_api_call(
    mesajlar: list,
    tools_bos: bool = False,
    session_id: Optional[str] = None,
    *,
    context_budget_chars: int = 300000,
    beyin=None,
) -> Optional[dict]:
    """Dogrudan OpenAI SDK ile API cagrisi (beyin yoksa fallback)."""
    import time as _time

    toplam_chars = sum(len(str(m.get("content", ""))) for m in mesajlar)
    if toplam_chars > context_budget_chars:
        kesilecek = toplam_chars - context_budget_chars
        _kesildi = 0
        for i in range(len(mesajlar) - 2, -1, -1):
            if _kesildi >= kesilecek:
                break
            m = mesajlar[i]
            if m.get("role") in ("assistant", "tool", "user"):
                icerik = str(m.get("content", ""))
                if len(icerik) > 100:
                    yeni = icerik[:50] + "... [TRUNCATED] ..." + icerik[-50:]
                    _kesildi += len(icerik) - len(yeni)
                    mesajlar[i]["content"] = yeni
        logger.warning(
            "[ContextBudget] %d chars -> %d char kesildi",
            toplam_chars, _kesildi,
        )

    # Gatekeeper
    try:
        son_kullanici_msg = ""
        for m in reversed(mesajlar):
            if m.get("role") == "user":
                son_kullanici_msg = m.get("content", "")
                break
        from reymen.guvenlik.agent_gatekeeper import (
            response_makes_numeric_claim, run_gatekept_turn,
        )
        if son_kullanici_msg and response_makes_numeric_claim(son_kullanici_msg):
            gk_messages = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in mesajlar]
            gk_yanit = run_gatekept_turn(
                session_id=session_id or "gatekeeper-unknown",
                messages=gk_messages,
            )
            if gk_yanit:
                return {"choices": [{"message": {"role": "assistant", "content": gk_yanit}}]}
    except Exception:
        pass

    # Beyin varsa onu kullan
    if beyin is not None:
        try:
            return beyin.uret(mesajlar)
        except Exception as e:
            logger.warning("Beyin hatasi: %s", e)

    # DeepSeek API
    try:
        from openai import OpenAI
        import os as _os

        client = OpenAI(
            api_key=_os.environ.get("DEEPSEEK_API_KEY", ""),
            base_url="https://api.deepseek.com",
        )
        api_kwargs = {
            "model": "deepseek-v4-flash",
            "messages": mesajlar,
            "max_tokens": 4096,
        }
        if not tools_bos:
            api_kwargs["frequency_penalty"] = 0.8
        r = client.chat.completions.create(**api_kwargs)
        secim = r.choices[0]
        if hasattr(secim.message, "tool_calls") and secim.message.tool_calls:
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": secim.message.content or "",
                        "tool_calls": [
                            {"id": tc.id, "type": "function",
                             "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                            for tc in secim.message.tool_calls
                        ],
                    }
                }]
            }
        return {
            "choices": [{"message": {"role": "assistant", "content": secim.message.content or ""}}]
        }
    except Exception as e:
        logger.warning("DeepSeek API hatasi: %s", e)
        return None
