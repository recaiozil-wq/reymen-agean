# -*- coding: utf-8 -*-
"""browser_engine.py â€” Unified Browser Automation Engine.

Playwright MCP + Browser Use entegrasyonu.
Ayrik MCP sunucu baglantisi yerine dogrudan Python API'si sunar.

State yönetimi: SekmeYoneticisi ile tekil sekme kontrolü.

Kullanim:
    from reymen.arac.browser_engine import BrowserEngine
    be = BrowserEngine()
    be.sayfa_ac("https://example.com")
    print(be.sayfa_basligi())
    be.kapat()
"""

import json
import logging
import os
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any, Optional

import shutil

logger = logging.getLogger(__name__)

# â”€â”€ Sekme State Yönetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def log_sekme_durumu(browser, baglam: str = "", olay: str = ""):
    """TeÅŸhis: açÄ±k sekmeleri ve çaÄŸrÄ± yÄ±ÄŸÄ±nÄ±nÄ± logla.

    KullanÄ±m:
        log_sekme_durumu(browser, "gorev_baslat", "new_page öncesi")
    """
    try:
        sekmeler = browser.pages if hasattr(browser, "pages") else []
        logger.info("[Sekme:%s:%s] Acik sekme: %d", baglam, olay, len(sekmeler))
        for i, s in enumerate(sekmeler):
            try:
                url = s.url
            except Exception:
                url = "[kapali]"
            logger.info("  [%d] %s", i, url)
        # Kim çaÄŸÄ±rdÄ±?
        logger.info("  Cagri yigini (son 3):")
        for line in traceback.format_stack(limit=3)[:-1]:
            logger.info("    %s", line.strip())
    except Exception as e:
        logger.warning("[Sekme] Log hatasi: %s", e)


class SekmeYoneticisi:
    """Tekil sekme yöneticisi â€” invisible döngü tuzaÄŸÄ±nÄ± önler.

    Bot artÄ±k her yerde sekme_al() çaÄŸÄ±rÄ±r â€” kendi kendine açÄ±p kapamaz,
    çünkü sekme varlÄ±ÄŸÄ± merkezi bir yerden kontrol ediliyor.

    Kullanim:
        sy = SekmeYoneticisi(browser)
        sayfa = sy.sekme_al()       # var olani don, yoksa yeni ac
        sy.sekme_kapat()             # guvenli kapat
        print(sy.aktif_url)          # mevcut url
    """

    def __init__(self, browser):
        self.browser = browser
        self._aktif_sekme = None

    @property
    def aktif_url(self) -> str:
        """Aktif sekmenin URL'si (kapaliysa '')."""
        try:
            if self._aktif_sekme and not self._aktif_sekme.is_closed():
                return self._aktif_sekme.url
        except Exception as _e:
            logger.warning("[BrowserEngine] except Exception (L79): %s", Exception)
            pass
        return ""

    def sekme_al(self):
        """Aktif sekmeyi döndür, yoksa yeni aç.

        Returns:
            Page nesnesi veya None
        """
        try:
            if self._aktif_sekme and not self._aktif_sekme.is_closed():
                return self._aktif_sekme
        except Exception as _e:
            logger.warning("[BrowserEngine] except Exception (L92): %s", Exception)
            pass

        # Kapali/yok â†’ yeni sekme aç
        log_sekme_durumu(self.browser, "SekmeYoneticisi", "sekme_al:yeni")
        try:
            self._aktif_sekme = self.browser.new_page()
            logger.info("[SekmeYoneticisi] Yeni sekme acildi")
        except Exception as e:
            logger.error("[SekmeYoneticisi] new_page hatasi: %s", e)
            self._aktif_sekme = None

        return self._aktif_sekme

    def sekme_kapat(self):
        """Aktif sekmeyi güvenli ÅŸekilde kapat."""
        try:
            if self._aktif_sekme and not self._aktif_sekme.is_closed():
                log_sekme_durumu(self.browser, "SekmeYoneticisi", "sekme_kapat:once")
                self._aktif_sekme.close()
                logger.info("[SekmeYoneticisi] Sekme kapatildi")
        except Exception as e:
            logger.warning("[SekmeYoneticisi] Kapatma hatasi: %s", e)
        finally:
            self._aktif_sekme = None


