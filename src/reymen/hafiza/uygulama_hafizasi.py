# -*- coding: utf-8 -*-
"""
uygulama_hafizasi.py â€” Her uygulama iÃ§in ayrÄ± kalÄ±cÄ± hafÄ±za.
"Photoshop'ta yeni proje ÅŸÃ¶yle aÃ§Ä±lÄ±r", "X uygulamasÄ±nda kaydet ÅŸurada"
gibi uygulamaya Ã¶zel iÅŸlem bilgilerini saklar ve geri Ã§aÄŸÄ±rÄ±r.

YapÄ±: .ReYMeN/uygulama_hafizasi/<uygulama_adi>.json
Her uygulamanÄ±n: islemler (ad -> adÄ±mlar), makrolar (ad -> makro dosyasÄ±), notlar.
"""

import json
import os


class UygulamaHafizasi:
    def __init__(self, kok=".ReYMeN/uygulama_hafizasi"):
        self.kok = kok
        os.makedirs(kok, exist_ok=True)

    def _yol(self, uygulama):
        guvenli = "".join(c if c.isalnum() else "_" for c in uygulama.lower())
        return os.path.join(self.kok, f"{guvenli}.json")

    def _yukle(self, uygulama):
        yol = self._yol(uygulama)
        if os.path.exists(yol):
            with open(yol, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"uygulama": uygulama, "islemler": {}, "makrolar": {}, "notlar": []}

    def _kaydet(self, uygulama, veri):
        with open(self._yol(uygulama), "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=2)

    def islem_kaydet(self, uygulama, islem_adi, adimlar):
        """Bir uygulamadaki bir iÅŸlemin adÄ±mlarÄ±nÄ± kaydeder.
        Ã–rn: islem_kaydet('TinyTask', 'yeni proje', ['Dosya menusu', 'Yeni', ...])"""
        veri = self._yukle(uygulama)
        veri["islemler"][islem_adi] = adimlar
        self._kaydet(uygulama, veri)
        return f"[UygHafÄ±za]: '{uygulama}' iÃ§in '{islem_adi}' kaydedildi."

    def islem_cagir(self, uygulama, islem_adi):
        """KayÄ±tlÄ± iÅŸlemin adÄ±mlarÄ±nÄ± geri getirir."""
        veri = self._yukle(uygulama)
        if islem_adi in veri["islemler"]:
            return veri["islemler"][islem_adi]
        return None

    def makro_bagla(self, uygulama, islem_adi, makro_dosyasi):
        """Bir iÅŸleme kayÄ±tlÄ± bir makro dosyasÄ± baÄŸlar."""
        veri = self._yukle(uygulama)
        veri["makrolar"][islem_adi] = makro_dosyasi
        self._kaydet(uygulama, veri)
        return f"[UygHafÄ±za]: '{islem_adi}' makrosu '{uygulama}' altÄ±na baÄŸlandÄ±."

    def not_ekle(self, uygulama, metin):
        veri = self._yukle(uygulama)
        veri["notlar"].append(metin)
        self._kaydet(uygulama, veri)
        return "[UygHafÄ±za]: Not eklendi."

    def ozet(self, uygulama):
        veri = self._yukle(uygulama)
        islemler = list(veri["islemler"].keys())
        return f"[{uygulama}] Bilinen iÅŸlemler: {', '.join(islemler) or 'yok'}"

    def tum_uygulamalar(self):
        return [f[:-5] for f in os.listdir(self.kok) if f.endswith(".json")]


if __name__ == "__main__":
    h = UygulamaHafizasi(kok="/tmp/ReYMeN_uyg")
    print(
        h.islem_kaydet(
            "TinyTask",
            "yeni proje",
            ["File menÃ¼sÃ¼ aÃ§", "Record'a bas", "iÅŸlemi yap", "Save"],
        )
    )
    print(h.islem_cagir("TinyTask", "yeni proje"))
    print(h.ozet("TinyTask"))
