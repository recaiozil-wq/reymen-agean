# -*- coding: utf-8 -*-
"""
providers/deepseek_plugin.py — DeepSeek AI bulut API plugin'i.

DeepSeek'i DEEPSEEK_API_KEY ile kullanır.
OpenAI uyumlu /v1/models ve /v1/chat/completions endpoint'lerini destekler.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class DeepSeekPlugin(ProviderPlugin):
    """DeepSeek AI bulut servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "deepseek"

    @property
    def base_url(self) -> str:
        """DeepSeek API temel URL'i."""
        return getattr(self, "_base_url", "https://api.deepseek.com")

    @property
    def api_key_schema(self) -> list[dict]:
        """DeepSeek API anahtarı tanımı."""
        return [{"key": "DEEPSEEK_API_KEY", "label": "DeepSeek API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Desteklenen DeepSeek modelleri."""
        return [
            "deepseek-chat",
            "deepseek-reasoner",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        DeepSeek API'ye bağlantı testi yapar (/v1/models endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "DeepSeek API anahtarı bulunamadı (DEEPSEEK_API_KEY)"
            url = f"{self.base_url}/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"DeepSeek API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "DeepSeek API anahtarı geçersiz (401 Unauthorized)"
            return False, f"DeepSeek yanıt kodu: {kod}"
        except Exception as e:
            return False, f"DeepSeek ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        DeepSeek'i test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ DeepSeek API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! DeepSeek bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! DeepSeek test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}DeepSeek Plugin Testi{Renk.RESET}")
    plugin = DeepSeekPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
