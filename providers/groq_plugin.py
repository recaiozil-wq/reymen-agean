# -*- coding: utf-8 -*-
"""
providers/groq_plugin.py — Groq Cloud API plugin'i.

Groq'u GROQ_API_KEY ile kullanır. Çok hızlı inferans sunar.
OpenAI uyumlu /openai/v1/models endpoint'ini kullanır.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class GroqPlugin(ProviderPlugin):
    """Groq Cloud hızlı inferans servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "groq"

    @property
    def base_url(self) -> str:
        """Groq API temel URL'i."""
        return getattr(self, "_base_url", "https://api.groq.com")

    @property
    def api_key_schema(self) -> list[dict]:
        """Groq API anahtarı tanımı."""
        return [{"key": "GROQ_API_KEY", "label": "Groq API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Desteklenen Groq modelleri."""
        return [
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        Groq API'ye bağlantı testi yapar (/openai/v1/models endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "Groq API anahtarı bulunamadı (GROQ_API_KEY)"
            url = f"{self.base_url}/openai/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"Groq API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "Groq API anahtarı geçersiz (401 Unauthorized)"
            return False, f"Groq yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Groq ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        Groq'u test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Groq API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! Groq bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Groq test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}Groq Plugin Testi{Renk.RESET}")
    plugin = GroqPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
