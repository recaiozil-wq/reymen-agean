"""Test: reymen/sistem/plugin_manager.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestPlugin:
    def test_import(self):
        from reymen.sistem.plugin_manager import PluginManager

        assert PluginManager is not None

    def test_create(self):
        from reymen.sistem.plugin_manager import PluginManager

        pm = PluginManager()
        assert pm is not None
