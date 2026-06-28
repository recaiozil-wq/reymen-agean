#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_mcp.py — MCP birim ve entegrasyon testleri.
"""

import sys
sys.path.insert(0, ".")

import asyncio
import json
import os
import tempfile
from pathlib import Path


class TestMCPManager:
    """MCPManager birim testleri (sunucusuz)."""

    def test_config_yukle_bos(self):
        from tools.mcp_manager import MCPManager
        mgr = MCPManager()
        cfg = mgr._config_yukle()
        assert isinstance(cfg, dict)
        # config.yaml'daki mcp_servers: {} -> {}
        assert cfg == {}

    def test_config_yukle_yok(self):
        from tools.mcp_manager import MCPManager
        mgr = MCPManager()
        cfg = mgr._config_yukle()
        assert isinstance(cfg, dict)

    def test_sunucu_sinifi(self):
        from tools.mcp_manager import MCPServerBaglantisi
        s = MCPServerBaglantisi("test", {"command": "echo", "args": [], "transport": "stdio"})
        assert s.ad == "test"
        assert s.transport == "stdio"
        assert s.baglandi is False
        assert s.tool_listesi() == []

    def test_sunucu_turu_http(self):
        from tools.mcp_manager import MCPServerBaglantisi
        s = MCPServerBaglantisi("remote", {"url": "https://example.com/mcp", "transport": "http"})
        assert s.transport == "http"


class TestMCPTool:
    """mcp_tool.py birim testleri."""

    def test_check_fn_bos_config(self):
        from tools.mcp_tool import check_fn
        # config'te mcp_servers: {} oldugu icin False
        assert check_fn() is False

    def test_TOOL_META(self):
        from tools.mcp_tool import TOOL_META
        assert "sunucu" in str(TOOL_META)
        assert TOOL_META["kategori"] == "entegrasyon"
        assert len(TOOL_META["parametreler"]) == 3

    def test_mcp_tool_cagir_sunucu_yok(self):
        from tools.mcp_tool import mcp_tool_cagir
        sonuc = mcp_tool_cagir("yok", "test")
        assert "HATA" in sonuc

    def test_mcp_tool_listele_bos(self):
        from tools.mcp_tool import mcp_tool_listele
        araclar = mcp_tool_listele()
        assert araclar == []


class TestMCPIntegration:
    """MCP entegrasyon testi (gercek MCP sunucusu ile).

    Calismasi icin: npm/npx kurulu olmali.
    """

    def test_filesystem_mcp(self):
        """Filesystem MCP sunucusuna baglan, tool'lari listele."""
        from tools.mcp_manager import MCPManager

        # Gecici bir dizin olustur
        with tempfile.TemporaryDirectory() as tmpdir:
            # MCPManager'i dogrudan config ile baslat
            mgr = MCPManager()
            mgr.config_yolu = None  # config'i atla

            # Manuel sunucu ekle
            from tools.mcp_manager import MCPServerBaglantisi
            sunucu = MCPServerBaglantisi("fs", {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", tmpdir],
                "timeout": 15,
            })

            # Baglan
            async def test():
                ok = await sunucu.tools_kesfet() > 0
                if not ok:
                    print("  MCP sunucusu baglanamadi (npm/npx gerekli)")
                    return  # Skip - npm olmayabilir

                tools = sunucu.tool_listesi()
                print(f"  Kesfedilen araclar: {[t['name'] for t in tools]}")
                assert len(tools) > 0
                assert any("read" in t["name"] for t in tools)

                # Bir dosya yaz ve oku
                test_file = os.path.join(tmpdir, "test.txt")
                with open(test_file, "w") as f:
                    f.write("Hello MCP!")

                sonuc = await sunucu.tool_cagir("read_file", {"path": test_file})
                print(f"  read_file sonucu: {sonuc['icerik'][:50]}")
                assert "Hello MCP!" in sonuc["icerik"]

            asyncio.run(test())


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
