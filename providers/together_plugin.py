# -*- coding: utf-8 -*-
"""
providers/together_plugin.py — Together AI bulut API plugin'i.

Together AI açık kaynak modelleri TOGETHER_API_KEY ile kullanır.
OpenAI uyumlu /v1/models endpoint'ini destekler.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class TogetherPlugin(ProviderPlugin):
    """Together AI açık kaynak model servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "together"

    @property
    def base_url(self) -> str:
        """Together AI API temel URL'i."""
        return getattr(self, "_base_url", "https://api.together.xyz")

    @property
    def api_key_schema(self) -> list[dict]:
        """Together AI API anahtarı tanımı."""
        return [{"key": "TOGETHER_API_KEY", "label": "Together AI API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Desteklenen Together AI modelleri."""
        return [
            "meta-llama/Llama-3.3-70B-Instruct",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        Together AI API'ye bağlantı testi yapar (/v1/models endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "Together AI API anahtarı bulunamadı (TOGETHER_API_KEY)"
            url = f"{self.base_url}/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"Together AI API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "Together AI API anahtarı geçersiz (401 Unauthorized)"
            return False, f"Together AI yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Together AI ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        Together AI'yı test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Together AI API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! Together AI bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Together AI test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}Together AI Plugin Testi{Renk.RESET}")
    plugin = TogetherPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
