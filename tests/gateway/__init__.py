# -*- coding: utf-8 -*-
"""tests/gateway — ReYMeN_reference/gateway dizinine yönlendirir."""

__all__ = []
from pathlib import Path as _Path
import sys as _sys

# src/gateway gercek paketini kullan (tests/gateway'i degil)
_src_gw = _Path(__file__).resolve().parent.parent.parent / "src" / "gateway"
if _src_gw.is_dir():
    __path__ = [str(_src_gw)]
else:
    __path__ = [str(_Path(__file__).parent.parent / "ReYMeN_reference" / "gateway")]
