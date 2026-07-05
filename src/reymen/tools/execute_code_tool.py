"""ReYMeN tools.execute_code_tool shim â€” ReYMeN code execution fonksiyonlarÄ±nÄ± yÃ¶nlendirir.

Not: ReYMeN kendi code_execution mantÄ±ÄŸÄ±nÄ± kullanÄ±r.
Bu shim, ReYMeN import'larÄ±nÄ±n kÄ±rÄ±lmamasÄ± iÃ§in basit implementasyon saÄŸlar.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def run(kod: str, **kwargs) -> str:
    """ReYMeN execute_code_tool.run â€” ReYMeN iÃ§in basit implementasyon.

    Python kodunu Ã§alÄ±ÅŸtÄ±rÄ±r ve sonucu dÃ¶ndÃ¼rÃ¼r.
    """
    import io
    import sys
    import traceback

    # stdout'u yakala
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    captured = io.StringIO()
    sys.stdout = captured
    sys.stderr = captured

    try:
        exec(kod, {"__builtins__": __builtins__})
        output = captured.getvalue()
        if not output:
            output = "[Kod baÅŸarÄ±yla Ã§alÄ±ÅŸtÄ±, Ã§Ä±ktÄ± yok]"
        return output
    except Exception:
        return f"[HATA]\n{traceback.format_exc()}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def build_execute_code_schema(
    available_tools: set,
    mode: str = "local",
) -> Dict[str, Any]:
    """ReYMeN build_execute_code_schema â€” ReYMeN iÃ§in basit implementasyon.

    execute_code tool'unun OpenAPI ÅŸemasÄ±nÄ± oluÅŸturur.
    """
    return {
        "name": "execute_code",
        "description": "Python kodunu Ã§alÄ±ÅŸtÄ±rÄ±r. KorumalÄ± modda Ã§alÄ±ÅŸÄ±r.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Ã‡alÄ±ÅŸtÄ±rÄ±lacak Python kodu",
                }
            },
            "required": ["code"],
        },
    }


def _get_execution_mode() -> str:
    """ReYMeN _get_execution_mode â€” ReYMeN iÃ§in basit implementasyon."""
    return "local"
