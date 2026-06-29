# -*- coding: utf-8 -*-
"""
araclar_gelismis.py — Gelismis Arac Seti.

Araçlar:
  BrowserTool      — Headless tarayici + screenshot + JS inject
  ApprovalTool     — Kullanici onay diyalogu (GUI/terminal)
  SupervisorTool   — Gorev izleme, thread saglik kontrolu, zaman asimi

motor.py'e dogrudan kayit edilebilir veya bagimsiz kullanilabilir.
"""
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent


# ═══════════════════════════════════════════════════════════════
# BROWSER TOOL — Headless Tarayici
# ═══════════════════════════════════════════════════════════════

class BrowserTool:
    """
    Playwright varsa: headless Chromium, screenshot, JS.
    Yoksa: urllib ile HTML → temiz metin fallback.

    Gelişmiş özellikler:
    - Form doldurma (fill, select_option)
    - Element bekleme (wait_for)
    - Hover, scroll, geçmiş
    - Sekme yönetimi
    - Sayfa snapshot / HTML
    - Network izleme
    - Dialog yönetimi
    """

    def __init__(self):
        self._pw = None
        self._browser = None
        self._page = None
        self._context = None
        self._playwright_var = None
        self._tabs: list = []
        self._tab_index = 0

    def _playwright_yukle(self) -> bool:
        if self._playwright_var is not None:
            return self._playwright_var
        try:
            from playwright.sync_api import sync_playwright
            self._playwright_var = True
        except ImportError:
            self._playwright_var = False
        return self._playwright_var

    def _sayfa_al(self):
        """Mevcut veya yeni sayfa döndür."""
        if self._page:
            return self._page
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True, args=["--no-sandbox"])
        self._context = self._browser.new_context(
            user_agent="Mozilla/5.0 ReYMeNAgent/1.0"
        )
        self._page = self._context.new_page()
        self._tabs = [self._page]
        self._tab_index = 0
        return self._page

    # ── Temel ──────────────────────────────────────────────────────

    def ac(self, url: str) -> str:
        if not self._playwright_yukle():
            return self._urllib_fallback(url)
        try:
            p = self._sayfa_al()
            p.goto(url, timeout=20000, wait_until="domcontentloaded")
            baslik = p.title()
            metin = p.inner_text("body")[:2000]
            return f"[Browser] {baslik}\nURL: {url}\n\n{metin}"
        except Exception as e:
            return self._urllib_fallback(url)

    def screenshot(self, url: str = "", cikti: str = "screenshot.png") -> str:
        if not self._playwright_yukle():
            return "[Browser] Playwright yuklu degil — screenshot alinamaz."
        try:
            p = self._sayfa_al()
            if url and self._page:
                p.goto(url, timeout=20000, wait_until="networkidle")
            p.screenshot(path=cikti, full_page=True)
            return f"[Browser] Screenshot alindi: {cikti}"
        except Exception as e:
            return f"[Browser] Screenshot hatasi: {e}"

    def js_calistir(self, url: str = "", js: str = "document.title") -> str:
        if not self._playwright_yukle():
            return "[Browser] Playwright yuklu degil."
        try:
            p = self._sayfa_al()
            if url:
                p.goto(url, timeout=20000)
            sonuc = p.evaluate(js)
            return f"[Browser] JS sonucu: {sonuc}"
        except Exception as e:
            return f"[Browser] JS hatasi: {e}"

    def tikla(self, secici: str) -> str:
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.click(secici, timeout=5000)
            time.sleep(0.5)
            return f"[Browser] Tiklandi: {secici}"
        except Exception as e:
            return f"[Browser] Tikla hatasi: {e}"

    def kapat(self):
        try:
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()
        except Exception as e:
            print(f"[UYARI] BrowserTool kapatma: {e}")
        self._page = self._tabs = None
        self._browser = self._pw = None
        self._context = None
        self._tab_index = 0

    # ── Gelişmiş ───────────────────────────────────────────────────

    def fill(self, secici: str, deger: str) -> str:
        """Form alanını doldur."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.fill(secici, deger, timeout=5000)
            return f"[Browser] Dolduruldu: {secici} = {deger[:50]}"
        except Exception as e:
            return f"[Browser] Fill hatasi: {e}"

    def type_text(self, secici: str, deger: str) -> str:
        """Karakter karakter yaz (keyboard event tetikler)."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.type(secici, deger, timeout=5000)
            return f"[Browser] Yazildi: {secici} = {deger[:50]}"
        except Exception as e:
            return f"[Browser] Type hatasi: {e}"

    def select_option(self, secici: str, deger: str) -> str:
        """Dropdown'tan değer seç."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.select_option(secici, deger, timeout=5000)
            return f"[Browser] Secildi: {secici} = {deger}"
        except Exception as e:
            return f"[Browser] Select hatasi: {e}"

    def wait_for(self, secici: str, timeout: int = 10) -> str:
        """Element sayfada görünene kadar bekle."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.wait_for_selector(secici, timeout=timeout * 1000)
            return f"[Browser] Element gorundu: {secici}"
        except Exception as e:
            return f"[Browser] Wait hatasi: {e}"

    def wait_for_text(self, metin: str, timeout: int = 10) -> str:
        """Metin sayfada görünene kadar bekle."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.wait_for_function(
                f'document.body.innerText.includes("{metin}")',
                timeout=timeout * 1000,
            )
            return f"[Browser] Metin gorundu: {metin[:50]}"
        except Exception as e:
            return f"[Browser] Wait text hatasi: {e}"

    def hover(self, secici: str) -> str:
        """Elementin üzerine gel."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.hover(secici, timeout=5000)
            return f"[Browser] Hover: {secici}"
        except Exception as e:
            return f"[Browser] Hover hatasi: {e}"

    def scroll(self, dx: int = 0, dy: int = 300) -> str:
        """Sayfayı kaydır."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.evaluate(f"window.scrollBy({dx}, {dy})")
            return f"[Browser] Scroll: dx={dx} dy={dy}"
        except Exception as e:
            return f"[Browser] Scroll hatasi: {e}"

    def scroll_to(self, secici: str) -> str:
        """Elemente kaydır."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.evaluate(f'document.querySelector("{secici}")?.scrollIntoView()')
            time.sleep(0.3)
            return f"[Browser] Scroll to: {secici}"
        except Exception as e:
            return f"[Browser] Scroll hatasi: {e}"

    def back(self) -> str:
        """Önceki sayfaya git."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.go_back()
            return f"[Browser] Geri: {self._page.title()}"
        except Exception as e:
            return f"[Browser] Geri hatasi: {e}"

    def forward(self) -> str:
        """Sonraki sayfaya git."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.go_forward()
            return f"[Browser] Ileri: {self._page.title()}"
        except Exception as e:
            return f"[Browser] Ileri hatasi: {e}"

    def reload(self) -> str:
        """Sayfayı yenile."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.reload()
            return f"[Browser] Yenilendi: {self._page.title()}"
        except Exception as e:
            return f"[Browser] Yenileme hatasi: {e}"

    def new_tab(self, url: str = "") -> str:
        """Yeni sekme aç."""
        if not self._playwright_yukle():
            return "[Browser] Playwright yuklu degil."
        try:
            p = self._sayfa_al()
            yeni = self._context.new_page() if self._context else p
            if url:
                yeni.goto(url, timeout=20000)
            self._tabs.append(yeni)
            self._page = yeni
            self._tab_index = len(self._tabs) - 1
            return f"[Browser] Yeni sekme #{self._tab_index}: {yeni.title()}"
        except Exception as e:
            return f"[Browser] Yeni sekme hatasi: {e}"

    def switch_tab(self, index: int) -> str:
        """Sekmeye geç."""
        if not self._tabs or index < 0 or index >= len(self._tabs):
            return f"[Browser] Gecersiz sekme: {index} (0-{len(self._tabs)-1})"
        try:
            self._page = self._tabs[index]
            self._tab_index = index
            return f"[Browser] Sekme #{index}: {self._page.title()}"
        except Exception as e:
            return f"[Browser] Sekme hatasi: {e}"

    def close_tab(self, index: int = -1) -> str:
        """Sekmeyi kapat (varsayilan: aktif)."""
        if not self._tabs:
            return "[Browser] Acik sekme yok."
        i = index if index >= 0 else self._tab_index
        if i < 0 or i >= len(self._tabs):
            return f"[Browser] Gecersiz sekme: {i}"
        try:
            self._tabs[i].close()
            self._tabs.pop(i)
            if i >= len(self._tabs):
                i = len(self._tabs) - 1
            self._page = self._tabs[i] if self._tabs else None
            self._tab_index = i if self._page else 0
            return f"[Browser] Sekme #{i} kapatildi."
        except Exception as e:
            return f"[Browser] Sekme kapatma hatasi: {e}"

    def tabs_list(self) -> str:
        """Açık sekmeleri listele."""
        if not self._tabs:
            return "[Browser] Acik sekme yok."
        satirlar = [f"[Browser] {len(self._tabs)} sekme:"]
        for i, t in enumerate(self._tabs):
            isaret = " <" if i == self._tab_index else "  "
            try:
                satirlar.append(f"  {isaret} #{i}: {t.title()[:60]}")
            except Exception:
                satirlar.append(f"  {isaret} #{i}: [kapali]")
        return "\n".join(satirlar)

    # ── Sayfa içeriği ──────────────────────────────────────────────

    def snapshot(self, maks: int = 3000) -> str:
        """Sayfanın tüm metnini döndür."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            metin = self._page.inner_text("body")
            return f"[Browser] Sayfa ({len(metin)} char):\n{metin[:maks]}"
        except Exception as e:
            return f"[Browser] Snapshot hatasi: {e}"

    def html(self, maks: int = 3000) -> str:
        """Sayfanın HTML kaynağını döndür."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            html_icerik = self._page.content()
            return f"[Browser] HTML ({len(html_icerik)} char):\n{html_icerik[:maks]}"
        except Exception as e:
            return f"[Browser] HTML hatasi: {e}"

    def title(self) -> str:
        """Sayfa başlığını döndür."""
        if not self._page:
            return "[Browser] Sayfa acik degil."
        try:
            return f"[Browser] Baslik: {self._page.title()}"
        except Exception as e:
            return f"[Browser] Baslik hatasi: {e}"

    def url(self) -> str:
        """Mevcut URL'yi döndür."""
        if not self._page:
            return "[Browser] Sayfa acik degil."
        try:
            return f"[Browser] URL: {self._page.url}"
        except Exception as e:
            return f"[Browser] URL hatasi: {e}"

    # ── Dialog ─────────────────────────────────────────────────────

    def dialog_accept(self) -> str:
        """Dialog'u onayla (alert/confirm/prompt)."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.once("dialog", lambda d: d.accept())
            return "[Browser] Dialog onaylandi."
        except Exception as e:
            return f"[Browser] Dialog hatasi: {e}"

    def dialog_dismiss(self) -> str:
        """Dialog'u reddet."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.once("dialog", lambda d: d.dismiss())
            return "[Browser] Dialog reddedildi."
        except Exception as e:
            return f"[Browser] Dialog hatasi: {e}"

    # ── Network ─────────────────────────────────────────────────────

    def network_requests(self, limit: int = 10) -> str:
        """Son network isteklerini listele (sadece URL)."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            from playwright.sync_api import Request
            requests = []
            def _kaydet(req: Request):
                if len(requests) < limit:
                    requests.append(f"{req.method} {req.url[:120]}")
            self._page.on("request", _kaydet)
            return f"[Browser] Network dinleyici aktif (son {limit} istek)."
        except Exception as e:
            return f"[Browser] Network hatasi: {e}"

    def clear_network(self) -> str:
        """Network log'larını temizle."""
        if not self._page:
            return "[Browser] Once ac() cagir."
        try:
            self._page.remove_listener("request", lambda _: None)
            return "[Browser] Network log temizlendi."
        except Exception as e:
            return f"[Browser] Temizleme hatasi: {e}"

    # ── Devlet yönetimi ────────────────────────────────────────────

    def cookies(self) -> str:
        """Mevcut cookie'leri listele."""
        if not self._context:
            return "[Browser] Context yok."
        try:
            ciks = self._context.cookies()
            if not ciks:
                return "[Browser] Cookie yok."
            satirlar = [f"[Browser] {len(ciks)} cookie:"]
            for c in ciks[:10]:
                satirlar.append(f"  {c['name']} = {c['value'][:40]}")
            return "\n".join(satirlar)
        except Exception as e:
            return f"[Browser] Cookie hatasi: {e}"

    def clear_state(self) -> str:
        """Cookie, storage, cache temizle."""
        if not self._context:
            return "[Browser] Context yok."
        if not self._page:
            return "[Browser] Sayfa acik degil."
        try:
            self._context.clear_cookies()
            self._page.evaluate("localStorage.clear(); sessionStorage.clear();")
            return "[Browser] State temizlendi (cookie+storage)."
        except Exception as e:
            return f"[Browser] State temizleme hatasi: {e}"

    # ── Fallback ───────────────────────────────────────────────────

    def _urllib_fallback(self, url: str) -> str:
        import urllib.request
        from html.parser import HTMLParser
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                html = r.read().decode(r.headers.get_content_charset("utf-8") or "utf-8", errors="replace")
            class P(HTMLParser):
                def __init__(self):
                    super().__init__(); self._t=[]; self._s=False
                def handle_starttag(self, t, _):
                    if t in ("script","style"): self._s=True
                def handle_endtag(self, t):
                    if t in ("script","style"): self._s=False
                def handle_data(self, d):
                    if not self._s and d.strip(): self._t.append(d.strip())
            p=P(); p.feed(html)
            return "[Browser:urllib] " + " ".join(p._t)[:2000]
        except Exception as e:
            return f"[Browser] Hata: {e}"


