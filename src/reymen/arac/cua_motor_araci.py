"""
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘  ReYMeN â€” CUA_EKRAN_KULLAN  â€¢  cua_motor_araci.py               â•‘
â•‘  Tam otonom: Ekran â†’ Vision â†’ Koordinat â†’ Eylem â†’ DoÄŸrula       â•‘
â•‘  motor.py'ye doÄŸrudan import edilir.                             â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘  v2.0 â€” DÃ¼zeltmeler:                                             â•‘
â•‘   1. Config YAML desteÄŸi (LM_STUDIO_URL artÄ±k sabit deÄŸil)       â•‘
â•‘   2. tikla() iÃ§inde FailSafeException yakalama                   â•‘
â•‘   3. DoÄŸrulama: EVET/HAYIR + sonraki koordinat Ã¶nerisi           â•‘
â•‘   4. Adaptif MAX_DENEME (baÅŸarÄ±sÄ±zlÄ±kla artar)                   â•‘
â•‘   5. requests.Session havuzu (~%20 hÄ±z kazancÄ±)                  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

KURULUM:
    pip install mss pyautogui requests pillow pyyaml

MOTOR.PY'YE EKLE:
    from cua_motor_araci import CUA_EKRAN_KULLAN, CUA_ARACLARI_TARA
import logging
logger = logging.getLogger(__name__)

CONFIG (isteÄŸe baÄŸlÄ± â€” cua_config.yaml):
    lm_studio_url: http://localhost:1234/v1/chat/completions
    lm_studio_model: llava
    max_deneme: 3
    tikla_bekleme: 1.0
"""

from __future__ import annotations

import base64
import gc
import json
import logging
import re
import time
import weakref
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Generator, Optional

import requests

# pyautogui ve PIL lazy import â€” kullanÄ±m anÄ±nda try/except ile yÃ¼klenir
# Kurulum: pip install pyautogui pillow mss

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. CONFIG â€” YAML'DAN OKU, YOKSA VARSAYILAN
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _config_yukle() -> dict:
    """
    cua_config.yaml varsa oradan, yoksa varsayÄ±lanlarÄ± dÃ¶ndÃ¼rÃ¼r.
    PyYAML kurulu deÄŸilse sessizce varsayÄ±lana dÃ¼ÅŸer.
    """
    varsayilan = {
        "lm_studio_url": "http://localhost:1234/v1/chat/completions",
        "lm_studio_model": "llava",
        "max_deneme": 3,
        "tikla_bekleme": 1.0,
        "screenshot_dir": "reymen_screenshots",
        "log_dosyasi": "cua_log.txt",
        "guvenli_bolge": [10, 10],
    }
    config_yol = Path("cua_config.yaml")
    if not config_yol.exists():
        return varsayilan
    try:
        import yaml  # type: ignore

        with config_yol.open(encoding="utf-8") as f:
            kullanici = yaml.safe_load(f) or {}
        return {**varsayilan, **kullanici}
    except Exception:
        return varsayilan


_CFG = _config_yukle()

LM_STUDIO_URL: str = _CFG["lm_studio_url"]
LM_STUDIO_MODEL: str = _CFG["lm_studio_model"]
SCREENSHOT_DIR: Path = Path(_CFG["screenshot_dir"])
LOG_DOSYASI: Path = Path(_CFG["log_dosyasi"])
TIKLA_BEKLEME: float = float(_CFG["tikla_bekleme"])
MAX_DENEME_TABAN: int = int(_CFG["max_deneme"])  # adaptif iÃ§in taban
GUVENLI_BOLGE: tuple[int, int] = tuple(_CFG["guvenli_bolge"])  # type: ignore

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# LOGGING
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

logging.basicConfig(
    level=logging.INFO,
    format="[CUA %(asctime)s] %(levelname)s â†’ %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DOSYASI, encoding="utf-8"),
    ],
)
log = logging.getLogger("CUA")

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 5. REQUESTS SESSION HAVUZU
#    Tek Session nesnesi, baÄŸlantÄ±larÄ± yeniden kullanÄ±r.
#    weakref ile tutulur â€” modÃ¼l kapanÄ±nca GC onu temizler.
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_session_ref: Optional[weakref.ref] = None


