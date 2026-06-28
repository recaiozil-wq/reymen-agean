# -*- coding: utf-8 -*-
"""
providers/fireworks_plugin.py — Fireworks AI bulut API plugin'i.

Fireworks AI'yı FIREWORKS_API_KEY ile kullanır.
Hızlı açık kaynak model inferansı sunar.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class FireworksPlugin(ProviderPlugin):
    """Fireworks AI hızlı inferans servisi için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "fireworks"

    @property
    def base_url(self) -> str:
        """Fireworks AI API temel URL'i."""
        return getattr(self, "_base_url", "https://api.fireworks.ai")

    @property
    def api_key_schema(self) -> list[dict]:
        """Fireworks AI API anahtarı tanımı."""
        return [{"key": "FIREWORKS_API_KEY", "label": "Fireworks AI API Key"}]

    @property
    def modeller(self) -> list[str]:
        """Desteklenen Fireworks AI modelleri."""
        return [
            "accounts/fireworks/models/llama-v3p3-70b-instruct",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        Fireworks AI API'ye bağlantı testi yapar (/v1/models endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            anahtar = self._api_anahtari()
            if not anahtar:
                return False, "Fireworks AI API anahtarı bulunamadı (FIREWORKS_API_KEY)"
            url = f"{self.base_url}/v1/models"
            basliklar = {"Authorization": f"Bearer {anahtar}"}
            kod, _ = self._http_get(url, headers=basliklar, zaman_asimi=6)
            if 200 <= kod < 300:
                return True, f"Fireworks AI API erişilebilir ({self.base_url})"
            if kod == 401:
                return False, "Fireworks AI API anahtarı geçersiz (401 Unauthorized)"
            return False, f"Fireworks AI yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Fireworks AI ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        Fireworks AI'yı test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Fireworks AI API erişilebilir{Renk.RESET}"
            return False, f"{Renk.SARI}! Fireworks AI bağlanamadı: {mesaj}{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Fireworks AI test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}Fireworks AI Plugin Testi{Renk.RESET}")
    plugin = FireworksPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
