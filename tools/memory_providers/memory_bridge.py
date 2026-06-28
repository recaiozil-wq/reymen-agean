# -*- coding: utf-8 -*-
"""memory_providers/memory_bridge.py — Tüm sağlayıcılar için tek run()."""

from __future__ import annotations
import threading
from typing import Any, Dict, Optional

from .base import BellekSaglayici

# ── Thread-safe singleton registry ────────────────────────────
_kilit: threading.Lock = threading.Lock()
_SAGLAYICILAR: Dict[str, BellekSaglayici] = {}

_GECERLI_EYLEMLER = frozenset({"kaydet", "oku", "ara", "sil", "durum"})
_GECERLI_TURLER   = frozenset({"chromadb", "file", "sqlite", "redis"})


def _get_saglayici(tur: str) -> BellekSaglayici:
    """Thread-safe lazy singleton factory."""
    with _kilit:
        if tur not in _SAGLAYICILAR:
            if tur == "chromadb":
                from .chromadb_provider import ChromaDBBellek
                _SAGLAYICILAR[tur] = ChromaDBBellek()
            elif tur == "file":
                from .file_provider import FileBellek
                _SAGLAYICILAR[tur] = FileBellek()
            elif tur == "sqlite":
                from .sqlite_provider import SQLiteBellek
                _SAGLAYICILAR[tur] = SQLiteBellek()
            elif tur == "redis":
                from .redis_provider import RedisBellek
                _SAGLAYICILAR[tur] = RedisBellek()
            else:
                raise ValueError(
                    f"Bilinmeyen tür: '{tur}'. "
                    f"Geçerli: {sorted(_GECERLI_TURLER)}"
                )
    return _SAGLAYICILAR[tur]


def _format_ara(sonuc: list, tur: str) -> str:
    if not sonuc:
        return "[Sonuç] Kayıt bulunamadı."
    satirlar = [f"[Arama] ({tur}) — {len(sonuc)} sonuç:"]
    for s in sonuc:
        satirlar.append(f"  [{s.get('id', '?')}] {s.get('icerik', '')}")
    return "\n".join(satirlar)


def run(
    tur:       str = "file",
    eylem:     str = "kaydet",
    anahtar:   str = "",
    deger:     Any = None,        # None default — "" ile tip kayması önlendi
    sorgu:     str = "",
    namespace: str = "default",
    limit:     int = 5,
) -> str:
    """Tüm bellek sağlayıcılarına tek giriş noktası.

    Örnekler:
        run("file",    "kaydet", "not1", "Bugün Python öğrendim")
        run("file",    "oku",    "not1")
        run("chromadb","kaydet", "fikir1", "Yeni proje: otonom ajan")
        run("chromadb","ara",    sorgu="Python nedir", limit=3)
        run("sqlite",  "ara",    sorgu="hafıza")
        run("file",    "durum")
    """
    # ── Parametre temizleme ────────────────────────────────────
    tur    = tur.strip().lower()
    eylem  = eylem.strip().lower()

    if tur not in _GECERLI_TURLER:
        return (f"[Hata]: Bilinmeyen tür '{tur}'. "
                f"Geçerli: {sorted(_GECERLI_TURLER)}")
    if eylem not in _GECERLI_EYLEMLER:
        return (f"[Hata]: Bilinmeyen eylem '{eylem}'. "
                f"Geçerli: {sorted(_GECERLI_EYLEMLER)}")

    # ── Sağlayıcı yükle ───────────────────────────────────────
    try:
        saglayici = _get_saglayici(tur)
    except ValueError as e:
        return f"[Hata]: {e}"
    except Exception as e:
        return f"[Hata]: '{tur}' yüklenemedi — {e}"

    # ── Eylem yönlendirme ─────────────────────────────────────
    if eylem == "kaydet":
        if not anahtar:
            return "[Hata]: 'kaydet' için anahtar gerekli."
        if deger is None:
            return "[Hata]: 'kaydet' için deger gerekli."
        return saglayici.kaydet(anahtar, deger, namespace)

    if eylem == "oku":
        if not anahtar:
            return "[Hata]: 'oku' için anahtar gerekli."
        sonuc = saglayici.oku(anahtar, namespace)
        if sonuc is None:
            return f"[Yok] '{anahtar}' → '{namespace}' bulunamadı."
        return str(sonuc)

    if eylem == "ara":
        if not sorgu.strip():
            return "[Hata]: 'ara' için sorgu gerekli."
        try:
            limit = max(1, min(int(limit), 50))
        except (TypeError, ValueError):
            limit = 5
        sonuclar = saglayici.ara(sorgu.strip(), limit)
        return _format_ara(sonuclar, tur)

    if eylem == "sil":
        if not anahtar:
            return "[Hata]: 'sil' için anahtar gerekli."
        return saglayici.sil(anahtar, namespace)

    if eylem == "durum":
        d = saglayici.durum()
        satirlar = [f"[Durum] {tur}:"]
        for k, v in d.items():
            satirlar.append(f"  {k}: {v}")
        return "\n".join(satirlar)

    # Bu noktaya ulaşılmamalı — frozenset guard zaten yakalar
    return f"[Hata]: Beklenmeyen durum — eylem='{eylem}'"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet(
        "MEMORY_PROVIDER",
        run,
        "Bellek sağlayıcı (chromadb/file/sqlite/redis): "
        "kaydet/oku/ara/sil/durum",
    )
