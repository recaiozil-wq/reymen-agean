# -*- coding: utf-8 -*-
"""memory_providers/file_provider.py — JSON dosya bellek."""

from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BellekSaglayici
import logging
logger = logging.getLogger(__name__)


class FileBellek(BellekSaglayici):
    """JSON dosyası ile basit anahtar-değer bellek."""

    def __init__(self, dosya: str = ".ReYMeN/memories/hafiza.json"):
        self._dosya = Path(dosya).resolve()
        self._veri: Dict = {}
        self._yukle()

    # ── İç yardımcılar ────────────────────────────────────────
    def _yukle(self) -> None:
        if not self._dosya.exists():
            self._veri = {}
            return
        try:
            with open(self._dosya, "r", encoding="utf-8") as f:
                yuklenen = json.load(f)
            # Beklenen yapı: {namespace: {anahtar: deger}}
            if isinstance(yuklenen, dict):
                self._veri = yuklenen
            else:
                # Eski flat format → default namespace'e taşı
                self._veri = {"default": yuklenen}
        except (json.JSONDecodeError, OSError):
            # Bozuk dosya — yedek al, boş başla
            self._veri = {}
            yedek = self._dosya.with_suffix(".bozuk.json")
            try:
                self._dosya.rename(yedek)
            except OSError:
                logger.warning("[fix_01_sessiz_except] OSError")

    def _diske_yaz(self) -> None:
        """Atomic write: temp file → rename; crash'te veri kaybı yok."""
        self._dosya.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_yol = tempfile.mkstemp(
            dir=self._dosya.parent, suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._veri, f, ensure_ascii=False, indent=2)
            # Windows uyumlu atomic replace
            os.replace(tmp_yol, self._dosya)
        except Exception:
            try:
                os.unlink(tmp_yol)
            except OSError:
                logger.warning("[fix_01_sessiz_except] OSError")
            raise

    # ── Interface ─────────────────────────────────────────────
    def kaydet(self, anahtar: str, deger: Any,
               namespace: str = "default") -> str:
        if not anahtar:
            return "[Hata]: anahtar boş olamaz."
        self._veri.setdefault(namespace, {})[anahtar] = deger
        try:
            self._diske_yaz()
        except OSError as e:
            return f"[Hata]: Diske yazılamadı — {e}"
        return f"[Tamam] FileBellek: '{anahtar}' → '{namespace}' kaydedildi."

    def oku(self, anahtar: str,
            namespace: str = "default") -> Optional[Any]:
        return self._veri.get(namespace, {}).get(anahtar)

    def ara(self, sorgu: str, limit: int = 5) -> List[Dict]:
        sonuc: List[Dict] = []
        sorgu_kucuk = sorgu.lower()
        for ns, veriler in self._veri.items():
            if not isinstance(veriler, dict):
                continue
            for anahtar, deger in veriler.items():
                deger_str = str(deger)
                if sorgu_kucuk in anahtar.lower() or sorgu_kucuk in deger_str.lower():
                    sonuc.append({
                        "id":     f"{ns}:{anahtar}",
                        "icerik": self._sinirla(deger_str),
                    })
                if len(sonuc) >= limit:
                    return sonuc
        return sonuc

    def sil(self, anahtar: str, namespace: str = "default") -> str:
        ns_veri = self._veri.get(namespace, {})
        if anahtar not in ns_veri:
            return f"[Hata]: '{anahtar}' → '{namespace}' bulunamadı."
        del ns_veri[anahtar]
        try:
            self._diske_yaz()
        except OSError as e:
            return f"[Hata]: Diske yazılamadı — {e}"
        return f"[Tamam] FileBellek: '{anahtar}' silindi."

    def durum(self) -> Dict:
        toplam = sum(
            len(v) for v in self._veri.values() if isinstance(v, dict)
        )
        return {
            "tur":       "file",
            "aktif":     True,
            "kayit":     toplam,
            "namespace": len(self._veri),
            "dosya":     str(self._dosya),
        }
