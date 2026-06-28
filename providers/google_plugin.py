# -*- coding: utf-8 -*-
"""
providers/google_plugin.py — Google Gemini API plugin'i.

Google Gemini modellerini GOOGLE_API_KEY ile kullanır.
/v1/models endpoint'i üzerinden bağlantı kontrolü yapar.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class GooglePlugin(ProviderPlugin):
    """Google Gemini servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "google"

    @property
    def base_url(self) -> str:
        """Google Generative Language API temel URL'i."""
        return getattr(self, "_base_url", "https://generativelanguage.googleapis.com")

    @property
    def api_key_schema(self) -> list[dict]:
        """Google API anahtarı tanımı."""
        return [{"key": "GOOGLE_API_KEY", "label": "Google API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Desteklenen Google Gemini modelleri."""
        return [
            "gemini-2.0-flash",
            "gemini-1.5-pro",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        Google API'ye bağlantı testi yapar (/v1/models endpoint'i, key parametresi ile).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                # GEMINI_API_KEY alternatifini de dene
                anahtar = self._env_anahtar("GEMINI_API_KEY")
            if not anahtar:
                return False, "Google API anahtarı bulunamadı (GOOGLE_API_KEY veya GEMINI_API_KEY)"
            url = f"{self.base_url}/v1/models?key={anahtar}"
            kod, _ = self._http_get(url, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"Google Gemini API erişilebilir ({self.base_url})"
            if kod == 400:
                return False, "Google API anahtarı geçersiz (400 Bad Request)"
            if kod == 403:
                return False, "Google API erişimi reddedildi (403 Forbidden)"
            return False, f"Google yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Google ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        Google Gemini'yi test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Google Gemini API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! Google Gemini bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Google test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}Google Gemini Plugin Testi{Renk.RESET}")
    plugin = GooglePlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
