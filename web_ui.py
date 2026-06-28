# -*- coding: utf-8 -*-
"""SHIM — desktop/dist/win-unpacked/resources/web_ui.py yönlendirir.

Desktop modülü doğrudan sys.modules['web_ui'] olarak yüklenir ki:
- monkeypatch.setattr("web_ui.X", ...) çalışsın
- inspect.getsource(web_ui) gerçek kodu dönsün
"""
import importlib.util as _ilu
import os as _os
import sys as _sys

_src = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                     'desktop', 'dist', 'win-unpacked', 'resources', 'web_ui.py')

if _os.path.exists(_src):
    _spec = _ilu.spec_from_file_location('web_ui', _src)
    _mod = _ilu.module_from_spec(_spec)
    _mod.__name__ = 'web_ui'
    _mod.__file__ = _src
    _mod.__package__ = ''
    _sys.modules['web_ui'] = _mod
    _spec.loader.exec_module(_mod)
    # Şimdiki modülün tüm isimlerini desktop modülüyle güncelle
    globals().update({k: v for k, v in vars(_mod).items() if not k.startswith('__')})
