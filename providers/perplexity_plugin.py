# -*- coding: utf-8 -*-
"""
providers/perplexity_plugin.py — Perplexity AI bulut API plugin'i.

Perplexity web aramalı modellerini PERPLEXITY_API_KEY ile kullanır.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class PerplexityPlugin(ProviderPlugin):
    """Perplexity AI web aramalı model servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        return "perplexity"

    @property
    def base_url(self) -> str:
        return getattr(self, "_base_url", "https://api.perplexity.ai")

    @property
    def api_key_schema(self) -> list[dict]:
        return [{"key": "PERPLEXITY_API_KEY", "label": "Perplexity API Key"}]

    @property
    def modeller(self) -> list[str]:
        return ["llama-3.1-sonar-small-128k-online", "llama-3.1-sonar-large-128k-online"]

    def ping(self) -> tuple[bool, str]:
        """Perplexity API'ye bağlantı testi yapar."""
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "Perplexity API anahtarı bulunamadı (PERPLEXITY_API_KEY)"
            url = f"{self.base_url}/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"Perplexity API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "Perplexity API anahtarı geçersiz (401)"
            return False, f"Perplexity yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Perplexity ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """Perplexity'yi test eder ve renkli sonuç döner."""
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Perplexity API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! Perplexity bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Perplexity test hatası: {e}{Renk.RESET}"


if __name__ == "__main__":
    print(f"{Renk.BOLD}Perplexity Plugin Testi{Renk.RESET}")
    plugin = PerplexityPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
