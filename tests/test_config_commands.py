"""Test: reymen/sistem/cli_commands/config_commands.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestConfigCommands:
    def test_import(self):
        import reymen.sistem.cli_commands.config_commands as m

        assert m is not None
