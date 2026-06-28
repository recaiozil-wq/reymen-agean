# -*- coding: utf-8 -*-
"""
sorun_coz.py — Reymen otomatik sorun bulma ve Claude Code'a iletme aracı.

Kullanim:
    python scripts/sorun_coz.py

Akis:
    sorun_bul.py calistir → rapor al → vscode_yaz.bat ile Claude Code'a gonder
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

KOK = Path(__file__).resolve().parent.parent
# DIS SISTEM YOLU — Bu satirdaki "hermes" degistirilmez; ReYMeN Agent'in
# AppData kurulum yolu olup proje adlandinmasi ile alakasizdir.
VSCODE_BAT = Path(r"C:\Users\marko\AppData\Local\hermes\scripts\vscode_yaz.bat")
RAPOR_DOSYA = KOK / "output" / "sorun_raporu.txt"

# Claude Code'a gönderilecek mesajın baş kısmı
MESAJ_BASLIGI = (
    "REYMEN OTOMATİK SORUN TARAMA RAPORU — lütfen aşağıdaki bulguları incele "
    "ve gerekli düzeltmeleri yap:\n\n"
)

# Tek seferde Claude'a gönderilebilecek maks karakter (clipboard güvenli sınır)
MAKS_KARAKTER = 3000


def sorun_bul_calistir() -> str:
    """sorun_bul.py'yi subprocess ile çalıştırır, stdout'u döndürür."""
    print("[1/3] Proje taraniyor (sorun_bul.py)...")
    script = KOK / "scripts" / "sorun_bul.py"
    if not script.exists():
        sys.exit(f"HATA: {script} bulunamadi. Once sorun_bul.py olusturulmus olmali.")

    sonuc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(KOK),
    )

    if sonuc.returncode != 0:
        print(f"[!] sorun_bul.py hata kodu {sonuc.returncode} ile cikti.")
        print(sonuc.stderr[:500] if sonuc.stderr else "")

    cikti = sonuc.stdout or ""

    # Kaydedilmis rapor varsa onu tercih et (daha temiz format)
    if RAPOR_DOSYA.exists():
        try:
            kayitli = RAPOR_DOSYA.read_text(encoding="utf-8")
            if kayitli.strip():
                cikti = kayitli
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")

    return cikti.strip()


def clipboard_ayarla(metin: str) -> bool:
    """PowerShell ile Windows clipboard'ına metin yazar."""
    try:
        # PowerShell stdin üzerinden alır — uzunluk sınırı yok
        ps_komut = (
            "$input = [Console]::In.ReadToEnd(); "
            "Set-Clipboard -Value $input"
        )
        subprocess.run(
            ["powershell", "-NonInteractive", "-Command", ps_komut],
            input=metin,
            text=True,
            encoding="utf-8",
            check=True,
            capture_output=True,
        )
        return True
    except Exception as e:
        print(f"[!] Clipboard hatasi: {e}")
        return False


def vscode_gonder(metin: str) -> bool:
    """
    vscode_yaz.bat kullanarak VS Code Claude Agent'a mesaj gönderir.
    Uzun metinleri clipboard üzerinden iletir.
    """
    if not VSCODE_BAT.exists():
        print(f"[!] vscode_yaz.bat bulunamadi: {VSCODE_BAT}")
        print("    Rapor ekrana yazildi, elle kopyalayabilirsin.")
        return False

    # Clipboard'a tam metni yaz, bat'e kısa teaser geçir
    tam_metin = MESAJ_BASLIGI + metin
    clipboard_basarili = clipboard_ayarla(tam_metin)

    if clipboard_basarili:
        # Bat'e sadece kısa bir tetikleyici gönder; asıl içerik zaten clipboard'da
        tetikleyici = (
            "REYMEN SORUN TARAMA RAPORU hazir — "
            "Ctrl+V ile yapistirip inceleyebilirsin."
        )
        subprocess.run(
            [str(VSCODE_BAT), tetikleyici],
            shell=True,
            check=False,
        )
        print("[OK] Tetikleyici mesaj VS Code'a gonderildi.")
        print("     Tam rapor clipboard'da — Claude Chat'e Ctrl+V ile yapistir.")
    else:
        # Clipboard basarisiz → raporu dogrudan bat argümani olarak gönder (kisalt)
        kisalt = (MESAJ_BASLIGI + metin)[:MAKS_KARAKTER]
        if len(metin) > MAKS_KARAKTER:
            kisalt += "\n\n[RAPOR KISALTI — tam rapor output/sorun_raporu.txt dosyasinda]"
        subprocess.run(
            [str(VSCODE_BAT)] + kisalt.split(),
            shell=True,
            check=False,
        )
        print("[OK] Kisaltilmis rapor VS Code'a gonderildi.")

    return True


def ana() -> None:
    print("=" * 55)
    print("  REYMEN → SORUN BULMA ve CLAUDE CODE'A İLETME")
    print("=" * 55)

    # Adim 1: Tara
    rapor = sorun_bul_calistir()
    if not rapor:
        print("[!] Rapor bos geldi, cikiliyor.")
        sys.exit(1)

    satir_sayisi = rapor.count("\n")
    print(f"[2/3] Rapor hazir — {satir_sayisi} satir, {len(rapor)} karakter.")

    # Rapor özetini ekrana bas
    ozet_satirlar = [
        s for s in rapor.splitlines()
        if s.startswith("  !!") or s.startswith("    !!") or s.startswith("    ??")
    ]
    if ozet_satirlar:
        print("\n  Bulunan sorunlar:")
        for s in ozet_satirlar[:15]:
            print(f"  {s.strip()}")
    else:
        print("\n  Belirgin sorun bulunamadi (veya tum bulgular raporda).")

    # Adim 2: Claude Code'a ilet
    print(f"\n[3/3] VS Code Claude Agent'a iletiliyor...")
    time.sleep(0.5)
    vscode_gonder(rapor)

    print("\nTamamlandi.")
    if RAPOR_DOSYA.exists():
        print(f"Tam rapor: {RAPOR_DOSYA}")


if __name__ == "__main__":
    ana()
