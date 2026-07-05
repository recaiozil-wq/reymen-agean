#!/usr/bin/env python3
"""
web_test_loop.py â€” WEB â†’ UYGULA â†’ PUANLA â†’ KARAR dÃ¶ngÃ¼sÃ¼.

Ajan web'den yeni bilgi bulur, eski bilgiyle test eder,
puanlar ve hangisinin daha iyi olduÄŸuna karar verir.

5 TETÄ°KLEYÄ°CÄ°:
1. HafÄ±za boÅŸ â†’ anÄ±nda web
2. GÃ¶rev baÅŸarÄ±sÄ±z (2. hata) â†’ web
3. GÃ¼ven < 0.5 â†’ web
4. GeÃ§erlilik geÃ§miÅŸ â†’ arka planda web
5. Ã‡eliÅŸki â†’ web
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable
from datetime import date

logger = logging.getLogger(__name__)


# â”€â”€ Veri YapÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class TestSonucu:
    """Bir yÃ¶ntemin test sonucu."""

    yontem_adi: str
    hiz_sn: float  # KaÃ§ saniye sÃ¼rdÃ¼? (dÃ¼ÅŸÃ¼k iyi)
    basari: bool  # Hata verdi mi? (True=baÅŸarÄ±lÄ±)
    cikti_dogru: bool  # Ã‡Ä±ktÄ± doÄŸru mu?
    guvenlik: float  # 0.0-1.0 (1.0=gÃ¼venli)
    kaynak_guven: float  # KaynaÄŸÄ±n gÃ¼venilirliÄŸi (web veya hafÄ±za)

    def puan(self) -> float:
        """Toplam puan [0.0, 1.0]"""
        p = 0.0
        # HÄ±z: 1sn altÄ± = 1.0, 60sn Ã¼stÃ¼ = 0.0
        p += max(0, 1.0 - self.hiz_sn / 60.0) * 0.2
        # BaÅŸarÄ±: hata yoksa 1.0
        p += (1.0 if self.basari else 0.0) * 0.3
        # Ã‡Ä±ktÄ± doÄŸruluÄŸu
        p += (1.0 if self.cikti_dogru else 0.0) * 0.2
        # GÃ¼venlik
        p += self.guvenlik * 0.15
        # Kaynak gÃ¼venilirliÄŸi
        p += self.kaynak_guven * 0.15
        return round(p, 4)


# â”€â”€ 5 Tetikleyici â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

TETIKLEYICI_TANIMLARI = {
    1: {
        "ad": "Hafiza Bos",
        "kosul": "once_hafiza.ara() â†’ bulunamadi",
        "ne_zaman": "Aninda web'e git",
        "ornek": "Yeni tool soruldu, hic bilmiyoruz",
    },
    2: {
        "ad": "Guven Dusuk",
        "kosul": "guven_skoru < 0.5",
        "ne_zaman": "Web'den dogrula",
        "ornek": "1 basari, 3 hata â†’ guven=0.25",
    },
    3: {
        "ad": "Gorev Basarisiz",
        "kosul": "2. hatadan sonra web'e git",
        "ne_zaman": "Retry 1 hata + Retry 2 hata â†’ web",
        "ornek": "Komut calismadi, neden?",
    },
    4: {
        "ad": "Gecerlilik Suresi Doldu",
        "kosul": "gecerlilik_tarihi < bugun",
        "ne_zaman": "Arka planda web'den tazele",
        "ornek": "6 ay once ogrendik, tool guncellenmis olabilir",
    },
    5: {
        "ad": "Celiski",
        "kosul": "Video/kullanici hafizadakinden farkli sey soyledi",
        "ne_zaman": "Web'den hakem karar al",
        "ornek": "Eski bilgi ile yeni bilgi uyusmuyor",
    },
}

ONCELIK_SIRASI = [1, 3, 2, 4, 5]
# 1. Hafiza bos â†’ aninda web
# 2. Gorev basarisiz (2. hata) â†’ web
# 3. Guven < 0.5 â†’ web
# 4. Gecerlilik gecmis â†’ arka planda web
# 5. Celiski â†’ web


def tetikleyici_kontrol(tetik_id: int, **kwargs) -> bool:
    """Belirtilen tetikleyicinin sartini kontrol et."""
    if tetik_id == 1:
        # Hafiza BoÅŸ: once_hafiza.ara() boÅŸ dÃ¶ndÃ¼ mÃ¼?
        return kwargs.get("hafiza_bos", False)

    elif tetik_id == 2:
        # GÃ¼ven DÃ¼ÅŸÃ¼k: guven_skoru < 0.5
        return kwargs.get("guven_skoru", 1.0) < 0.5

    elif tetik_id == 3:
        # GÃ¶rev BaÅŸarÄ±sÄ±z: 2. hatadan sonra
        return kwargs.get("basarisiz_deneme_sayisi", 0) >= 2

    elif tetik_id == 4:
        # GeÃ§erlilik SÃ¼resi Doldu
        gecerlilik = kwargs.get("gecerlilik_tarihi")
        if gecerlilik:
            return str(gecerlilik) < str(date.today())
        return False

    elif tetik_id == 5:
        # Ã‡eliÅŸki: iki farklÄ± bilgi Ã§akÄ±ÅŸÄ±yor
        return kwargs.get("celiski_var", False)

    return False


def hangi_tetikleyici(
    hafiza_bos: bool = False,
    guven_skoru: float = 1.0,
    basarisiz_deneme_sayisi: int = 0,
    gecerlilik_tarihi: str | None = None,
    celiski_var: bool = False,
) -> tuple[int | None, dict]:
    """
    Hangi tetikleyicinin ateÅŸlendiÄŸini bul.

    Returns:
        (tetikleyici_id, tetikleyici_bilgisi) veya (None, {})
    """
    kwargs = {
        "hafiza_bos": hafiza_bos,
        "guven_skoru": guven_skoru,
        "basarisiz_deneme_sayisi": basarisiz_deneme_sayisi,
        "gecerlilik_tarihi": gecerlilik_tarihi,
        "celiski_var": celiski_var,
    }

    for tid in ONCELIK_SIRASI:
        if tetikleyici_kontrol(tid, **kwargs):
            return tid, TETIKLEYICI_TANIMLARI[tid]

    return None, {}


# â”€â”€ Puanlama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

PUAN_KRITERLERI = {
    "hiz": {"agirlik": 0.2, "aciklama": "Kac saniyede tamamlandi?"},
    "basari": {"agirlik": 0.3, "aciklama": "Hata verdi mi?"},
    "cikti": {"agirlik": 0.2, "aciklama": "Cikti dogru mu?"},
    "guvenlik": {"agirlik": 0.15, "aciklama": "Guvenli mi?"},
    "kaynak": {"agirlik": 0.15, "aciklama": "Kaynagin guvenilirligi?"},
}


def puanla(
    yontem_adi: str,
    hiz_sn: float,
    basari: bool,
    cikti_dogru: bool,
    guvenlik: float,
    kaynak_guven: float,
) -> TestSonucu:
    """Bir yÃ¶ntemi puanla ve TestSonucu dÃ¶ndÃ¼r."""
    return TestSonucu(
        yontem_adi=yontem_adi,
        hiz_sn=hiz_sn,
        basari=basari,
        cikti_dogru=cikti_dogru,
        guvenlik=guvenlik,
        kaynak_guven=kaynak_guven,
    )


# â”€â”€ Karar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class KararSonucu:
    kazanan: str
    kaybeden: str
    fark: float
    gerekce: str
    eski_korundu: bool


def karar_ver(eski: TestSonucu, yeni: TestSonucu) -> KararSonucu:
    """Ä°ki yÃ¶ntemi karÅŸÄ±laÅŸtÄ±r ve hangisinin kazandÄ±ÄŸÄ±na karar ver."""
    eski_puan = eski.puan()
    yeni_puan = yeni.puan()
    fark = abs(eski_puan - yeni_puan)

    # Yeni baÅŸarÄ±sÄ±z â†’ eski korunur
    if not yeni.basari or not yeni.cikti_dogru:
        return KararSonucu(
            kazanan=eski.yontem_adi,
            kaybeden=yeni.yontem_adi,
            fark=fark,
            gerekce=f"Yeni yontem basarisiz (basari={yeni.basari}, cikti={yeni.cikti_dogru}). Eski korunur.",
            eski_korundu=True,
        )

    # Eski baÅŸarÄ±sÄ±z, yeni baÅŸarÄ±lÄ± â†’ yeniye geÃ§
    if (not eski.basari or not eski.cikti_dogru) and (yeni.basari and yeni.cikti_dogru):
        return KararSonucu(
            kazanan=yeni.yontem_adi,
            kaybeden=eski.yontem_adi,
            fark=fark,
            gerekce=f"Eski basarisiz, yeni basarili. Yeniye geciliyor.",
            eski_korundu=False,
        )

    # Yeni > Eski + 0.2 fark â†’ yeniye geÃ§
    if yeni_puan > eski_puan + 0.2:
        return KararSonucu(
            kazanan=yeni.yontem_adi,
            kaybeden=eski.yontem_adi,
            fark=fark,
            gerekce=f"Yeni yontem {fark:.2f} puan daha iyi. Yeniye geciliyor.",
            eski_korundu=False,
        )

    # Fark < 0.2 â†’ eski korunur
    if fark < 0.2:
        return KararSonucu(
            kazanan=eski.yontem_adi,
            kaybeden=yeni.yontem_adi,
            fark=fark,
            gerekce=f"Fark {fark:.2f} < 0.2. Eski korunur (stable).",
            eski_korundu=True,
        )

    # Yeni daha iyi ama fark < 0.2 deÄŸil
    return KararSonucu(
        kazanan=yeni.yontem_adi,
        kaybeden=eski.yontem_adi,
        fark=fark,
        gerekce=f"Yeni yontem {fark:.2f} puan daha iyi. Geciliyor.",
        eski_korundu=False,
    )


# â”€â”€ 5 Tetikleyici SimÃ¼lasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

SIMULASYON_SENARYOLARI = [
    {
        "ad": "TETIK 1 â€” Hafiza Bos",
        "hafiza_bos": True,
        "guven_skoru": 1.0,
        "basarisiz_deneme": 0,
        "gecerlilik": "2027-12-31",
        "celiski": False,
        "beklenen_tetik": 1,
    },
    {
        "ad": "TETIK 2 â€” Guven Dusuk",
        "hafiza_bos": False,
        "guven_skoru": 0.25,
        "basarisiz_deneme": 0,
        "gecerlilik": "2027-12-31",
        "celiski": False,
        "beklenen_tetik": 2,
    },
    {
        "ad": "TETIK 3 â€” Gorev Basarisiz",
        "hafiza_bos": False,
        "guven_skoru": 0.9,
        "basarisiz_deneme": 2,
        "gecerlilik": "2027-12-31",
        "celiski": False,
        "beklenen_tetik": 3,
    },
    {
        "ad": "TETIK 4 â€” Gecerlilik Doldu",
        "hafiza_bos": False,
        "guven_skoru": 0.9,
        "basarisiz_deneme": 0,
        "gecerlilik": "2025-01-01",
        "celiski": False,
        "beklenen_tetik": 4,
    },
    {
        "ad": "TETIK 5 â€” Celiski",
        "hafiza_bos": False,
        "guven_skoru": 0.9,
        "basarisiz_deneme": 0,
        "gecerlilik": "2027-12-31",
        "celiski": True,
        "beklenen_tetik": 5,
    },
]


def tetikleyici_simulasyonu() -> list[dict]:
    """5 tetikleyiciyi simÃ¼le et ve sonuÃ§larÄ± dÃ¶ndÃ¼r."""
    sonuclar = []
    for senaryo in SIMULASYON_SENARYOLARI:
        tid, bilgi = hangi_tetikleyici(
            hafiza_bos=senaryo["hafiza_bos"],
            guven_skoru=senaryo["guven_skoru"],
            basarisiz_deneme_sayisi=senaryo["basarisiz_deneme"],
            gecerlilik_tarihi=senaryo["gecerlilik"],
            celiski_var=senaryo["celiski"],
        )

        beklenen = senaryo["beklenen_tetik"]
        durum = "âœ…" if tid == beklenen else "âŒ"

        sonuclar.append(
            {
                "senaryo": senaryo["ad"],
                "durum": durum,
                "ateslenen_tetik": tid,
                "beklenen_tetik": beklenen,
                "tetikleyici_adi": bilgi.get("ad", "YOK"),
                "kosul": bilgi.get("kosul", ""),
            }
        )

    return sonuclar


# â”€â”€ Tam DÃ¶ngÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def web_test_loop(
    konu: str,
    eski_yontem: Callable[[], TestSonucu],
    yeni_yontem: Callable[[], TestSonucu],
) -> dict[str, Any]:
    """
    WEB â†’ UYGULA â†’ PUANLA â†’ KARAR tam dÃ¶ngÃ¼sÃ¼.

    Args:
        konu: Test edilen konu (Ã¶rn. "nmap UDP tarama")
        eski_yontem: Eski yÃ¶ntemi Ã§alÄ±ÅŸtÄ±rÄ±p TestSonucu dÃ¶ndÃ¼ren fonksiyon
        yeni_yontem: Yeni yÃ¶ntemi Ã§alÄ±ÅŸtÄ±rÄ±p TestSonucu dÃ¶ndÃ¼ren fonksiyon

    Returns:
        {
            "konu": ...,
            "eski_puan": ...,
            "yeni_puan": ...,
            "karar": KararSonucu,
            "puan_tablosu": {...}
        }
    """
    # ADIM 2 â€” Uygula (sandbox'ta test et)
    eski_sonuc = eski_yontem()
    yeni_sonuc = yeni_yontem()

    # ADIM 3 â€” Puanla
    eski_puan = eski_sonuc.puan()
    yeni_puan = yeni_sonuc.puan()

    # ADIM 4 â€” Karar
    karar = karar_ver(eski_sonuc, yeni_sonuc)

    return {
        "konu": konu,
        "eski": {
            "yontem": eski_sonuc.yontem_adi,
            "puan": eski_puan,
            "detay": eski_sonuc,
        },
        "yeni": {
            "yontem": yeni_sonuc.yontem_adi,
            "puan": yeni_puan,
            "detay": yeni_sonuc,
        },
        "karar": {
            "kazanan": karar.kazanan,
            "kaybeden": karar.kaybeden,
            "fark": round(karar.fark, 2),
            "gerekce": karar.gerekce,
            "eski_korundu": karar.eski_korundu,
        },
        "puan_tablosu": {
            "kriterler": PUAN_KRITERLERI,
            "eski_kriter": {
                "hiz": eski_sonuc.hiz_sn,
                "basari": eski_sonuc.basari,
                "cikti": eski_sonuc.cikti_dogru,
                "guvenlik": eski_sonuc.guvenlik,
                "kaynak": eski_sonuc.kaynak_guven,
            },
            "yeni_kriter": {
                "hiz": yeni_sonuc.hiz_sn,
                "basari": yeni_sonuc.basari,
                "cikti": yeni_sonuc.cikti_dogru,
                "guvenlik": yeni_sonuc.guvenlik,
                "kaynak": yeni_sonuc.kaynak_guven,
            },
        },
    }


if __name__ == "__main__":
    # â”€â”€ TEST: nmap UDP tarama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("=" * 65)
    print("TEST: nmap icin en hizli UDP tarama yontemi")
    print("=" * 65)

    # Eski yÃ¶ntem: nmap -sU -p 1-1000 (tam UDP tarama, yavaÅŸ)
    eski_yontem = lambda: TestSonucu(
        yontem_adi="nmap -sU tam UDP tarama",
        hiz_sn=45.0,  # yavaÅŸ
        basari=True,
        cikti_dogru=True,
        guvenlik=1.0,  # nmap gÃ¼venli
        kaynak_guven=0.9,  # resmi doc
    )

    # Yeni yÃ¶ntem (web'den bulunan): nmap -sU --top-ports 100 (hÄ±zlÄ±)
    yeni_yontem = lambda: TestSonucu(
        yontem_adi="nmap -sU --top-ports 100",
        hiz_sn=5.0,  # Ã§ok hÄ±zlÄ±
        basari=True,
        cikti_dogru=True,  # ilk 100 port yeterli
        guvenlik=1.0,
        kaynak_guven=0.7,  # stackoverflow
    )

    sonuc = web_test_loop(
        konu="nmap UDP tarama",
        eski_yontem=eski_yontem,
        yeni_yontem=yeni_yontem,
    )

    print(f"\nKonu: {sonuc['konu']}")
    print(f"\n--- Puan Tablosu ---")
    print(f"{'Kriter':<12} {'Eski':<8} {'Yeni':<8}")
    print("-" * 30)
    for kriter in PUAN_KRITERLERI:
        eski_val = sonuc["puan_tablosu"]["eski_kriter"][kriter]
        yeni_val = sonuc["puan_tablosu"]["yeni_kriter"][kriter]
        print(f"{kriter:<12} {str(eski_val):<8} {str(yeni_val):<8}")

    print(f"\nEski puan: {sonuc['eski']['puan']:.4f}")
    print(f"Yeni puan: {sonuc['yeni']['puan']:.4f}")
    print(f"\nKARAR: {sonuc['karar']['kazanan']}")
    print(f"Gerekce: {sonuc['karar']['gerekce']}")
    print(f"Fark: {sonuc['karar']['fark']}")
    print(f"Eski korundu: {sonuc['karar']['eski_korundu']}")

    # â”€â”€ 5 Tetikleyici Test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n" + "=" * 65)
    print("5 TETIKLEYICI TESTI")
    print("=" * 65)
    tetik_sonuclari = tetikleyici_simulasyonu()
    for t in tetik_sonuclari:
        print(f"{t['durum']} {t['senaryo']}")
        print(f"   Ateslenen: #{t['ateslenen_tetik']} ({t['tetikleyici_adi']})")
        print(f"   Kosul: {t['kosul']}")

    # â”€â”€ Puanlama testi: fark < 0.2 durumu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("\n" + "=" * 65)
    print("TEST: Fark < 0.2 â†’ Eski korunur")
    print("=" * 65)
    eski2 = TestSonucu("nmap -sU -p 1-100", 10.0, True, True, 1.0, 0.9)
    yeni2 = TestSonucu("nmap -sU --top-ports 50", 8.0, True, True, 1.0, 0.7)
    karar2 = karar_ver(eski2, yeni2)
    print(f"Eski: {eski2.puan():.4f}, Yeni: {yeni2.puan():.4f}")
    print(f"Karar: {karar2.kazanan}")
    print(f"Gerekce: {karar2.gerekce}")
