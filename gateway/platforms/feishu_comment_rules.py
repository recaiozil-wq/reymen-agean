# -*- coding: utf-8 -*-
"""gateway/platforms/feishu_comment_rules.py — Feishu Yorum Kurallari.

Otomatik yorum filtreleme, bildirim kurallari, sessiz saatler.
"""

import os
import re
import time
import logging
from datetime import datetime, time as dt_time, timedelta

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. FILTRELEME KURALLARI
# ---------------------------------------------------------------------------

class YorumFiltre:
    """Yorum filtreleme kurallarini yonetir."""

    def __init__(self):
        self.kurallar = []
        self._varsayilan_kurallari_yukle()

    def _varsayilan_kurallari_yukle(self):
        """Varsayilan filtreleme kurallarini yukle."""
        self.ekle("spam", r"(?:https?://[^\s]+){3,}", "Cok fazla baglanti (spam)")
        self.ekle("reklam", r"\b(reklam|sponsor|üyelik[^ ]* kazan|bedava para)\b", "Rekam icerigi")
        self.ekle("kufur", r"\b(?:amk|aq|sik|s\*k)\b", "Uygunsuz dil")

    def ekle(self, etiket: str, desen: str, aciklama: str = ""):
        """Yeni filtre kurali ekle.

        Args:
            etiket: Kural etiketi
            desen: Regex deseni
            aciklama: Kural aciklamasi (opsiyonel)
        """
        try:
            self.kurallar.append({
                "etiket": etiket,
                "desen": re.compile(desen, re.IGNORECASE),
                "aciklama": aciklama,
            })
        except re.error as e:
            logger.error("Gecersiz regex '%s': %s", desen, e)

    def kaldir(self, etiket: str) -> bool:
        """Kural kaldir.

        Args:
            etiket: Kural etiketi

        Returns:
            bool: Kaldirildi ise True
        """
        onceki = len(self.kurallar)
        self.kurallar = [k for k in self.kurallar if k["etiket"] != etiket]
        return len(self.kurallar) < onceki

    def filtrele(self, metin: str) -> dict:
        """Metni filtre kurallarina gore kontrol et.

        Args:
            metin: Kontrol edilecek yorum metni

        Returns:
            dict: {"gecerli": bool, "eslesenler": [{"etiket": ..., "aciklama": ...}, ...]}
        """
        eslesenler = []
        for kural in self.kurallar:
            if kural["desen"].search(metin):
                eslesenler.append({
                    "etiket": kural["etiket"],
                    "aciklama": kural["aciklama"],
                })

        return {
            "gecerli": len(eslesenler) == 0,
            "eslesenler": eslesenler,
        }

    def listele(self) -> list:
        """Tum filtre kurallarini listele.

        Returns:
            list: Kural listesi
        """
        return [
            {"etiket": k["etiket"], "aciklama": k["aciklama"]}
            for k in self.kurallar
        ]


# ---------------------------------------------------------------------------
# 2. BILDIRIM KURALLARI
# ---------------------------------------------------------------------------

class BildirimKurali:
    """Bildirim kurali tanimi."""

    def __init__(self, anahtar_kelime: str, hedef: str, oncelik: str = "normal",
                 aciklama: str = ""):
        self.anahtar_kelime = anahtar_kelime
        self.hedef = hedef
        self.oncelik = oncelik  # "dusuk", "normal", "yuksek", "kritik"
        self.aciklama = aciklama
        self._desen = re.compile(re.escape(anahtar_kelime), re.IGNORECASE)

    def eslesme(self, metin: str) -> bool:
        """Metin anahtar kelimeyi iceriyor mu?

        Args:
            metin: Kontrol edilecek metin

        Returns:
            bool: Eslesme varsa True
        """
        return bool(self._desen.search(metin))


