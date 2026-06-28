"""Test reymen.core.mcp_server — MCP Server Host."""
import pytest


class TestMCPServer:
    def test_import(self):
        from reymen.core import mcp_server
        assert hasattr(mcp_server, "tool_kaydet")
        assert hasattr(mcp_server, "tool_sil")
        assert hasattr(mcp_server, "get_tools")

    def test_tool_kaydet_ve_get(self):
        from reymen.core.mcp_server import tool_kaydet, get_tools, tool_sil
        tool_kaydet(
            name="test_tool",
            description="Test aracı",
            input_schema={"type": "object", "properties": {}},
            handler=lambda args: '{"result": "ok"}',
        )
        tools = get_tools()
        assert any(t.get("name") == "test_tool" for t in tools)
        # Temizle
        tool_sil("test_tool")

    def test_tool_sil(self):
        from reymen.core.mcp_server import tool_kaydet, get_tools, tool_sil
        tool_kaydet(
            name="temp_tool",
            description="Geçici",
            input_schema={"type": "object", "properties": {}},
            handler=lambda args: "{}",
        )
        result = tool_sil("temp_tool")
        assert result is True
        tools = get_tools()
        assert not any(t.get("name") == "temp_tool" for t in tools)