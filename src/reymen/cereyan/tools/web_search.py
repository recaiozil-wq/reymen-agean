# -*- coding: utf-8 -*-
"""Web arama araclari.

conversation_loop.py'den extract edilmistir.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger("conversation_loop")


def mcp_web_ara(
    sorgu: str,
    maks_sonuc: int = 3,
    *,
    native_mcp=None,
    mcp_client_get=None,
    mcp_istemci_get=None,
) -> Optional[str]:
    """MCP uzerinden web aramayi dene."""
    # 1. Native MCP
    if native_mcp is not None:
        try:
            baglantilar = getattr(native_mcp, "_baglantilar", {})
            for ad, baglanti in baglantilar.items():
                if "firecrawl" in ad.lower() or "search" in ad.lower():
                    if getattr(baglanti, "bagli", False):
                        sonuc = baglanti.arac_cagir(
                            "search", {"query": sorgu, "limit": maks_sonuc}
                        )
                        if sonuc and sonuc.strip() not in ("[]", "{}", ""):
                            return f"[MCP-{ad}] {sonuc}"
        except Exception:
            pass

    # 2. MCP Client
    if mcp_client_get is not None:
        try:
            yonetici = mcp_client_get()
            durum = yonetici.durum()
            for ad in durum:
                if "firecrawl" in ad.lower() or "search" in ad.lower():
                    sonuc = yonetici.arac_cagir(ad, "search", {"query": sorgu, "limit": maks_sonuc})
                    if sonuc and not sonuc.startswith("[MCPClient]"):
                        return f"[MCP-{ad}] {sonuc}"
        except Exception:
            pass

    # 3. MCP Tool
    if mcp_istemci_get is not None:
        try:
            istemci = mcp_istemci_get()
            durum = istemci.durum()
            for ad, bilgi in durum.items():
                if "firecrawl" in ad.lower() or "search" in ad.lower():
                    if bilgi.get("aktif", False):
                        sonuc = istemci.arac_cagir(ad, "search", {"query": sorgu, "limit": maks_sonuc})
                        if sonuc and not sonuc.startswith("[MCP]"):
                            return f"[MCP-{ad}] {sonuc}"
        except Exception:
            pass

    return None