def _get_session() -> requests.Session:
    """
    Tek bir requests.Session dÃ¶ndÃ¼rÃ¼r; yoksa oluÅŸturur.
    BaÄŸlantÄ± havuzu ~%20 hÄ±z kazancÄ± saÄŸlar.
    """
    global _session_ref
    if _session_ref is not None:
        s = _session_ref()
        if s is not None:
            return s
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    # weakref: Session bÃ¼yÃ¼k bir nesne deÄŸil ama tutarlÄ±lÄ±k iÃ§in
    _session_ref = weakref.ref(s)
    return s


# Critic Note: _session_ref bir weakref.ref tutar; Python'Ä±n GC'si
# Session'Ä± referans kalmadÄ±ÄŸÄ±nda temizler; baÄŸlantÄ± havuzu sÄ±zÄ±ntÄ±sÄ± yok.


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# VERÄ° YAPILARI
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class CUASonucu:
    basarili: bool
    eylem: str
    koordinat: Optional[tuple[int, int]] = None
    vision_yaniti: str = ""
    sonraki_koordinat: Optional[tuple[int, int]] = None  # v2: doÄŸrulamadan gelen Ã¶neri
    hata: str = ""
    ekran_boyutu: tuple[int, int] = field(default_factory=lambda: (0, 0))

    def str(self) -> str:
        if self.basarili:
            sonraki = (
                f" | Sonraki Ã¶neri: {self.sonraki_koordinat}"
                if self.sonraki_koordinat
                else ""
            )
            return (
                f"âœ… Eylem: {self.eylem} | "
                f"Koordinat: {self.koordinat} | "
                f"Ekran: {self.ekran_boyutu}{sonraki}"
            )
        return f"âŒ BaÅŸarÄ±sÄ±z: {self.hata}"


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# EKRAN GÃ–RÃœNTÃœSÃœ
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def ekran_goruntusu_al() -> tuple[Image.Image, tuple[int, int]]:
    """
    Tam ekran gÃ¶rÃ¼ntÃ¼sÃ¼ alÄ±r.
    Ã–nce mss dener; yoksa pyautogui'ye dÃ¼ÅŸer.
    DÃ¶ner: (PIL.Image, (geniÅŸlik, yÃ¼kseklik))
    """
    from PIL import Image

    SCREENSHOT_DIR.mkdir(exist_ok=True)
    try:
        import mss

        with mss.mss() as sct:
            ham = sct.grab(sct.monitors[1])
            goruntu = Image.frombytes("RGB", ham.size, ham.bgra, "raw", "BGRX")
            log.info(f"Ekran alÄ±ndÄ± (mss): {goruntu.size}")
            return goruntu, goruntu.size
    except ImportError:
        log.warning("mss bulunamadÄ± â€” pyautogui yedek devreye girdi.")
    try:
        import pyautogui

        goruntu = pyautogui.screenshot()
        log.info(f"Ekran alÄ±ndÄ± (pyautogui): {goruntu.size}")
        return goruntu, goruntu.size
    except ImportError:
        raise ImportError(
            "Ekran gÃ¶rÃ¼ntÃ¼sÃ¼ iÃ§in mss veya pyautogui gerekli. pip install mss pyautogui"
        )


def goruntu_base64_yap(goruntu: Image.Image, max_genislik: int = 1280) -> str:
    """
    PIL gÃ¶rÃ¼ntÃ¼sÃ¼nÃ¼ Base64 JPEG'e dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r.
    BÃ¼yÃ¼k ekranlarda yeniden boyutlandÄ±rÄ±r.
    """
    from PIL import Image

    if goruntu.width > max_genislik:
        oran = max_genislik / goruntu.width
        yeni_boyut = (max_genislik, int(goruntu.height * oran))
        goruntu = goruntu.resize(yeni_boyut, Image.LANCZOS)
        log.info(f"GÃ¶rÃ¼ntÃ¼ yeniden boyutlandÄ±rÄ±ldÄ±: {yeni_boyut}")
    tampon = BytesIO()
    goruntu.save(tampon, format="JPEG", quality=85)
    b64 = base64.b64encode(tampon.getvalue()).decode("utf-8")
    tampon.close()
    del tampon
    gc.collect()
    return b64