# ═══════════════════════════════════════════════════════════════
# APPROVAL TOOL — Onay Diyalogu
# ═══════════════════════════════════════════════════════════════

class ApprovalTool:
    """
    Riskli eylemler icin kullanici onayi ister.
    GUI varsa tkinter dialog, yoksa terminal prompt.
    Zaman asiminda auto-deny.
    """

    def __init__(self, varsayilan_ret: bool = True, timeout: int = 30):
        self.varsayilan_ret = varsayilan_ret
        self.timeout = timeout

    def onay_iste(self, baslik: str, mesaj: str, eylem: str = "") -> bool:
        """True = onaylandi, False = reddedildi."""
        tam_mesaj = f"{mesaj}"
        if eylem:
            tam_mesaj += f"\nEylem: {eylem}"

        # GUI dene
        if self._gui_dene(baslik, tam_mesaj):
            return True

        # Terminal fallback — zaman asimi ile
        return self._terminal_onay(baslik, tam_mesaj)

    def _gui_dene(self, baslik: str, mesaj: str) -> bool | None:
        """tkinter mesaj kutusu — True=onay, None=GUI yok/hata."""
        try:
            import tkinter as tk
            from tkinter import messagebox
            sonuc = [None]
            def _goster():
                root = tk.Tk()
                root.withdraw()
                cevap = messagebox.askyesno(baslik, mesaj, default="no")
                sonuc[0] = cevap
                root.destroy()
            t = threading.Thread(target=_goster, daemon=True)
            t.start()
            t.join(timeout=self.timeout)
            return sonuc[0]
        except Exception:
            return None

    def _terminal_onay(self, baslik: str, mesaj: str) -> bool:
        """Terminal'de [e/H] onayi — zaman asimi = ret."""
        print(f"\n{'='*50}")
        print(f"  ONAY GEREKIYOR: {baslik}")
        print(f"  {mesaj}")
        print(f"  [{self.timeout}sn icinde cevap verilmezse ret]")
        print(f"{'='*50}")

        cevap = [None]

        def _oku():
            try:
                c = input("  Onayliyor musunuz? [e/H] > ").strip().lower()
                cevap[0] = c in ("e", "evet", "y", "yes")
            except Exception:
                cevap[0] = False

        t = threading.Thread(target=_oku, daemon=True)
        t.start()
        t.join(timeout=self.timeout)

        if cevap[0] is None:
            print(f"  [Zaman asimi] Otomatik red.")
            return False

        return bool(cevap[0])

    def motor_onay_fonksiyonu(self, arac: str, ozet: str) -> bool:
        """motor.py onay_fonksiyonu formatina uygun wrapper."""
        RISKLI_ARAÇLAR = {
            "KOMUT_CALISTIR": "Sistem komutu calistirilacak",
            "PYTHON_CALISTIR": "Python kodu calistirilacak",
            "DOSYA_YAZ": "Dosya yazilacak",
            "TARAYICI_AC": "Tarayici acilacak",
            "EKRAN_TIKLA": "Ekrana tiklanacak",
        }
        aciklama = RISKLI_ARAÇLAR.get(arac, f"{arac} calismak uzerine")
        return self.onay_iste(
            f"Onay: {arac}",
            f"{aciklama}:\n{ozet[:200]}",
            eylem=arac,
        )