class BildirimYoneticisi:
    """Bildirim kurallarini yonetir."""

    def __init__(self):
        self.kurallar: list[BildirimKurali] = []

    def kural_ekle(self, anahtar_kelime: str, hedef: str,
                   oncelik: str = "normal", aciklama: str = ""):
        """Yeni bildirim kurali ekle.

        Args:
            anahtar_kelime: Tetikleyici kelime
            hedef: Bildirim gonderilecek hedef
            oncelik: Oncelik seviyesi
            aciklama: Kural aciklamasi
        """
        self.kurallar.append(
            BildirimKurali(anahtar_kelime, hedef, oncelik, aciklama)
        )

    def kural_kaldir(self, anahtar_kelime: str) -> bool:
        """Kural kaldir.

        Args:
            anahtar_kelime: Silinecek anahtar kelime

        Returns:
            bool: Kaldirildi ise True
        """
        onceki = len(self.kurallar)
        self.kurallar = [k for k in self.kurallar if k.anahtar_kelime != anahtar_kelime]
        return len(self.kurallar) < onceki

    def kontrol_et(self, metin: str) -> list:
        """Metni tum bildirim kurallarina gore kontrol et.

        Args:
            metin: Kontrol edilecek metin

        Returns:
            list: [{"anahtar_kelime": ..., "hedef": ..., "oncelik": ...}, ...]
        """
        eslesenler = []
        for kural in self.kurallar:
            if kural.eslesme(metin):
                eslesenler.append({
                    "anahtar_kelime": kural.anahtar_kelime,
                    "hedef": kural.hedef,
                    "oncelik": kural.oncelik,
                    "aciklama": kural.aciklama,
                })
        return eslesenler

    def listele(self) -> list:
        """Tum kurallari listele.

        Returns:
            list: Kural listesi
        """
        return [
            {
                "anahtar_kelime": k.anahtar_kelime,
                "hedef": k.hedef,
                "oncelik": k.oncelik,
                "aciklama": k.aciklama,
            }
            for k in self.kurallar
        ]


# ---------------------------------------------------------------------------
# 3. SESSIZ SAATLER
# ---------------------------------------------------------------------------

class SessizSaatler:
    """Bildirimlerin sessize alindigi saat araliklarini yonetir."""

    def __init__(self):
        self.araliklar: list[dict] = []

    def ekle(self, baslangic: str, bitis: str, gunler: list = None,
             aciklama: str = ""):
        """Sessiz saat araligi ekle.

        Args:
            baslangic: Baslangic saati (HH:MM formatinda)
            bitis: Bitis saati (HH:MM formatinda)
            gunler: Hangi gunler gecerli (None = her gun, 0=Pazartesi ... 6=Pazar)
            aciklama: Aciklama (opsiyonel)
        """
        try:
            bas_saat = dt_time(
                int(baslangic.split(":")[0]),
                int(baslangic.split(":")[1])
            )
            bit_saat = dt_time(
                int(bitis.split(":")[0]),
                int(bitis.split(":")[1])
            )
        except (ValueError, IndexError):
            logger.error("Gecersiz saat formati: %s - %s", baslangic, bitis)
            return

        self.araliklar.append({
            "baslangic": bas_saat,
            "bitis": bit_saat,
            "gunler": gunler,
            "aciklama": aciklama,
        })

    def kaldir(self, baslangic: str, bitis: str) -> bool:
        """Sessiz saat araligi kaldir.

        Args:
            baslangic: Baslangic saati (HH:MM)
            bitis: Bitis saati (HH:MM)

        Returns:
            bool: Kaldirildi ise True
        """
        onceki = len(self.araliklar)
        self.araliklar = [
            a for a in self.araliklar
            if not (a["baslangic"].strftime("%H:%M") == baslangic
                    and a["bitis"].strftime("%H:%M") == bitis)
        ]
        return len(self.araliklar) < onceki

    def sessiz_mi(self, su_an: datetime = None) -> bool:
        """Simdiki zamanin sessiz saatlere denk gelip gelmedigini kontrol et.

        Args:
            su_an: Kontrol edilecek zaman (None = simdiki zaman)

        Returns:
            bool: Sessiz saatlerde ise True
        """
        if su_an is None:
            su_an = datetime.now()

        bugun = su_an.weekday()  # 0=Pazartesi ... 6=Pazar
        simdi = su_an.time()

        for aralik in self.araliklar:
            # Gun kontrolu
            if aralik["gunler"] is not None and bugun not in aralik["gunler"]:
                continue

            # Saat kontrolu
            bas = aralik["baslangic"]
            bit = aralik["bitis"]

            if bas <= bit:
                # Ayni gun icinde (ornek: 22:00 - 08:00 degil, 09:00 - 17:00)
                if bas <= simdi <= bit:
                    return True
            else:
                # Gece yarisini asan aralik (ornek: 22:00 - 08:00)
                if simdi >= bas or simdi <= bit:
                    return True

        return False

    def kalan_sure(self, su_an: datetime = None) -> int:
        """Sessiz saatlerin bitmesine kalan sure (saniye).

        Args:
            su_an: Kontrol edilecek zaman (None = simdiki zaman)

        Returns:
            int: Kalan sure (saniye). Sessiz saatlerde degilse 0.
        """
        if su_an is None:
            su_an = datetime.now()

        if not self.sessiz_mi(su_an):
            return 0

        bugun = su_an.weekday()
        simdi = su_an.time()

        for aralik in self.araliklar:
            if aralik["gunler"] is not None and bugun not in aralik["gunler"]:
                continue

            bas = aralik["baslangic"]
            bit = aralik["bitis"]

            if bas <= bit:
                if bas <= simdi <= bit:
                    bitis_dt = su_an.replace(
                        hour=bit.hour, minute=bit.minute, second=0
                    )
                    return int((bitis_dt - su_an).total_seconds())
            else:
                if simdi >= bas:
                    # Yarin bitiyor
                    bitis_dt = su_an.replace(
                        hour=bit.hour, minute=bit.minute, second=0
                    ) + timedelta(days=1)
                    return int((bitis_dt - su_an).total_seconds())
                elif simdi <= bit:
                    bitis_dt = su_an.replace(
                        hour=bit.hour, minute=bit.minute, second=0
                    )
                    return int((bitis_dt - su_an).total_seconds())

        return 0

    def listele(self) -> list:
        """Tum sessiz saat araliklarini listele.

        Returns:
            list: Aralik listesi
        """
        return [
            {
                "baslangic": a["baslangic"].strftime("%H:%M"),
                "bitis": a["bitis"].strftime("%H:%M"),
                "gunler": a["gunler"],
                "aciklama": a["aciklama"],
            }
            for a in self.araliklar
        ]


