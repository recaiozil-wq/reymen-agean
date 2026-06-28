# -*- coding: utf-8 -*-
"""tools/file_ops.py — Dosya Isleme Araci.

DOSYA_YAZ ve DOSYA_OKU islemleri. file_safety + path_security entegre.
"""

import os
from pathlib import Path

try:
    from file_safety import guvenli_mi as _guvenli
except ImportError:
    _guvenli = lambda p: (True, "")
try:
    from path_security import yol_dogrula as _yol_dogrula
except ImportError:
    _yol_dogrula = lambda p: (True, p)


def yaz(dosya_adi: str, icerik: str) -> str:
    """Dosyaya yaz.

    Args:
        dosya_adi: Dosya yolu
        icerik: Yazilacak icerik

    Returns:
        Durum mesaji
    """
    if not dosya_adi:
        return "[Dosya]: Dosya adi gerekli."
    guvenli, mesaj = _guvenli(dosya_adi)
    if not guvenli:
        return f"[Guvenlik]: {mesaj}"
    gecerli, yol = _yol_dogrula(dosya_adi)
    if not gecerli:
        return f"[Guvenlik]: {yol}"
    try:
        icerik = icerik.replace("\\n", "\n")
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write(icerik)
        return f"[Tamam]: {dosya_adi} yazildi ({len(icerik)} karakter)."
    except Exception as e:
        return f"[Dosya]: Hata: {e}"


def oku(dosya_adi: str) -> str:
    """Dosyadan oku.

    Args:
        dosya_adi: Dosya yolu

    Returns:
        Dosya icerigi
    """
    if not dosya_adi:
        return "[Dosya]: Dosya adi gerekli."
    if not os.path.exists(dosya_adi):
        return f"[Hata]: {dosya_adi} bulunamadi."
    gecerli, mesaj = _yol_dogrula(dosya_adi)
    if not gecerli:
        return f"[Guvenlik]: {mesaj}"
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            return f"[Dosya Icerigi]:\n{f.read()}"
    except Exception as e:
        return f"[Dosya]: Hata: {e}"


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(yaz("_test.txt", "test"))
    print(oku("_test.txt"))
    os.unlink("_test.txt")
