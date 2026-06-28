# -*- coding: utf-8 -*-
"""
providers/openai_plugin.py — OpenAI bulut API plugin'i.

OpenAI GPT modellerini OPENAI_API_KEY ile kullanır.
/v1/models endpoint'i üzerinden bağlantı kontrolü yapar.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class OpenAIPlugin(ProviderPlugin):
    """OpenAI GPT servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "openai"

    @property
    def base_url(self) -> str:
        """OpenAI API temel URL'i."""
        return getattr(self, "_base_url", "https://api.openai.com")

    @property
    def api_key_schema(self) -> list[dict]:
        """OpenAI API anahtarı tanımı."""
        return [{"key": "OPENAI_API_KEY", "label": "OpenAI API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Desteklenen OpenAI modelleri."""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        OpenAI API'ye bağlantı testi yapar (/v1/models endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "OpenAI API anahtarı bulunamadı (OPENAI_API_KEY)"
            url = f"{self.base_url}/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"OpenAI API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "OpenAI API anahtarı geçersiz (401 Unauthorized)"
            return False, f"OpenAI yanıt kodu: {kod}"
        except Exception as e:
            return False, f"OpenAI ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        OpenAI'yı test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ OpenAI API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! OpenAI bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! OpenAI test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}OpenAI Plugin Testi{Renk.RESET}")
    plugin = OpenAIPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
