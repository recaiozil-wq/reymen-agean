# -*- coding: utf-8 -*-
"""
providers/mistral_plugin.py — Mistral AI bulut API plugin'i.

Mistral AI modellerini MISTRAL_API_KEY ile kullanır.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class MistralPlugin(ProviderPlugin):
    """Mistral AI servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        return "mistral"

    @property
    def base_url(self) -> str:
        return getattr(self, "_base_url", "https://api.mistral.ai")

    @property
    def api_key_schema(self) -> list[dict]:
        return [{"key": "MISTRAL_API_KEY", "label": "Mistral AI API Key"}]

    @property
    def modeller(self) -> list[str]:
        return ["mistral-small-latest", "mistral-large-latest"]

    def ping(self) -> tuple[bool, str]:
        """Mistral API'ye bağlantı testi yapar."""
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "Mistral API anahtarı bulunamadı (MISTRAL_API_KEY)"
            url = f"{self.base_url}/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"Mistral API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "Mistral API anahtarı geçersiz (401)"
            return False, f"Mistral yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Mistral ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """Mistral'ı test eder ve renkli sonuç döner."""
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Mistral API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! Mistral bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Mistral test hatası: {e}{Renk.RESET}"


if __name__ == "__main__":
    print(f"{Renk.BOLD}Mistral Plugin Testi{Renk.RESET}")
    plugin = MistralPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
