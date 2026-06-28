# -*- coding: utf-8 -*-
"""
providers/openrouter_plugin.py — OpenRouter API plugin'i.

OpenRouter üzerinden 100+ modele erişim sağlar. Ücretsiz modeller mevcuttur.
OPENROUTER_API_KEY ile kullanılır.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class OpenRouterPlugin(ProviderPlugin):
    """OpenRouter çoklu model yönlendirici servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "openrouter"

    @property
    def base_url(self) -> str:
        """OpenRouter API temel URL'i."""
        return getattr(self, "_base_url", "https://openrouter.ai/api")

    @property
    def api_key_schema(self) -> list[dict]:
        """OpenRouter API anahtarı tanımı."""
        return [{"key": "OPENROUTER_API_KEY", "label": "OpenRouter API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Önerilen OpenRouter modelleri."""
        return [
            "openrouter/auto",
            "anthropic/claude-sonnet-4-5",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        OpenRouter API'ye bağlantı testi yapar (/v1/models endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "OpenRouter API anahtarı bulunamadı (OPENROUTER_API_KEY)"
            url = f"{self.base_url}/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"OpenRouter API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "OpenRouter API anahtarı geçersiz (401 Unauthorized)"
            return False, f"OpenRouter yanıt kodu: {kod}"
        except Exception as e:
            return False, f"OpenRouter ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        OpenRouter'ı test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ OpenRouter API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! OpenRouter bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! OpenRouter test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}OpenRouter Plugin Testi{Renk.RESET}")
    plugin = OpenRouterPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
