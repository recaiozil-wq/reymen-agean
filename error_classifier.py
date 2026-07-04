# -*- coding: utf-8 -*-
"""Basit hata sınıflandırıcı — hata türüne göre kategori ve çözüm üretir."""

from __future__ import annotations

import re
from typing import Any, Dict, Tuple


# ── Kategoriler ve kalıplar ────────────────────────────────────────────────

_KATEGORI_KALIPLARI: list[Tuple[re.Pattern[str], str]] = [
    # import hataları (dizin'den önce — "not found" ortak kalıbı var)
    (re.compile(r"module\W*not\W*found|import\W*error", re.IGNORECASE), "import"),
    # sözdizimi
    (re.compile(r"syntax\W*error|indentation\W*error", re.IGNORECASE), "syntax"),
    # dosya / dizin
    (re.compile(r"file\W*not\W*found|no\W*such\W*file|not\W*found", re.IGNORECASE), "dizin"),
    # bağlantı
    (re.compile(r"connection\W*refused|econnrefused|connection\W*error", re.IGNORECASE), "baglanti"),
    # API
    (re.compile(r"\b[45]\d{2}\b|api\W*key|api\W*hatasi|rate\W*limit|unauthorized|forbidden", re.IGNORECASE), "api"),
    # tip
    (re.compile(r"type\W*error|value\W*error", re.IGNORECASE), "tip"),
    # izin
    (re.compile(r"permission\W*error|izin\W*yok", re.IGNORECASE), "izin"),
    # zaman aşımı
    (re.compile(r"timeout\W*error|timed?\W*out|zaman\W*asimi", re.IGNORECASE), "zaman_asimi"),
]

# ── Çözüm şablonları ──────────────────────────────────────────────────────

_COZUM_SABLONLARI: Dict[str, str] = {
    "import": "Eksik paketi pip ile yükleyin.",
    "syntax": "Kodda söz dizimi hatası var, satırları kontrol edin.",
    "dizin": "Dosya yolu yanlış veya dosya mevcut değil — yolunu kontrol edin.",
    "baglanti": "Ağ bağlantısı kurulamadı — sunucu durumunu ve ağ ayarlarını kontrol edin.",
    "api": "API hatası — API anahtarını ve istek limitlerini kontrol edin.",
    "tip": "Değişken tipini kontrol edin — değerlerin ve tiplerin eşleştiğinden emin olun.",
    "izin": "Yeterli izin yok — dosya izinlerini kontrol edin.",
    "zaman_asimi": "Zaman aşımı oluştu — bağlantıyı veya isteği tekrar deneyin.",
    "diger": "Beklenmeyen hata — traceback dosyasını inceleyin.",
}


# ── ErrorClassifier sınıfı ────────────────────────────────────────────────


class ErrorClassifier:
    """Hata nesnelerini veya metinlerini sınıflandırır ve çözüm üretir."""

    # ── Yardımcı metodlar ──────────────────────────────────────────────────

    def _metne_cevir(self, hata: Any) -> str:
        """Herhangi bir girdiyi string'e çevirir."""
        if isinstance(hata, str):
            return hata
        if isinstance(hata, BaseException):
            msg = str(hata).strip()
            return f"{type(hata).__name__}: {msg}" if msg else f"{type(hata).__name__}:"
        return str(hata)

    def _kategori_bul(self, metin: str) -> str:
        """Hata metnine en uygun kategoriyi bulur."""
        for kalip, kategori in _KATEGORI_KALIPLARI:
            if kalip.search(metin):
                return kategori
        return "diger"

    def _cozum_olustur(self, kategori: str, metin: str) -> str:
        """Kategoriye göre çözüm önerisi üretir."""
        if kategori == "import":
            return self._import_cozumu(metin)
        if kategori == "api" and re.search(r"429|rate\s*limit", metin, re.IGNORECASE):
            return "Rate limit aşıldı — kısa bir süre bekleyip tekrar deneyin."
        return _COZUM_SABLONLARI.get(kategori, "Hata mesajını incele")

    def _import_cozumu(self, metin: str) -> str:
        """Import hatasından paket adını çıkarır ve pip install komutu üretir."""
        eslesme = re.search(r"no\s+module\s+named\s+['\"]([^'\"]+)['\"]", metin, re.IGNORECASE)
        if eslesme:
            paket = eslesme.group(1).split(".")[0]
            return f"pip install {paket}"
        return "pip install <paket-adi>"

    # ── Ana API ────────────────────────────────────────────────────────────

    def siniflandir(self, hata: Any) -> Dict[str, str]:
        """Hatayı sınıflandırır: kategori, çözüm ve mesaj döndürür."""
        mesaj = self._metne_cevir(hata)
        if len(mesaj) > 200:
            mesaj = mesaj[:200]
        kategori = self._kategori_bul(mesaj)
        cozum = self._cozum_olustur(kategori, mesaj)
        return {"kategori": kategori, "cozum": cozum, "mesaj": mesaj}


# ── Komut satırı testi ────────────────────────────────────────────────────

if __name__ == "__main__":
    clf = ErrorClassifier()
    ornekler = [
        "ModuleNotFoundError: No module named 'requests'",
        "SyntaxError: invalid syntax on line 5",
        "FileNotFoundError: config.yaml bulunamadi",
        "ConnectionRefusedError: sunucu kapali",
        "HTTP 401: Unauthorized",
        "TypeError: unsupported operand type(s)",
        "PermissionError: [Errno 13] izin yok",
        "TimeoutError: islem zaman asimi",
        "Beklenmedik bir hata olustu",
        "",
    ]
    for hata in ornekler:
        sonuc = clf.siniflandir(hata)
        print(f"  {sonuc['kategori']:>12} | {sonuc['cozum'][:50]:<50} | {sonuc['mesaj'][:40]}")
