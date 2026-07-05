# -*- coding: utf-8 -*-
"""
memory_manager.py â€” ReYMeN kalÄ±cÄ± hafÄ±za yÃ¶neticisi.

ReYMeN'teki MEMORY.md + USER.md sisteminin ReYMeN versiyonu.
Her oturum baÅŸÄ±nda hafÄ±zayÄ± yÃ¼kler, gerektiÄŸinde gÃ¼nceller.

KullanÄ±m:
    >>> from reymen.hafiza.memory_manager import MemoryManager
    >>> mm = MemoryManager()
    >>> hafiza = mm.yukle()
    >>> mm.ekle("memory", "KullanÄ±cÄ± kÄ±sa cevaplarÄ± sever")
    >>> print(mm.ozet())
"""

import os
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

MEMORY_LIMIT_CHARS = 50000
USER_LIMIT_CHARS = 50000


class MemoryManager:
    """KalÄ±cÄ± hafÄ±za yÃ¶neticisi.

    MEMORY.md: AjanÄ±n kalÄ±cÄ± notlarÄ± (ortam, Ã¶ÄŸrenilen bilgiler).
    USER.md: KullanÄ±cÄ± profili (tercihler, iletiÅŸim tarzÄ±).
    """

    def __init__(self, memory_path: str = None, user_path: str = None):
        """HafÄ±za yÃ¶neticisini baÅŸlat.

        Args:
            memory_path: MEMORY.md tam yolu (None=varsayÄ±lan)
            user_path: USER.md tam yolu (None=varsayÄ±lan)
        """
        kok = Path(__file__).parent.resolve()
        self.memory_path = Path(memory_path) if memory_path else kok / "MEMORY.md"
        self.user_path = Path(user_path) if user_path else kok / "USER.md"

    def yukle(self) -> dict:
        """MEMORY.md ve USER.md'yi oku.

        Returns:
            {"memory": str, "user": str, "memory_limit": int, "user_limit": int}
        """
        return {
            "memory": self._oku(self.memory_path),
            "user": self._oku(self.user_path),
            "memory_limit": MEMORY_LIMIT_CHARS,
            "user_limit": USER_LIMIT_CHARS,
        }

    def kaydet(self, memory_icerik: str = None, user_icerik: str = None) -> bool:
        """GÃ¼ncellenmiÅŸ hafÄ±zayÄ± dosyaya yaz.

        Args:
            memory_icerik: MEMORY.md iÃ§in yeni iÃ§erik (None=dokunma)
            user_icerik: USER.md iÃ§in yeni iÃ§erik (None=dokunma)

        Returns:
            BaÅŸarÄ±lÄ± mÄ±?
        """
        try:
            if memory_icerik is not None:
                self._yaz(self.memory_path, memory_icerik[:MEMORY_LIMIT_CHARS])
            if user_icerik is not None:
                self._yaz(self.user_path, user_icerik[:USER_LIMIT_CHARS])
            return True
        except Exception as e:
            print(f"[MemoryManager] KayÄ±t hatasÄ±: {e}")
            return False

    def guncelle(self, hedef: str, anahtar: str, deger: str) -> bool:
        """HafÄ±zada bir anahtarÄ± gÃ¼ncelle.

        Args:
            hedef: "memory" veya "user"
            anahtar: BaÅŸlÄ±k (Ã¶rn: "KullanÄ±cÄ± Tercihleri")
            deger: Yeni deÄŸer

        Returns:
            BaÅŸarÄ±lÄ± mÄ±?
        """
        dosya = self.memory_path if hedef == "memory" else self.user_path
        icerik = self._oku(dosya)
        sinir = MEMORY_LIMIT_CHARS if hedef == "memory" else USER_LIMIT_CHARS

        # AnahtarÄ± bul ve gÃ¼ncelle, yoksa ekle
        yeni = self._anahtar_guncelle(icerik, anahtar, deger)

        if len(yeni) > sinir:
            print(
                f"[MemoryManager] UYARI: {dosya.name} limit aÅŸÄ±ldÄ± ({len(yeni)}/{sinir})"
            )
            yeni = yeni[:sinir]

        return self._yaz(dosya, yeni)

    def ekle(self, hedef: str, metin: str) -> bool:
        """HafÄ±zaya yeni bilgi ekle (sona ekler).

        Args:
            hedef: "memory" veya "user"
            metin: Eklenecek metin

        Returns:
            BaÅŸarÄ±lÄ± mÄ±?
        """
        dosya = self.memory_path if hedef == "memory" else self.user_path
        icerik = self._oku(dosya)
        sinir = MEMORY_LIMIT_CHARS if hedef == "memory" else USER_LIMIT_CHARS

        yeni = icerik + f"\n- {metin}\n"

        if len(yeni) > sinir:
            print(
                f"[MemoryManager] UYARI: {dosya.name} limit aÅŸÄ±ldÄ± ({len(yeni)}/{sinir})"
            )
            yeni = yeni[-sinir:]

        return self._yaz(dosya, yeni)

    def ozet(self) -> str:
        """HafÄ±za Ã¶zeti: karakter sayÄ±sÄ±, doluluk oranÄ±."""
        m_icerik = self._oku(self.memory_path)
        u_icerik = self._oku(self.user_path)

        return (
            f"ğŸ“ MEMORY.md: {len(m_icerik):,}/{MEMORY_LIMIT_CHARS:,} karakter "
            f"(%{len(m_icerik)*100//MEMORY_LIMIT_CHARS})\n"
            f"ğŸ‘¤ USER.md: {len(u_icerik):,}/{USER_LIMIT_CHARS:,} karakter "
            f"(%{len(u_icerik)*100//USER_LIMIT_CHARS})"
        )

    def _oku(self, dosya: Path) -> str:
        """DosyayÄ± oku, yoksa boÅŸ dÃ¶n."""
        try:
            if dosya.exists():
                return dosya.read_text(encoding="utf-8")
        except Exception as _e:
            logger.warning("[MemoryManager] except Exception (L138): %s", Exception)
            pass
        return ""

    def _yaz(self, dosya: Path, icerik: str) -> bool:
        """Dosyaya yaz."""
        try:
            dosya.parent.mkdir(parents=True, exist_ok=True)
            dosya.write_text(icerik, encoding="utf-8")
            return True
        except Exception as e:
            print(f"[MemoryManager] Yazma hatasÄ±: {e}")
            return False

    def _anahtar_guncelle(self, icerik: str, anahtar: str, deger: str) -> str:
        """Ä°Ã§erikte bir baÅŸlÄ±k altÄ±ndaki deÄŸeri gÃ¼ncelle."""
        satirlar = icerik.split("\n")
        yeni = []
        hedef_baslik = f"## {anahtar}"
        bulundu = False
        baslik_satiri = -1

        for i, satir in enumerate(satirlar):
            if satir.strip().startswith(f"## {anahtar}"):
                baslik_satiri = i
                bulundu = True
                yeni.append(satir)
            elif baslik_satiri >= 0 and i > baslik_satiri:
                # BaÅŸlÄ±ktan sonraki boÅŸ satÄ±r veya iÃ§erik
                if satir.strip().startswith("##"):
                    # Yeni baÅŸlÄ±k baÅŸladÄ±, eski baÅŸlÄ±ÄŸÄ± atla
                    yeni.append(satir)
                    baslik_satiri = -1
                elif not bulundu:
                    yeni.append(deger)
                    bulundu = True
                else:
                    # Eski iÃ§eriÄŸi atla
                    continue
            else:
                yeni.append(satir)

        # BaÅŸlÄ±k hiÃ§ bulunamadÄ±ysa ekle
        if baslik_satiri == -1 and anahtar:
            yeni.append(f"\n## {anahtar}")
            yeni.append(deger)

        return "\n".join(yeni)


# Tekil nesne (singleton)
_singleton = None


def get_memory() -> MemoryManager:
    """Tekil MemoryManager Ã¶rneÄŸini dÃ¶ndÃ¼r."""
    global _singleton
    if _singleton is None:
        _singleton = MemoryManager()
    return _singleton


def hafiza_yukle() -> dict:
    """KÄ±sayol: hafÄ±zayÄ± yÃ¼kle."""
    return get_memory().yukle()


def hafiza_ekle(hedef: str, metin: str) -> bool:
    """KÄ±sayol: hafÄ±zaya bilgi ekle."""
    return get_memory().ekle(hedef, metin)


def hafiza_guncelle(hedef: str, anahtar: str, deger: str) -> bool:
    """KÄ±sayol: hafÄ±zada gÃ¼ncelle."""
    return get_memory().guncelle(hedef, anahtar, deger)


def hafiza_ozet() -> str:
    """KÄ±sayol: hafÄ±za Ã¶zeti."""
    return get_memory().ozet()
