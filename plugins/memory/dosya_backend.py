# -*- coding: utf-8 -*-
"""plugins/memory/dosya_backend.py — JSON Dosya Memory Backend.

Basit anahtar-deger deposu. .ReYMeN/memories/ klasorunde calisir.
ChromaBag bagli olmadiginda yedek olarak kullanilir.
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class DosyaBackend:
    """JSON dosya tabanli basit bellek backend'i.

    .ReYMeN/memories/ klasorunde tek bir JSON dosyasi ile calisir.

    Fonksiyonlar:
        kaydet(anahtar, deger) -> str
        oku(anahtar) -> str
        listele() -> str
        sil(anahtar) -> str
    """

    def __init__(self, dosya_adi: str = "bellek.json"):
        """DosyaBackend baslatma.

        Args:
            dosya_adi: JSON dosya adi (varsayilan: bellek.json)
        """
        self._dosya_yolu = self._memories_klasoru() / dosya_adi
        self._veri: dict[str, str] = {}
        self._yukle()

    @staticmethod
    def _memories_klasoru() -> Path:
        """.ReYMeN/memories/ klasorunu bulur veya olusturur."""
        # Proje kokune gore .ReYMeN/memories/
        proje_kok = Path(__file__).resolve().parent.parent.parent
        memories_dir = proje_kok / ".ReYMeN" / "memories"
        memories_dir.mkdir(parents=True, exist_ok=True)
        return memories_dir

    def _yukle(self):
        """JSON dosyasindan veriyi yukler."""
        try:
            if self._dosya_yolu.exists():
                with open(self._dosya_yolu, "r", encoding="utf-8") as f:
                    self._veri = json.load(f)
            else:
                self._veri = {}
                self._kaydet_dosya()
        except (json.JSONDecodeError, Exception) as e:
            logger.warning("Bellek dosyasi yuklenemedi, yeniden baslatiliyor: %s", e)
            self._veri = {}
            self._kaydet_dosya()

    def _kaydet_dosya(self):
        """Veriyi JSON dosyasina kaydeder."""
        try:
            with open(self._dosya_yolu, "w", encoding="utf-8") as f:
                json.dump(self._veri, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Bellek dosyasi yazilamadi: %s", e)

    def kaydet(self, anahtar: str, deger: str) -> str:
        """Bir anahtar-deger ikilisini hafizaya kaydeder.

        Args:
            anahtar: Kayit anahtari
            deger: Kaydedilecek deger (metin)

        Returns:
            str: Islem sonucu
        """
        if not anahtar:
            return "[DosyaMemory]: Anahtar gerekli."
        if deger is None:
            deger = ""

        try:
            self._veri[anahtar] = str(deger)
            self._kaydet_dosya()
            return f"[DosyaMemory]: '{anahtar}' kaydedildi."
        except Exception as e:
            return f"[DosyaMemory]: Kaydetme hatasi - {e}"

    def oku(self, anahtar: str) -> str:
        """Bir anahtarin degerini hafizadan okur.

        Args:
            anahtar: Okunacak anahtar

        Returns:
            str: Anahtarin degeri veya hata mesaji
        """
        if not anahtar:
            return "[DosyaMemory]: Anahtar gerekli."

        try:
            deger = self._veri.get(anahtar)
            if deger is None:
                return f"[DosyaMemory]: '{anahtar}' bulunamadi."
            return f"[DosyaMemory]: {anahtar} = {deger}"
        except Exception as e:
            return f"[DosyaMemory]: Okuma hatasi - {e}"

    def listele(self) -> str:
        """Hafizadaki tum anahtarlari listeler.

        Returns:
            str: Anahtar listesi
        """
        try:
            if not self._veri:
                return "[DosyaMemory]: Hafiza bos."

            sonuc = [f"[DosyaMemory]: Toplam {len(self._veri)} kayit:"]
            for i, (anahtar, deger) in enumerate(sorted(self._veri.items()), 1):
                deger_str = str(deger)[:80]
                sonuc.append(f"  {i}. {anahtar} = {deger_str}")
            return "\n".join(sonuc)
        except Exception as e:
            return f"[DosyaMemory]: Listeleme hatasi - {e}"

    def sil(self, anahtar: str) -> str:
        """Bir anahtari hafizadan siler.

        Args:
            anahtar: Silinecek anahtar

        Returns:
            str: Islem sonucu
        """
        if not anahtar:
            return "[DosyaMemory]: Anahtar gerekli."

        try:
            if anahtar in self._veri:
                del self._veri[anahtar]
                self._kaydet_dosya()
                return f"[DosyaMemory]: '{anahtar}' silindi."
            return f"[DosyaMemory]: '{anahtar}' bulunamadi."
        except Exception as e:
            return f"[DosyaMemory]: Silme hatasi - {e}"

    def __repr__(self) -> str:
        return f"<DosyaBackend dosya={self._dosya_yolu.name} kayit={len(self._veri)}>"