# ---------------------------------------------------------------------------
# 4. MODUL SEVIYESI FONKSIYONLAR
# ---------------------------------------------------------------------------

# Varsayilan ornekler
_varsayilan_filtre = YorumFiltre()
_varsayilan_bildirim = BildirimYoneticisi()
_varsayilan_sessiz = SessizSaatler()


def yorum_kontrol(metin: str) -> dict:
    """Yorum metnini tum kurallara gore kontrol et.

    Args:
        metin: Yorum metni

    Returns:
        dict: {
            "gecerli": bool,
            "filtre_sonuc": {...},
            "bildirimler": [...],
            "sessiz_mi": bool,
        }
    """
    filtre_sonuc = _varsayilan_filtre.filtrele(metin)
    bildirimler = _varsayilan_bildirim.kontrol_et(metin)
    sessiz = _varsayilan_sessiz.sessiz_mi()

    return {
        "gecerli": filtre_sonuc["gecerli"],
        "filtre_sonuc": filtre_sonuc,
        "bildirimler": bildirimler,
        "sessiz_mi": sessiz,
    }


def filtre_ekle(etiket: str, desen: str, aciklama: str = ""):
    """Varsayilan filtreye kural ekle."""
    _varsayilan_filtre.ekle(etiket, desen, aciklama)


def bildirim_ekle(anahtar_kelime: str, hedef: str,
                  oncelik: str = "normal", aciklama: str = ""):
    """Varsayilan bildirim yoneticisine kural ekle."""
    _varsayilan_bildirim.kural_ekle(anahtar_kelime, hedef, oncelik, aciklama)


def sessiz_saat_ekle(baslangic: str, bitis: str, gunler: list = None,
                     aciklama: str = ""):
    """Varsayilan sessiz saatlere aralik ekle."""
    _varsayilan_sessiz.ekle(baslangic, bitis, gunler, aciklama)


def durum_raporu() -> dict:
    """Mevcut kural durumunu raporla.

    Returns:
        dict: Filtre, bildirim ve sessiz saat durumu
    """
    return {
        "filtre_kurallari": _varsayilan_filtre.listele(),
        "bildirim_kurallari": _varsayilan_bildirim.listele(),
        "sessiz_saatler": _varsayilan_sessiz.listele(),
        "su_an_sessiz_mi": _varsayilan_sessiz.sessiz_mi(),
    }


def ping() -> bool:
    """Feishu yorum kurallari modulu kontrolu.

    Returns:
        bool: Her zaman True (kural motoru bagimsiz calisir)
    """
    return True


def send_message(hedef: str, mesaj: str, **kwargs) -> dict:
    """Yorum kural durumunu mesaj olarak gonder (goruntuleme amacli).

    Args:
        hedef: Kullanici ID (log amacli)
        mesaj: Mesaj icerigi (kontrol edilecek metin)

    Returns:
        dict: Yorum kontrol sonucu
    """
    try:
        sonuc = yorum_kontrol(mesaj)
        return {
            "durum": "basarili",
            "hedef": hedef,
            "gecerli": sonuc["gecerli"],
            "bildirim_sayisi": len(sonuc["bildirimler"]),
            "sessiz_mi": sonuc["sessiz_mi"],
        }
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}
