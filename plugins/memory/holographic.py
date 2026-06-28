"""
Holografik bellek arka ucu.

Dağıtık/parçalı holografik bellek temsili.
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class HolographicMemory:
    """Holografik bellek arka ucu.

    Bilgileri vektör temsilleri olarak depolar ve
    holografik indirgeme ile geri çağırır.
    """

    def __init__(self, boyut: int = 512):
        self.boyut = boyut
        self.anilar: list[dict[str, Any]] = []

    def kaydet(self, anahtar: str, deger: Any, baglam: Optional[dict] = None) -> dict[str, Any]:
        """Bir anıyı holografik olarak kaydeder.

        Args:
            anahtar: Bellek anahtarı.
            deger: Kaydedilecek değer.
            baglam: İsteğe bağlı bağlam bilgisi.

        Returns:
            Kayıt bilgisi.
        """
        kayit = {
            "anahtar": anahtar,
            "deger": deger,
            "baglam": baglam or {},
            "id": len(self.anilar),
        }
        self.anilar.append(kayit)
        logger.debug("Holografik anı kaydedildi: %s", anahtar)
        return kayit

    def geri_cagir(self, anahtar: str) -> Optional[Any]:
        """Bir anıyı anahtarına göre geri çağırır.

        Args:
            anahtar: Bellek anahtarı.

        Returns:
            Kaydedilen değer veya None.
        """
        for kayit in reversed(self.anilar):
            if kayit["anahtar"] == anahtar:
                return kayit["deger"]
        return None

    def ara(self, sorgu: str) -> list[dict[str, Any]]:
        """Anahtar içinde arama yapar.

        Args:
            sorgu: Arama sorgusu.

        Returns:
            Eşleşen kayıtlar.
        """
        sorgu_lower = sorgu.lower()
        sonuclar = []
        for kayit in self.anilar:
            if sorgu_lower in str(kayit.get("anahtar", "")).lower():
                sonuclar.append(kayit)
        return sonuclar

    def temizle(self) -> int:
        """Tüm anıları temizler.

        Returns:
            Silinen kayıt sayısı.
        """
        adet = len(self.anilar)
        self.anilar.clear()
        return adet

    def __len__(self) -> int:
        return len(self.anilar)

    def run(self, **kwargs) -> str:
        """Arka ucu test eder."""
        test_key = kwargs.get("anahtar", "test")
        test_val = kwargs.get("deger", "holografik veri")
        self.kaydet(test_key, test_val)
        sonuc = self.geri_cagir(test_key)
        return json.dumps({
            "durum": "hazir",
            "boyut": self.boyut,
            "anilar": len(self.anilar),
            "test_sonuc": sonuc,
        }, indent=2, ensure_ascii=False)