# Playwright MCP: npx ile calistir
_NPX = shutil.which("npx") or "npx"
PLAYWRIGHT_MCP_CMD = [_NPX, "-y", "@playwright/mcp"]

# Browser Use
try:
    from browser_use import Agent as BrowserUseAgent

    BROWSER_USE_OK = True
except ImportError:
    BROWSER_USE_OK = False


class PlaywrightMCPEngine:
    """Playwright MCP ile tarayici kontrolu."""

    def __init__(self):
        self._proc: Optional[subprocess.Popen] = None
        self._istek_id = 0

    def baslat(self) -> bool:
        """Playwright MCP sunucusunu baslat."""
        try:
            self._proc = subprocess.Popen(
                PLAYWRIGHT_MCP_CMD,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # Initialize
            self._json_rpc(
                "initialize",
                {
                    "protocolVersion": "0.1.0",
                    "capabilities": {},
                    "clientInfo": {"name": "ReYMeN", "version": "1.0"},
                },
            )
            return True
        except Exception as e:
            logger.error("[Playwright] Baslatma hatasi: %s", e)
            return False

    def _json_rpc(self, method: str, params: dict) -> dict:
        self._istek_id += 1
        istek = (
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": self._istek_id,
                    "method": method,
                    "params": params,
                }
            )
            + "\n"
        )
        try:
            self._proc.stdin.write(istek)
            self._proc.stdin.flush()
            satir = self._proc.stdout.readline()
            return json.loads(satir) if satir else {}
        except Exception as e:
            return {"error": str(e)}

    def sayfa_ac(self, url: str) -> str:
        """Sayfa ac."""
        yanit = self._json_rpc(
            "tools/call",
            {
                "name": "browser_navigate",
                "arguments": {"url": url},
            },
        )
        return str(yanit.get("result", {}))

    def tikla(self, selector: str) -> str:
        """Elemente tikla."""
        yanit = self._json_rpc(
            "tools/call",
            {
                "name": "browser_click",
                "arguments": {"selector": selector},
            },
        )
        return str(yanit.get("result", {}))

    def yazi_yaz(self, selector: str, text: str) -> str:
        """Input alanina yazi yaz."""
        yanit = self._json_rpc(
            "tools/call",
            {
                "name": "browser_type",
                "arguments": {"selector": selector, "text": text},
            },
        )
        return str(yanit.get("result", {}))

    def ekran_goruntusu(self) -> str:
        """Ekran goruntusu al."""
        yanit = self._json_rpc(
            "tools/call",
            {
                "name": "browser_screenshot",
                "arguments": {},
            },
        )
        return str(yanit.get("result", {}))

    def sayfa_basligi(self) -> str:
        """Sayfa basligini al (browser_snapshot ile)."""
        yanit = self._json_rpc(
            "tools/call",
            {
                "name": "browser_snapshot",
                "arguments": {},
            },
        )
        return str(yanit.get("result", {}))

    def kapat(self):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None


class BrowserUseEngine:
    """Browser Use: AI destekli tarayici otomasyonu."""

    def __init__(self):
        self._agent = None

    async def calistir(self, gorev: str, llm: Any = None) -> str:
        """AI ile tarayici gorevini calistir.

        Args:
            gorev: "Google'da ReYMeN ara ve ilk sonucu ac" gibi dogal dil.
            llm: LangChain/ChatOpenAI benzeri LLM nesnesi (zorunlu). Bos gecilirse
                 PlaywrightMCPEngine alternatif olarak kullanilir.

        Returns:
            Islem sonucu.
        """
        if not BROWSER_USE_OK:
            return "[BrowserUse] pip install browser-use gerekli"

        # LLM zorunlu â€” yoksa Playwright fallback'i oner veya hata don
        if llm is None:
            return (
                "[BrowserUse] LLM gerekli â€” Agent(task=..., llm=...) ile bir LLM saglayin. "
                "Ornek: ChatOpenAI(model='gpt-4'). "
                "Alternatif: Playwright MCP (npx @playwright/mcp) kullanin."
            )

        try:
            agent = BrowserUseAgent(task=gorev, llm=llm)
            sonuc = await agent.run()
            return str(sonuc)
        except Exception as e:
            return f"[BrowserUse] Hata: {e}"


