# -*- coding: utf-8 -*-
"""reymen/mcp/mcp_catalog.py â€” MCP Sunucu KataloÄŸu.

Ã–nceden tanÄ±mlÄ± MCP sunucularÄ±nÄ± listeler ve tek komutla kurulum saÄŸlar.
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# â”€â”€ Katalog: ad â†’ kurulum bilgisi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
KATALOG = {
    "github": {
        "adi": "GitHub MCP",
        "aciklama": "GitHub API: issue, PR, repo, dosya yÃ¶netimi",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "transport": "stdio",
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/github",
    },
    "filesystem": {
        "adi": "Dosya Sistemi MCP",
        "aciklama": "GÃ¼venli dosya okuma/yazma/dizin iÅŸlemleri",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"],
        "transport": "stdio",
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem",
    },
    "postgres": {
        "adi": "PostgreSQL MCP",
        "aciklama": "PostgreSQL veritabanÄ± sorgulama ve ÅŸema okuma",
        "komut": "npx",
        "args": ["-y", "@anthropic/server-postgres"],
        "transport": "stdio",
        "dokuman": "https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp-server-postgres",
    },
    "sqlite": {
        "adi": "SQLite MCP",
        "aciklama": "SQLite veritabanÄ± sorgulama ve yÃ¶netim",
        "komut": "uvx",
        "args": ["mcp-server-sqlite", "--db", "reymen.db"],
        "transport": "stdio",
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite",
    },
    "memory": {
        "adi": "Bellek (Knowledge Graph) MCP",
        "aciklama": "JSON tabanlÄ± bellek/knowledge graph depolama",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "transport": "stdio",
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/memory",
    },
    "puppeteer": {
        "adi": "Puppeteer (Browser) MCP",
        "aciklama": "Headless Chrome ile web scraping ve ekran gÃ¶rÃ¼ntÃ¼sÃ¼",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "transport": "stdio",
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer",
    },
    "playwright": {
        "adi": "Playwright MCP",
        "aciklama": "TarayÄ±cÄ± otomasyonu: sayfa yÃ¼kleme, tÄ±klama, form doldurma, ekran gÃ¶rÃ¼ntÃ¼sÃ¼",
        "komut": "npx",
        "args": ["-y", "@playwright/mcp"],
        "transport": "stdio",
        "dokuman": "https://github.com/microsoft/playwright-mcp",
    },
    "brave-search": {
        "adi": "Brave Search MCP",
        "aciklama": "Brave Search API ile web arama",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "transport": "stdio",
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search",
    },
    "sequential-thinking": {
        "adi": "Sequential Thinking MCP",
        "aciklama": "AdÄ±m adÄ±m dÃ¼ÅŸÃ¼nme ve problem Ã§Ã¶zme",
        "komut": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "transport": "stdio",
        "dokuman": "https://github.com/modelcontextprotocol/servers/tree/main/src/sequential-thinking",
    },
    "reymen-local": {
        "adi": "ReYMeN Local MCP",
        "aciklama": "ReYMeN'in kendi araÃ§larÄ±nÄ± MCP Ã¼zerinden sunar",
        "command": ["python", "-m", "reymen.mcp.server"],
        "transport": "stdio",
        "dokuman": "YerleÅŸik â€” reymen.mcp.server modÃ¼lÃ¼",
    },
}


def listele() -> list[dict]:
    """Katalogdaki tÃ¼m sunucularÄ± listele."""
    return [
        {
            "ad": ad,
            "adi": bilgi["adi"],
            "aciklama": bilgi["aciklama"],
            "transport": bilgi.get("transport", "stdio"),
            "komut": bilgi.get("komut", ""),
        }
        for ad, bilgi in KATALOG.items()
    ]


def bilgi(sunucu_adi: str) -> Optional[dict]:
    """Belirtilen sunucu hakkÄ±nda detaylÄ± bilgi."""
    if sunucu_adi not in KATALOG:
        return None
    return KATALOG[sunucu_adi]


def kur(sunucu_adi: str) -> dict:
    """MCP sunucusunu Ã§alÄ±ÅŸma zamanÄ±na ekle (kurulum+yapÄ±landÄ±rma).

    Not: Bu fonksiyon sadece yapÄ±landÄ±rma bilgisini dÃ¶ndÃ¼rÃ¼r.
    GerÃ§ek MCP sunucu baÅŸlatma config.yaml Ã¼zerinden veya
    mcp_manager().ekle() ile yapÄ±lÄ±r.
    """
    if sunucu_adi not in KATALOG:
        return {"durum": "hata", "hata": f"'{sunucu_adi}' katalogda yok"}

    bilgiler = KATALOG[sunucu_adi]
    cfg = {
        "command": bilgiler.get("command")
        or [bilgiler["komut"]] + bilgiler.get("args", []),
        "transport": bilgiler.get("transport", "stdio"),
    }

    # Async manager'a ekle
    try:
        from reymen.mcp.mcp_manager import mcp_manager
        import asyncio

        mgr = mcp_manager()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            baglanti = mgr.ekle(sunucu_adi, cfg)
            sayi = loop.run_until_complete(baglanti.tools_kesfet())
            loop.close()
            return {
                "durum": "basarili",
                "sunucu": sunucu_adi,
                "tool_sayisi": sayi,
                "config": cfg,
            }
        except Exception:
            loop.close()
            return {
                "durum": "kaydedildi",
                "sunucu": sunucu_adi,
                "not": "Sunucu kaydedildi ama baÄŸlantÄ± kurulamadÄ± (Ã§alÄ±ÅŸmÄ±yor olabilir)",
                "config": cfg,
            }
    except Exception as e:
        return {
            "durum": "kaydedildi",
            "sunucu": sunucu_adi,
            "config": cfg,
            "not": f"YapÄ±landÄ±rma hazÄ±r, manuel baÅŸlatma gerekebilir: {e}",
        }