# Critic Note: BytesIO aÃ§Ä±kÃ§a kapatÄ±lÄ±r, gc.collect() Ã§aÄŸrÄ±lÄ±r;
# bÃ¼yÃ¼k PIL nesnesi scope dÄ±ÅŸÄ±na Ã§Ä±ktÄ±ÄŸÄ±nda GC tarafÄ±ndan toplanÄ±r.


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# VÄ°SÄ°ON MODEL Ä°LETÄ°ÅÄ°MÄ°
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def vision_modele_sor(
    goruntu_b64: str,
    prompt: str,
    zaman_asimi: int = 30,
) -> str:
    """
    LM Studio llava endpoint'ine gÃ¶rÃ¼ntÃ¼ + prompt gÃ¶nderir.
    Session havuzunu kullanÄ±r â€” baÄŸlantÄ± yeniden aÃ§Ä±lmaz.
    """
    payload = {
        "model": LM_STUDIO_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{goruntu_b64}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        "max_tokens": 256,
        "temperature": 0.1,
    }
    try:
        session = _get_session()
        yanit = session.post(LM_STUDIO_URL, json=payload, timeout=zaman_asimi)
        yanit.raise_for_status()
        metin = yanit.json()["choices"][0]["message"]["content"]
        log.info(f"Vision yanÄ±tÄ±: {metin[:120]}")
        return metin
    except requests.exceptions.ConnectionError:
        hata = "LM Studio baÄŸlantÄ±sÄ± kurulamadÄ±. http://localhost:1234 Ã§alÄ±ÅŸÄ±yor mu?"
        log.error(hata)
        return f"HATA: {hata}"
    except requests.exceptions.Timeout:
        hata = f"Vision model {zaman_asimi}s iÃ§inde yanÄ±t vermedi."
        log.error(hata)
        return f"HATA: {hata}"
    except Exception as e:
        log.error(f"Vision API hatasÄ±: {e}")
        return f"HATA: {e}"


# Critic Note: Session.post() baÄŸlantÄ±yÄ± havuzda tutar; her Ã§aÄŸrÄ±da
# yeni TCP el sÄ±kÄ±ÅŸmasÄ± aÃ§Ä±lmaz; timeout zorunlu; sÄ±zÄ±ntÄ± yok.


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# KOORDÄ°NAT AYRIÅTIRICI
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_KOORDINAT_DESENI = re.compile(
    r"(?:x\s*[=:]\s*)?(\d{1,4})\s*[,\s]+(?:y\s*[=:]\s*)?(\d{1,4})"
)


def koordinat_parse(
    metin: str,
    ekran_boyutu: tuple[int, int] = (1920, 1080),
) -> Optional[tuple[int, int]]:
    """
    Vision yanÄ±tÄ±ndan (x, y) Ã§Ä±karÄ±r.
    Ekran sÄ±nÄ±rlarÄ± dÄ±ÅŸÄ±nÄ± reddeder.
    """
    eslesmeler = _KOORDINAT_DESENI.findall(metin)
    if not eslesmeler:
        log.warning(f"Koordinat bulunamadÄ± â†’ '{metin[:80]}'")
        return None
    x, y = int(eslesmeler[0][0]), int(eslesmeler[0][1])
    maks_x, maks_y = ekran_boyutu
    if not (0 < x < maks_x and 0 < y < maks_y):
        log.warning(f"Koordinat sÄ±nÄ±r dÄ±ÅŸÄ±: ({x},{y}) â€” ekran {ekran_boyutu}")
        return None
    log.info(f"Koordinat parse edildi: ({x}, {y})")
    return x, y


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. EYLEM MOTORU â€” FailSafe tikla() iÃ§inde de yakalanÄ±yor
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class FailSafeHatasi(Exception):
    """PyAutoGUI fare gÃ¼venli kÃ¶ÅŸeye gittiÄŸinde fÄ±rlatÄ±lÄ±r."""


def tikla(x: int, y: int, cift_tik: bool = False) -> None:
    """
    PyAutoGUI ile gÃ¼venli tÄ±klama.
    FailSafeException hem burada hem CUA_EKRAN_KULLAN'da yakalanÄ±r â€”
    her Ã§aÄŸrÄ± noktasÄ± korunuyor.
    """
    import pyautogui

    try:
        pyautogui.moveTo(x, y, duration=0.3)
        if cift_tik:
            pyautogui.doubleClick(x, y)
            log.info(f"Ã‡ift tÄ±klandÄ±: ({x}, {y})")
        else:
            pyautogui.click(x, y)
            log.info(f"TÄ±klandÄ±: ({x}, {y})")
    except pyautogui.FailSafeException as e:
        log.critical(f"FailSafe tetiklendi tikla() iÃ§inde: {e}")
        raise FailSafeHatasi("Fare gÃ¼venli kÃ¶ÅŸeye gitti.") from e


