# -*- coding: utf-8 -*-
"""plugins/security_guidance/__init__.py — Guvenlik Rehberligi Plugin.

Prompt guvenligi, veri dogrulama, cikti filtreleme.
"""


__all__ = ['guvenlik_denetle', 'guvenlik_temizle', 'kaydet']
plugin_adi = "security_guidance"
plugin_aciklamasi = "Prompt guvenligi, veri dogrulama ve cikti filtreleme"


def kaydet(motor):
    try:
        import re

        HASSAS_MODELLER = [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",  # email
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b",  # kart no
            r"\bTR\d{24}\b",  # IBAN
            r"\b(?:T[CR])\d{11}\b",  # TCKN
        ]

        def guvenlik_denetle(args):
            """Prompt veya mesaji guvenlik acisindan denetle."""
            uyarilar = []
            for idx, desen in enumerate(HASSAS_MODELLER):
                eslesmeler = re.findall(desen, args)
                if eslesmeler:
                    uyarilar.append(f"Hassas veri tespit edildi (tip {idx}): {len(eslesmeler)} adet")
            if not uyarilar:
                return "[Guvenlik] Denetim gecti: hassas veri bulunamadi."
            return "[Guvenlik] Uyari:\n" + "\n".join(uyarilar)

        def guvenlik_temizle(args):
            """Hassas verileri metinden maskele."""
            for desen in HASSAS_MODELLER:
                args = re.sub(desen, "[GIZLI]", args)
            return args

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("GUVENLIK_DENETLE", guvenlik_denetle)
            motor._registry.kaydet("GUVENLIK_TEMIZLE", guvenlik_temizle)
    except Exception:
        pass
