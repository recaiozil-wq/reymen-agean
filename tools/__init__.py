# tools/__init__.py
"""tools — Tum tool cagrilerini executor uzerinden yonetir.

Dis kod `safe_execute` kullanarak hem guardrails hem de
executor katmanindan gecen guvenli cagri yapabilir.
"""

from tools.tool_executor import execute_tool
from tools.tool_guardrails import guard_check, path_safety, command_safety
from tools.tool_dispatch_helpers import (
    validate_params,
    coerce_types,
    filter_sensitive_params,
)


def safe_execute(name: str, args: dict, context: dict | None = None,
                 timeout_s: int = 30) -> dict:
    """Guvenlik kontrollu tool calistirici.

    Siralama:
      1. guard_check  — path/komut/yetki filtresi
      2. execute_tool — retry + timeout calistirma motoru

    Args:
        name: Tool modul adi (tools/ icinde).
        args: Tool parametreleri.
        context: Guvenlik baglami ({'yetki': 'admin'|'normal'}).
        timeout_s: Her deneme icin zaman asimi saniyesi.

    Returns:
        dict: {'ok': bool, 'result': Any, 'error': str|None, 'attempts': int}
    """
    izin, neden = guard_check(name, args, context or {})
    if not izin:
        return {"ok": False, "result": None, "error": neden, "attempts": 0}
    return execute_tool(name, args, timeout_s)


__all__ = [
    "safe_execute",
    "execute_tool",
    "guard_check",
    "path_safety",
    "command_safety",
    "validate_params",
    "coerce_types",
    "filter_sensitive_params",
]
