# -*- coding: utf-8 -*-
"""tools/path_security.py — Yol guvenligi sarmalayicisi.

Kok dizindeki path_security.py modulunu import eder ve
yol_dogrula() fonksiyonunu delegasyonla calistirir.
"""
import os


def run(islem='dogrula', **kwargs) -> str:
    """Yol guvenligi islemlerini yonetir.

    Parametreler:
        islem (str): 'dogrula' veya 'symlink_kontrol'
        yol (str): Kontrol edilecek dosya yolu

    Returns:
        str: Islem sonucu.
    """
    try:
        from path_security import yol_dogrula, sembolik_link_kontrol

        yol = kwargs.get('yol', '')
        if not yol:
            return "Hata: 'yol' parametresi zorunludur."

        if islem == 'dogrula':
            gecerli, mesaj = yol_dogrula(yol)
            durum = "GUVENLI" if gecerli else "ENGELLENDI"
            return f"[{durum}] {mesaj}"

        elif islem == 'symlink_kontrol':
            guvenli, mesaj = sembolik_link_kontrol(yol)
            durum = "GUVENLI" if guvenli else "RISKLI"
            return f"[{durum}] {mesaj}"

        else:
            return f"Hata: Gecersiz islem '{islem}'."

    except Exception as e:
        return f"Yol guvenligi hatasi: {e}"
