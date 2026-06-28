# -*- coding: utf-8 -*-
# SHIM — reymen/ag/acp_server.py yonlendirir
from reymen.ag.acp_server import *  # noqa: F401, F403
from reymen.ag.acp_server import (  # noqa: F401 — test ve dogrudan erisim icin
    _json_safe,
    _zaman_damgasi,
    _acp_baslat,
)
import sys as _sys

_ACP_SERVER_INSTANCE = None


def _acp_durum() -> str:
    """Shim wrapper: tests bu modüldeki _ACP_SERVER_INSTANCE'ı kontrol edebilir."""
    inst = _sys.modules[__name__].__dict__.get('_ACP_SERVER_INSTANCE')
    if inst is None:
        return "[ACP] Sunucu baslatilmadi."
    return (
        f"[ACP] Durum: {'calisiyor' if inst.running else 'durduruldu'}\n"
        f"  Transport: {inst.transport}\n"
        f"  Baslatildi: {getattr(inst, '_start_time', '?')}\n"
        f"  Initialized: {inst._initialized}"
    )
