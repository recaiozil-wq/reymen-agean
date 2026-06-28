#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
context_files.py — Proje baglam dosyalari (AGENTS.md, CLAUDE.md, .cursorrules).

ReYMeN'teki progressive discovery:
- .hermes.md -> AGENTS.md -> CLAUDE.md -> .cursorrules (ilk eslesen kazanir)
- Alt dizinlere inildikce AGENTS.md otomatik yuklenir
- Prompt injection taramasi + truncation
"""

import os
import re
from pathlib import Path
from typing import Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("reymen.context")
    logging.basicConfig(level=logging.INFO)

# Oncelik sirasi (ilk eslesen kullanilir)
CONTEXT_FILE_PRIORITY = [
    ".hermes.md",
    "HERMES.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".cursorrules",
]

# Guvenlik: prompt injection desenleri
INJECTION_PATTERNS = [
    re.compile(r"ignore all (previous|above)\s+(instructions|commands)", re.I),
    re.compile(r"you are (now|free|released)", re.I),
    re.compile(r"system( prompt)?:\s*(override|ignore)", re.I),
    re.compile(r"forget (everything|all|previous)", re.I),
    re.compile(r"Do not follow.*instructions", re.I),
]

MAX_CONTENT_CHARS = 20_000
MAX_SUBDIR_CHARS = 8_000


def _tara_injection(icerik: str, kaynak: str) -> bool:
    """Prompt injection desenlerini tara. True = guvenli."""
    for pattern in INJECTION_PATTERNS:
        if pattern.search(icerik):
            logger.warning(
                f"Context file injection tespit edildi: {kaynak} "
                f"-> {pattern.pattern[:40]}"
            )
            return False
    return True


def _kirp(icerik: str, max_chars: int, kaynak: str) -> str:
    """Cok uzun icerikleri kirp (bas 70%, son 20%, uyari 10%)."""
    if len(icerik) <= max_chars:
        return icerik

    head = int(max_chars * 0.7)
    tail = int(max_chars * 0.2)
    warning_chars = max_chars - head - tail

    uyari = (
        f"\n\n[... {len(icerik) - head - tail} karakter kirpildi. "
        f"Dosyanin tamami {len(icerik)} karakter. "
        f"read_file ile okuyun.]\n\n"
    )[:warning_chars]

    return icerik[:head] + uyari + icerik[-tail:]


class ContextFileLoader:
    """Baglam dosyalarini bul, yukle, guvenlikten gecir."""

    def __init__(self, calisma_dizini: Optional[str] = None):
        self.calisma_dizini = Path(calisma_dizini or os.getcwd())
        self._yuklenen_dizinler: set[str] = set()
        self._kok_icerik: Optional[str] = None

    def kok_yukle(self) -> Optional[str]:
        """Calisma dizinindeki baglam dosyasini bul ve yukle.

        Oncelik: .hermes.md -> AGENTS.md -> CLAUDE.md -> .cursorrules
        """
        for dosya_adi in CONTEXT_FILE_PRIORITY:
            yol = self.calisma_dizini / dosya_adi
            if yol.exists():
                icerik = self._dosya_yukle(yol)
                if icerik:
                    self._kok_icerik = icerik
                    self._yuklenen_dizinler.add(str(self.calisma_dizini))
                    logger.info(
                        f"Context: {dosya_adi} yuklendi "
                        f"({len(icerik)} chars)"
                    )
                    return icerik

        logger.debug("Context: kok dizinde baglam dosyasi bulunamadi")
        return None

    def alt_dizin_yukle(self, dizin_yolu: str) -> Optional[str]:
        """Bir alt dizindeki AGENTS.md'yi yukle (progressive discovery).

        Args:
            dizin_yolu: Kesfedilen dizin yolu

        Returns:
            Icerik veya None
        """
        dizin = Path(dizin_yolu)
        if not dizin.is_dir():
            dizin = dizin.parent

        # Daha once yuklendiyse atla
        if str(dizin) in self._yuklenen_dizinler:
            return None

        # 5 uste kadar ara
        for parent in [dizin] + list(dizin.parents)[:5]:
            if str(parent) in self._yuklenen_dizinler:
                continue

            for dosya_adi in CONTEXT_FILE_PRIORITY:
                yol = parent / dosya_adi
                if yol.exists() and yol.parent != self.calisma_dizini:
                    icerik = self._dosya_yukle(yol, alt_dizin=True)
                    if icerik:
                        self._yuklenen_dizinler.add(str(parent))
                        logger.info(
                            f"Context: {dosya_adi} kesfedildi "
                            f"({parent.name}/{dosya_adi}, {len(icerik)} chars)"
                        )
                        return icerik

        self._yuklenen_dizinler.add(str(dizin))
        return None

    def _dosya_yukle(
        self, yol: Path, alt_dizin: bool = False
    ) -> Optional[str]:
        """Bir dosyayi oku, injection tara, kirp."""
        try:
            icerik = yol.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.warning(f"Context okunamadi: {yol} -> {e}")
            return None

        # Injection taramasi
        if not _tara_injection(icerik, str(yol)):
            return None

        # Kirp
        max_chars = MAX_SUBDIR_CHARS if alt_dizin else MAX_CONTENT_CHARS
        icerik = _kirp(icerik, max_chars, str(yol))

        return f"## {yol.name}\n\n{icerik}\n"

    @property
    def kok_var_mi(self) -> bool:
        return self._kok_icerik is not None

    def sifirla(self) -> None:
        """Session sonunda state'i sifirla."""
        self._yuklenen_dizinler.clear()
        self._kok_icerik = None


class SubdirectoryHintTracker:
    """Alt dizin kesif takipcisi.

    Her tool cagrisindan sonra dosya yollarini analiz eder,
    henuz yuklenmemis alt dizinlerdeki AGENTS.md'yi bulur.
    """

    def __init__(self, loader: ContextFileLoader):
        self.loader = loader
        self._yeni_ipuclari: list[str] = []

    def yollari_islet(self, dosya_yollari: list[str]) -> list[str]:
        """Dosya yollarindan yeni context ipuclari cikar.

        Args:
            dosya_yollari: Tool argumanlarindan cikarilan dosya yollari

        Returns:
            Yeni yuklenen context icerikleri
        """
        yeni_icerikler = []
        for yol in dosya_yollari:
            icerik = self.loader.alt_dizin_yukle(yol)
            if icerik:
                yeni_icerikler.append(icerik)
                self._yeni_ipuclari.append(yol)
        return yeni_icerikler

    def sifirla(self) -> None:
        self._yeni_ipuclari.clear()
