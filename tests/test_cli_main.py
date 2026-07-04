"""Test: reymen/sistem/cli_main.py ve CLI modulleri"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestCLIMain:
    def test_import(self):
        import reymen.sistem.cli_main as m

        assert m is not None

    def test_import_cli_agent(self):
        import reymen.sistem.cli_agent as m

        assert m is not None

    def test_import_main(self):
        import reymen.sistem as m

        assert m is not None
