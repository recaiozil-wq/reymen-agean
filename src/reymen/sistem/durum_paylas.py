# -*- coding: utf-8 -*-
"""
durum_paylas.py â€” Botlar ArasÄ± PaylaÅŸÄ±mlÄ± Durum Sistemi.

Tüm botlarÄ±n (R>eYMeN_Â¥, Kral_38, PaÅŸa_38 vb.) aynÄ±
durum.json dosyasÄ±nÄ± okuyup yazmasÄ±nÄ± saÄŸlar. Böylece
her bot güncel proje durumunu görür.

KullanÄ±m:
    from reymen.sistem.durum_paylas import durum_oku, durum_guncelle

    # Durumu oku
    durum = durum_oku()

    # Durumu güncelle
    durum_guncelle(bot_adi="Kral_38", ozellik="provider_sistemi", durum="tamam")

    # CLI: python -m reymen.sistem.durum_paylas --oku
    # CLI: python -m reymen.sistem.durum_paylas --guncelle --bot Kral_38 --ozellik provider_sistemi --durum tamam
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import logging

logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# durum.json proje kökünde â€” tüm botlar eriÅŸebilir
# Ortak yol: her bot aynÄ± proje dizininden çalÄ±ÅŸÄ±yorsa
_PROJE_KOKU = (
    Path(__file__).resolve().parent.parent.parent
)  # reymen/sistem/ -> reymen/ -> proje/
_DURUM_DOSYASI = _PROJE_KOKU / "durum.json"

# VarsayÄ±lan durum ÅŸablonu (dosya yoksa kullanÄ±lÄ±r)
VARSAYILAN_DURUM: Dict[str, Any] = {
    "proje": "ReYMeN Ajan",
    "surum": datetime.now().strftime("%Y-%m-%d"),
    "son_guncelleme": "",
    "guncelleyen_bot": "",
    "ozellikler": {},
    "aktif_ajanlar": {},
    "toplam_ozellik": 0,
    "tamam": 0,
    "isleniyor": 0,
}


# â”€â”€ Ana Fonksiyonlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _kilitle():
    """Basit dosya kilidi â€” aynÄ± anda yazma çakÄ±ÅŸmasÄ±nÄ± önler."""
    kilit_dosyasi = _DURUM_DOSYASI.with_suffix(".json.lock")
    max_bekle = 5  # saniye
    baslangic = time.monotonic()
    while time.monotonic() - baslangic < max_bekle:
        try:
            fd = os.open(str(kilit_dosyasi), os.O_CREAT | os.O_EXCL)
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(0.1)
    logger.warning(f"Kilit alÄ±namadÄ± (>{max_bekle}s): {kilit_dosyasi}")
    return False


def _kilidi_ac():
    """Dosya kilidini kaldÄ±r."""
    kilit_dosyasi = _DURUM_DOSYASI.with_suffix(".json.lock")
    try:
        kilit_dosyasi.unlink()
    except FileNotFoundError as _e:
        logger.warning("[DurumPaylas] Dosya/klasor hatasi (L79): %s", FileNotFoundError)
        pass


def durum_oku() -> Dict[str, Any]:
    """durum.json dosyasÄ±nÄ± oku.

    Returns:
        Durum sözlüÄŸü. Dosya yoksa varsayÄ±lan ÅŸablon döner.
    """
    if not _DURUM_DOSYASI.exists():
        return dict(VARSAYILAN_DURUM)

    try:
        with open(_DURUM_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"durum.json okunamadÄ±: {e}")
        return dict(VARSAYILAN_DURUM)


def durum_yaz(durum: Dict[str, Any], bot_adi: str = ""):
    """durum.json dosyasÄ±na yaz.

    Args:
        durum: YazÄ±lacak durum sözlüÄŸü
        bot_adi: Güncelleyen bot adÄ± (opsiyonel)
    """
    durum["son_guncelleme"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if bot_adi:
        durum["guncelleyen_bot"] = bot_adi

    kilitli = _kilitle()
    try:
        with open(_DURUM_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(durum, f, ensure_ascii=False, indent=2)
    except OSError as e:
        logger.error(f"durum.json yazÄ±lamadÄ±: {e}")
    finally:
        if kilitli:
            _kilidi_ac()


def durum_guncelle(
    bot_adi: str,
    ozellik: str,
    durum: str,
    detay: str = "",
    dosyalar: Optional[List[str]] = None,
    aktif_ajan: bool = False,
) -> Dict[str, Any]:
    """Tek bir özellik durumunu güncelle.

    Args:
        bot_adi: Güncelleyen bot adÄ± (örn: "R>eYMeN_Â¥", "Kral_38")
        ozellik: Ã–zellik adÄ± (örn: "provider_sistemi")
        durum: Yeni durum ("tamam", "isleniyor", "eksik")
        detay: AçÄ±klama (opsiyonel)
        dosyalar: Ä°lgili dosya listesi (opsiyonel)
        aktif_ajan: True ise aktif_ajanlar listesine ekle

    Returns:
        GüncellenmiÅŸ durum sözlüÄŸü
    """
    mevcut = durum_oku()

    # Ã–zellik bilgilerini güncelle
    mevcut.setdefault("ozellikler", {})
    guncel = mevcut["ozellikler"].get(ozellik, {})
    guncel["durum"] = durum
    guncel["son_guncelleme"] = datetime.now().strftime("%H:%M")
    guncel["guncelleyen"] = bot_adi
    if detay:
        guncel["detay"] = detay
    if dosyalar:
        guncel["dosyalar"] = dosyalar
    mevcut["ozellikler"][ozellik] = guncel

    # Aktif ajan listesini güncelle
    if aktif_ajan and durum == "isleniyor":
        mevcut.setdefault("aktif_ajanlar", {})
        mevcut["aktif_ajanlar"][ozellik] = "calisiyor"
    elif aktif_ajan and durum == "tamam":
        mevcut.setdefault("aktif_ajanlar", {})
        mevcut["aktif_ajanlar"].pop(ozellik, None)
    elif aktif_ajan and durum == "eksik":
        mevcut.setdefault("aktif_ajanlar", {})
        mevcut["aktif_ajanlar"].pop(ozellik, None)

    # Ä°statistikleri yeniden hesapla
    ozellikler = mevcut.get("ozellikler", {})
    mevcut["toplam_ozellik"] = len(ozellikler)
    mevcut["tamam"] = sum(1 for o in ozellikler.values() if o.get("durum") == "tamam")
    mevcut["isleniyor"] = sum(
        1 for o in ozellikler.values() if o.get("durum") == "isleniyor"
    )

    durum_yaz(mevcut, bot_adi)
    return mevcut


# â”€â”€ Tamamlanan Modül Entegrasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _sync_tamamlanan_moduller(mevcut: dict) -> None:
    """tamamlanan_moduller'i coverage_durumu.core_moduller'dan senkronize eder.

    coverage_durumu.core_moduller TEK kaynaktÄ±r. tamamlanan_moduller
    buradan türetilir. Böylece iki ayrÄ± kaynak olmaz.
    """
    mevcut.setdefault("coverage_durumu", {})
    mevcut["coverage_durumu"].setdefault("core_moduller", {})

    yeni_moduller: Dict[str, dict] = {}
    yeni_liste: List[str] = []

    for modul_adi, bilgi in mevcut["coverage_durumu"]["core_moduller"].items():
        if bilgi.get("tamamlandi"):
            yeni_moduller[modul_adi] = {
                "tamamlandi": True,
                "tarih": datetime.now().strftime("%Y-%m-%d"),
                "coverage": bilgi.get("simdi", ""),
                "test_sayisi": bilgi.get("test_sayisi", 0),
                "aciklama": bilgi.get("eksik_analizi", ""),
            }
            yeni_liste.append(modul_adi)

    mevcut["tamamlanan_moduller"] = yeni_moduller
    mevcut["coverage_durumu"]["tamamlanan_moduller"] = yeni_liste


def modul_tamamla(
    modul_adi: str,
    coverage: str,
    test_sayisi: int,
    aciklama: str = "",
):
    """Bir modülü tamamlandÄ± olarak durum.json'a kaydeder.

    TEK kaynak coverage_durumu.core_moduller'dir. tamamlanan_moduller
    otomatik senkronize edilir.

    Args:
        modul_adi: Modül adÄ± (örn: "guardrails_manager")
        coverage: Coverage yüzdesi (örn: "100.00%")
        test_sayisi: Test sayÄ±sÄ±
        aciklama: AçÄ±klama (opsiyonel)

    Ã–rnek:
        modul_tamamla("guardrails_manager", "100.00%", 58,
                       "sinir durumu + hata durumu kapsandi")
    """
    mevcut = durum_oku()
    mevcut.setdefault("coverage_durumu", {})
    mevcut["coverage_durumu"].setdefault("core_moduller", {})

    simdi = bilgi = mevcut["coverage_durumu"]["core_moduller"].get(modul_adi, {})

    # coverage_durumu.core_moduller TEK kaynak â€” tüm veriyi buraya yaz
    mevcut["coverage_durumu"]["core_moduller"][modul_adi] = {
        "once": simdi.get("once", ""),
        "simdi": coverage,
        "degisim": simdi.get("degisim", ""),
        "durum": f"TAMAM âœ… (%{coverage.replace('%','')}+)",
        "test_sayisi": test_sayisi,
        "test_dosyalari": simdi.get("test_dosyalari", []),
        "eksik_analizi": aciklama,
        "kapsanan": simdi.get("kapsanan", ""),
        "guncelleme": datetime.now().astimezone().isoformat(),
        "tamamlandi": True,
        "tamamlanma_tarihi": datetime.now().astimezone().isoformat(),
    }

    # tamamlanan_moduller'i coverage_durumu.core_moduller'dan senkronize et
    _sync_tamamlanan_moduller(mevcut)

    mevcut["son_guncelleme"] = datetime.now().astimezone().isoformat()
    mevcut["guncelleyen_bot"] = "system"
    durum_yaz(mevcut)


def tamamlanan_moduller() -> List[str]:
    """Tamamlanan modül adlarÄ±nÄ± döndürür.

    Returns:
        Modül adÄ± listesi (örn: ["guardrails_manager", "oauth_manager"])
    """
    mevcut = durum_oku()
    # Ã–NCE coverage_durumu.core_moduller'dan senkronize et
    _sync_tamamlanan_moduller(mevcut)
    moduller = mevcut.get("tamamlanan_moduller", {})
    return list(moduller.keys())


def modul_tamamlandi_mi(modul_adi: str) -> bool:
    """Bir modülün tamamlandÄ± olarak iÅŸaretlenip iÅŸaretlenmediÄŸini kontrol eder.

    Args:
        modul_adi: Modül adÄ±

    Returns:
        True ise modül daha önce tamamlandÄ±
    """
    return modul_adi in tamamlanan_moduller()


def tamamlanmayanlar(tum_moduller: List[str]) -> List[str]:
    """Verilen listeden tamamlanmÄ±ÅŸ modülleri çÄ±karÄ±r.

    Args:
        tum_moduller: Kontrol edilecek modül adÄ± listesi

    Returns:
        Sadece tamamlanmamÄ±ÅŸ modüller

    Ã–rnek:
        adaylar = ["guardrails_manager", "cost_tracker", "kanban"]
        kalan = tamamlanmayanlar(adyalar)
        # -> ["cost_tracker", "kanban"] (guardrails zaten tamam)
    """
    tamamlanan = set(tamamlanan_moduller())
    return [m for m in tum_moduller if m not in tamamlanan]


def durum_raporu() -> str:
    """Ä°nsan tarafÄ±ndan okunabilir durum raporu üret.

    Returns:
        FormatlÄ± metin raporu
    """
    durum = durum_oku()
    satirlar = [
        f"ğŸ“Š ReYMeN Proje Durumu",
        f"   Son Güncelleme: {durum.get('son_guncelleme', '?')}",
        f"   Güncelleyen: {durum.get('guncelleyen_bot', '?')}",
        f"   Ä°statistik: {durum.get('tamam', 0)}/{durum.get('toplam_ozellik', 0)} tamam, {durum.get('isleniyor', 0)} iÅŸleniyor",
        "",
    ]

    # Aktif ajanlar
    aktif = durum.get("aktif_ajanlar", {})
    if aktif:
        satirlar.append("ğŸŸ¢ Aktif Ajanlar:")
        for ajan, durum_str in aktif.items():
            satirlar.append(f"   â€¢ {ajan}: {durum_str}")
        satirlar.append("")

    # Ã–zellik listesi
    satirlar.append("Ã–zellikler:")
    for ad, bilgi in durum.get("ozellikler", {}).items():
        durum_simge = {"tamam": "âœ…", "isleniyor": "ğŸ”„", "eksik": "âŒ"}.get(
            bilgi.get("durum", ""), "â“"
        )
        satirlar.append(f"  {durum_simge} {ad}: {bilgi.get('detay', '')}")
        dosyalar = bilgi.get("dosyalar", [])
        if dosyalar:
            for d in dosyalar[:3]:  # En fazla 3 dosya göster
                satirlar.append(f"      ğŸ“„ {d}")

    return "\n".join(satirlar)


# â”€â”€ CLI Entry â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _cli():
    """Komut satÄ±rÄ±ndan kullanÄ±m: python -m reymen.sistem.durum_paylas --oku"""
    import argparse

    parser = argparse.ArgumentParser(description="Botlar ArasÄ± PaylaÅŸÄ±mlÄ± Durum")
    parser.add_argument("--oku", action="store_true", help="Durumu oku ve göster")
    parser.add_argument(
        "--rapor", action="store_true", help="Ä°nsan-okunabilir rapor göster"
    )
    parser.add_argument("--guncelle", action="store_true", help="Durum güncelle")
    parser.add_argument("--bot", default="cli", help="Güncelleyen bot adÄ±")
    parser.add_argument("--ozellik", help="Ã–zellik adÄ±")
    parser.add_argument(
        "--durum", choices=["tamam", "isleniyor", "eksik"], help="Yeni durum"
    )
    parser.add_argument("--detay", default="", help="AçÄ±klama")

    args = parser.parse_args()

    if args.oku:
        print(json.dumps(durum_oku(), ensure_ascii=False, indent=2))
    elif args.rapor:
        print(durum_raporu())
    elif args.guncelle:
        if not args.ozellik or not args.durum:
            print("Hata: --guncelle için --ozellik ve --durum gerekli")
            sys.exit(1)
        durum_guncelle(args.bot, args.ozellik, args.durum, args.detay)
        print(f"âœ… {args.ozellik} â†’ {args.durum} olarak güncellendi (bot: {args.bot})")
    else:
        parser.print_help()


if __name__ == "__main__":
    _cli()