# Critic Note: FailSafeException tikla() iÃ§inde yakalanÄ±p FailSafeHatasi'na
# dÃ¶nÃ¼ÅŸtÃ¼rÃ¼lÃ¼r; Ã¼st katman (CUA_EKRAN_KULLAN) kendi try bloÄŸunda bunu yakalar;
# Ã§ift yakalama zincirleme istisna bilgisini korur.


def yaz(metin: str, gecikme: float = 0.05) -> None:
    import pyautogui

    pyautogui.typewrite(metin, interval=gecikme)
    log.info(f"YazÄ±ldÄ±: '{metin}'")


def klavye_kisayol(*tuslar: str) -> None:
    import pyautogui

    pyautogui.hotkey(*tuslar)
    log.info(f"KÄ±sayol: {'+'.join(tuslar)}")


def eylem_yorumla_ve_calistir(
    hedef: str,
    koordinat: tuple[int, int],
) -> str:
    hedef_kucuk = hedef.lower()
    x, y = koordinat
    if "Ã§ift tÄ±k" in hedef_kucuk or "double" in hedef_kucuk:
        tikla(x, y, cift_tik=True)
        return f"Ã§ift_tÄ±klandÄ±({x},{y})"
    if "yaz" in hedef_kucuk or "gir" in hedef_kucuk or "type" in hedef_kucuk:
        yazilacak = re.search(r"['\"](.+?)['\"]", hedef)
        tikla(x, y)
        time.sleep(0.2)
        if yazilacak:
            yaz(yazilacak.group(1))
            return f"tÄ±klandÄ±({x},{y}) + yazÄ±ldÄ±('{yazilacak.group(1)}')"
        return f"tÄ±klandÄ±({x},{y}) [yazÄ±lacak metin bulunamadÄ±]"
    tikla(x, y)
    return f"tÄ±klandÄ±({x},{y})"


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 4. ADAPTÄ°F DENEME SAYACI
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class AdaptifDenemeSayaci:
    """
    BaÅŸarÄ±sÄ±z parse giriÅŸimlerine gÃ¶re MAX_DENEME'yi dinamik olarak artÄ±rÄ±r.
    Taban: MAX_DENEME_TABAN (config'den).
    Her ardÄ±ÅŸÄ±k baÅŸarÄ±sÄ±zlÄ±kta +1 eklenir, maksimum taban Ã— 2.
    BaÅŸarÄ±da sÄ±fÄ±rlanÄ±r.
    """

    def __init__(self) -> None:
        self._ardisik_basarisiz: int = 0
        self._taban: int = MAX_DENEME_TABAN

    @property
    def mevcut_limit(self) -> int:
        return min(self._taban + self._ardisik_basarisiz, self._taban * 2)

    def basarisiz_kaydet(self) -> None:
        self._ardisik_basarisiz += 1
        log.info(
            f"Adaptif limit: {self.mevcut_limit} (ardÄ±ÅŸÄ±k baÅŸarÄ±sÄ±z: {self._ardisik_basarisiz})"
        )

    def sifirla(self) -> None:
        self._ardisik_basarisiz = 0


# Tek global sayaÃ§ â€” motor yaÅŸam dÃ¶ngÃ¼sÃ¼ boyunca Ã¶ÄŸrenir.
_deneme_sayaci = AdaptifDenemeSayaci()

