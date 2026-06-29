# -*- coding: utf-8 -*-
"""reymen_launcher.py — ReYMeN özel REPL. Hermes UI açılmaz, sadece motor kullanılır."""

import os
import sys
import time
import shutil
import threading
import itertools
from pathlib import Path
from datetime import datetime
import re as _re

import logging
logging.basicConfig(level=logging.ERROR, force=True)
for _l in ['CUA', 'Motor', 'motor', 'hermes', 'reymen', 'conversation_loop',
           'beyin', 'plugin', 'cron', 'skill', 'root', '__main__']:
    logging.getLogger(_l).setLevel(logging.ERROR)
logger = logging.getLogger("reymen_launcher")

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_KOK = Path(__file__).parent.resolve()
os.chdir(_KOK)
sys.path.insert(0, str(_KOK))

_HERMES_AGENT = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "hermes-agent"
if _HERMES_AGENT.exists():
    sys.path.insert(0, str(_HERMES_AGENT))

_HERMES_HOME  = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes"
_PROFILE_CFG  = _HERMES_HOME / "profiles" / "reymen" / "config.yaml"

try:
    from dotenv import load_dotenv
    load_dotenv(_KOK / ".env", override=True)
    load_dotenv(_HERMES_HOME / ".env", override=True)
    load_dotenv(_HERMES_HOME / "profiles" / "reymen" / ".env", override=True)
except Exception:
    pass

# ── Renkler ────────────────────────────────────────────────────────────────────
_R   = "\033[0m"
_C   = "\033[96m"   # cyan
_G   = "\033[92m"   # green
_Y   = "\033[93m"   # yellow
_B   = "\033[94m"   # blue
_M   = "\033[95m"   # magenta
_W   = "\033[97m"   # white
_D   = "\033[2m"    # dim
_RED = "\033[91m"   # kirmizi

def _c(t):   return f"{_C}{t}{_R}"
def _g(t):   return f"{_G}{t}{_R}"
def _y(t):   return f"{_Y}{t}{_R}"
def _mavi(t): return f"{_B}{t}{_R}"  # fix #6: _b -> _mavi
def _d(t):   return f"{_D}{t}{_R}"
def _r(t):   return f"{_RED}{t}{_R}"
def _gb(t):  return f"{_G}{_B}{t}{_R}"
def _cb(t):  return f"{_C}{_B}{t}{_R}"

# ── API Cache ──────────────────────────────────────────────────────────────────
_API_CACHE: dict = {}

# ── ReYMeN config (sabit) ──────────────────────────────────────────────────────
_REYMEN_CONFIG = {
    "provider": os.environ.get("REYMEN_PROVIDER", "deepseek"),
    "model": os.environ.get("REYMEN_MODEL", "deepseek-v4-flash"),
    "temperature": 0.7,
    "max_tokens": 4096,
    "frequency_penalty": 0.8,
}

# ── Model yardimcilari ─────────────────────────────────────────────────────────
_MODEL_DB = {
    "deepseek": {
        "ad": "DeepSeek",
        "modeller": ["deepseek-v4-flash", "deepseek-chat"],
        "env": "DEEPSEEK_API_KEY",
        "url": "https://api.deepseek.com/v1/models",
    },
    "openrouter": {
        "ad": "OpenRouter",
        "modeller": ["openrouter/auto", "anthropic/claude-sonnet-4"],
        "env": "OPENROUTER_API_KEY",
        "url": "https://openrouter.ai/api/v1/models",
    },
    "groq": {
        "ad": "Groq",
        "modeller": ["groq/llama-3.3-70b-versatile", "groq/llama-3.1-8b-instant"],
        "env": "GROQ_API_KEY",
        "url": "https://api.groq.com/openai/v1/models",
    },
    "xiaomi": {
        "ad": "Xiaomi",
        "modeller": ["xiaomi/mimo-v2.5-pro"],
        "env": "XIAOMI_API_KEY",
        "url": "https://api.minimax.chat/v1/models",
    },
    "xai": {
        "ad": "xAI",
        "modeller": ["xai/grok-2-latest"],
        "env": "XAI_API_KEY",
        "url": "https://api.x.ai/v1/models",
    },
}

def _mevcut_model():
    m = os.environ.get("REYMEN_MODEL", "deepseek-v4-flash")
    p = os.environ.get("REYMEN_PROVIDER", "deepseek")
    return m, p

