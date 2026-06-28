# -*- coding: utf-8 -*-
# SHIM — reymen/guvenlik/file_safety.py + ReYMeN uzantıları
from reymen.guvenlik.file_safety import *  # noqa: F401, F403
from reymen.guvenlik.file_safety import YASAK_DOSYALAR as _YD_SRC
from reymen.guvenlik.file_safety import YASAK_UZANTILAR as _YU_SRC
from reymen.guvenlik.file_safety import YASAK_DIZINLER as _YDZ_SRC
import re as _re

# ── Genişletilmiş sabitler ────────────────────────────────────────────────────

YASAK_DOSYALAR: list = list(_YD_SRC) + [
    "hosts", "passwd", "shadow", "sudoers", "fstab",
    ".env", ".env.local", ".env.production",
    "id_rsa", "id_dsa", "authorized_keys",
]

YASAK_UZANTILAR: set = set(_YU_SRC) | {
    ".bat", ".cmd", ".vbs", ".ps1", ".sh", ".scr",
}

YASAK_DIZINLER: list = list(_YDZ_SRC) + [
    "/etc", "/etc/", "/proc", "/sys",
    "C:\\Windows", "C:\\Windows\\System32",
    "C:\\Program Files", "C:\\Program Files (x86)",
]


def guvenli_mi(yol: str) -> tuple:
    """Dosya yolunun güvenli olup olmadığını denetler.

    Returns:
        (guvenli: bool, mesaj: str)
    """
    if not yol:
        return (True, "Güvenli")

    # Path traversal kontrolü
    if ".." in yol:
        return (False, "Path traversal tespit edildi")

    yol_lower = yol.replace("\\", "/").lower()
    yol_norm = yol.replace("\\", "/")

    # Yasak dosya adı kontrolü
    dosya_adi = yol_norm.rstrip("/").rsplit("/", 1)[-1]
    if dosya_adi.lower() in (d.lower() for d in YASAK_DOSYALAR):
        return (False, f"Yasak dosya adı: {dosya_adi}")

    # Yasak uzantı kontrolü
    dot = dosya_adi.rfind(".")
    if dot > 0:
        uzanti = dosya_adi[dot:].lower()
        if uzanti in YASAK_UZANTILAR:
            return (False, f"Yasak uzantı: {uzanti}")

    # Yasak dizin kontrolü
    for dizin in YASAK_DIZINLER:
        dizin_norm = dizin.replace("\\", "/").rstrip("/").lower()
        if yol_lower.startswith(dizin_norm + "/") or yol_lower.startswith(dizin_norm + "\\"):
            return (False, f"Yasak dizin: {dizin}")
        # Tam yol eşleşmesi
        if yol_lower == dizin_norm:
            return (False, f"Yasak dizin: {dizin}")

    return (True, "Güvenli")