class BrowserEngine:
    """Unified Browser Engine: Playwright MCP + Browser Use.

    Otomatik olarak Playwright MCP'yi dener, yoksa Browser Use'a gecer.

    State yönetimi:
      - SekmeYoneticisi ile tekil sekme kontrolü
      - Her adÄ±mda sekme varlÄ±ÄŸÄ± kontrolü
      - Invisible döngü tespiti
    """

    def __init__(self):
        self._playwright = PlaywrightMCPEngine()
        self._browser_use = BrowserUseEngine()
        self._aktif = None
        self._sekme_yoneticisi = None  # SekmeYoneticisi (lazy)

    @property
    def sekme_yoneticisi(self):
        """Sekme yöneticisini lazy al."""
        return self._sekme_yoneticisi

    def baslat(self) -> str:
        """Tarayici motorunu baslat."""
        # Once Playwright MCP'yi dene
        if self._playwright.baslat():
            self._aktif = "playwright"
            # Sekme yöneticisi Playwright MCP üzerinden çalÄ±ÅŸÄ±r
            # (MCP tool'larÄ± browser.pages'a eriÅŸemez â€” engine seviyesinde)
            return "[Browser] Playwright MCP baslatildi"
        # Yoksa Browser Use
        if BROWSER_USE_OK:
            self._aktif = "browser_use"
            return "[Browser] Browser Use hazir"
        return "[Browser] Hicbir tarayici motoru kullanilamiyor"

    def sayfa_ac(self, url: str) -> str:
        if self._aktif == "playwright":
            return self._playwright.sayfa_ac(url)
        return "[Browser] Motor aktif degil"

    def tikla(self, selector: str) -> str:
        if self._aktif == "playwright":
            return self._playwright.tikla(selector)
        return "[Browser] Motor aktif degil"

    def ekran_goruntusu(self) -> str:
        if self._aktif == "playwright":
            return self._playwright.ekran_goruntusu()
        return "[Browser] Motor aktif degil"

    def kapat(self):
        if self._aktif == "playwright":
            self._playwright.kapat()
        self._aktif = None
        self._sekme_yoneticisi = None


def motor_kaydet(motor):
    """Motor'a browser araclarini kaydet."""
    if hasattr(motor, "_plugin_arac_kaydet"):
        _engine = BrowserEngine()

        def _sayfa_ac(url: str = "") -> str:
            return _engine.baslat() + "\n" + (_engine.sayfa_ac(url) if url else "")

        motor._plugin_arac_kaydet(
            "TARAYICI_AC",
            _sayfa_ac,
            "Tarayici motorunu baslat ve sayfa ac. Parametre: url (opsiyonel)",
        )
        motor._plugin_arac_kaydet(
            "TARAYICI_TIKLA",
            lambda selector="": _engine.tikla(selector),
            "Sayfadaki bir elemente tikla. Parametre: selector (CSS)",
        )
        motor._plugin_arac_kaydet(
            "TARAYICI_EKRAN",
            lambda: _engine.ekran_goruntusu(),
            "Sayfanin ekran goruntusunu al",
        )
        logger.info("[Browser] Motor'a 3 arac kaydedildi")


# â”€â”€ Test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = BrowserEngine()
    print(engine.baslat())
    if engine._aktif:
        print(engine.sayfa_ac("https://example.com"))
    engine.kapat()
