# -*- coding: utf-8 -*-
"""
plugins/__init__.py — ReYMeN Plugin Sistemi Merkezi API.

Bu modül tüm plugin altyapısını dışa aktarır:
  - PluginYukleyici  → plugin_loader.py (yükleme motoru)
  - PluginYoneticisi → plugin_manager.py (yönetim CLI)
  - PluginManifest   → plugin_manager.py (meta veri)

Kullanim:
    from plugins import PluginYukleyici, PluginYoneticisi
    yukleyici = PluginYukleyici()
    yukleyici.hepsini_yukle()
"""
from __future__ import annotations

import sys
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

PLUGIN_DIZIN = Path(__file__).parent

# ── Ana ihracat ─────────────────────────────────────────────────────────────

# plugin_loader — PluginYukleyici
try:
    from plugin_loader import PluginYukleyici
except ImportError as e:
    PluginYukleyici = None  # type: ignore
    logger.debug("plugin_loader mevcut degil: %s", e)

# plugin_manager — PluginYoneticisi, PluginManifest
try:
    from plugin_manager import PluginYoneticisi, PluginManifest
except ImportError as e:
    PluginYoneticisi = None  # type: ignore
    PluginManifest = None  # type: ignore
    logger.debug("plugin_manager mevcut degil: %s", e)

# ── Otomatik yukleme (plugins/ altindaki tum alt paketleri gorunur yap) ─────

def _auto_import_subpackages() -> None:
    """Tum plugins.* alt paketlerini sys.modules'e ekle ve attribute olarak set et."""
    _parent = sys.modules.get('plugins')
    if _parent is None:
        return
    for _mod_name in list(sys.modules.keys()):
        if _mod_name.startswith('plugins.') and '.' not in _mod_name[len('plugins.'):]:
            _pkg = _mod_name[len('plugins.'):]
            if not hasattr(_parent, _pkg):
                setattr(_parent, _pkg, sys.modules[_mod_name])

# Bootstrap: PluginYukleyici ile tum pluginleri yukle
yukleyici: PluginYukleyici | None = None
yuklenen_pluginler: list[str] = []

if PluginYukleyici is not None:
    try:
        yukleyici = PluginYukleyici(dizin=PLUGIN_DIZIN)
        yuklenen_pluginler = yukleyici.hepsini_yukle()
        logger.debug("plugins.__init__: %d plugin yuklendi", len(yuklenen_pluginler))
    except Exception as exc:
        logger.warning("plugins.__init__ otomatik yukleme hatasi: %s", exc)

# Alt paketleri gorunur yap
_auto_import_subpackages()

__all__ = [
    "PluginYukleyici",
    "PluginYoneticisi",
    "PluginManifest",
    "yukleyici",
    "yuklenen_pluginler",
    "PLUGIN_DIZIN",
]
