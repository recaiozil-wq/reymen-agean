# -*- coding: utf-8 -*-
"""tests/test_acp.py — ACP modulu testleri."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestACPServer:
    def test_server_olusturma(self):
        from acp_adapter.server import ACPServer
        s = ACPServer(port=9999)
        assert s.port == 9999
        assert s._tools == {}

    def test_tool_kaydet(self):
        from acp_adapter.server import ACPServer
        s = ACPServer(port=9998)
        s.tool_kaydet("ping", lambda args: "pong")
        assert "ping" in s._tools

    def test_istek_isle(self):
        from acp_adapter.server import ACPServer
        s = ACPServer(port=9997)
        s.tool_kaydet("ping", lambda args: "pong")
        yanit = s._istek_isle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert "ping" in yanit


class TestACPClient:
    def test_client_olusturma(self):
        from acp_adapter.client import ACPClient
        c = ACPClient()
        assert c is not None
        assert c._req_id == 0


class TestACPAuth:
    def test_imzalama(self):
        from acp_adapter.auth import ACPAuth
        a = ACPAuth(token="test-token")
        imzali = a.imzala("mesaj")
        assert ":" in imzali
        assert a.dogrula(imzali, "mesaj")

    def test_gecersiz_imza(self):
        from acp_adapter.auth import ACPAuth
        a = ACPAuth(token="test-token")
        assert not a.dogrula("gecersiz:imza", "mesaj")
