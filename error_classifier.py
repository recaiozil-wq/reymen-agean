# -*- coding: utf-8 -*-
# SHIM — agent/error_classifier.py yönlendirir + ReYMeN ErrorClassifier
from agent.error_classifier import *  # noqa: F401, F403

# Private name export
import importlib as _imp_ec, sys as _sys_ec
_src_ec = _imp_ec.import_module('agent.error_classifier')
_sys_ec.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src_ec).items() if k.startswith('_') and not k.startswith('__')}
)

import re as _re


class ErrorClassifier:
    """ReYMeN hata sınıflandırıcı."""

    KATEGORILER = {
        "import":      ["ImportError", "ModuleNotFoundError", "No module named"],
        "syntax":      ["SyntaxError", "IndentationError", "TabError"],
        "dizin":       ["FileNotFoundError", "IsADirectoryError", "not found", "no such file"],
        "baglanti":    ["ConnectionError", "ConnectionRefused", "ECONNREFUSED",
                        "ConnectionReset", "BrokenPipe", "NetworkError"],
        "api":         ["HTTP 401", "HTTP 403", "HTTP 429", "401:", "403:", "429:",
                        "401 ", "403 ", "429 ", "API key", "API Key", "Unauthorized",
                        "Forbidden", "rate limit", "Rate limit"],
        "tip":         ["TypeError", "ValueError", "AttributeError"],
        "izin":        ["PermissionError", "AccessDenied", "[Errno 13]"],
        "zaman_asimi": ["TimeoutError", "timed out", "Timeout", "timeout"],
        "diger":       [],
    }

    COZUM_ONERILERI = {
        "import":      "pip install {modul}",
        "syntax":      "Sözdizimi (söz dizimi) hatası — kodu gözden geçir",
        "dizin":       "Dosya/dizin yolunu kontrol et",
        "baglanti":    "Ağ bağlantısını kontrol et",
        "api":         "API anahtarını ve kimlik bilgilerini kontrol et",
        "tip":         "Değişken tipini kontrol et",
        "izin":        "Dosya/dizin izinlerini kontrol et",
        "zaman_asimi": "Zaman aşımı — bağlantıyı ve sunucuyu kontrol et",
        "diger":       "Hata mesajını incele ve traceback'i kontrol et",
    }

    def _metne_cevir(self, hata) -> str:
        if isinstance(hata, BaseException):
            return f"{type(hata).__name__}: {hata}"
        return str(hata)

    def _kategori_bul(self, metin: str) -> str:
        metin_lower = metin.lower()
        for kategori, desenler in self.KATEGORILER.items():
            if kategori == "diger":
                continue
            for desen in desenler:
                if desen.lower() in metin_lower:
                    return kategori
        return "diger"

    def _cozum_olustur(self, kategori: str, metin: str) -> str:
        if kategori == "import":
            m = _re.search(r"No module named '([^']+)'", metin)
            if m:
                modul = m.group(1).split(".")[0]
                return f"pip install {modul}"
            m = _re.search(r"module named '?([A-Za-z0-9_-]+)", metin)
            if m:
                return f"pip install {m.group(1)}"
        if kategori == "api":
            if "429" in metin or "rate limit" in metin.lower():
                return "Rate limit aşıldı — kısa süre bekle veya API anahtarını değiştir"
            return self.COZUM_ONERILERI["api"]
        return self.COZUM_ONERILERI.get(kategori, "Hata mesajını incele")

    def siniflandir(self, hata) -> dict:
        mesaj = self._metne_cevir(hata)[:200]
        kategori = self._kategori_bul(mesaj)
        cozum = self._cozum_olustur(kategori, mesaj)
        return {"kategori": kategori, "cozum": cozum, "mesaj": mesaj}
