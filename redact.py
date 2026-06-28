# -*- coding: utf-8 -*-
# SHIM — reymen/guvenlik/redact.py yonlendirir
from reymen.guvenlik.redact import *  # noqa: F401, F403
from reymen.guvenlik.redact import tam_temizle  # noqa: F401

# Private name export — test patching için
import importlib as _imp_r, sys as _sys_r
_src_r = _imp_r.import_module('reymen.guvenlik.redact')
_sys_r.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src_r).items() if k.startswith('_') and not k.startswith('__')}
)
