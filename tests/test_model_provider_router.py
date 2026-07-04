"""Test: reymen/ag/model_provider_router.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestModelRouter:
    def test_import(self):
        import reymen.ag.model_provider_router as m

        assert m is not None

    def test_provider_durum(self):
        from reymen.ag.model_provider_router import router_al

        r = router_al()
        assert r is not None
