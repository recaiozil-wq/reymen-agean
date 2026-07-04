"""Test: CLI mixin modulleri"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestMixinler:
    def test_cli_mixin_core(self):
        import reymen.sistem.cli_mixin_core as m

        assert m is not None

    def test_cli_mixin_display(self):
        import reymen.sistem.cli_mixin_display as m

        assert m is not None

    def test_cli_session(self):
        import reymen.sistem.cli_session as m

        assert m is not None

    def test_cli_stream(self):
        import reymen.sistem.cli_stream as m

        assert m is not None
