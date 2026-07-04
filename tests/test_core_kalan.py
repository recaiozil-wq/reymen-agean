"""Test: reymen/core/ kalan moduller"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestCore:
    def test_mcp_server(self):
        import reymen.core.mcp_server

        assert reymen.core.mcp_server is not None

    def test_orchestrator(self):
        import reymen.core.orchestrator

        assert reymen.core.orchestrator is not None

    def test_model_adapter(self):
        import reymen.core.model_adapter

        assert reymen.core.model_adapter is not None
