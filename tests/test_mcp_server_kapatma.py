"""Test: mcp_server."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestMCP:
    def test_import(self):
        import reymen.core.mcp_server as m

        assert m is not None

    def test_client_session_import(self):
        from reymen.core.mcp_server import ClientSession

        assert ClientSession is not None
