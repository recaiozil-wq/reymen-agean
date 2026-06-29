# -*- coding: utf-8 -*-
"""reymen/mcp/__init__.py — ReYMeN MCP İstemci Paketi.

Model Context Protocol (MCP) sunucularına bağlanma, tool keşfetme ve çağırma.

Kullanım:
    from reymen.mcp.mcp_manager import mcp_manager

    # Otomatik başlat (config.yaml'daki mcp_servers'dan)
    await mcp_manager().baslat()

    # Tool çağır
    sonuc = await mcp_manager().cagir("github", "issues/list", {"repo": "user/repo"})

    # Tüm tool'ları listele
    tools = mcp_manager().tum_araclari_getir()
"""

from reymen.mcp.mcp_tool import motor_kaydet

__all__ = ["motor_kaydet"]