# ═══════════════════════════════════════════════════════════════
# SUPERVISOR TOOL — Gorev Izleyici
# ═══════════════════════════════════════════════════════════════

class SupervisorTool:
    """
    Gorev izleyici — thread saglik kontrolu, zaman asimi, hata sayaci.
    Ana dongunun disinda bir watchdog gibi calisir.
    """

    def __init__(self, zaman_asimi: int = 300, hata_esigi: int = 5):
        self.zaman_asimi = zaman_asimi
        self.hata_esigi = hata_esigi
        self._gorevler: dict[str, dict] = {}
        self._kilit = threading.Lock()
        self._izleyici: threading.Thread | None = None
        self._calisiyor = False

    def izlemeyi_baslat(self):
        self._calisiyor = True
        self._izleyici = threading.Thread(target=self._izle, daemon=True)
        self._izleyici.start()

    def izlemeyi_durdur(self):
        self._calisiyor = False

    def gorev_kaydet(self, gorev_id: str, thread: threading.Thread, meta: dict = None):
        with self._kilit:
            self._gorevler[gorev_id] = {
                "thread": thread,
                "baslangic": time.time(),
                "hata_sayisi": 0,
                "durum": "calisiyor",
                "meta": meta or {},
            }

    def hata_bildir(self, gorev_id: str):
        with self._kilit:
            if gorev_id in self._gorevler:
                self._gorevler[gorev_id]["hata_sayisi"] += 1

    def gorev_durumu(self, gorev_id: str) -> dict:
        with self._kilit:
            return dict(self._gorevler.get(gorev_id, {}))

    def tum_gorevler(self) -> list[dict]:
        with self._kilit:
            sonuc = []
            for gid, g in self._gorevler.items():
                sure = round(time.time() - g["baslangic"], 1)
                canli = g["thread"].is_alive() if g.get("thread") else False
                sonuc.append({
                    "id": gid,
                    "sure": sure,
                    "canli": canli,
                    "hata": g["hata_sayisi"],
                    "durum": g["durum"],
                })
            return sonuc

    def _izle(self):
        while self._calisiyor:
            time.sleep(5)
            with self._kilit:
                olmus = []
                for gid, g in self._gorevler.items():
                    sure = time.time() - g["baslangic"]
                    if g.get("thread") and not g["thread"].is_alive():
                        g["durum"] = "bitti"
                        olmus.append(gid)
                    elif sure > self.zaman_asimi:
                        g["durum"] = "zaman_asimi"
                        print(f"[Supervisor] Zaman asimi: {gid} ({sure:.0f}s)")
                    elif g["hata_sayisi"] >= self.hata_esigi:
                        g["durum"] = "hata_esigi"
                        print(f"[Supervisor] Hata esigi: {gid} ({g['hata_sayisi']} hata)")

    def rapor(self) -> str:
        gorevler = self.tum_gorevler()
        if not gorevler:
            return "[Supervisor] Izlenen gorev yok."
        satirlar = [f"[Supervisor] {len(gorevler)} gorev:"]
        for g in gorevler:
            canli = "CANLI" if g["canli"] else "BITTI"
            satirlar.append(
                f"  {g['id']:20s} {canli:6s} {g['sure']:6.1f}s  "
                f"hata:{g['hata']} {g['durum']}"
            )
        return "\n".join(satirlar)


