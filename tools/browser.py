# -*- coding: utf-8 -*-
"""tools/browser.py — Tarayici Otomasyon Araci.

Playwright ile sayfa acma, okuma ve etkilesim.
"""

from pathlib import Path
import logging
logger = logging.getLogger(__name__)


def sayfa_ac(url: str) -> str:
    """Bir sayfayi ac ve icerigini oku.

    Args:
        url: Acilacak URL

    Returns:
        Sayfa icerigi
    """
    if not url:
        return "[Browser]: URL gerekli."

    try:
        from araclar_tarayici import TarayiciKontrol
        t = TarayiciKontrol()
        return t.sayfa_ac_ve_oku(url)
    except ImportError:
        logger.warning("[fix_01_sessiz_except] ImportError")

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            icerik = page.content()[:3000]
            browser.close()
            return f"[Browser] {len(icerik)} karakter:\n{icerik[:1000]}"
    except ImportError:
        return "[Browser]: playwright kurulu degil."
    except Exception as e:
        return f"[Browser]: Hata: {e}"


def ping() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    print(sayfa_ac("https://example.com"))
