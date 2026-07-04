"""Test: reymen/sistem/plugin_loader.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestPluginLoader:
    def test_import(self):
        from reymen.sistem.plugin_loader import PluginYukleyici

        assert PluginYukleyici is not None

    def test_olustur(self):
        from reymen.sistem.plugin_loader import PluginYukleyici

        py = PluginYukleyici(dizin=str(PROJE_KOK / "reymen" / "sistem" / "plugins"))
        assert py is not None
