"""Tavily web search + extract plugin — bundled, auto-loaded."""


__all__ = ['TavilyWebSearchProvider', 'annotations', 'register']
from __future__ import annotations

from plugins.web.tavily.provider import TavilyWebSearchProvider


def register(ctx) -> None:
    """Register the Tavily provider with the plugin context."""
    ctx.register_web_search_provider(TavilyWebSearchProvider())
