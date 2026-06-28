# -*- coding: utf-8 -*-
"""SHIM — agent/web_search_provider.py yönlendirir"""
from agent.web_search_provider import *  # noqa: F401, F403
import agent.web_search_provider as _wsp_mod

# Soyut sınıfı concrete stub ile geri yaz
class WebSearchProvider(_wsp_mod.WebSearchProvider):
    """Somut web arama sağlayıcısı stub."""
    name = "stub"

    def is_available(self) -> bool:
        return False

    def search(self, sorgu: str, **kwargs) -> list:
        return []

    def ara(self, sorgu: str, **kwargs) -> list:
        return self.search(sorgu, **kwargs)