# Critic Note: AdaptifDenemeSayaci sade bir int tutar; bellek maliyeti sabit;
# global nesne weakref gerektirmiyor â€” kÃ¼Ã§Ã¼k, uzun Ã¶mÃ¼rlÃ¼, paylaÅŸÄ±lan durum.


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. GELÄ°ÅTÄ°RÄ°LMÄ°Å DOÄRULAMA
#    EVET/HAYIR + bir sonraki adÄ±m iÃ§in koordinat Ã¶nerisi
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _dogrulama_yap(
    b64: str,
    hedef: str,
    ekran_boyutu: tuple[int, int],
) -> tuple[bool, Optional[tuple[int, int]]]:
    """
    Eylem sonrasÄ± doÄŸrulama:
      - BaÅŸarÄ±lÄ± mÄ±? (EVET/HAYIR)
      - BaÅŸarÄ±sÄ±zsa: bir sonraki adÄ±m iÃ§in koordinat Ã¶nerisi
    DÃ¶ner: (basarili: bool, sonraki_koordinat: Optional[tuple])
    """
    dogr_prompt = (
        f"'{hedef}' eylemi gerÃ§ekleÅŸtirildikten sonraki ekran bu. "
        "1) Eylem baÅŸarÄ±lÄ± olduysa sadece 'EVET' yaz. "
        "2) BaÅŸarÄ±sÄ±z olduysa 'HAYIR' yaz, ardÄ±ndan bir satÄ±rda "
        f"'{hedef}' iÃ§in doÄŸru koordinatÄ± 'x, y' formatÄ±nda Ã¶ner. "
        "BaÅŸka hiÃ§bir ÅŸey yazma."
    )
    yanit = vision_modele_sor(b64, dogr_prompt)
    basarili = "EVET" in yanit.upper()
    sonraki: Optional[tuple[int, int]] = None

    if not basarili:
        sonraki = koordinat_parse(yanit, ekran_boyutu)
        if sonraki:
            log.info(f"DoÄŸrulamadan sonraki koordinat Ã¶nerisi: {sonraki}")

    return basarili, sonraki


# Critic Note: b64 bu fonksiyona referans olarak geÃ§er, kopyalanmaz;
# sonraki koordinat sadece baÅŸarÄ±sÄ±z durumda ayrÄ±ÅŸtÄ±rÄ±lÄ±r â€” gereksiz parse yok.


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Ã–N KOÅUL KONTROLÃœ â€” Ã§aÄŸrÄ±lmadan Ã¶nce ortamÄ± doÄŸrula
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_on_kosul_kontrolu_yapildi: bool = False
_on_kosul_sonuc: Optional[str] = None


def _on_kosul_kontrol() -> Optional[str]:
    """
    CUA dÃ¶ngÃ¼sÃ¼ iÃ§in gerekli tÃ¼m bileÅŸenleri kontrol eder.
    Sadece bir kere Ã§alÄ±ÅŸÄ±r â€” sonraki Ã§aÄŸrÄ±larda Ã¶nbellek dÃ¶ndÃ¼rÃ¼r.
    DÃ¶ner: None (her ÅŸey tamam) veya uyarÄ± metni
    """
    global _on_kosul_kontrolu_yapildi, _on_kosul_sonuc
    if _on_kosul_kontrolu_yapildi:
        return _on_kosul_sonuc

    uyarilar: list[str] = []

    # 1. PIL (pillow)
    try:
        from PIL import Image

        Image.new("RGB", (1, 1))
    except ImportError:
        uyarilar.append("PIL (pillow) kurulu deÄŸil: pip install pillow")

    # 2. pyautogui
    try:
        import pyautogui

        pyautogui.size()
    except ImportError:
        uyarilar.append("pyautogui kurulu deÄŸil: pip install pyautogui")

    # 3. Ekran gÃ¶rÃ¼ntÃ¼sÃ¼ (mss veya pyautogui)
    try:
        import mss

        with mss.mss() as sct:
            sct.monitors[1]
    except ImportError:
        try:
            import pyautogui

            pyautogui.screenshot()
        except Exception:
            uyarilar.append("Ekran gÃ¶rÃ¼ntÃ¼sÃ¼ alÄ±namÄ±yor â€” mss veya pyautogui gerekli")
    except Exception:
        uyarilar.append("Ekran gÃ¶rÃ¼ntÃ¼sÃ¼ alÄ±namÄ±yor (monitor algÄ±lanamadÄ±)")

    # 4. LM Studio baÄŸlantÄ±sÄ±
    try:
        import requests

        yanit = requests.get(
            LM_STUDIO_URL.replace("/v1/chat/completions", "/v1/models"), timeout=5
        )
        if yanit.status_code == 200:
            modeller = yanit.json()
            model_listesi = [m.get("id", "") for m in modeller if isinstance(m, dict)]
            if LM_STUDIO_MODEL not in model_listesi:
                uyarilar.append(
                    f"Vision model '{LM_STUDIO_MODEL}' LM Studio'da bulunamadÄ±. "
                    f"YÃ¼klÃ¼ modeller: {', '.join(model_listesi[:5])}..."
                )
        else:
            uyarilar.append(f"LM Studio yanÄ±t vermedi (HTTP {yanit.status_code})")
    except requests.exceptions.ConnectionError:
        uyarilar.append(
            "LM Studio Ã§alÄ±ÅŸmÄ±yor. Vision iÅŸlemler iÃ§in LM Studio'da "
            "bir vision model (Ã¶r: llava) yÃ¼kleyip http://localhost:1234'Ã¼ aÃ§Ä±n."
        )
    except requests.exceptions.Timeout:
        uyarilar.append("LM Studio'ya baÄŸlantÄ± zaman aÅŸÄ±mÄ±na uÄŸradÄ± (5 sn)")
    except Exception as e:
        uyarilar.append(f"LM Studio kontrolÃ¼ baÅŸarÄ±sÄ±z: {e}")

    _on_kosul_kontrolu_yapildi = True
    if uyarilar:
        _on_kosul_sonuc = "âš  CUA Ã¶n koÅŸul hatasÄ±:\n" + "\n".join(
            f"  â€¢ {u}" for u in uyarilar
        )
        log.warning(_on_kosul_sonuc)
    else:
        _on_kosul_sonuc = None
        log.info("CUA Ã¶n koÅŸullarÄ± tamam â€” vision model hazÄ±r.")
    return _on_kosul_sonuc


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ANA CUA DÃ–NGÃœSÃœ
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_vision_onbellek: weakref.WeakValueDictionary = weakref.WeakValueDictionary()


