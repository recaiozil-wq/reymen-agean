"""Test: reymen/mcp/ modulleri"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestMCP:
    def test_manager(self):
        from reymen.mcp.mcp_manager import MCPManager

        mm = MCPManager()
        assert isinstance(mm.sunucu_listesi(), list)

    def test_catalog(self):
        try:
            from reymen.mcp.mcp_catalog import MCPCatalog

            assert MCPCatalog is not None
        except ImportError:
            pytest.skip("MCPCatalog")

    def test_discovery(self):
        try:
            from reymen.mcp.mcp_discovery import MCPDiscovery

            assert MCPDiscovery is not None
        except ImportError:
            pytest.skip("MCPDiscovery")
