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
# Tum loglari ERROR'a cek - kullaniciya hicbir log gosterme
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
        logger.warning("[reymen_launcher] Exception (detaysiz)")

_KOK = Path(__file__).parent.resolve()
os.chdir(_KOK)
sys.path.insert(0, str(_KOK))

_HERMES_HOME  = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes"
_PROFILE_CFG  = _HERMES_HOME / "profiles" / "reymen" / "config.yaml"

try:
    from dotenv import load_dotenv
    load_dotenv(_KOK / ".env", override=True)
    load_dotenv(_HERMES_HOME / ".env", override=True)
    load_dotenv(_HERMES_HOME / "profiles" / "reymen" / ".env", override=True)
except Exception:
    logger.warning("[reymen_launcher] Exception (detaysiz)")

# ── Renkler ────────────────────────────────────────────────────────────────────
_R   = "\033[0m"
_C   = "\033[96m"   # cyan
_G   = "\033[92m"   # green
_Y   = "\033[93m"   # yellow
_B   = "\033[94m"   # blue
_M   = "\033[95m"   # magenta
_W   = "\033[97m"   # white
_D   = "\033[2m"    # dim
_RED = "\033[91m"   # kırmızı

# ── Renk yardimcıları ─────────────────────────────────────────────────────────
def _c(t):   return f"{_C}{t}{_R}"
def _g(t):   return f"{_G}{t}{_R}"
def _y(t):   return f"{_Y}{t}{_R}"
def _b(t):   return f"{_B}{t}{_R}"
def _d(t):   return f"{_D}{t}{_R}"
def _r(t):   return f"{_RED}{t}{_R}"
def _gb(t):  return f"{_G}{_B}{t}{_R}"
def _cb(t):  return f"{_C}{_B}{t}{_R}"

# ── API Cache ──────────────────────────────────────────────────────────────────
_API_CACHE: dict = {}
_KAYNAK_RE = None

# ── ReYMeN config (sabit) ──────────────────────────────────────────────────────
_REYMEN_CONFIG = {
    "provider": os.environ.get("REYMEN_PROVIDER", "deepseek"),
    "model": os.environ.get("REYMEN_MODEL", "deepseek-v4-flash"),
    "temperature": 0.7,
    "max_tokens": 4096,
    "frequency_penalty": 0.8,
}

# ── Versiyon ────────────────────────────────────────────────────────────────────
_REYMEN_VERSION = "v0.1.0"
_REYMEN_DATE   = "2026.6.29"

# ── Ekran ──────────────────────────────────────────────────────────────────────
def _ekran():
    """Ekrani temizle + logo bas."""
    os.system("cls" if os.name == "nt" else "clear")
    banner = r"""
  ██████  ███████  ██    ██ ███    ███ ███████ ███    ██
  ██   ██ ██        ██  ██  ████  ████ ██      ████   ██
  ██████  █████      ████   ██ ████ ██ █████   ██ ██  ██
  ██   ██ ██          ██    ██  ██  ██ ██      ██  ██ ██
  ██   ██ ███████     ██    ██      ██ ███████ ██   ████
    """
    print(f"{_C}{banner}{_R}")
    print(f"  {_gb('ReYMeN Otonom Ajan')}  {_d(_REYMEN_VERSION)}  ({_REYMEN_DATE})")
    print(f"  {_d('─'*56)}")
    print()

# ── Model yardımcıları ─────────────────────────────────────────────────────────
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

def _model_guncelle(provider, model):
    """Provider+model'i .env'ye yaz."""
    os.environ["REYMEN_PROVIDER"] = provider
    os.environ["REYMEN_MODEL"] = model
    _REYMEN_CONFIG["provider"] = provider
    _REYMEN_CONFIG["model"] = model
    try:
        env_path = _KOK / ".env"
        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"\nREYMEN_PROVIDER={provider}\n")
            f.write(f"\nREYMEN_MODEL={model}\n")
    except Exception:
        pass