def _env_replace(key, value):
    """.env'deki bir satiri replace et (fix #3: append yerine in-place)."""
    env_path = _KOK / ".env"
    if not env_path.exists():
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
        return
    lines = []
    found = False
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(f"{key}=") or line.strip().startswith(f"#{key}="):
                lines.append(f"{key}={value}\n")
                found = True
            else:
                lines.append(line)
    if not found:
        lines.append(f"\n{key}={value}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def _model_guncelle(provider, model):
    """Provider+model'i .env'ye yaz (fix #3: in-place replace)."""
    os.environ["REYMEN_PROVIDER"] = provider
    os.environ["REYMEN_MODEL"] = model
    _REYMEN_CONFIG["provider"] = provider
    _REYMEN_CONFIG["model"] = model
    try:
        _env_replace("REYMEN_PROVIDER", provider)
        _env_replace("REYMEN_MODEL", model)
    except Exception:
        pass

# ── API kontrol (fix #4: background + timeout) ─────────────────────────────────
_API_KONTROL_SONUC = {}
_API_KONTROL_KILIT = threading.Lock()
_API_KONTROL_BITTI = threading.Event()

def _api_kontrol_arkaplan():
    """Provider API key'lerini background thread'te test et."""
    global _API_KONTROL_SONUC
    import http.client as _hc

    sonuclar = {}
    kilid = threading.Lock()

    def _tek(prov, url, env_var):
        key = os.environ.get(env_var, "")
        if not key:
            with kilid:
                sonuclar[prov] = "401"
            return
        try:
            parsed = _re.match(r"https?://([^/]+)(/.*)", url)
            if not parsed:
                with kilid:
                    sonuclar[prov] = False
                return
            host = parsed.group(1)
            path = parsed.group(2) or "/"
            conn = _hc.HTTPSConnection(host, timeout=3)
            conn.request("GET", path, headers={"Authorization": f"Bearer {key}"})
            resp = conn.getresponse()
            ok = resp.status == 200
            conn.close()
            with kilid:
                sonuclar[prov] = ok
        except Exception:
            with kilid:
                sonuclar[prov] = False

    threads = []
    for p, info in _MODEL_DB.items():
        t = threading.Thread(target=_tek, args=(p, info["url"], info["env"]), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join(timeout=4)

    for p in _MODEL_DB:
        if p not in sonuclar:
            sonuclar[p] = "zaman_asimi"
    with _API_KONTROL_KILIT:
        _API_KONTROL_SONUC = sonuclar
    _API_KONTROL_BITTI.set()

def _api_kontrol_bekle(timeout=4):
    """Background API kontrol sonucunu bekle (en fazla timeout saniye)."""
    _API_KONTROL_BITTI.wait(timeout=timeout)
    with _API_KONTROL_KILIT:
        return dict(_API_KONTROL_SONUC)

# Arka planda baslat
_API_KONTROL_BITTI.clear()
threading.Thread(target=_api_kontrol_arkaplan, daemon=True).start()

# ── REYMEN-AGENT Logo (Hermes'teki HERMES-AGENT logosuyla birebir ayni font/punta) ─
_REYMEN_AGENT_LOGO = """[bold #FFD700]██████╗ ███████╗██╗   ██╗███╗   ███╗███████╗███╗   ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗[/]
[bold #FFD700]██╔══██╗██╔════╝╚██╗ ██╔╝████╗ ████║██╔════╝████╗  ██║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝[/]
[#FFBF00]██████╔╝█████╗   ╚████╔╝ ██╔████╔██║█████╗  ██╔██╗ ██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║[/]
[#FFBF00]██╔══██╗██╔══╝    ╚██╔╝  ██║╚██╔╝██║██╔══╝  ██║╚██╗██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║[/]
[#CD7F32]██║  ██║███████╗   ██║   ██║ ╚═╝ ██║███████╗██║ ╚████║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║[/]
[#CD7F32]╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝[/]"""

# ── Hermes-style welcome banner ────────────────────────────────────────────────
def _hermes_welcome(model: str, session_id: str = ""):
    try:
        import hermes_cli.banner as _hb
        _hb.HERMES_AGENT_LOGO = _REYMEN_AGENT_LOGO
        _hb.HERMES_CADUCEUS = ""
        _hb.format_banner_version_label = lambda: "R>eYMeN Ajan v0.1.0 (2026.6.29)"
        _hb._NOUS_LABEL = "R>eYMeN Ajan"

        from hermes_cli.banner import build_welcome_banner
        from rich.console import Console

        import hermes_cli.banner as _banner_mod
        import types
        _orig_bwb = _banner_mod.build_welcome_banner

        def _rey_welcome_banner(*args, **kwargs):
            _orig_logo = _banner_mod.HERMES_AGENT_LOGO
            _orig_cad = _banner_mod.HERMES_CADUCEUS
            _orig_ver = _banner_mod.format_banner_version_label
            _banner_mod.HERMES_AGENT_LOGO = _REYMEN_AGENT_LOGO
            _banner_mod.HERMES_CADUCEUS = ""
            _banner_mod.format_banner_version_label = lambda: "ReYMeN Agent v0.1.0 (2026.6.29)"
            result = _orig_bwb(*args, **kwargs)
            _banner_mod.HERMES_AGENT_LOGO = _orig_logo
            _banner_mod.HERMES_CADUCEUS = _orig_cad
            _banner_mod.format_banner_version_label = _orig_ver
            return result

        console = Console()
        _rey_welcome_banner(
            console=console,
            model=model,
            cwd=str(_KOK),
            tools=[],
            enabled_toolsets=[],
            session_id=session_id,
            context_length=1048576,
        )
    except Exception:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"\n  {_mavi('R>eYMeN Ajan')}  {_d('v0.1.0')}")
        print(f"  {_d('─'*50)}")
        print(f"  {_d('Model:')} {model}  {_d('Oturum:')} {session_id}")
        print(f"  {_d('─'*50)}\n")

# ── Model secim ekrani ─────────────────────────────────────────────────────────
def _model_sec(api_sonuc=None):
    cur_m, cur_p = _mevcut_model()
    print(f"\n  {_gb('ReYMeN — Model Seçimi')}")
    print(f"  {_d('─'*50)}")
    if api_sonuc:
        for ad, durum in api_sonuc.items():
            ikon = _g("✓") if durum is True else (_r("✗") if durum == "401" else _y("?"))
            print(f"  {ikon} {_mavi(ad):<16} {_d(str(durum))}")
    print(f"  {_d('─'*50)}")
    print(f"  {_d('Aktif:')} {_g(cur_m)}")
    print()

# ── Spinner ───────────────────────────────────────────────────────────────────
def _spinner(stop_evt):
    frames = ["◈", "◉", "◎", "⊙", "○"]
    cyc_f = itertools.cycle(frames)
    while not stop_evt.is_set():
        frame = next(cyc_f)
        print(f"\r  {frame} ", end="", flush=True)
        time.sleep(0.12)
    print(f"\r{' '*30}\r", end="", flush=True)

# ── ReYMeN cagrisi ────────────────────────────────────────────────────────────
_HERMES = shutil.which("hermes") or shutil.which("hermes") or "hermes"
_ilk_tur = True

def _sistem_prompu_al() -> str:
    """SOUL.md + DURUM_OKU talimati ile sistem promptu olustur."""
    try:
        soul_path = Path(__file__).parent / "reymen" / "arac" / ".ReYMeN" / "SOUL.md"
        if soul_path.exists():
            soul = soul_path.read_text(encoding="utf-8")
        else:
            soul = ""
    except Exception:
        soul = ""
    return (
        "Sen ReYMeN adinda yardimsever bir AI asistanisin. "
        "Kisa ve oz cevap ver. Turkce konus.\\n\\n"
        "## \\u26a0\\ufe0f DURUM_OKU() ZORUNLU TALIMAT\\n"
        "ReYMeN durumu/projesi/eksikleri/kapasitesi hakkinda soru gelince "
        "KESINLIKLE ONCE DOGRUDAN DURUM_OKU() tool'unu cagir. "
        "Kendi bilginle asla liste olusturma. durum.json TEK KAYNAK.\\n"
        "Karsilastirma/eksik/liste/sayi sorularinda ONCE DURUM_OKU().\\n"
        + (f"\\n## SOUL.md\\n{soul[:2000]}\\n" if soul else "")
    )

def _sor(soru: str) -> tuple[str, str]:
    """ReYMeN'e soru sor — Telegram bot ile AYNI full pipeline."""
    global _ilk_tur
    _ilk_tur = False

    stop = threading.Event()
    t = threading.Thread(target=_spinner, args=(stop,), daemon=True)
    t.start()

    try:
        from reymen.cereyan.beyin import Beyin
        from reymen.cereyan.motor import Motor
        from reymen.cereyan.conversation_loop import ConversationLoop

        # fix #2: SOUL.md entegrasyonu
        system_prompt = _sistem_prompu_al()
        config = dict(_REYMEN_CONFIG)
        config["system_prompt"] = system_prompt

        beyin = Beyin(config=config)
        motor = Motor()
        motor._plugin_moduller_yukle()
        cl = ConversationLoop(
            motor=motor,
            beyin=beyin,
            max_tur=15,
        )
        # fix #1: provider hardcode kaldirildi
        sonuc = cl.run_conversation(
            hedef=soru,
            provider=_REYMEN_CONFIG["provider"],
        )

        if sonuc.get("basarili"):
            yanit = sonuc.get("yanit") or sonuc.get("sonuc", "")
            return yanit, ""
        else:
            hata = sonuc.get("hata") or "Bilinmeyen hata"
            # fix #8: fallback dene
            return _sor_direkt_api(soru)

    except Exception as e:
        # fix #8: fallback dene
        return _sor_direkt_api(soru)
    finally:
        stop.set()
        t.join(timeout=5)  # fix #5: 1s -> 5s


def _sor_direkt_api(soru: str) -> tuple[str, str]:
    """Fallback: direkt API cagrisi (Beyin.uret ile)."""
    try:
        from reymen.cereyan.beyin import Beyin as _BeyinMod
        _beyin_inst = _BeyinMod(config=_REYMEN_CONFIG)
        _s = _sistem_prompu_al()
        _c = _beyin_inst.uret(_s, [{"role": "user", "content": soru}])
        return _c or "Cevap alinamadi", ""
    except Exception as e:
        return f"HATA: {e}", ""


_YARDIM = f"""
  {_cb('ReYMeN Komutlar')}

  {_c('/yardim')}        Bu menüyü göster
  {_c('/model')}         Model değiştir
  {_c('/temizle')}       Ekranı temizle
  {_c('/cik')}           Çıkış

  {_d('Herhangi bir metin yaz → ReYMeN cevaplar.')}
"""

# ── Ana REPL ──────────────────────────────────────────────────────────────────
def _repl(session_id=""):
    cur_m, cur_p = _mevcut_model()
    print(f"  {_gb('ReYMeN')} hazır. /yardim /model /temizle /cik")
    print()

    while True:
        try:
            girdi = input(f"  {_gb('ReYMeN')}{_R} > ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {_d('ReYMeN kapanıyor.')}")
            break

        if not girdi:
            continue

        if girdi.lower() in ("/cik", "/çık", "exit", "quit", "q"):
            print(f"  {_d('ReYMeN kapanıyor.')}")
            break
        if girdi.lower() in ("/yardim", "/help", "/?"):
            print(_YARDIM)
            continue
        if girdi.lower() in ("/temizle", "/cls", "/clear"):
            _hermes_welcome(cur_m, session_id)
            continue
        if girdi.lower().startswith("/model"):
            _model_sec()
            continue

        t0 = time.time()
        cevap, kaynak = _sor(girdi)
        dt = time.time() - t0
        print(f"\n  {'─'*50}")
        print(f"  {cevap}")
        print(f"  {'─'*50}")
        t_in = len(girdi.split())
        t_out = len(cevap.split())
        print(f"  {_y(cur_m)} {_d('|')} {_c(f'{t_in*2}K/1M')} {_d('|')} [{_g('█'*int(min(20, t_in*2//5000)))}{_d('▒'*max(0,20-int(min(20, t_in*2//5000))))}] {_g(f'{min(99, t_in*2//10000)}%')} {_d('|')} {_y(f'{dt:.0f}s')}", flush=True)

# ── Giriş noktası ────────────────────────────────────────────────────────────
def main():
    import uuid as _uid
    session_id = _uid.uuid4().hex[:8]

    cur_m, cur_p = _mevcut_model()

    # fix #4: background API kontrol — bekleme yok
    _api_sonuc = _api_kontrol_bekle(timeout=3)
    durum = _api_sonuc.get(cur_p)
    if durum is not True:
        _model_sec(_api_sonuc)
        print(f"  {_d('Varsayılan model ile devam ediliyor...')}\n")

    _hermes_welcome(cur_m, session_id)

    try:
        from hermes_cli.skin_engine import get_active_skin
        _skin = get_active_skin()
        _welcome_text = _skin.get_branding("welcome", "R>eYMeN Ajan'a hoş geldiniz! Mesajınızı yazın veya /yardım yazın.")
        _welcome_color = _skin.get_color("banner_text", "#FFF8DC")
    except Exception:
        _welcome_text = "R>eYMeN Ajan'a hoş geldiniz! Mesajınızı yazın veya /yardım yazın."
        _welcome_color = "#FFF8DC"

    from rich.console import Console
    Console().print(f"[{_welcome_color}]{_welcome_text}[/]")
    print()

    _repl(session_id)

if __name__ == "__main__":
    main()
