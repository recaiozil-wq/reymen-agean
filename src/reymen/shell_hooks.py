# -*- coding: utf-8 -*-
"""Shell hook'ları — terminal komutlari oncesi/sonrasi.

Hermes agent/shell_hooks.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

_pre_hooks = []
_post_hooks = []

def pre_hook_ekle(fn) -> None:
    _pre_hooks.append(fn)

def post_hook_ekle(fn) -> None:
    _post_hooks.append(fn)

def pre_hook_calistir(komut: str) -> str:
    for hook in _pre_hooks:
        try:
            komut = hook(komut) or komut
        except Exception:
            continue
    return komut

def post_hook_calistir(komut: str, cikti: str) -> str:
    for hook in _post_hooks:
        try:
            cikti = hook(komut, cikti) or cikti
        except Exception:
            continue
    return cikti
