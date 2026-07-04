"""Test: reymen/ag/gateway_yonetici.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestGatewayYonetici:
    def test_import(self):
        import reymen.ag.gateway_yonetici as m

        assert m is not None
