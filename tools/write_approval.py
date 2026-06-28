# -*- coding: utf-8 -*-
"""tools/write_approval.py — Dosya yazma onayi.

Hassas dosya islemleri icin ozel onay.
Belirli dosya desenlerini (.env, config, secret) otomatik onay gerektirir.
"""

import json
import os
import re
import time
import uuid
from pathlib import Path


# Otomatik onay gerektiren hassas dosya desenleri
HASSAS_DESENLER = [
    r"\.env$",
    r"\.env\..+$",
    r"config\.(yml|yaml|json|toml|ini|cfg)$",
    r"secret",
    r"credential",
    r"password",
    r"token\.",
    r"\.key$",
    r"\.pem$",
    r"\.cert$",
    r"id_rsa",
    r"dockercfg",
    r"\.netrc",
    r"aws/credentials",
    r"\.gitconfig",
]


def _pending_klasoru() -> Path:
    """.ReYMeN/pending/ klasorunun yolunu dondurur."""
    tool_path = Path(__file__).resolve().parent
    proje_kok = tool_path.parent
    pending_dir = proje_kok / ".ReYMeN" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    return pending_dir


def _dosyadan_yukle(dosya_yolu: str) -> dict:
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return {}


def _dosyaya_kaydet(dosya_yolu: str, veri: dict) -> None:
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)


def _hassas_mi(dosya_yolu: str) -> bool:
    """Dosyanin hassas desenlerden birine uyup uymadigini kontrol eder."""
    for desen in HASSAS_DESENLER:
        if re.search(desen, dosya_yolu, re.IGNORECASE):
            return True
    return False


def write_approval(islem: str = "dosya_kontrol", dosya_yolu: str = "",
                   icerik_ozeti: str = "") -> str:
    """Dosya yazma onay mekanizmasi.

    Args:
        islem: "yazma_onayla", "yazma_reddet", "dosya_kontrol".
        dosya_yolu: Hedef dosya yolu.
        icerik_ozeti: Yazilacak icerigin kisa ozeti.

    Returns:
        Islem sonucu metni.
    """
    try:
        pending_dir = _pending_klasoru()

        if islem == "dosya_kontrol":
            return _dosya_kontrol(pending_dir, dosya_yolu, icerik_ozeti)

        elif islem == "yazma_onayla":
            return _yazma_onayla(pending_dir, dosya_yolu)

        elif islem == "yazma_reddet":
            return _yazma_reddet(pending_dir, dosya_yolu)

        elif islem == "liste":
            return _listele(pending_dir)

        else:
            return (f"[Hata] Bilinmeyen islem: {islem}. "
                    f"Secenekler: dosya_kontrol, yazma_onayla, yazma_reddet, liste")

    except Exception as e:
        return f"[Hata] Yazma onayi: {e}"


def _dosya_kontrol(pending_dir: Path, dosya_yolu: str,
                   icerik_ozeti: str) -> str:
    """Dosyayi kontrol eder, hassassa onay istegi olusturur."""
    if not dosya_yolu:
        return "[Hata] dosya_yolu gerekli."

    hassas = _hassas_mi(dosya_yolu)
    islem_id = f"write_{uuid.uuid4().hex[:6]}"

    if hassas:
        # Hassas dosya -> onay gerektirir
        kayit = {
            "id": islem_id,
            "tur": "yazma_onayi",
            "dosya_yolu": dosya_yolu,
            "icerik_ozeti": icerik_ozeti or "(ozet yok)",
            "durum": "beklemede",
            "hassas": True,
            "olusturma": time.time(),
            "son_guncelleme": time.time(),
        }
        kayit_yolu = pending_dir / f"{islem_id}.json"
        _dosyaya_kaydet(str(kayit_yolu), kayit)

        return (
            f"[Guvenlik] Hassas dosya: {dosya_yolu}\n"
            f"  Icerik: {icerik_ozeti or '(ozet yok)'}\n"
            f"  Onay gerekiyor! ID: {islem_id}\n"
            f"  Onay: write_approval(islem='yazma_onayla', dosya_yolu='{dosya_yolu}')\n"
            f"  Red: write_approval(islem='yazma_reddet', dosya_yolu='{dosya_yolu}')"
        )
    else:
        # Guvenli dosya -> dogrudan izin
        return (
            f"[Guvenli] Dosya guvenli: {dosya_yolu}\n"
            f"  Icerik: {icerik_ozeti or '(ozet yok)'}\n"
            f"  Yazma izni verildi."
        )


def _yazma_onayla(pending_dir: Path, dosya_yolu: str) -> str:
    """Dosya yazma islemini onaylar."""
    if not dosya_yolu:
        return "[Hata] dosya_yolu gerekli."

    # Ilgili kaydi bul
    for f in pending_dir.glob("*.json"):
        kayit = _dosyadan_yukle(str(f))
        if (kayit.get("tur") == "yazma_onayi"
                and kayit.get("dosya_yolu") == dosya_yolu
                and kayit.get("durum") == "beklemede"):
            kayit["durum"] = "onaylandi"
            kayit["son_guncelleme"] = time.time()
            _dosyaya_kaydet(str(f), kayit)
            return f"[Onay] '{dosya_yolu}' yazma izni verildi."

    return f"[Hata] Bekleyen yazma istegi bulunamadi: {dosya_yolu}"


def _yazma_reddet(pending_dir: Path, dosya_yolu: str) -> str:
    """Dosya yazma islemini reddeder."""
    if not dosya_yolu:
        return "[Hata] dosya_yolu gerekli."

    for f in pending_dir.glob("*.json"):
        kayit = _dosyadan_yukle(str(f))
        if (kayit.get("tur") == "yazma_onayi"
                and kayit.get("dosya_yolu") == dosya_yolu
                and kayit.get("durum") == "beklemede"):
            kayit["durum"] = "reddedildi"
            kayit["son_guncelleme"] = time.time()
            _dosyaya_kaydet(str(f), kayit)
            return f"[Red] '{dosya_yolu}' yazma istegi reddedildi."

    return f"[Hata] Bekleyen yazma istegi bulunamadi: {dosya_yolu}"


def _listele(pending_dir: Path) -> str:
    """Bekleyen yazma onaylarini listeler."""
    dosyalar = sorted(pending_dir.glob("*.json"))

    yazma_kayitlari = []
    for f in dosyalar:
        kayit = _dosyadan_yukle(str(f))
        if kayit.get("tur") == "yazma_onayi":
            yazma_kayitlari.append(kayit)

    if not yazma_kayitlari:
        return "[Onay] Bekleyen yazma istegi yok."

    sonuc = ["[Onay] Bekleyen yazma istekleri:"]
    for kayit in yazma_kayitlari:
        hassas_etiketi = " [HASSAS]" if kayit.get("hassas") else ""
        sonuc.append(
            f"  - {kayit.get('dosya_yolu', '?')}: "
            f"{kayit.get('durum', '?')}{hassas_etiketi} | "
            f"{kayit.get('icerik_ozeti', '')[:50]}"
        )

    return "\n".join(sonuc)


def kontrol_et(dosya_yolu: str, icerik_ozeti: str = "") -> tuple:
    """Disardan cagrilabilir kontrol fonksiyonu.

    Returns:
        (izin_verildi, mesaj) ikilisi.
        izin_verildi=True ise yazma islemine devam edilebilir.
    """
    dosya_yolu = dosya_yolu.replace("\\", "/")

    if _hassas_mi(dosya_yolu):
        return (False,
                f"Hassas dosya: {dosya_yolu}. write_approval() ile onay gerekiyor.")
    return (True, "Guvenli dosya, yazma izni var.")
