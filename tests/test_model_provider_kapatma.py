"""Test: model_provider."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestModelProvider:
    def test_import(self):
        import reymen.core.model_provider as m

        assert m is not None

    def test_varsayilan_zincir(self):
        from reymen.core.model_provider import varsayilan_zincir

        z = varsayilan_zincir()
        assert z is not None