# ═══════════════════════════════════════════════════════════════
# Motor kayit fonksiyonu
# ═══════════════════════════════════════════════════════════════

_browser = BrowserTool()
_supervisor = SupervisorTool()
_supervisor.izlemeyi_baslat()


def motor_kaydet(motor, onay_tool: ApprovalTool = None):
    """motor.py'ye gelismis araclari kaydet."""
    from plugins.kanban import _plugin_arac_kaydet

    def browser_ac(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        return _browser.ac(params[0] if params else ham.strip('"'))

    def browser_screenshot(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        url = params[0] if params else ""
        dosya = params[1] if len(params) > 1 else "screenshot.png"
        return _browser.screenshot(url, dosya)

    def browser_js(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        url = params[0] if params else ""
        js = params[1] if len(params) > 1 else "document.title"
        return _browser.js_calistir(url, js)

    def browser_fill(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        if len(params) < 2:
            return '[Browser] Kullanim: BROWSER_FILL "secici" "deger"'
        return _browser.fill(params[0], params[1])

    def browser_click(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        return _browser.tikla(params[0] if params else ham.strip('"'))

    def browser_wait(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        secici = params[0] if params else ham.strip('"')
        timeout = int(params[1]) if len(params) > 1 else 10
        return _browser.wait_for(secici, timeout)

    def browser_select(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        if len(params) < 2:
            return '[Browser] Kullanim: BROWSER_SELECT "secici" "deger"'
        return _browser.select_option(params[0], params[1])

    def browser_snapshot(ham: str) -> str:
        return _browser.snapshot()

    def browser_html(ham: str) -> str:
        return _browser.html()

    def browser_tabs(ham: str) -> str:
        """BROWSER_TABS: sekmeleri listele"""
        return _browser.tabs_list()

    def browser_new_tab(ham: str) -> str:
        """BROWSER_NEW_TAB "url": yeni sekme ac"""
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        return _browser.new_tab(params[0] if params else "")

    def browser_switch_tab(ham: str) -> str:
        """BROWSER_SWITCH_TAB index: sekmeye gec"""
        try:
            idx = int(ham.strip())
            return _browser.switch_tab(idx)
        except ValueError:
            return "[Browser] Gecersiz sekme index."

    def browser_back(ham: str) -> str:
        return _browser.back()

    def browser_forward(ham: str) -> str:
        return _browser.forward()

    def browser_reload(ham: str) -> str:
        return _browser.reload()

    def browser_scroll(ham: str) -> str:
        """BROWSER_SCROLL "dy" veya BROWSER_SCROLL: 300px asagi"""
        try:
            dy = int(ham.strip())
            return _browser.scroll(dy=dy)
        except ValueError:
            return _browser.scroll(dy=300)

    def browser_hover(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        return _browser.hover(params[0] if params else ham.strip('"'))

    def browser_close(ham: str) -> str:
        _browser.kapat()
        return "[Browser] Kapandi."

    def browser_status(ham: str) -> str:
        if _browser._page:
            return f"[Browser] Acik: {_browser.title()}\n{_browser.url()}"
        return "[Browser] Kapali."

    def supervisor_rapor(ham: str) -> str:
        return _supervisor.rapor()

    def onay_iste_arac(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        mesaj = params[0] if params else ham
        tool = onay_tool or ApprovalTool()
        sonuc = tool.onay_iste("ReYMeN Onay", mesaj)
        return f"[Onay] {'ONAYLANDI' if sonuc else 'REDDEDILDI'}"

    # Temel
    _plugin_arac_kaydet(motor, "BROWSER_HEADLESS", browser_ac)
    _plugin_arac_kaydet(motor, "BROWSER_SCREENSHOT", browser_screenshot)
    _plugin_arac_kaydet(motor, "BROWSER_JS", browser_js)
    _plugin_arac_kaydet(motor, "SUPERVISOR_RAPOR", supervisor_rapor)
    _plugin_arac_kaydet(motor, "ONAY_ISTE", onay_iste_arac)

    # Gelişmiş browser
    _plugin_arac_kaydet(motor, "BROWSER_FILL", browser_fill)
    _plugin_arac_kaydet(motor, "BROWSER_CLICK", browser_click)
    _plugin_arac_kaydet(motor, "BROWSER_WAIT", browser_wait)
    _plugin_arac_kaydet(motor, "BROWSER_SELECT", browser_select)
    _plugin_arac_kaydet(motor, "BROWSER_SNAPSHOT", browser_snapshot)
    _plugin_arac_kaydet(motor, "BROWSER_HTML", browser_html)
    _plugin_arac_kaydet(motor, "BROWSER_TABS", browser_tabs)
    _plugin_arac_kaydet(motor, "BROWSER_NEW_TAB", browser_new_tab)
    _plugin_arac_kaydet(motor, "BROWSER_SWITCH_TAB", browser_switch_tab)
    _plugin_arac_kaydet(motor, "BROWSER_BACK", browser_back)
    _plugin_arac_kaydet(motor, "BROWSER_FORWARD", browser_forward)
    _plugin_arac_kaydet(motor, "BROWSER_RELOAD", browser_reload)
    _plugin_arac_kaydet(motor, "BROWSER_SCROLL", browser_scroll)
    _plugin_arac_kaydet(motor, "BROWSER_HOVER", browser_hover)
    _plugin_arac_kaydet(motor, "BROWSER_CLOSE", browser_close)
    _plugin_arac_kaydet(motor, "BROWSER_STATUS", browser_status)
    print("[GelismisTools] 21 arac kayit edildi.")


# ═══════════════════════════════════════════════════════════════
# FAL.AI — Görsel Oluşturma (KALDIRILDI: araclar_goruntu.py'ye tasindi)
# ═══════════════════════════════════════════════════════════════
