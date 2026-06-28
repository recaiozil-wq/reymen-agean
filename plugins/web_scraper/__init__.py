# -*- coding: utf-8 -*-
"""
plugins/web_scraper — Gelismis web kazima plugin'i.
Motor'a WEB_GETIR araci ekler.
"""

__all__ = ['HTMLParser', 'handle_data', 'handle_endtag', 'handle_starttag', 'kaydet', 'metin', 'web_getir']
plugin_adi = "web_scraper"
plugin_aciklamasi = "requests ile URL icerigini getirir, baslik + metin ayiklar"
plugin_araclar = ["WEB_GETIR"]


def web_getir(url: str) -> str:
    try:
        import requests
        from html.parser import HTMLParser

        class _Temizleyici(HTMLParser):
            def __init__(self):
                super().__init__()
                self._metin = []
                self._atla = False
            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "nav", "footer"):
                    self._atla = True
            def handle_endtag(self, tag):
                if tag in ("script", "style", "nav", "footer"):
                    self._atla = False
            def handle_data(self, data):
                if not self._atla and data.strip():
                    self._metin.append(data.strip())
            def metin(self):
                return " ".join(self._metin)[:4000]

        r = requests.get(url, timeout=15, headers={"User-Agent": "ReYMeN/1.0"})
        r.raise_for_status()
        t = _Temizleyici()
        t.feed(r.text)
        return t.metin() or "(Icerik alinamadi)"
    except Exception as e:
        return f"[WEB_GETIR Hatasi] {e}"


def kaydet(motor) -> None:
    """WEB_GETIR aracini motor'a ekle."""
    orijinal = motor.calistir.__func__ if hasattr(motor.calistir, "__func__") else None

    def _yeni_calistir(self, arac, ham_param):
        if arac == "WEB_GETIR":
            params = self._parametreleri_coz(ham_param)
            return web_getir(params[0] if params else "")
        return _orijinal_calistir(self, arac, ham_param)

    _orijinal_calistir = motor.calistir.__func__ if hasattr(motor.calistir, "__func__") else motor.calistir
    import types
    motor.calistir = types.MethodType(_yeni_calistir, motor)