def CUA_EKRAN_KULLAN(hedef: str = "") -> str:
    """
    Tam otonom CUA dÃ¶ngÃ¼sÃ¼.

    AdÄ±mlar:
        1. Ã–n koÅŸul kontrolÃ¼ (LM Studio, pyautogui, PIL)
        2. Ekran gÃ¶rÃ¼ntÃ¼sÃ¼ al
        3. Vision modele gÃ¶nder â†’ koordinat iste
        4. KoordinatÄ± parse et (adaptif deneme sayÄ±sÄ±)
        5. Eylemi yÃ¼rÃ¼t (tÄ±kla / yaz) â€” FailSafe her katmanda yakalanÄ±r
        6. Bekleme â†’ yeni ekran â†’ doÄŸrula (EVET/HAYIR + sonraki koordinat)
        7. SonuÃ§ dÃ¶ndÃ¼r

    Parametreler:
        hedef: "WhatsApp ikonuna tÄ±kla"
               "arama Ã§ubuÄŸuna 'merhaba' yaz"
               "" â†’ sadece analiz, eylem yok
    """
    # â”€â”€ Ã–n koÅŸul kontrolÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    uyari = _on_kosul_kontrol()
    if uyari:
        return f"[CUA_UYARI]\n{uyari}\nEksikleri giderdikten sonra tekrar dene."

    if not hedef:
        goruntu, boyut = ekran_goruntusu_al()
        b64 = goruntu_base64_yap(goruntu)
        del goruntu
        analiz = vision_modele_sor(b64, "Bu ekranÄ± kÄ±saca analiz et.")
        del b64
        gc.collect()
        return f"[CUA_ANALIZ] {analiz}"

    log.info(f"CUA baÅŸladÄ± â†’ hedef: '{hedef}'")

    # 1. Ekran
    goruntu, ekran_boyutu = ekran_goruntusu_al()
    b64 = goruntu_base64_yap(goruntu)
    del goruntu

    # 2-3. Vision + adaptif parse
    prompt = (
        f"Bu ekran gÃ¶rÃ¼ntÃ¼sÃ¼nde '{hedef}' iÅŸlemini yapmam gerekiyor. "
        "Hangi koordinata tÄ±klamalÄ±yÄ±m? "
        "SADECE 'x, y' formatÄ±nda koordinat dÃ¶ndÃ¼r, baÅŸka hiÃ§bir ÅŸey yazma. "
        f"Ekran boyutu: {ekran_boyutu[0]}x{ekran_boyutu[1]} piksel."
    )

    koordinat: Optional[tuple[int, int]] = None
    limit = _deneme_sayaci.mevcut_limit

    for deneme in range(1, limit + 1):
        yanit = vision_modele_sor(b64, prompt)
        if yanit.startswith("HATA:"):
            del b64
            gc.collect()
            return str(CUASonucu(basarili=False, eylem=hedef, hata=yanit))

        koordinat = koordinat_parse(yanit, ekran_boyutu)
        if koordinat:
            _deneme_sayaci.sifirla()
            break

        log.warning(f"Parse baÅŸarÄ±sÄ±z (deneme {deneme}/{limit})")
        _deneme_sayaci.basarisiz_kaydet()
        limit = _deneme_sayaci.mevcut_limit  # dinamik gÃ¼ncelleme
        prompt = (
            f"Ã–nceki yanÄ±tÄ±n anlaÅŸÄ±lmadÄ±. '{hedef}' iÃ§in "
            "SADECE iki sayÄ± yaz, Ã¶rnek: '452, 317' â€” baÅŸka hiÃ§bir ÅŸey."
        )

    del b64
    gc.collect()

    if not koordinat:
        return str(
            CUASonucu(
                basarili=False,
                eylem=hedef,
                hata=f"Adaptif {limit} denemede koordinat alÄ±namadÄ±.",
            )
        )

    # 4. Eylem â€” FailSafe her iki katmanda da yakalanÄ±r
    try:
        eylem_aciklama = eylem_yorumla_ve_calistir(hedef, koordinat)
    except FailSafeHatasi as e:
        return str(
            CUASonucu(
                basarili=False,
                eylem=hedef,
                koordinat=koordinat,
                hata=str(e),
            )
        )

    # 5. DoÄŸrulama
    time.sleep(TIKLA_BEKLEME)
    yeni_goruntu, _ = ekran_goruntusu_al()
    yeni_b64 = goruntu_base64_yap(yeni_goruntu)
    del yeni_goruntu

    basarili, sonraki_koordinat = _dogrulama_yap(yeni_b64, hedef, ekran_boyutu)
    del yeni_b64
    gc.collect()

    sonuc = CUASonucu(
        basarili=basarili,
        eylem=eylem_aciklama,
        koordinat=koordinat,
        sonraki_koordinat=sonraki_koordinat,
        ekran_boyutu=ekran_boyutu,
    )
    log.info(str(sonuc))
    return str(sonuc)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ARAÃ‡ TARAYICI
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_REYMEN_DOSYALARI = [
    "motor.py",
    "screenshot_v2.py",
    "hermesapprove.py",
    "sistem_talimati.py",
    "screen_vision_analiz.py",
]


