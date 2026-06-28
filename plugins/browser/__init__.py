# -*- coding: utf-8 -*-
"""
plugins/browser/__init__.py — Tarayici Otomasyonu Plugin.

Araçlar: BROWSER_AC, BROWSER_OKU, BROWSER_TIKLA, BROWSER_FORM_DOLDUR
Playwright varsa tam otomasyon, yoksa urllib fallback.
"""

__all__ = ['HTMLParser', 'P', 'browser_ac', 'browser_form', 'browser_oku', 'browser_tikla', 'handle_data', 'handle_endtag', 'handle_starttag', 'kaydet', 'sync_playwright']
import re
import urllib.request

PLUGIN_ADI = "browser"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Web tarayicisi otomasyonu (Playwright/urllib)"

_PLAYWRIGHT_VAR = None


def _playwright_kontrol() -> bool:
    global _PLAYWRIGHT_VAR
    if _PLAYWRIGHT_VAR is None:
        try:
            import playwright
            _PLAYWRIGHT_VAR = True
        except ImportError:
            _PLAYWRIGHT_VAR = False
    return _PLAYWRIGHT_VAR


def _url_oku_fallback(url: str, max_k: int = 3000) -> str:
    """Playwright yoksa stdlib ile oku."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ReYMeNAgent/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode(r.headers.get_content_charset("utf-8"), errors="replace")
        from html.parser import HTMLParser
        class P(HTMLParser):
            def __init__(self):
                super().__init__()
                self._t = []
                self._s = False
            def handle_starttag(self, t, _):
                if t in ("script", "style"):
                    self._s = True
            def handle_endtag(self, t):
                if t in ("script", "style"):
                    self._s = False
            def handle_data(self, d):
                if not self._s and d.strip():
                    self._t.append(d.strip())
        p = P(); p.feed(html)
        return " ".join(p._t)[:max_k]
    except Exception as e:
        return f"[BrowserHata]: {e}"


def _pw_oku(url: str) -> str:
    """Playwright ile tam sayfa okuma."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            p = b.new_page()
            p.goto(url, timeout=20000)
            metin = p.inner_text("body")[:3000]
            b.close()
            return metin
    except Exception as e:
        return _url_oku_fallback(url)


def _pw_tikla(url: str, secici: str) -> str:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            p = b.new_page()
            p.goto(url, timeout=20000)
            p.click(secici)
            p.wait_for_timeout(1000)
            metin = p.inner_text("body")[:2000]
            b.close()
            return f"[Browser] Tiklandi: {secici}\n{metin}"
    except Exception as e:
        return f"[BrowserHata]: {e}"


def _pw_form(url: str, veri_json: str) -> str:
    try:
        import json
        veri = json.loads(veri_json)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            p = b.new_page()
            p.goto(url, timeout=20000)
            for secici, deger in veri.items():
                p.fill(secici, str(deger))
            p.wait_for_timeout(500)
            b.close()
            return f"[Browser] Form dolduruldu: {list(veri)}"
    except Exception as e:
        return f"[BrowserHata]: {e}"


def kaydet(motor):
    def browser_ac(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        url = params[0] if params else ham.strip('"')
        return _pw_oku(url) if _playwright_kontrol() else _url_oku_fallback(url)

    def browser_oku(ham: str) -> str:
        return browser_ac(ham)

    def browser_tikla(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        url = params[0] if params else ""
        secici = params[1] if len(params) > 1 else "button"
        return _pw_tikla(url, secici)

    def browser_form(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        url = params[0] if params else ""
        veri = params[1] if len(params) > 1 else "{}"
        return _pw_form(url, veri)

    from plugins.kanban import _plugin_arac_kaydet
    _plugin_arac_kaydet(motor, "BROWSER_AC",         browser_ac)
    _plugin_arac_kaydet(motor, "BROWSER_OKU",        browser_oku)
    _plugin_arac_kaydet(motor, "BROWSER_TIKLA",      browser_tikla)
    _plugin_arac_kaydet(motor, "BROWSER_FORM_DOLDUR",browser_form)
    mod = "Playwright" if _playwright_kontrol() else "urllib-fallback"
    print(f"[Plugin:{PLUGIN_ADI}] 4 arac kayit edildi ({mod}).")
