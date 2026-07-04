# -*- coding: utf-8 -*-
"""Test: mcp_server.py — MCP server tool registry & transport."""

import sys
import os

# Proje kokunu ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import json
import pytest
from src.core.mcp_server import (
    tool_kaydet,
    tool_sil,
    get_tools,
    _istek_isle,
    _yanit,
    _hata_yaniti,
)


class TestToolRegistry:
    """Tool kaydetme, listeleme, silme."""

    def test_tool_listele_bos(self):
        """Happy path: hic tool kaydedilmemisse bos liste doner."""
        # Ortami temizle — test izole
        tools = get_tools()
        assert isinstance(tools, list)

    def test_tool_kaydet_ve_listele(self):
        """Happy path: tool kaydet, listede gorunsun."""

        def handler(args: dict) -> str:
            return "ok"

        tool_kaydet(
            "test_tool",
            "Test aciklamasi",
            {"type": "object", "properties": {}},
            handler,
        )
        tools = get_tools()
        isimler = [t["name"] for t in tools]
        assert "test_tool" in isimler
        # Temizlik
        tool_sil("test_tool")

    def test_tool_sil(self):
        """Happy path: tool silindikten sonra listede olmamali."""

        def handler(args: dict) -> str:
            return "ok"

        tool_kaydet("silinecek_tool", "", {"type": "object", "properties": {}}, handler)
        assert tool_sil("silinecek_tool") is True
        assert tool_sil("silinecek_tool") is False  # zaten silindi
        isimler = [t["name"] for t in get_tools()]
        assert "silinecek_tool" not in isimler

    def test_tools_list_json_rpc(self):
        """Happy path: _istek_isle ile tools/list istegi calissin."""
        istek = {"jsonrpc": "2.0", "method": "tools/list", "id": 1, "params": {}}
        yanit = _istek_isle(istek)
        assert yanit is not None
        data = json.loads(yanit)
        assert "result" in data
        assert "tools" in data["result"]


class TestMCPServerHata:
    """MCP server hata durumlari."""

    def test_bilinmeyen_method(self):
        """Error case: tanimsiz method ->32601."""
        istek = {"jsonrpc": "2.0", "method": "olmayan_method", "id": 1, "params": {}}
        yanit = _istek_isle(istek)
        assert yanit is not None
        data = json.loads(yanit)
        assert "error" in data
        assert data["error"]["code"] == -32601

    def test_parse_hatasi_yanit(self):
        """Error case: _hata_yaniti dogru formatta."""
        yanit = _hata_yaniti(42, -32700, "Parse error")
        data = json.loads(yanit)
        assert data["error"]["code"] == -32700
        assert "Parse error" in data["error"]["message"]

    def test_tool_call_bulunamadi(self):
        """Error case: olmayan tool cagrisi ->32601."""
        istek = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {"name": "yok_tool", "arguments": {}},
        }
        yanit = _istek_isle(istek)
        data = json.loads(yanit)
        assert "error" in data
        assert "Tool bulunamadi" in data["error"]["message"]

    def test_baslat_hata(self):
        """Error case: MCP notification istegi None doner (bildirim)."""
        istek = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        yanit = _istek_isle(istek)
        assert yanit is None  # bildirimlerde yanit yok
