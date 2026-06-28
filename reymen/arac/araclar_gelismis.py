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
    """

    def __init__(self):
        self._pw = None
        self._browser = None
        self._page = None
        self._playwright_var = None

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
        """Mevcut veya yeni sayfa dondur."""
        if self._page:
            return self._page
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True, args=["--no-sandbox"])
        self._page = self._browser.new_page()
        self._page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 ReYMeNAgent/1.0"})
        return self._page

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

    def screenshot(self, url: str, cikti: str = "screenshot.png") -> str:
        if not self._playwright_yukle():
            return "[Browser] Playwright yuklu degil — screenshot alinamaz."
        try:
            p = self._sayfa_al()
            p.goto(url, timeout=20000, wait_until="networkidle")
            p.screenshot(path=cikti, full_page=True)
            return f"[Browser] Screenshot alindi: {cikti}"
        except Exception as e:
            return f"[Browser] Screenshot hatasi: {e}"

    def js_calistir(self, url: str, js: str) -> str:
        if not self._playwright_yukle():
            return "[Browser] Playwright yuklu degil."
        try:
            p = self._sayfa_al()
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
        except Exception as _araclar__e109:
            print(f"[UYARI] araclar_gelismis.py:110 - {_araclar__e109}")
        self._page = self._browser = self._pw = None

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

    def supervisor_rapor(ham: str) -> str:
        return _supervisor.rapor()

    def onay_iste_arac(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        mesaj = params[0] if params else ham
        tool = onay_tool or ApprovalTool()
        sonuc = tool.onay_iste("ReYMeN Onay", mesaj)
        return f"[Onay] {'ONAYLANDI' if sonuc else 'REDDEDILDI'}"

    _plugin_arac_kaydet(motor, "BROWSER_HEADLESS", browser_ac)
    _plugin_arac_kaydet(motor, "BROWSER_SCREENSHOT", browser_screenshot)
    _plugin_arac_kaydet(motor, "BROWSER_JS", browser_js)
    _plugin_arac_kaydet(motor, "SUPERVISOR_RAPOR", supervisor_rapor)
    _plugin_arac_kaydet(motor, "ONAY_ISTE", onay_iste_arac)
    _plugin_arac_kaydet(motor, "RESIM_OLUSTUR", resim_olustur)
    _plugin_arac_kaydet(motor, "VISION_ANALIZ", vision_analiz)
    print("[GelismisTools] 7 arac kayit edildi.")


# ═══════════════════════════════════════════════════════════════
# FAL.AI — Görsel Oluşturma
# ═══════════════════════════════════════════════════════════════

def resim_olustur(ham: str) -> str:
    """FAL.ai ile prompt'tan görsel oluşturur.

    Kullanım: RESIM_OLUSTUR "prompt"
    """
    try:
        import fal_client
        import os

        prompt = ham.strip().strip('"\'')
        if not prompt:
            return "[RESIM_OLUSTUR]: Prompt gerekli."

        # FAL_KEY kontrol
        api_key = os.environ.get("FAL_KEY") or os.environ.get("FAL_API_KEY")
        if not api_key:
            return "[RESIM_OLUSTUR]: FAL_KEY ortam değişkeni ayarlanmamış. 'set FAL_KEY=...' ile ayarlayın."

        sonuc = fal_client.run(
            "fal-ai/flux/schnell",
            arguments={"prompt": prompt},
        )
        if sonuc and "images" in sonuc and len(sonuc["images"]) > 0:
            img_url = sonuc["images"][0].get("url", "")
            return f"[RESIM_OLUSTUR]: ✅ Görsel oluşturuldu\nURL: {img_url}"
        return f"[RESIM_OLUSTUR]: Yanıt alınamadı: {sonuc}"
    except ImportError:
        return "[RESIM_OLUSTUR]: fal_client kurulu değil. 'pip install fal-client' çalıştırın."
    except Exception as e:
        return f"[RESIM_OLUSTUR]: Hata: {e}"


# ═══════════════════════════════════════════════════════════════
# VISION — FAL.ai ile Görsel Analiz (yedek)
# ═══════════════════════════════════════════════════════════════

def vision_analiz(ham: str) -> str:
    """FAL.ai vision modeli ile görsel analiz eder.

    Kullanım: VISION_ANALIZ "gorsel_yolu: soru"
    """
    try:
        import fal_client
        import os
        import base64

        params = ham.strip().split(":", 1)
        gorsel_yolu = params[0].strip().strip('"\'')
        soru = params[1].strip() if len(params) > 1 else "Bu görselde ne var?"

        if not os.path.exists(gorsel_yolu):
            return f"[VISION_ANALIZ]: Dosya bulunamadı: {gorsel_yolu}"

        api_key = os.environ.get("FAL_KEY") or os.environ.get("FAL_API_KEY")
        if not api_key:
            return "[VISION_ANALIZ]: FAL_KEY ortam değişkeni ayarlanmamış."

        with open(gorsel_yolu, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()

        sonuc = fal_client.run(
            "fal-ai/llavav15-13b",
            arguments={
                "image": f"data:image/jpeg;base64,{img_b64}",
                "prompt": soru,
            },
        )
        if sonuc and "output" in sonuc:
            return f"[VISION_ANALIZ]: {sonuc['output']}"
        return f"[VISION_ANALIZ]: Yanıt alınamadı: {sonuc}"
    except ImportError:
        return "[VISION_ANALIZ]: fal_client kurulu değil."
    except Exception as e:
        return f"[VISION_ANALIZ]: Hata: {e}"
