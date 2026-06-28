# -*- coding: utf-8 -*-
"""
providers/lmstudio_plugin.py — LM Studio yerel sunucu plugin'i.

LM Studio'yu localhost:1234 üzerinden OpenAI uyumlu API ile kullanır.
API anahtarı gerektirmez.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class LMStudioPlugin(ProviderPlugin):
    """LM Studio yerel LLM sunucusu için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "lmstudio"

    @property
    def base_url(self) -> str:
        """LM Studio varsayılan adresi."""
        return getattr(self, "_base_url", "http://localhost:1234")

    @property
    def api_key_schema(self) -> list[dict]:
        """LM Studio API anahtarı gerektirmez."""
        return []

    @property
    def modeller(self) -> list[str]:
        """Önerilen LM Studio modelleri."""
        return [
            "cognitivecomputations.dolphin3.0-llama3.1-8b",
            "llama-3.2-3b",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        LM Studio'ya bağlantı testi yapar (/api/v1/models endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            url = f"{self.base_url}/api/v1/models"
            kod, _ = self._http_get(url, zaman_asimi=4)
            if 200 <= kod < 300:
                return True, f"LM Studio çalışıyor ({self.base_url})"
            return False, f"LM Studio yanıt kodu: {kod}"
        except Exception as e:
            return False, f"LM Studio ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        LM Studio'yu test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ LM Studio çalışıyor{Renk.RESET}"
            return False, f"{Renk.SARI}! LM Studio bağlanamadı{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! LM Studio test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}LM Studio Plugin Testi{Renk.RESET}")
    plugin = LMStudioPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
