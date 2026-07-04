"""Test: gateway_manager."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestGateway:
    def test_import(self):
        import reymen.core.gateway_manager as m

        assert m is not None

    def test_class(self):
        from reymen.core.gateway_manager import GatewayYoneticisi

        g = GatewayYoneticisi()
        assert g is not None
