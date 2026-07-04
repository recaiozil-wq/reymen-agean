"""Test: reymen/reymen_cli/commands.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestCommands:
    def test_import(self):
        import reymen.reymen_cli.commands as m

        assert m is not None
