# -*- coding: utf-8 -*-
"""tools/browser_camofox.py — Parmak İzi Korumalı Tarayıcı.

Playwright tabanlı, anti-bot tespitine karşı parmak izi maskeleme.
User-agent rotasyonu, viewport varyasyonu, bot sinyallerini gizler.
"""

import os
import random
from pathlib import Path
from typing import Optional

# Playwright opsiyonel — import hatası verirse zarif geçiş
try:
    from playwright.sync_api import sync_playwright, Page, Browser
    _PLAYWRIGHT_VAR = True
except ImportError:
    _PLAYWRIGHT_VAR = False

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

VIEWPORT_HAVUZU = [
    {"width": 1920, "height": 1080},
    {"width": 1440, "height": 900},
    {"width": 1366, "height": 768},
    {"width": 1280, "height": 800},
    {"width": 2560, "height": 1440},
]

# Bot tespitini gizleyen JS enjeksiyonu
STEALTH_JS = """
// navigator.webdriver gizle
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
// Chrome runtime sahte ekle
window.chrome = { runtime: {} };
// Dil/platform gibi bot işaretlerini maskele
Object.defineProperty(navigator, 'languages', { get: () => ['tr-TR', 'tr', 'en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
"""


class CamofoxBrowser:
    """Parmak izi korumalı Playwright tarayıcısı."""

    def __init__(
        self,
        gorunsuz: bool = True,
        proxy: str = "",
        kullanici_veri: str = "",
    ):
        if not _PLAYWRIGHT_VAR:
            raise ImportError("playwright yüklü değil: pip install playwright && playwright install chromium")
        self.gorunsuz      = gorunsuz
        self.proxy         = proxy
        self.kullanici_veri = kullanici_veri
        self._pw           = None
        self._tarayici: Optional[Browser] = None

    def baslat(self) -> "CamofoxBrowser":
        self._pw = sync_playwright().start()
        user_agent = random.choice(USER_AGENTS)
        viewport   = random.choice(VIEWPORT_HAVUZU)

        baslat_kw: dict = {
            "headless":      self.gorunsuz,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--disable-infobars",
                f"--window-size={viewport['width']},{viewport['height']}",
            ],
        }
        if self.proxy:
            baslat_kw["proxy"] = {"server": self.proxy}
        if self.kullanici_veri:
            baslat_kw["user_data_dir"] = self.kullanici_veri

        self._tarayici = self._pw.chromium.launch(**baslat_kw)
        self._user_agent = user_agent
        self._viewport   = viewport
        return self

    def yeni_sayfa(self) -> "Page":
        """Stealth modda yeni sayfa aç."""
        baglam = self._tarayici.new_context(
            user_agent       = self._user_agent,
            viewport         = self._viewport,
            locale           = "tr-TR",
            timezone_id      = "Europe/Istanbul",
            bypass_csp       = True,
            ignore_https_errors=True,
        )
        sayfa = baglam.new_page()
        sayfa.add_init_script(STEALTH_JS)
        return sayfa

    def sayfa_oku(self, url: str, bekleme: str = "networkidle", zaman_asimi: int = 30000) -> str:
        """URL'yi yükle ve içeriğini döndür."""
        with self:
            sayfa = self.yeni_sayfa()
            try:
                sayfa.goto(url, wait_until=bekleme, timeout=zaman_asimi)
                return sayfa.content()
            except Exception as e:
                return f"[Camofox]: {e}"

    def ekran_goruntus(self, url: str, kayit_yolu: str = "") -> str:
        """URL'nin ekran görüntüsünü al."""
        with self:
            sayfa = self.yeni_sayfa()
            try:
                sayfa.goto(url, wait_until="networkidle", timeout=30000)
                yol = kayit_yolu or f"/tmp/camofox_{int(__import__('time').time())}.png"
                sayfa.screenshot(path=yol, full_page=True)
                return yol
            except Exception as e:
                return f"[Camofox Ekran]: {e}"

    def kapat(self):
        if self._tarayici:
            self._tarayici.close()
        if self._pw:
            self._pw.stop()

    def __enter__(self):
        return self.baslat()

    def __exit__(self, *_):
        self.kapat()


def motor_kaydet(motor):
    """Camofox araçlarını motora kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    def _sayfa_oku(url: str) -> str:
        if not _PLAYWRIGHT_VAR:
            return "[Camofox]: playwright yüklü değil."
        try:
            c = CamofoxBrowser()
            return c.sayfa_oku(url)[:5000]
        except Exception as e:
            return f"[Camofox]: {e}"

    motor._plugin_arac_kaydet(
        "CAMOFOX_OKU",
        _sayfa_oku,
        "Anti-bot korumalı web sayfası içeriği getir",
    )


def run(url: str = "", bekleme: str = "networkidle", zaman_asimi: int = 30000) -> str:
    """Camofox modulu icin genel run() wrapper'ı."""
    if not url:
        return "[Camofox]: 'url' parametresi zorunludur."
    if not _PLAYWRIGHT_VAR:
        return "[Camofox]: playwright yüklü değil."
    try:
        with CamofoxBrowser() as browser:
            return browser.sayfa_oku(url, bekleme=bekleme, zaman_asimi=zaman_asimi)
    except Exception as e:
        return f"[Camofox]: {e}"


if __name__ == "__main__":
    if _PLAYWRIGHT_VAR:
        browser = CamofoxBrowser(gorunsuz=True)
        icerik = browser.sayfa_oku("https://example.com")
        print(icerik[:500])
    else:
        print("Playwright yüklü değil.")
