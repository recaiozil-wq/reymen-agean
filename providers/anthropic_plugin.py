# -*- coding: utf-8 -*-
"""
providers/anthropic_plugin.py — Anthropic Claude API plugin'i.

Anthropic Messages API'sini ANTHROPIC_API_KEY ile kullanır.
OpenAI uyumlu değil; x-api-key başlığı ve /v1/messages endpoint'i kullanır.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class AnthropicPlugin(ProviderPlugin):
    """Anthropic Claude servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "anthropic"

    @property
    def base_url(self) -> str:
        """Anthropic API temel URL'i."""
        return getattr(self, "_base_url", "https://api.anthropic.com")

    @property
    def api_key_schema(self) -> list[dict]:
        """Anthropic API anahtarı tanımı."""
        return [{"key": "ANTHROPIC_API_KEY", "label": "Anthropic API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Desteklenen Anthropic Claude modelleri."""
        return [
            "claude-sonnet-4-5",
            "claude-haiku-4-5-20251001",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        Anthropic API'ye bağlantı testi yapar (/v1/messages endpoint'i HEAD isteği).
        Anthropic özel x-api-key başlığı kullanır (Bearer değil).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            import urllib.request
            import urllib.error

            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "Anthropic API anahtarı bulunamadı (ANTHROPIC_API_KEY)"

            url = f"{self.base_url}/v1/messages"
            basliklar = {
                "x-api-key": anahtar,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            }
            req = urllib.request.Request(url, headers=basliklar, method="HEAD")
            try:
                with urllib.request.urlopen(req, timeout=6) as yanit:
                    kod = yanit.status
            except urllib.error.HTTPError as e:
                kod = e.code

            # 200 veya 405 (Method Not Allowed) → API erişilebilir
            if kod in (200, 405):
                return True, f"Anthropic API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "Anthropic API anahtarı geçersiz (401 Unauthorized)"
            return False, f"Anthropic yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Anthropic ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        Anthropic'i test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Anthropic API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! Anthropic bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Anthropic test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}Anthropic Plugin Testi{Renk.RESET}")
    plugin = AnthropicPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
