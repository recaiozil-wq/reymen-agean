# -*- coding: utf-8 -*-
"""plugins/web_search_plugin/__init__.py — Web Arama Plugin.

Web arama fonksiyonunu plugin olarak sarar.
"""


__all__ = ['ara', 'kaydet', 'web_ara']
plugin_adi = "web_search"
plugin_aciklamasi = "Web'de arama yap ve sonuclari getir"


def kaydet(motor):
    try:
        from tools.web_search import ara

        def web_ara(args):
            return ara(args)

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("WEB_ARAMA", web_ara)
    except Exception:
        pass
