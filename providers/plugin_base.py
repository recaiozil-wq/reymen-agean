# -*- coding: utf-8 -*-
"""
providers/plugin_base.py — Tüm provider plugin'leri için soyut temel sınıf.

Her LLM sağlayıcı plugin'i bu sınıftan türetilir ve zorunlu
metodları/özellikleri uygular (provider adı, URL, model listesi, ping/test).
"""
import sys
from abc import ABC, abstractmethod
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))


class Renk:
    """Terminal renk kodları."""
    MOR     = "\033[95m"
    MAVI    = "\033[94m"
    YESIL   = "\033[92m"
    SARI    = "\033[93m"
    KIRMIZI = "\033[91m"
    CYAN    = "\033[96m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"


class ProviderPlugin(ABC):
    """Tüm provider plugin'ler için abstract base."""

    def __init__(self, api_key: str = "", base_url: str = ""):
        """Plugin'i başlat; opsiyonel api_key ve base_url override'ı."""
        self._api_key = api_key
        if base_url:
            self._base_url = base_url

    # ── Soyut özellikler ─────────────────────────────────────────────

    @property
    @abstractmethod
    def provider_adi(self) -> str:
        """Provider'ın benzersiz adı (örn. 'openai', 'lmstudio')."""
        ...

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Provider API'sinin temel URL'i."""
        ...

    @property
    @abstractmethod
    def api_key_schema(self) -> list[dict]:
        """
        API anahtarı tanımları.
        Örn: [{"key": "OPENAI_API_KEY", "label": "OpenAI API Key"}]
        Anahtar gerektirmeyen providerlar için boş liste döner.
        """
        ...

    @property
    @abstractmethod
    def modeller(self) -> list[str]:
        """Bu provider için önerilen model listesi."""
        ...

    # ── Soyut metodlar ───────────────────────────────────────────────

    @abstractmethod
    def ping(self) -> tuple[bool, str]:
        """
        Provider'a bağlantı testi yapar.
        Döner: (başarılı_mı: bool, mesaj: str)
        """
        ...

    @abstractmethod
    def test(self) -> tuple[bool, str]:
        """
        Provider'ı test eder ve renkli sonuç döner.
        Döner: (başarılı_mı: bool, mesaj: str)
        """
        ...

    # ── Yardımcı metodlar ────────────────────────────────────────────

    def _env_anahtar(self, anahtar: str) -> str:
        """.env dosyasından veya os.environ'dan anahtar değerini oku."""
        try:
            import os
            ortam_degeri = os.environ.get(anahtar, "").strip()
            if ortam_degeri:
                return ortam_degeri
            env_yolu = PROJE_KOK / ".env"
            if not env_yolu.exists():
                return ""
            with open(env_yolu, "r", encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir.startswith("#") or "=" not in satir:
                        continue
                    k, v = satir.split("=", 1)
                    if k.strip() == anahtar:
                        return v.strip().strip('"').strip("'")
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return ""

    def _api_anahtari(self) -> str:
        """api_key_schema'dan ilk anahtarı çöz."""
        try:
            if self._api_key:
                return self._api_key
            schema = self.api_key_schema
            if not schema:
                return ""
            return self._env_anahtar(schema[0]["key"])
        except Exception:
            return ""

    def _http_get(self, url: str, headers: dict | None = None, zaman_asimi: int = 5) -> tuple[int, str]:
        """
        Basit HTTP GET isteği gönderir.
        Döner: (durum_kodu, gövde_metni)
        """
        try:
            import urllib.request
            import urllib.error
            req = urllib.request.Request(url, headers=headers or {}, method="GET")
            with urllib.request.urlopen(req, timeout=zaman_asimi) as yanit:
                return yanit.status, yanit.read(512).decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            return e.code, str(e.reason)
        except Exception as e:
            return 0, str(e)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} provider={self.provider_adi!r} url={self.base_url!r}>"


# ── Test bloğu ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{Renk.BOLD}plugin_base.py — soyut sınıf testi{Renk.RESET}")
    print(f"{Renk.YESIL}ProviderPlugin ABC tanımlı, import OK{Renk.RESET}")
    print(f"PROJE_KOK: {PROJE_KOK}")
