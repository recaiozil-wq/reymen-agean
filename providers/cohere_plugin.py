# -*- coding: utf-8 -*-
"""
providers/cohere_plugin.py — Cohere AI bulut API plugin'i.

Cohere Command modellerini COHERE_API_KEY ile kullanır.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class CoherePlugin(ProviderPlugin):
    """Cohere AI servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        return "cohere"

    @property
    def base_url(self) -> str:
        return getattr(self, "_base_url", "https://api.cohere.ai")

    @property
    def api_key_schema(self) -> list[dict]:
        return [{"key": "COHERE_API_KEY", "label": "Cohere API Key"}]

    @property
    def modeller(self) -> list[str]:
        return ["command-r", "command-r-plus"]

    def ping(self) -> tuple[bool, str]:
        """Cohere API'ye bağlantı testi yapar."""
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "Cohere API anahtarı bulunamadı (COHERE_API_KEY)"
            url = f"{self.base_url}/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"Cohere API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "Cohere API anahtarı geçersiz (401)"
            return False, f"Cohere yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Cohere ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """Cohere'ı test eder ve renkli sonuç döner."""
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Cohere API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! Cohere bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Cohere test hatası: {e}{Renk.RESET}"


if __name__ == "__main__":
    print(f"{Renk.BOLD}Cohere Plugin Testi{Renk.RESET}")
    plugin = CoherePlugin()
    print(f"  Provider: {plugin.provider_adi}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