# ── API kontrol ────────────────────────────────────────────────────────────────
def _api_kontrol(yenile=False):
    """Provider'larin API key'lerini test et."""
    import http.client as _hc
    import json as _js

    if not yenile and _API_CACHE:
        return _API_CACHE

    import threading as _th

    sonuclar = {}
    kilid = _th.Lock()

    def _tek_kontrol(prov, url, env_var, sonuclar, kilid):
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
            conn = _hc.HTTPSConnection(host, timeout=5)
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
        t = _th.Thread(target=_tek_kontrol, args=(p, info["url"], info["env"], sonuclar, kilid), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join(timeout=6)

    for p in _MODEL_DB:
        if p not in sonuclar:
            sonuclar[p] = "zaman_asimi"
    _API_CACHE.clear()
    _API_CACHE.update(sonuclar)
    return sonuclar

# ── Skill sayaci ───────────────────────────────────────────────────────────────
def _skill_sayisi():
    skill_dir = _KOK / "reymen" / "cereyan" / "skills"
    if not skill_dir.exists():
        return 0
    return len([f for f in skill_dir.rglob("*") if f.is_file() and f.suffix in (".md", ".yaml", ".yml")])

def _mem_kayit():
    """Memory kayit sayisini kabaca tahmin et."""
    mem_file = _KOK / ".ReYMeN" / "MEMORY.md"
    if not mem_file.exists():
        return 0
    return sum(1 for _ in open(mem_file, encoding="utf-8") if _.strip() and not _.startswith("#"))

# ── İstatistik paneli ──────────────────────────────────────────────────────────
def _istatistik_paneli():
    """Hermes-style istatistik satırı: tool · skill · memory · session"""
    import uuid as _uid
    skill_n = _skill_sayisi()
    mem_n = _mem_kayit()
    tool_n = 8  # sabit: motor tool'ları
    session = _uid.uuid4().hex[:8]
    print(f"  {_d('─'*56)}")
    print(f"  {_c('●')} {_b('tool')} {_d(str(tool_n))}  {_c('●')} {_b('skill')} {_d(str(skill_n))}  {_c('●')} {_b('memory')} {_d(str(mem_n))}  {_c('●')} {_b('session')} {_d(session)}")
    print(f"  {_d('─'*56)}")
    print()

# ── Model secim ekrani ─────────────────────────────────────────────────────────
def _model_sec(api_sonuc=None, force=False):
    """Etkilesimli model secim ekrani. force=True => her acilista secim."""
    cur_m, cur_p = _mevcut_model()
    W = 56
    _istatistik_paneli()
    print(f"  {_c('┌' + '─'*W + '┐')}")
    print(f"  {_c('│')}  {_gb('Model Seçimi')}{' '*(W-17)}{_c('│')}")
    print(f"  {_c('├' + '─'*W + '┤')}")
    if api_sonuc:
        for ad, durum in api_sonuc.items():
            ikon = _g("✓") if durum is True else (_r("✗") if durum == "401" else _y("?"))
            print(f"  {_c('│')}  {ikon} {_b(ad):<16} {_d(str(durum))}{' '*(W-22-len(str(durum)))}{_c('│')}")
    else:
        print(f"  {_c('│')}  {_d('API kontrol ediliyor...')}{' '*(W-27)}{_c('│')}")
    if cur_p:
        print(f"  {_c('├' + '─'*W + '┤')}")
        print(f"  {_c('│')}  {_g('✓')} {_b(cur_m)} {_d('— aktif')}{' '*(W-18-len(cur_m))}{_c('│')}")
        print(f"  {_c('└' + '─'*W + '┘')}")
    else:
        print(f"  {_c('└' + '─'*W + '┘')}")
    print()
    print(f"  {_d('Komut: /model değiştir  /temizle ekran  /cik çıkış')}")
    print()

# ── Tablo duzeltme ─────────────────────────────────────────────────────────────
def _tablo_duzelt(metin: str) -> str:
    """Markdown tablosunu duzgun hizala."""
    satirlar = metin.split("\n")
    yeni = []
    for s in satirlar:
        if "|" in s and s.count("|") >= 2:
            cols = [c.strip() for c in s.split("|")]
            yeni.append(" | ".join(cols))
        else:
            yeni.append(s)
    return "\n".join(yeni)

# ── Cevap kutusu ──────────────────────────────────────────────────────────────
def _kutu(metin: str, kaynak: str = ""):
    """Cevap kutusu — duzgun cerceve, kaynak bilgisi yok."""
    metin = _tablo_duzelt(metin)
    W = 56
    print(f"\n  {_c('┌' + '─'*W + '┐')}")
    for satir in metin.strip().split("\n"):
        # wrap long lines
        while len(satir) > W:
            print(f"  {_c('│')} {satir[:W]}{' '*(W-len(satir[:W]))} {_c('│')}")
            satir = satir[W:]
        print(f"  {_c('│')} {satir:<{W}} {_c('│')}")
    print(f"  {_c('└' + '─'*W + '┘')}", flush=True)

# ── Spinner ───────────────────────────────────────────────────────────────────
def _spinner(stop_evt):
    frames = ["◈", "◉", "◎", "⊙", "○"]
    cyc_f = itertools.cycle(frames)
    while not stop_evt.is_set():
        frame = next(cyc_f)
        print(f"\r  {frame} ", end="", flush=True)
        time.sleep(0.12)
    print(f"\r{' '*30}\r", end="", flush=True)

# ── ReYMeN çağrısı ────────────────────────────────────────────────────────────
_HERMES = shutil.which("hermes") or shutil.which("hermes") or "hermes"
_ilk_tur = True

# ── SOUL.md oku (Telegram bot ile ayni system prompt) ────────────────────────
def _sistem_prompu_al() -> str:
    """Telegram bot ile aynı system prompt'u üret: SOUL.md + DURUM_OKU."""
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
    """ReYMeN'e soru sor — Telegram bot ile AYNI full pipeline.
    Returns: (yanit, kaynak)
    """
    global _ilk_tur
    _ilk_tur = False

    stop = threading.Event()
    t = threading.Thread(target=_spinner, args=(stop,), daemon=True)
    t.start()

    try:
        # ── 1. GERCEK Beyin (Telegram bot ile ayni) ──────────────
        from reymen.cereyan.beyin import Beyin
        from reymen.cereyan.motor import Motor
        from reymen.cereyan.conversation_loop import ConversationLoop

        # Beyin'i Telegram bot ile ayni config ile baslat
        beyin = Beyin(config=_REYMEN_CONFIG)

        # Motor'u tool'lar ile baslat
        motor = Motor()
        motor._plugin_moduller_yukle()

        # ConversationLoop — Telegram bot ile birebir ayni
        cl = ConversationLoop(
            motor=motor,
            beyin=beyin,
            max_tur=15,
        )

        # Telegram bot ile ayni: run_conversation
        sonuc = cl.run_conversation(
            hedef=soru,
            provider="deepseek",
        )

        if sonuc.get("basarili"):
            yanit = sonuc.get("yanit") or sonuc.get("sonuc", "")
            return yanit, ""
        else:
            hata = sonuc.get("hata") or "Bilinmeyen hata"
            return f"HATA: {hata}", ""

    except Exception as e:
        return f"HATA: {e}", ""
    finally:
        stop.set()
        t.join(timeout=1)


def _sor_direkt_api(soru: str) -> tuple[str, str]:
    """Fallback: gercek Beyin ile direkt API cagrisi."""
    try:
        from reymen.cereyan.beyin import Beyin as _Beyin
        _b = _Beyin(config=_REYMEN_CONFIG)
        _s = "Sen ReYMeN adinda yardimsever bir AI asistanisin. Kisa ve oz cevap ver. Turkce konus."
        _c = _b.uret(_s, [{"role": "user", "content": soru}])
        return _c or "Cevap alinamadi", ""
    except Exception as e:
        return f"HATA: {e}", ""


_YARDIM = f"""
  {_cb('ReYMeN Komutlar')}

  {_c('/yardim')}        Bu menüyü göster
  {_c('/model')}         Model değiştir
  {_c('/temizle')}       Ekranı temizle
  {_c('/skill')} {_d('<ara>')}  Skill ara
  {_c('/cik')}           Çıkış

  {_d('Herhangi bir metin yaz → ReYMeN cevaplar.')}
"""

# ── Ana REPL ──────────────────────────────────────────────────────────────────
def _repl():
    cur_m, cur_p = _mevcut_model()
    print(f"  {_d('ReYMeN hazır. Komut ver.')}")
    print(f"  {_d(f'Model: {cur_m} · /yardım /model /temizle /cik')}")
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
            _ekran()
            _repl()
            return
        if girdi.lower().startswith("/model"):
            _model_sec()
            continue
        if girdi.lower().startswith("/skill "):
            ara = girdi[7:].strip()
            t0 = time.time()
            cevap, kaynak = _sor(f"skill ara: {ara}")
            dt = time.time() - t0
            _kutu(cevap, kaynak)
            print(f"  {_d(f'{dt:.1f}s · skill: {ara}')}")
            continue

        t0 = time.time()
        cevap, kaynak = _sor(girdi)
        dt = time.time() - t0
        _kutu(cevap, kaynak)
        # status line — Hermes tarzi
        t_in = len(girdi.split())
        t_out = len(cevap.split())
        print(f"  {_d(f'{dt:.1f}s · token yaklaşık: giriş={t_in*2} çıkış={t_out*2}')}")

# ── Giriş noktası ────────────────────────────────────────────────────────────
def main():
    # Açılış: banner + istatistik
    _ekran()
    _istatistik_paneli()

    skill_n = _skill_sayisi()
    mem_n = _mem_kayit()

    # Skill ve memory boşsa → model seçimini atla, direkt deepseek
    if skill_n == 0 and mem_n == 0:
        _model_guncelle("deepseek", "deepseek-v4-flash")
        print(f"  {_d('İlk kurulum — deepseek-v4-flash varsayılan.')}\n")
        _repl()
        return

    while True:
        # 1. API durumu kontrol et
        _api_sonuc = _api_kontrol(yenile=True)

        # 2. Model seçimini göster
        _model_sec(_api_sonuc, force=True)
        cur_m, cur_p = _mevcut_model()

        durum = _api_sonuc.get(cur_p)
        if durum is True:
            break  # API key geçerli, devam

        # 3. Hata durumunda uyarı
        if durum == "401":
            print(f"  {_r('401')} {_b(cur_p)}: API anahtarı geçersiz veya eksik.")
        elif durum == "402":
            print(f"  {_r('402')} {_b(cur_p)}: Kredi yetersiz.")
        elif durum is False:
            print(f"  {_r('✗')} {_b(cur_p)}: API hatası.")
        else:
            print(f"  {_y('?')} {_b(cur_p)}: API kontrol edilemedi (zaman aşımı).")
        print(f"  {_d('Başka bir model seçin veya tekrar deneyin.')}\n")

    print(f"  {_g('✓')} {_b('Model aktif, REPL başlatılıyor...')}\n")
    _repl()

if __name__ == "__main__":
    main()