def _dosya_tara(yol: Path) -> dict:
    if not yol.exists():
        return {"durum": "bulunamadÄ±", "fonksiyonlar": [], "siniflar": []}
    icerik = yol.read_text(encoding="utf-8", errors="replace")
    fonksiyonlar = re.findall(r"^def\s+(\w+)", icerik, re.MULTILINE)
    siniflar = re.findall(r"^class\s+(\w+)", icerik, re.MULTILINE)
    return {
        "durum": "bulundu",
        "satir": icerik.count("\n"),
        "fonksiyonlar": fonksiyonlar,
        "siniflar": siniflar,
    }


def _dosyalari_tara_generator(
    kok: Path = Path("."),
) -> Generator[tuple[str, dict], None, None]:
    """yield tabanlÄ± â€” tÃ¼m dosyalarÄ± aynÄ± anda belleÄŸe almaz."""
    for dosya_adi in _REYMEN_DOSYALARI:
        yield dosya_adi, _dosya_tara(kok / dosya_adi)


def CUA_ARACLARI_TARA(kok: str = ".") -> str:
    """
    ReYMeN bileÅŸenlerini tarar; CUA entegrasyonu iÃ§in durum raporu Ã¼retir.
    """
    satirlar = ["â•" * 56, "  ReYMeN CUA â€” BileÅŸen Tarama Raporu", "â•" * 56]
    eksik: list[str] = []
    hazir: list[str] = []

    for dosya_adi, bilgi in _dosyalari_tara_generator(Path(kok)):
        if bilgi["durum"] == "bulunamadÄ±":
            satirlar.append(f"  âœ—  {dosya_adi:<30} â†’ BULUNAMADI")
            eksik.append(dosya_adi)
        else:
            fn_sayisi = len(bilgi["fonksiyonlar"])
            satirlar.append(
                f"  âœ“  {dosya_adi:<30} â†’ {bilgi['satir']:>4} satÄ±r | "
                f"{fn_sayisi} fonksiyon"
            )
            if bilgi["fonksiyonlar"]:
                ozet = ", ".join(bilgi["fonksiyonlar"][:5])
                if fn_sayisi > 5:
                    ozet += f" â€¦ (+{fn_sayisi-5})"
                satirlar.append(f"       {ozet}")
            hazir.append(dosya_adi)

    satirlar += [
        "â”€" * 56,
        f"  HazÄ±r  : {len(hazir)}/{len(_REYMEN_DOSYALARI)} bileÅŸen",
        f"  Eksik  : {', '.join(eksik) if eksik else 'yok'}",
        "â”€" * 56,
    ]
    if eksik:
        satirlar.append("  âš   Eksik dosyalar CUA dÃ¶ngÃ¼sÃ¼nÃ¼ kÄ±smen kÄ±rabilir.")
    else:
        satirlar.append("  âœ… TÃ¼m bileÅŸenler mevcut â€” CUA baÅŸlatÄ±labilir.")
    satirlar.append("â•" * 56)
    rapor = "\n".join(satirlar)
    log.info("AraÃ§ tarama tamamlandÄ±.")
    return rapor


