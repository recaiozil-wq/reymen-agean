# -*- coding: utf-8 -*-
"""file_safety.py — Dosya Guvenlik Taramasi.

Dosya yazma/okuma islemlerini guvenlik acisindan kontrol eder.
Zararli yollari, yasak dizinleri ve yasak dosya tiplerini engeller.
"""

import os
from pathlib import Path

# Varsayilan olarak izin verilen dizinler
IZINLI_DIZINLER = [
    Path(__file__).parent.parent.resolve(),  # proje koku
]

# Kesinlikle yasak dizinler
YASAK_DIZINLER = [
    "C:\\Windows",
    "C:\\Windows\\System32",
    "C:\\Windows\\System",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "/etc",
    "/bin",
    "/sbin",
    "/usr",
    "/boot",
    "/dev",
]

# Yasal dosya uzantilari (sistem dosyalari)
YASAK_UZANTILAR = [
    ".exe", ".dll", ".sys", ".bin", ".msi", ".bat",
    ".cmd", ".ps1", ".vbs", ".scr", ".com",
]

# Kritik dosya adlari
YASAK_DOSYALAR = [
    "boot.ini", "ntldr", "ntdetect.com", "pagefile.sys",
    "hiberfil.sys", "swapfile.sys", "config.db",
]


def guvenli_mi(dosya_yolu: str) -> tuple[bool, str]:
    """Bir dosya yolunun guvenli olup olmadigini kontrol et.

    Args:
        dosya_yolu: Kontrol edilecek yol

    Returns:
        (guvenli_mi, hata_mesaji)
    """
    try:
        yol = Path(dosya_yolu).resolve()
    except Exception:
        return False, "Gecersiz dosya yolu."

    # Path traversal kontrolu
    if ".." in str(yol):
        return False, "Path traversal engellendi."

    # Yasak dizin kontrolu
    for yasak in YASAK_DIZINLER:
        if str(yol).lower().startswith(yasak.lower()):
            return False, f"Yasak dizin: {yasak}"

    # Yasak uzanti kontrolu
    for uzanti in YASAK_UZANTILAR:
        if yol.suffix.lower() == uzanti:
            return False, f"Yasak dosya turu: {uzanti}"

    # Kritik dosya kontrolu
    if yol.name.lower() in [y.lower() for y in YASAK_DOSYALAR]:
        return False, "Kritik sistem dosyasi."

    return True, ""


def izinli_dizin_ekle(dizin: str):
    """Izin verilen dizinlere yeni bir dizin ekle."""
    IZINLI_DIZINLER.append(Path(dizin).resolve())


if __name__ == "__main__":
    testler = [
        "test.txt",
        "../../Windows/System32/config.dll",
        "C:\\Windows\\System32\\drivers\\etc\\hosts",
        ".ReYMeN/memories/MEMORY.md",
    ]
    for t in testler:
        guvenli, mesaj = guvenli_mi(t)
        print(f"  {t}: {'GUVENLI' if guvenli else 'ENGELLENDI'} ({mesaj})")
