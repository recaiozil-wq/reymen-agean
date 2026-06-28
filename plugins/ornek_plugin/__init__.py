# -*- coding: utf-8 -*-
"""plugins/ornak_plugin/__init__.py — Ornek Plugin.

Plugin sisteminin nasil calistigini gosteren basit bir plugin.
Plugin'lerde zorunlu alanlar: plugin_adi, plugin_aciklamasi, kaydet()
"""


__all__ = ['kaydet', 'ornek_fonksiyon']
plugin_adi = "ornek_plugin"
plugin_aciklamasi = "Basit bir ornek plugin. Sadece kayit mekanizmasini gosterir."


def kaydet(motor):
    """Plugin'i motor'a kaydet.

    Args:
        motor: Motor nesnesi (tool_registry'ye erisim icin)
    """
    # Ornek: yeni bir arac ekle
    def ornek_fonksiyon(parametre=""):
        return f"[OrnekPlugin]: '{parametre}' parametresi ile cagrildi."

    if hasattr(motor, "_registry") and motor._registry:
        motor._registry.kaydet("ORNEK_PLUGIN", ornek_fonksiyon)
