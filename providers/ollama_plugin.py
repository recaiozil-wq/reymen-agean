# -*- coding: utf-8 -*-
"""
providers/ollama_plugin.py — Ollama yerel sunucu plugin'i.

Ollama'yı localhost:11434 üzerinden kullanır.
API anahtarı gerektirmez.
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.plugin_base import ProviderPlugin, Renk


class OllamaPlugin(ProviderPlugin):
    """Ollama yerel LLM çalışma ortamı için plugin."""

    @property
    def provider_adi(self) -> str:
        """Provider adı."""
        return "ollama"

    @property
    def base_url(self) -> str:
        """Ollama varsayılan adresi."""
        return getattr(self, "_base_url", "http://localhost:11434")

    @property
    def api_key_schema(self) -> list[dict]:
        """Ollama API anahtarı gerektirmez."""
        return []

    @property
    def modeller(self) -> list[str]:
        """Önerilen Ollama modelleri."""
        return [
            "llama3.1:8b",
            "mistral:7b",
        ]

    def ping(self) -> tuple[bool, str]:
        """
        Ollama'ya bağlantı testi yapar (/api/tags endpoint'i).
        Döner: (başarılı_mı, mesaj)
        """
        try:
            url = f"{self.base_url}/api/tags"
            kod, _ = self._http_get(url, zaman_asimi=4)
            if 200 <= kod < 300:
                return True, f"Ollama çalışıyor ({self.base_url})"
            return False, f"Ollama yanıt kodu: {kod}"
        except Exception as e:
            return False, f"Ollama ping hatası: {e}"

    def test(self) -> tuple[bool, str]:
        """
        Ollama'yı test eder ve renkli sonuç döner.
        Döner: (başarılı_mı, renkli_mesaj)
        """
        try:
            ok, mesaj = self.ping()
            if ok:
                return True, f"{Renk.YESIL}+ Ollama çalışıyor{Renk.RESET}"
            return False, f"{Renk.SARI}! Ollama bağlanamadı{Renk.RESET}"
        except Exception as e:
            return False, f"{Renk.KIRMIZI}! Ollama test hatası: {e}{Renk.RESET}"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}Ollama Plugin Testi{Renk.RESET}")
    plugin = OllamaPlugin()
    print(f"  Provider: {plugin.provider_adi}")
    print(f"  URL:      {plugin.base_url}")
    print(f"  Modeller: {plugin.modeller}")
    ok, mesaj = plugin.test()
    print(f"  Sonuç:    {mesaj}")
