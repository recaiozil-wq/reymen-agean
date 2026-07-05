"""ReYMeN tools.clarify_tool shim â€” ReYMeN clarify fonksiyonlarÄ±nÄ± ReYMeN'e yönlendirir."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def run(
    soru: str,
    secenekler: Optional[List[str]] = None,
    varsayilan: str = "",
) -> str:
    """ReYMeN clarify_tool.run â€” ReYMeN için basit implementasyon.

    KullanÄ±cÄ±ya soru sorar ve cevabÄ± döndürür.
    Telegram bot için direkt input() kullanÄ±r.
    """
    if secenekler:
        secenek_metni = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(secenekler))
        prompt = f"{soru}\n{secenek_metni}\n"
        if varsayilan:
            prompt += f"VarsayÄ±lan: {varsayilan}\n"
        prompt += "CevabÄ±nÄ±z: "
    else:
        prompt = f"{soru}: "
        if varsayilan:
            prompt += f" (varsayÄ±lan: {varsayilan}) "

    try:
        cevap = input(prompt).strip()
        if not cevap and varsayilan:
            return varsayilan
        return cevap
    except (EOFError, KeyboardInterrupt):
        return varsayilan or "[iptal]"


def ask_user(
    question: str,
    choices: Optional[List[str]] = None,
    default: Optional[str] = None,
) -> Dict[str, Any]:
    """ReYMeN ask_user â€” ReYMeN için basit implementasyon."""
    result = run(question, choices, default or "")
    return {"result": result, "cancelled": result == "[iptal]"}
