# -*- coding: utf-8 -*-
"""
providers/xai_plugin.py — xAI Grok API plugin'i.

xAI'nın Grok modellerini XAI_API_KEY ile kullanır.
OpenAI uyumlu /v1/models endpoint'ini destekler.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class XAIPlugin(ProviderPlugin):
    """xAI Grok servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "xai"

    @property
    def base_url(self) -> str:
        """xAI API temel URL'i."""
        return getattr(self, "_base_url", "https://api.x.ai")

    @property
    def api_key_schema(self) -> list[dict]:
        """xAI API anahtarı tanımı."""
        return [{"key": "XAI_API_KEY", "label": "xAI API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Desteklenen xAI Grok modelleri."""
        return [
            "grok-2",
            "grok-beta",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        xAI API'ye bağlantı testi yapar (/v1/models endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "xAI API anahtarı bulunamadı (XAI_API_KEY)"
            url = f"{self.base_url}/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"xAI API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "xAI API anahtarı geçersiz (401 Unauthorized)"
            return False, f"xAI yanıt kodu: {kod}"
        except Exception as e:
            return False, f"xAI ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        xAI Grok'u test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ xAI API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! xAI bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! xAI test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}xAI Grok Plugin Testi{Renk.RESET}")
    plugin = XAIPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