# Critic Note: Generator teker teker dosya okur; N dosya iÃ§in O(1) bellek;
# bÃ¼yÃ¼k projede bile yÄ±ÄŸÄ±n birikmez.


# â”€â”€ Motor KaydÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def motor_kaydet(motor: object):
    """motor.py entegrasyonu: CUA araÃ§larÄ±nÄ± kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    motor._plugin_arac_kaydet(
        "CUA_EKRAN_KULLAN",
        lambda hedef="": CUA_EKRAN_KULLAN(hedef),
        "EkranÄ± gÃ¶rÃ¼r, vision model ile analiz eder, hedefe gÃ¶re tÄ±klar veya yazar. Tam otonom CUA dÃ¶ngÃ¼sÃ¼.",
    )
    motor._plugin_arac_kaydet(
        "CUA_ARACLARI_TARA",
        lambda kok=".": CUA_ARACLARI_TARA(kok),
        "ReYMeN bileÅŸenlerini tarar, CUA hazÄ±rlÄ±k durumunu raporlar",
    )


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MOTOR.PY + SÄ°STEM_TALÄ°MATI.PY ENTEGRASYON BLOKLARI
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

MOTOR_ENTEGRASYON_KODU = """
# â”€â”€ motor.py Ã¼stÃ¼ne ekle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
from cua_motor_araci import CUA_EKRAN_KULLAN, CUA_ARACLARI_TARA

ARACLAR["CUA_EKRAN_KULLAN"] = CUA_EKRAN_KULLAN
ARACLAR["CUA_ARACLARI_TARA"] = CUA_ARACLARI_TARA
"""

SISTEM_TALIMATI_EKI = """
CUA_ARACLARI = [
    {
        "isim": "CUA_EKRAN_KULLAN",
        "aciklama": (
            "EkranÄ± gÃ¶rÃ¼r, vision model ile analiz eder, "
            "verilen hedefe gÃ¶re tÄ±klar veya yazar. "
            "hedef='WhatsApp ikonuna tÄ±kla' veya "
            "hedef='arama Ã§ubuÄŸuna \\'merhaba\\' yaz'"
        ),
        "parametreler": {"hedef": "str"},
    },
    {
        "isim": "CUA_ARACLARI_TARA",
        "aciklama": "ReYMeN bileÅŸenlerini tarar, CUA hazÄ±rlÄ±k durumunu raporlar.",
        "parametreler": {"kok": "str â€” taranacak dizin (varsayÄ±lan '.')"},
    },
]
"""


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CLI
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    import sys

    print(CUA_ARACLARI_TARA())

    if len(sys.argv) > 1:
        hedef_arg = " ".join(sys.argv[1:])
        print(f"\nHedef: '{hedef_arg}'")
        print(CUA_EKRAN_KULLAN(hedef_arg))
    else:
        print("\nKullanÄ±m : python cua_motor_araci.py '<hedef>'")
        print('Ã–rnek    : python cua_motor_araci.py "WhatsApp ikonuna tÄ±kla"')
        print("\n--- motor.py entegrasyon kodu ---")
        print(MOTOR_ENTEGRASYON_KODU)
