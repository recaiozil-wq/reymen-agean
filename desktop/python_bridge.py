# -*- coding: utf-8 -*-
"""
desktop/python_bridge.py — Python <-> Electron IPC Bridge.

Electron main process'i ile web_ui.py arasinda kopru gorevi gorur.
JSON tabanli stdin/stdout iletisimi.

ASAR UYUMLULUGU:
    Electron build sirasinda .py dosyalari app.asar icine gomulur.
    Python dosyalari asar icine gomuldugunde Path(__file__) calismaz.
    Cozum: extraResources veya asarUnpack ile .py dosyalari asar disina cikarilir.

Kullanim (Electron tarafindan cagrilir):
    python python_bridge.py --port 8765
"""

import json
import os
import platform
import signal
import subprocess
import sys
from pathlib import Path
import logging
logger = logging.getLogger(__name__)


# ── Sabitler ──────────────────────────────────────────────────────────
WEB_UI_PORT = int(os.environ.get("WEB_UI_PORT", "8765"))

def _proje_kokunu_bul() -> Path:
    """
    Proje kokunu bul (asar + extraResources + dev mod fallback).
    
    Sira:
    1. REYMEN_PROJE_KOK env var (en oncelikli, test/ozel durumlar)
    2. resources/web_ui.py varsa → resources/../ = proje koku (extraResources)
    3. __file__ parent.parent → normal dev modu
    4. app.asar.unpacked → asarUnpack modu
    5. process.cwd() → son care
    """
    # 1. Env var
    env_kok = os.environ.get("REYMEN_PROJE_KOK")
    if env_kok:
        kok = Path(env_kok)
        if kok.exists():
            return kok

    # 2. extraResources: web_ui.py ayni klasorde mi?
    BuDizin = Path(__file__).parent.resolve()
    if (BuDizin / "web_ui.py").exists():
        # python_bridge.py ve web_ui.py ayni yerde (extraResources)
        return BuDizin.parent  # resources/ alti → proje koku

    # 3. Dev mod: __file__ parent.parent
    try:
        kok = Path(__file__).resolve().parent.parent
        if (kok / "web_ui.py").exists() or (kok / "motor.py").exists():
            return kok
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")

    # 4. asar dedektoru: __file__ icinde .asar varsa
    _me = str(__file__)
    if ".asar" in _me:
        # resources/app.asar/... → resources/app.asar.unpacked/ dene
        asar_unpacked = _me.replace("app.asar", "app.asar.unpacked")
        kok = Path(asar_unpacked).parent.parent
        if (kok / "web_ui.py").exists():
            return kok
        # resources/ altina ekstra kaynaklari koy
        resources = Path(__file__).parent
        if (resources / "web_ui.py").exists():
            return resources.parent

    # 5. CWD (current working directory) — son care
    return Path.cwd()


# Proje kokunu bul
PROJE_KOK = _proje_kokunu_bul()
WEB_UI_PATH = PROJE_KOK / "web_ui.py"

# Debug: hangi yol kullaniliyor
DEBUG_PATH = os.environ.get("DEBUG_BRIDGE", "").lower() in ("1", "true", "yes")


def web_ui_baslat() -> subprocess.Popen | None:
    """
    web_ui.py'yi headless modda arkaplanda baslat.

    Returns:
        subprocess.Popen: Baslatilan process, veya None (hata).
    """
    if not WEB_UI_PATH.exists():
        print(json.dumps({
            "tur": "hata",
            "mesaj": (
                f"web_ui.py bulunamadi: {WEB_UI_PATH}\n"
                f"  Denenen proje koku: {PROJE_KOK}\n"
                f"  __file__: {__file__}\n"
                f"  CWD: {Path.cwd()}"
            ),
        }))
        return None

    if DEBUG_PATH:
        print(json.dumps({
            "tur": "debug",
            "mesaj": {
                "proje_kok": str(PROJE_KOK),
                "web_ui_path": str(WEB_UI_PATH),
                "python": sys.executable,
                "platform": platform.platform(),
                "asar_mode": ".asar" in str(__file__),
            }
        }))

    print(json.dumps({
        "tur": "bilgi",
        "mesaj": f"web_ui baslatiliyor: {WEB_UI_PATH}",
    }))

    try:
        env = os.environ.copy()
        env.update({
            "REYMEN_DESKTOP": "1",
            "PYTHONUNBUFFERED": "1",
            "WEB_UI_PORT": str(WEB_UI_PORT),
            "REYMEN_PROJE_KOK": str(PROJE_KOK),
        })
        proc = subprocess.Popen(
            [sys.executable, str(WEB_UI_PATH)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        return proc
    except FileNotFoundError:
        print(json.dumps({
            "tur": "hata",
            "mesaj": f"Python yorumlayicisi bulunamadi: {sys.executable}",
        }))
        return None
    except Exception as e:
        print(json.dumps({
            "tur": "hata",
            "mesaj": f"web_ui baslatilamadi: {e}",
        }))
        return None


def web_ui_durum_kontrol(proc: subprocess.Popen) -> bool:
    """web_ui process'inin calisip calismadigini kontrol et."""
    if proc is None:
        return False
    poll = proc.poll()
    return poll is None  # None = hala calisiyor


def web_ui_durdur(proc: subprocess.Popen):
    """web_ui process'ini guvenli sekilde durdur."""
    if proc is None:
        return

    proc.terminate()  # SIGTERM
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()  # SIGKILL
        proc.wait()

    print(json.dumps({
        "tur": "bilgi",
        "mesaj": "web_ui durduruldu",
    }))


def komut_gonder(komut: str, args: dict = None) -> dict:
    """
    Electron'dan gelen komutu web_ui API'sine ilet.

    Args:
        komut: Komut adi (ornek: "status", "restart").
        args: Komut parametreleri (opsiyonel).

    Returns:
        dict: API yaniti.
    """
    try:
        import requests

        url = f"http://localhost:{WEB_UI_PORT}/api/komut"
        resp = requests.post(
            url,
            json={"komut": komut, "args": args or {}},
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
        return resp.json()

    except ImportError:
        return {"hata": "requests kutuphanesi kurulu degil"}
    except requests.exceptions.ConnectionError:
        return {"hata": f"Web UI calismiyor (port {WEB_UI_PORT})"}
    except requests.exceptions.Timeout:
        return {"hata": "Web UI yanit vermedi (timeout 10s)"}
    except Exception as e:
        return {"hata": str(e)}


if __name__ == "__main__":
    proc = web_ui_baslat()
    if proc:
        print(json.dumps({"tur": "hazir", "port": WEB_UI_PORT}))
        # Electron tarafından yönetilen process — arkaplanda kal
        import signal
        signal.signal(signal.SIGTERM, lambda *_: web_ui_durdur(proc))
        try:
            proc.wait()
        except (KeyboardInterrupt, EOFError):
            web_ui_durdur(proc)
