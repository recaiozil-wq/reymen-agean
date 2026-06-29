# -*- coding: utf-8 -*-
"""
reymen_launcher.py — ReYMeN özel REPL. Hermes UI açılmaz, sadece motor kullanılır.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import re as _re

import logging
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

# ── ANSI ─────────────────────────────────────────────────────────────────────
_R   = "\033[0m"
_B   = "\033[1m"
_C   = "\033[96m"   # cyan
_G   = "\033[92m"   # green
_Y   = "\033[93m"   # yellow
_M   = "\033[95m"   # magenta
_D   = "\033[2m"    # dim
_W   = "\033[97m"   # white
_RED = "\033[91m"   # kırmızı

# ── Finans Kaynakları ─────────────────────────────────────────────────────────
# ── ANSI ─────────────────────────────────────────────────────────────────────
def _c(t):   return f"{_C}{t}{_R}"
def _g(t):   return f"{_G}{t}{_R}"
def _y(t):   return f"{_Y}{t}{_R}"
def _b(t):   return f"{_B}{t}{_R}"
def _d(t):   return f"{_D}{t}{_R}"
def _r(t):   return f"{_RED}{t}{_R}"
def _gb(t):  return f"{_G}{_B}{t}{_R}"
def _cb(t):  return f"{_C}{_B}{t}{_R}"
def _wb(t):  return f"{_W}{_B}{t}{_R}"

# ── Logo ─────────────────────────────────────────────────────────────────────
_LOGO = [
    r"██████╗ ███████╗██╗   ██╗███╗   ███╗███████╗███╗   ██╗",
    r"██╔══██╗██╔════╝╚██╗ ██╔╝████╗ ████║██╔════╝████╗  ██║",
    r"██████╔╝█████╗   ╚████╔╝ ██╔████╔██║█████╗  ██╔██╗ ██║",
    r"██╔══██╗██╔══╝    ╚██╔╝  ██║╚██╔╝██║██╔══╝  ██║╚██╗██║",
    r"██║  ██║███████╗   ██║   ██║ ╚═╝ ██║███████╗██║ ╚████║",
    r"╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝",
]

# ── Config helpers ────────────────────────────────────────────────────────────
def _mevcut_model():
    try:
        import yaml
        cfg = yaml.safe_load(_PROFILE_CFG.read_text(encoding="utf-8"))
        return cfg.get("model", {}).get("default", "deepseek-v4-flash"), \
               cfg.get("model", {}).get("provider", "deepseek")
    except Exception:
        return "deepseek-v4-flash", "deepseek"

def _gateway_hazir_mi(deneme=10, aralik=0.7):
    """reymen gateway list çıktısında reymen ✓ görünene kadar bekle."""
    hermes_bin = _HERMES or "hermes"
    import time as _t
    for _ in range(deneme):
        try:
            r = subprocess.run(
                [hermes_bin, "gateway", "list"],
                capture_output=True, text=True, timeout=5
            )
            satirlar = r.stdout.splitlines()
            for s in satirlar:
                if "reymen" in s and s.strip().startswith("✓"):
                    return True
        except Exception:
            logger.warning("[reymen_launcher] Exception (detaysiz)")
        _t.sleep(aralik)
    return False

def _model_guncelle(provider, model, base_url=""):
    global _ilk_tur
    # Model seçimini yerel .env'ye kaydet (REYMEN_MODEL, REYMEN_PROVIDER)
    try:
        env_path = _KOK / ".env"
        env_content = ""
        if env_path.exists():
            env_content = env_path.read_text(encoding="utf-8")
        lines = env_content.splitlines()
        # Mevcut değerleri güncelle veya ekle
        new_lines = []
        found_model = found_prov = False
        for line in lines:
            if line.startswith("REYMEN_MODEL="):
                new_lines.append(f"REYMEN_MODEL={model}")
                found_model = True
            elif line.startswith("REYMEN_PROVIDER="):
                new_lines.append(f"REYMEN_PROVIDER={provider}")
                found_prov = True
            elif line.startswith("REYMEN_BASE_URL="):
                if base_url:
                    new_lines.append(f"REYMEN_BASE_URL={base_url}")
            else:
                new_lines.append(line)
        if not found_model:
            new_lines.append(f"REYMEN_MODEL={model}")
        if not found_prov:
            new_lines.append(f"REYMEN_PROVIDER={provider}")
        if base_url and not any(l.startswith("REYMEN_BASE_URL=") for l in lines):
            new_lines.append(f"REYMEN_BASE_URL={base_url}")
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    except Exception:
        logger.warning("[reymen_launcher] Exception (detaysiz)")
    _ilk_tur = True

def _skill_sayisi():
    d = _KOK / "skills"
    if not d.exists():
        return 0
    _skip_names = {"README.md", "DESCRIPTION.md", "readme-template.md"}
    _skip_parts = {"ecc", "references", "_kok_copluk_backup", "_ecc_hermes_builtin_backup"}
    return sum(
        1 for p in d.rglob("*.md")
        if p.name not in _skip_names
        and not any(part in _skip_parts for part in p.parts)
    )

def _mem_kayit():
    mem = _HERMES_HOME / "profiles" / "reymen" / "memories" / "MEMORY.md"
    try:
        return mem.read_text(encoding="utf-8", errors="replace").count("§") + 1
    except Exception:
        return 0

# ── API Key Durum Kontrolü ────────────────────────────────────────────────────
import urllib.request, urllib.error, json, time as _time
import threading as _th

_API_CACHE     = {}
_API_CACHE_TTL = 300

_API_KONTROL_ENDPOINTS = [
    ("deepseek",   "https://api.deepseek.com/user/balance",   "DEEPSEEK_API_KEY"),
    ("xiaomi",     "https://api.xiaomimimo.com/v1/models",       "XIAOMI_API_KEY"),
    ("xai",        "https://api.x.ai/v1/models",              "XAI_API_KEY"),
    ("openrouter", "https://openrouter.ai/api/v1/auth/key",   "OPENROUTER_API_KEY"),
    # ── Yeni sağlayıcılar ─────────────────────────────────────────────
    ("together",   "https://api.together.xyz/v1/models",      "TOGETHER_API_KEY"),
    ("fireworks",  "https://api.fireworks.ai/v1/models",      "FIREWORKS_API_KEY"),
    ("mistral",    "https://api.mistral.ai/v1/models",        "MISTRAL_API_KEY"),
    ("cohere",     "https://api.cohere.ai/v1/models",         "COHERE_API_KEY"),
    ("perplexity", "https://api.perplexity.ai/v1/models",     "PERPLEXITY_API_KEY"),
]

def _tek_kontrol(prov, url, env_var, sonuclar, kilid):
    key = os.environ.get(env_var, "").strip()
    if not key:
        with kilid:
            sonuclar[prov] = "401"  # key yok
        return
    try:
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {key}", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=6) as r:
            if prov == "deepseek":
                data = json.loads(r.read().decode())
                ok = data.get("is_available", True)
            else:
                ok = True
    except urllib.error.HTTPError as e:
        if e.code == 401:
            ok = "401"  # API key gecersiz
        elif e.code == 402:
            ok = "402"  # kredi yetersiz
        else:
            ok = None
    except Exception:
        ok = None
    with kilid:
        sonuclar[prov] = ok

def _api_kontrol(yenile=False):
    simdi = _time.time()
    provlar = [p for p,_,__ in _API_KONTROL_ENDPOINTS]
    if not yenile and all(
        p in _API_CACHE and (simdi - _API_CACHE[p][1]) < _API_CACHE_TTL
        for p in provlar
    ):
        return {p: _API_CACHE[p][0] for p in provlar}

    sonuclar, kilid = {}, _th.Lock()
    threadler = [
        _th.Thread(target=_tek_kontrol, args=(p, u, e, sonuclar, kilid), daemon=True)
        for p, u, e in _API_KONTROL_ENDPOINTS
    ]
    for t in threadler: t.start()
    for t in threadler: t.join(timeout=7)

    for p in provlar:
        _API_CACHE[p] = (sonuclar.get(p), _time.time())
    return sonuclar

def _api_ikon(prov, api_d):
    if prov == "lmstudio":
        return _d("--")
    d = api_d.get(prov)
    if d is True:     return _g("✓")
    if d == "401":    return _r("401")
    if d == "402":    return _r("402")
    if d is False:    return _r("✗")
    return _y("?")

def _model_adi(prov, model):
    for p, m, ad, _env, _url in _MODELLER:
        if p == prov and m == model:
            return ad
    return model

# ── Açılış ekranı ─────────────────────────────────────────────────────────────
def _ekran(api_d=None):
    import subprocess as _sp
    try:
        _sp.run("cls" if os.name == "nt" else "clear", shell=True)
    except Exception:
        logger.warning("[reymen_launcher] Exception (detaysiz)")
    for s in _LOGO:
        print(f"  {_cb(s)}")
    print()

    tarih   = datetime.now().strftime("%Y-%m-%d %H:%M")
    model, prov = _mevcut_model()
    skill_n = _skill_sayisi()
    mem_n   = _mem_kayit()
    W = 60

    try:
        ad = _model_adi(prov, model)
    except Exception:
        ad = model
    if api_d is not None:
        ikon = " " + _api_ikon(prov, api_d)
        ikon_len = 2
    else:
        ikon = ""
        ikon_len = 0

    def _row(lbl, val, fn=_g, extra="", extra_len=0):
        pad = W - len(lbl) - len(val) - 5 - extra_len
        print(f"  {_c('║')}  {_d(lbl + ':')} {fn(val)}{extra}{' ' * max(0, pad)}{_c('║')}")

    print(f"  {_c('╔' + '═'*W + '╗')}")
    print(f"  {_c('║')}  {_gb('ReYMeN Otonom Ajan')}{' '*(W-22)}{_c('║')}")
    print(f"  {_c('║')}  {_d('Cave Modu · Türkçe · Otonom REPL')}{' '*(W-36)}{_c('║')}")
    print(f"  {_c('╠' + '═'*W + '╣')}")
    _row("Tarih  ", tarih)
    _row("Model  ", f"{ad}  ({model})", _y, ikon, ikon_len)
    _row("Skill  ", f"{skill_n} adet")
    _row("Hafiza ", f"{mem_n} kayit")
    print(f"  {_c('╚' + '═'*W + '╝')}")
    print()

# ── Model seçimi ──────────────────────────────────────────────────────────────
# (provider, model_id, görünen_ad, env_var, base_url)
_MODELLER = [
    ("deepseek",   "deepseek-v4-flash",        "DeepSeek V4 Flash",      "DEEPSEEK_API_KEY",   ""),
    ("deepseek",   "deepseek-chat",             "DeepSeek V3",            "DEEPSEEK_API_KEY",   ""),
    ("deepseek",   "deepseek-reasoner",         "DeepSeek R1",            "DEEPSEEK_API_KEY",   ""),
    ("xiaomi",     "mimo-v2.5",                 "MiMo V2.5",              "XIAOMI_API_KEY",     "https://api.xiaomimimo.com/v1"),
    ("xai",        "grok-3",                    "xAI Grok 3",             "XAI_API_KEY",        ""),
    ("xai",        "grok-3-mini",               "xAI Grok 3 Mini",        "XAI_API_KEY",        ""),
    ("xai",        "grok-beta",                 "xAI Grok Beta",          "XAI_API_KEY",        ""),
    ("openrouter", "deepseek/deepseek-chat",    "OpenRouter / DeepSeek",  "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    ("lmstudio",   "local",                     "LM Studio (Yerel)",      "",                   "http://localhost:1234/v1"),
]

def _model_sec(api_d=None, force=False):
    """
    Model seçim ekranı.
    - force=True: her zaman göster (açılışta)
    - force=False: mevcut model varsa atla
    """
    if api_d is None:
        api_d = {}

    cur_m, cur_p = _mevcut_model()

    # force=True ise seçim ekranını her zaman göster
    if not force and cur_m and cur_p:
        for p, m, ad, _env, _url in _MODELLER:
            if p == cur_p and m == cur_m:
                print(f"  {_g('✓')} {_b(ad)} {_d('— aktif, /model ile değiştir')}")
                print()
                return  # seçim ekranını atla

    # Mevcut model yok veya False — seçim ekranını göster
    liste = [(p,m,a,url) for p,m,a,env,url in _MODELLER
             if not env or os.environ.get(env,"").strip()]
    if not liste:
        return

    print(f"  {_b('Model Sec:')}")
    print()
    for i,(prov,mod,ad,url) in enumerate(liste, 1):
        aktif = (mod == cur_m and prov == cur_p)
        isk   = _gb("→") if aktif else _d(" ")
        ikon  = _api_ikon(prov, api_d)
        durum = api_d.get(prov)
        uyari = ""
        if durum == "402":
            uyari = f" {_r('[402]')}"
        elif durum == "401":
            uyari = f" {_r('[401]')}"
        elif durum is False:
            uyari = f" {_y('[hata]')}"
        print(f"  {isk} [{_cb(str(i))}] {ikon} {_g(ad):<26} {_d(mod)}{uyari}")
    print()
    try:
        y = input(f"  {_d('[ENTER: mevcut koru]')}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(); return

    if y.isdigit():
        idx = int(y) - 1
        if 0 <= idx < len(liste):
            prov, mod, ad, url = liste[idx]
            # DeepSeek kredisi bitmiş bile olsa seçime izin ver
            # ReYMeN fallback_providers otomatik openrouter/lmstudio'ya geçer
            print(f"  {_y('◌')} {_d('model kaydediliyor...')}", end="", flush=True)
            _model_guncelle(prov, mod, url)
            print(f"\r  {_g('✓')} {_b(ad)} aktif.                        ")
    print()

# ── Tablo düzeltme ────────────────────────────────────────────────────────────
def _tablo_duzelt(metin: str) -> str:
    """Markdown tablo satirlarindaki bosluklari duzeltir."""
    satirlar = metin.split('\n')
    yeni = []
    for s in satirlar:
        if '|' in s and s.count('|') >= 2:
            cols = [c.strip() for c in s.split('|')]
            yeni.append(' | '.join(cols))
        else:
            yeni.append(s)
    return '\n'.join(yeni)

# ── Cevap kutusu ──────────────────────────────────────────────────────────────
def _kutu(metin: str, kaynak: str = ""):
    """Hermes formatinda cevap kutusu — emoji + baslik + tablo."""
    metin = _tablo_duzelt(metin)
    # Kaynak emojisi
    kaynak_emoji = {
        "once_hafiza": "💾", "(hafiza)": "💾",
        "web_arama": "🌐", "(web)": "🌐",
        "oncelik_cache": "⚡", "(cache)": "⚡",
        "llm": "🧠",
    }.get(kaynak, "🤖")
    print(f"\n  {'─'*50}", flush=True)
    print(f"  {kaynak_emoji} {_W}{metin}{_R}", flush=True)
    if kaynak:
        print(f"  {_M}└─ Kaynak: {kaynak}{_R}", flush=True)
    print(f"  {'─'*50}", flush=True)


# ── Spinner ───────────────────────────────────────────────────────────────────
import threading, itertools, time

def _spinner(stop_evt):
    frames = ["◈", "◉", "◎", "⊙", "○"]
    verbs  = ["analiz", "düşün", "işlem", "araştır", "hesapla"]
    cyc_f  = itertools.cycle(frames)
    cyc_v  = itertools.cycle(verbs)
    verb   = next(cyc_v)
    count  = 0
    while not stop_evt.is_set():
        frame = next(cyc_f)
        print(f"\r  {_c(frame)} {_d(verb)}...   ", end="", flush=True)
        time.sleep(0.12)
        count += 1
        if count % 10 == 0:
            verb = next(cyc_v)
    print(f"\r{' '*30}\r", end="", flush=True)

# ── ReYMeN çağrısı ────────────────────────────────────────────────────────────
_HERMES = shutil.which("hermes") or shutil.which("hermes") or "hermes"
_ilk_tur = True

# ── Once tanimli config (Telegram bot ile ayni) ──────────────────────────────
_REYMEN_CONFIG = {
    "default_model":    "deepseek-v4-flash",
    "default_provider": "deepseek",
    "secure_binding": True,
    "providers": {
        "deepseek":     {"base_url": "https://api.deepseek.com",
                         "api_key": os.environ.get("DEEPSEEK_API_KEY", "")},
        "xiaomi":       {"base_url": os.environ.get("XIAOMI_BASE_URL", "https://api.xiaomimimo.com/v1"),
                         "api_key": os.environ.get("XIAOMI_API_KEY", "")},
        "xai":          {"base_url": "https://api.x.ai",
                         "api_key": os.environ.get("XAI_API_KEY", "")},
        "openrouter":   {"base_url": "https://openrouter.ai/api/v1",
                         "api_key": os.environ.get("OPENROUTER_API_KEY", "")},
    },
}

_KREDI_SINYALLER = (
    "insufficient_quota", "insufficient balance", "insufficient funds",
    "out of credits", "no credits", "quota exceeded", "exceeded your current quota",
    "billing", "payment required", "402", "topup", "recharge",
    "account balance", "credits remaining", "credit limit",
)
_BRANDING_FILTRE = (
    "hermes", "nous research", "© nous", "hermes agent",
    "update available", "upgrade available", "version",
)
_KAYNAK_RE = None  # lazy import

def _kaynak_ayikla(cevap: str) -> tuple[str, str]:
    """Yanıttan Kaynak: satırını ayıklar. Returns: (temiz_cevap, kaynak_url)"""
    global _KAYNAK_RE
    if _KAYNAK_RE is None:
        import re
        _KAYNAK_RE = re.compile(r'^.*?Kaynak:\s*(https?://\S+).*$', re.MULTILINE | re.IGNORECASE)
    m = _KAYNAK_RE.search(cevap)
    if m:
        url = m.group(1).strip()
        # Kaynak satırını cevaptan çıkar
        temiz = _KAYNAK_RE.sub('', cevap).strip()
        return temiz, url
    return cevap, ""


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
        "## \u26a0\ufe0f DURUM_OKU() ZORUNLU TALIMAT\\n"
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
            kaynak = sonuc.get("kaynak", "llm")
            if kaynak == "once_hafiza":
                return f"{yanit}", "(hafiza)"
            elif kaynak == "web_arama":
                return f"{yanit}", "(web)"
            elif kaynak == "oncelik_cache":
                return f"{yanit}", "(cache)"
            else:
                return f"{yanit}", ""
        else:
            hata = sonuc.get("hata", "Bilinmeyen hata")
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
    print(f"  {_d('ReYMeN hazır. Komut ver. (/yardim için /yardim yaz)')}")
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
            print(f"  {_d('ReYMeN hazır.')}\n")
            continue
        if girdi.lower().startswith("/model"):
            _model_sec()
            continue
        if girdi.lower().startswith("/skill "):
            ara = girdi[7:].strip()
            cevap, kaynak = _sor(f"skill ara: {ara}")
            _kutu(cevap, kaynak)
            continue

        cevap, kaynak = _sor(girdi)
        _kutu(cevap, kaynak)

# ── Giriş noktası ────────────────────────────────────────────────────────────
def main():
    _ekran()
    skill_n = _skill_sayisi()
    mem_n = _mem_kayit()

    # Skill ve memory boşsa → model seçimini atla, direkt deepseek-v4-flash
    if skill_n == 0 and mem_n == 0:
        _model_guncelle("deepseek", "deepseek-v4-flash")
        print(f"  {_d('İlk kurulum — deepseek-v4-flash varsayılan olarak ayarlandı.')}\n")
        _repl()
        return

    while True:
        # 1. Model seçimini göster (api_sonuc varsa göster, yoksa ilk açılış)
        _model_sec(_api_sonuc if '_api_sonuc' in dir() else None, force=True)
        cur_m, cur_p = _mevcut_model()

        # 2. Seçilen modelin API key'ini kontrol et
        _api_sonuc = _api_kontrol(yenile=True)

        durum = _api_sonuc.get(cur_p)
        if durum is True:
            break  # API key geçerli, devam

        # 3. Hata durumunda uyarı göster ve döngüye devam
        if durum == "401":
            print(f"  {_r('401')} {_b(cur_p)}: API anahtarı geçersiz veya eksik.")
            print(f"  {_d('Başka bir model seçin.')}\n")
        elif durum == "402":
            print(f"  {_r('402')} {_b(cur_p)}: Kredi yetersiz.")
            print(f"  {_d('Bakiye yükleyin veya başka model seçin.')}\n")
        elif durum is False:
            print(f"  {_r('✗')} {_b(cur_p)}: API hatası.")
            print(f"  {_d('Başka bir model seçin.')}\n")
        else:
            print(f"  {_y('?')} {_b(cur_p)}: API kontrol edilemedi (zaman aşımı).")
            print(f"  {_d('Başka bir model seçin veya tekrar deneyin.')}\n")

    print(f"  {_g('✓')} {_b('Model aktif, REPL başlatılıyor...')}\n")
    _repl()

if __name__ == "__main__":
    main()
