# -*- coding: utf-8 -*-
"""tools/screen.py — Ekran OCR + Tiklama Araci.

easyocr ile ekran metnini okuma ve pyautogui ile tiklamave.
"""


def ekran_oku() -> str:
    """Ekran metnini oku (OCR)."""
    try:
        from araclar_ekran import EkranOCRTikla
        e = EkranOCRTikla()
        return e.ekran_metnini_oku()
    except ImportError:
        return "[Screen]: araclar_ekran modulu yok."
    except Exception as ex:
        return f"[Screen]: Hata: {ex}"


def tikla(yazi: str, hangi: int = 0) -> str:
    """Ekranda yaziyi bul ve tikla.

    Args:
        yazi: Aranacak yazi
        hangi: Kacinci eslesme (0=ilk)

    Returns:
        Durum mesaji
    """
    try:
        from araclar_ekran import EkranOCRTikla
        e = EkranOCRTikla()
        return e.yaziyi_bul_ve_tikla(yazi, hangi=hangi)
    except ImportError:
        return "[Screen]: araclar_ekran modulu yok."
    except Exception as ex:
        return f"[Screen]: Hata: {ex}"


def nisan_ciz(yazi: str) -> str:
    """Ekranda yazinin yerini nisanla goster (tiklamadan).

    Args:
        yazi: Aranacak yazi

    Returns:
        Nisan dosyasi yolu
    """
    try:
        from araclar_ekran import EkranOCRTikla
        e = EkranOCRTikla()
        return e.yaziyi_bul_ve_tikla(yazi, tikla=False, nisan=True)
    except ImportError:
        return "[Screen]: araclar_ekran modulu yok."


def ping() -> bool:
    try:
        import pyautogui
        return True
    except ImportError:
        return False
