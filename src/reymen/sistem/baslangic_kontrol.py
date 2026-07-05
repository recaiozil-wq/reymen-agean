# -*- coding: utf-8 -*-
"""
baslangic_kontrol.py â€” ReYMeN BaÅŸlangÄ±Ã§ ve Ortam KontrolÃ¼.

Program aÃ§Ä±lÄ±ÅŸÄ±nda Ã§alÄ±ÅŸÄ±r:
  1. Harici API anahtarÄ± var mÄ±? â†’ varsa o provider ile baÅŸlat
  2. Yoksa Ollama Ã§alÄ±ÅŸÄ±yor mu?  â†’ Ã§alÄ±ÅŸmÄ±yorsa uyarÄ± ver
  3. llava modeli yÃ¼klÃ¼ mÃ¼?      â†’ yoksa indir seÃ§eneÄŸi sun
  4. /model komutu               â†’ Ã§alÄ±ÅŸma sÄ±rasÄ±nda model deÄŸiÅŸtir
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

OLLAMA_BASE = "http://localhost:11434"
LMSTUDIO_BASE = "http://localhost:1234"
_HTTP_TIMEOUT = 3

# Kontrol edilecek harici API anahtarlarÄ± (env deÄŸiÅŸken adÄ± â†’ provider adÄ±)
HARICI_API_ENV = {
    "DEEPSEEK_API_KEY": "DeepSeek",
    "ANTHROPIC_API_KEY": "Anthropic",
    "OPENAI_API_KEY": "OpenAI",
    "GROQ_API_KEY": "Groq",
    "MOONSHOT_API_KEY": "Moonshot",
}

# Ollama'dan indirilecek modeller (hafif genel + gÃ¶rsel)
ONERILIR_MODEL = "llama3.2:3b"  # kÃ¼Ã§Ã¼k ama yetenekli
GORUNTUSEL_MODEL = "llava:7b"  # gÃ¶rsel/OCR iÃ§in


# â”€â”€ YardÄ±mcÄ± fonksiyonlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _reymen_env_yolu() -> Path:
    """Platform-bagimsiz .env yolu (Windows / Linux / macOS)."""
    import platform

    ev = Path.home()
    if platform.system() == "Windows":
        return ev / "AppData" / "Local" / "reymen" / ".env"
    return ev / ".config" / "reymen" / ".env"


def _env_deger(anahtar: str) -> str:
    """Env veya ReYMeN .env dosyasÄ±ndan deÄŸer oku."""
    deger = os.environ.get(anahtar, "").strip()
    if deger:
        return deger
    env_dosya = _reymen_env_yolu()
    if env_dosya.exists():
        try:
            for satir in env_dosya.read_text(encoding="utf-8").splitlines():
                if satir.startswith(f"{anahtar}="):
                    val = satir.split("=", 1)[1].strip()
                    if val and not val.startswith("***"):
                        return val
        except OSError as _baslangi_e60:
            print(f"[UYARI] baslangic_kontrol.py:61 - {_baslangi_e60}")
    return ""


def api_anahtari_var_mi() -> dict:
    """TanÄ±mlÄ± harici API anahtarlarÄ±nÄ± dÃ¶ndÃ¼r. {provider_adi: anahtar}"""
    bulunanlar = {}
    for env_adi, provider_adi in HARICI_API_ENV.items():
        val = _env_deger(env_adi)
        if val:
            bulunanlar[provider_adi] = val
    return bulunanlar


def lmstudio_modeller(base_url: str = LMSTUDIO_BASE) -> list:
    """LM Studio'da yuklÃ¼ modellerin isim listesini donDur."""
    try:
        import urllib.request

        req = urllib.request.Request(
            f"{base_url}/v1/models",
            headers={"Authorization": "Bearer not-needed"},
        )
        with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
            return [m["id"] for m in json.loads(r.read().decode()).get("data", [])]
    except Exception:
        return []


def ollama_calisiyor_mu() -> bool:
    """Ollama servisinin calisip calismadigini kontrol et."""
    try:
        import urllib.request

        with urllib.request.urlopen(
            f"{OLLAMA_BASE}/api/tags", timeout=_HTTP_TIMEOUT
        ) as r:
            return r.status == 200
    except Exception:
        return False


def ollama_modeller() -> list:
    """Ollama'da yÃ¼klÃ¼ modellerin isim listesini dÃ¶ndÃ¼r."""
    try:
        import urllib.request

        with urllib.request.urlopen(f"{OLLAMA_BASE}/api/tags", timeout=5) as r:
            data = json.loads(r.read().decode())
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def llava_yuklu_mu() -> bool:
    """llava modeli yÃ¼klÃ¼ mÃ¼?"""
    return any("llava" in m.lower() for m in ollama_modeller())


def model_indir(model_adi: str) -> bool:
    """Ollama API Ã¼zerinden model indir, ilerlemeyi konsola yaz."""
    print(f"\n  Ä°ndiriliyor: {model_adi} ...")
    try:
        import urllib.request

        istek = json.dumps({"name": model_adi, "stream": True}).encode()
        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/pull",
            data=istek,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        onceki_durum = ""
        with urllib.request.urlopen(req, timeout=600) as r:
            for satir in r:
                if not satir.strip():
                    continue
                try:
                    veri = json.loads(satir.decode())
                except json.JSONDecodeError:
                    continue

                durum = veri.get("status", "")
                toplam = veri.get("total", 0)
                tamamlanan = veri.get("completed", 0)

                if toplam and tamamlanan:
                    yuzde = int(tamamlanan / toplam * 100)
                    ilerleme = f"[{'â–ˆ' * (yuzde // 5):<20}] {yuzde}%"
                    print(f"\r  {durum}: {ilerleme}", end="", flush=True)
                elif durum != onceki_durum and durum:
                    print(f"\r  {durum:<60}", end="", flush=True)
                onceki_durum = durum

        print(f"\r  {model_adi} indirildi.{' ' * 40}")
        return True
    except Exception as e:
        print(f"\n  [Hata] {model_adi} indirilemedi: {e}")
        return False


# â”€â”€ Ana baÅŸlangÄ±Ã§ kontrolÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def baslangic_kontrolu(config: dict) -> dict:
    """
    Program baÅŸlangÄ±cÄ±nda Ã§alÄ±ÅŸÄ±r. Config'i doÄŸrular/gÃ¼nceller.
    - Harici API varsa kullan â†’ Ollama kontrolÃ¼ atla
    - Yoksa Ollama + llava zorunlu
    """
    # (baslangiÃ§ banner startup_ekrani.py tarafindan gosterilir)

    # 0. Kaydedilmis bulut tercihi var mi? â†’ LM Studio'yu gecersiz kilma
    _BULUT_ENV_MAP = {
        "deepseek": "DEEPSEEK_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "groq": "GROQ_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    try:
        _setup_dosya = Path(__file__).parent / ".ReYMeN" / "setup.json"
        if _setup_dosya.exists():
            _saved = json.loads(_setup_dosya.read_text(encoding="utf-8"))
            _tercih_prov = _saved.get("tercih_provider", "")
            _tercih_model = _saved.get("tercih_model", "")
            if (
                _tercih_prov
                and _tercih_prov not in ("lmstudio", "ollama")
                and _tercih_model
            ):
                _env_key = _BULUT_ENV_MAP.get(_tercih_prov, "")
                if _env_key and os.environ.get(_env_key, "").strip():
                    config["default_provider"] = _tercih_prov
                    config["default_model"] = _tercih_model
                    return config
    except Exception as _baslangi_e186:
        print(f"[UYARI] baslangic_kontrol.py:187 - {_baslangi_e186}")

    # 1. LM Studio kontrolÃ¼ (API anahtarÄ±na gerek yok)
    ls_url = (
        config.get("providers", {}).get("lmstudio", {}).get("base_url", LMSTUDIO_BASE)
    )
    ls_modeller = lmstudio_modeller(ls_url)
    if ls_modeller:
        vizyon_m = next(
            (m for m in ls_modeller if "llava" in m.lower() or "vision" in m.lower()),
            None,
        )
        if vizyon_m:
            config.setdefault("auxiliary", {}).setdefault("vision", {})["model"] = (
                vizyon_m
            )
        config["default_model"] = ls_modeller[0]
        config["default_provider"] = "lmstudio"
        return config

    # 2. Harici API anahtarÄ± kontrolÃ¼
    aktif_api = api_anahtari_var_mi()
    if aktif_api:
        provider_listesi = ", ".join(aktif_api.keys())
        return config  # Ollama'ya gerek yok

    # 3. API yok â†’ Ollama zorunlu
    print("\n  LM Studio ve harici API anahtarÄ± bulunamadÄ±.")
    print("  Yerel calisma icin Ollama gereklidir.\n")

    if not ollama_calisiyor_mu():
        print("  [UYARI] Ollama calismiyor veya kurulu degil!")
        print()
        print("  Secenekler:")
        print("    1. Ollama'yÄ± baslatÄ±n : ollama serve")
        print("    2. Ollama kurun       : https://ollama.ai/download")
        print("    3. LM Studio'yu baslatÄ±n")
        print("    4. API anahtarÄ± ekleyin (.env dosyasÄ±na DEEPSEEK_API_KEY vb.)")
        print()
        yanit = (
            input("  Ollama zaten calisÄ±yor, tekrar kontrol et? [e/h]: ")
            .strip()
            .lower()
        )
        if yanit == "e" and ollama_calisiyor_mu():
            print("  Ollama baglantÄ±sÄ± saglandi.")
        else:
            print("  Devam ediliyor â€” LLM erismeden calÄ±sacak (sÄ±nÄ±rlÄ± mod).")
            return config

    # 3. Ollama Ã§alÄ±ÅŸÄ±yor â€” model listesini gÃ¶ster
    mevcut_modeller = ollama_modeller()
    print(f"  Ollama Ã§alÄ±ÅŸÄ±yor â€” {len(mevcut_modeller)} model yÃ¼klÃ¼:")
    for m in mevcut_modeller:
        isaretci = "  â†’" if "llava" in m.lower() else "   "
        print(f"  {isaretci} {m}")

    # 4. llava kontrolÃ¼
    if not llava_yuklu_mu():
        print()
        print("  [BÄ°LGÄ°] GÃ¶rsel/OCR iÅŸlevleri iÃ§in 'llava' modeli gereklidir.")
        print(f"  Ä°ndirilecek modeller:")
        print(f"    â€¢ {ONERILIR_MODEL}  (genel amaÃ§lÄ±, hafif)")
        print(f"    â€¢ {GORUNTUSEL_MODEL} (gÃ¶rsel analiz)")
        print()
        print("  [Ä°] Ä°ndir    [G] GeÃ§    [Ã‡] Ã‡Ä±kÄ±ÅŸ")
        yanit = input("  SeÃ§iminiz: ").strip().upper()

        if yanit == "Ä°" or yanit == "I":
            # Genel model â€” sadece listede yoksa indir
            genel_yuklu = any(
                ONERILIR_MODEL.split(":")[0] in m for m in mevcut_modeller
            )
            if not genel_yuklu:
                model_indir(ONERILIR_MODEL)
            else:
                print(f"  {ONERILIR_MODEL} zaten mevcut, atlanÄ±yor.")
            model_indir(GORUNTUSEL_MODEL)
            # Config'i llava'ya gÃ¼ncelle
            if "auxiliary" in config:
                config["auxiliary"]["vision"]["model"] = GORUNTUSEL_MODEL

        elif yanit == "Ã‡" or yanit == "C":
            print("  Ã‡Ä±kÄ±lÄ±yor.")
            sys.exit(0)
        else:
            print("  GeÃ§iliyor â€” llava olmadan devam ediliyor.")
    else:
        # llava var, modeli config'e yaz
        llava_adi = next(m for m in mevcut_modeller if "llava" in m.lower())
        if "auxiliary" in config:
            config["auxiliary"]["vision"]["model"] = llava_adi
        print(f"\n  GÃ¶rsel model hazÄ±r: {llava_adi}")

    # 5. VarsayÄ±lan provider'Ä± Ollama'ya ayarla
    if not config.get("default_provider") or config["default_provider"] in (
        "lmstudio",
    ):
        if mevcut_modeller:
            config["default_provider"] = "ollama"
            config["default_model"] = mevcut_modeller[0]
            # Ollama provider giriÅŸi ekle
            config.setdefault("providers", {})["ollama"] = {
                "base_url": OLLAMA_BASE,
                "api_key": "not-needed",
            }
            print(f"  Aktif model: {mevcut_modeller[0]}")

    # 6. Arka planda gÃ¼ncelleme kontrolÃ¼ baÅŸlat (kullanÄ±cÄ±yÄ± bekletmez)
    try:
        from reymen.sistem.guncelle import arka_plan_baslat

        arka_plan_baslat()
    except ImportError as _baslangi_e284:
        print(f"[UYARI] baslangic_kontrol.py:285 - {_baslangi_e284}")

    return config


# Bulut saÄŸlayÄ±cÄ± â†’ (model_adi, aciklama) listesi
_BULUT_MODELLER = {
    "deepseek": [
        ("deepseek-chat", "DeepSeek Chat"),
        ("deepseek-reasoner", "DeepSeek Reasoner"),
    ],
    "openai": [("gpt-4o", "GPT-4o"), ("gpt-4o-mini", "GPT-4o Mini")],
    "anthropic": [
        ("claude-haiku-4-5-20251001", "Claude Haiku 4.5"),
        ("claude-sonnet-4-6", "Claude Sonnet 4.6"),
    ],
    "groq": [
        ("llama-3.1-70b-versatile", "LLaMA 3.1 70B (Groq)"),
        ("mixtral-8x7b-32768", "Mixtral 8x7B"),
    ],
    "moonshot": [
        ("moonshot-v1-8k", "Moonshot 8k"),
        ("moonshot-v1-32k", "Moonshot 32k"),
    ],
}

# Bulut provider â†’ env degisken adi
_BULUT_ENV = {
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "moonshot": "MOONSHOT_API_KEY",
}


# â”€â”€ /model komutu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def model_degistir(agent) -> bool:
    """
    Calisma sÄ±rasÄ±nda /model komutuyla model degistirir.
    LM Studio, Ollama ve API anahtarÄ± olan bulut saglayÄ±cÄ±larÄ± listeler.

    Returns:
        True  â†’ model degistirildi
        False â†’ iptal
    """
    mevcut_p = agent.config.get("default_provider", "?")
    mevcut_m = agent.config.get("default_model", "?")
    ls_url = (
        agent.config.get("providers", {})
        .get("lmstudio", {})
        .get("base_url", LMSTUDIO_BASE)
    )

    print(f"\n  Mevcut: [{mevcut_p}] {mevcut_m}")
    print("  " + "â”€" * 50)

    secenekler = []  # [(provider, model, aciklama), ...]
    idx = 1

    # LM Studio modelleri
    ls_mods = lmstudio_modeller(ls_url)
    if ls_mods:
        print(f"\n  LM Studio ({ls_url}):")
        for m in ls_mods[:6]:
            isaret = "â†’" if m == mevcut_m and mevcut_p == "lmstudio" else " "
            print(f"  {isaret} [{idx}] {m}")
            secenekler.append(("lmstudio", m, m))
            idx += 1

    # Ollama modelleri
    if ollama_calisiyor_mu():
        oll_mods = ollama_modeller()
        if oll_mods:
            print(f"\n  Ollama ({OLLAMA_BASE}):")
            for m in oll_mods[:6]:
                isaret = "â†’" if m == mevcut_m and mevcut_p == "ollama" else " "
                print(f"  {isaret} [{idx}] {m}")
                secenekler.append(("ollama", m, m))
                idx += 1

    # Bulut modeller (sadece API anahtarÄ± olanlar)
    for provider, mods in _BULUT_MODELLER.items():
        env_adi = _BULUT_ENV.get(provider, "")
        anahtar = os.environ.get(env_adi, "").strip()
        if anahtar and not anahtar.startswith("***"):
            print(f"\n  {provider.capitalize()} (API key mevcut):")
            for model_adi, aciklama in mods:
                isaret = "â†’" if model_adi == mevcut_m and mevcut_p == provider else " "
                print(f"  {isaret} [{idx}] {aciklama}")
                secenekler.append((provider, model_adi, aciklama))
                idx += 1

    if not secenekler:
        print("  [/model] Hicbir model bulunamadÄ±.")
        return False

    print(f"\n  [0] Iptal")
    yanit = input("\n  Secin (numara veya model adÄ±): ").strip()

    if yanit == "0" or not yanit:
        print("  Iptal edildi.")
        return False

    # Numara ile seÃ§im
    if yanit.isdigit():
        num = int(yanit) - 1
        if 0 <= num < len(secenekler):
            yeni_provider, yeni_model, _ = secenekler[num]
        else:
            print("  Gecersiz numara.")
            return False
    else:
        # Ä°sim ile kÄ±smi eÅŸleÅŸme
        eslesen = [
            (p, m, a)
            for p, m, a in secenekler
            if yanit.lower() in m.lower() or yanit.lower() in a.lower()
        ]
        if not eslesen:
            print(f"  '{yanit}' adÄ±nda model bulunamadÄ±.")
            return False
        yeni_provider, yeni_model, _ = eslesen[0]

    # Agent config'ini guncelle
    agent.config["default_model"] = yeni_model
    agent.config["default_provider"] = yeni_provider

    if yeni_provider == "ollama":
        agent.config.setdefault("providers", {})["ollama"] = {
            "base_url": OLLAMA_BASE,
            "api_key": "not-needed",
        }

    # Provider'i dogrula (kredi kontrolu)
    if yeni_provider not in ("lmstudio", "ollama", "groq", "moonshot"):
        print(f"  {yeni_provider} kontrol ediliyor...")
        import urllib.request as _ureq
        import urllib.error as _uerr

        try:
            prov_conf = agent.config.get("providers", {}).get(yeni_provider, {})
            base_url = prov_conf.get("base_url", "")
            api_key = prov_conf.get("api_key", "") or _env_deger(
                _BULUT_ENV.get(yeni_provider, "")
            )
            if not api_key:
                print(f"  [HATA] API anahtari bulunamadi ({yeni_provider})")
                return False

            req = _ureq.Request(
                f"{base_url.rstrip('/')}/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                method="GET",
            )
            with _ureq.urlopen(req, timeout=5) as resp:
                pass
        except _uerr.HTTPError as e:
            if e.code == 402:
                print(f"  [HATA] {yeni_provider} kredisi yok (HTTP 402)")
                print("  Lutfen baska bir model secin.")
                return False
            elif e.code == 401:
                print(f"  [HATA] {yeni_provider} API anahtari gecersiz (HTTP 401)")
                return False
            else:
                print(f"  [HATA] {yeni_provider} erisim hatasi: HTTP {e.code}")
                print("  Bu modeli tekrar denemek icin /model yazin.")
                return False
        except Exception as e:
            print(f"  [UYARI] {yeni_provider} dogrulama basarisiz: {e}")
            print("  Devam ediliyor...")

    # Provider'i yeniden olustur
    try:
        from reymen.cereyan.beyin import Beyin

        yeni_beyin = Beyin(agent.config)
        agent.provider = yeni_beyin
        # planlayici da yenile (Planlayici(provider) alÄ±yor)
        try:
            from reymen.cereyan.planlayici import Planlayici

            agent.planlayici = Planlayici(agent.provider)
        except Exception as _baslangi_e443:
            print(f"[UYARI] baslangic_kontrol.py:444 - {_baslangi_e443}")
        print(f"\n  [OK] Model degistirildi: [{yeni_provider}] {yeni_model}")
        return True
    except Exception as e:
        print(f"  [Hata] Provider yenilenirken sorun: {e}")
        return False


if __name__ == "__main__":
    print("=== BaÅŸlangÄ±Ã§ Kontrol Testi ===")
    print(f"API anahtarlarÄ±: {api_anahtari_var_mi()}")
    print(f"Ollama Ã§alÄ±ÅŸÄ±yor: {ollama_calisiyor_mu()}")
    print(f"YÃ¼klÃ¼ modeller: {ollama_modeller()}")
    print(f"llava yÃ¼klÃ¼: {llava_yuklu_mu()}")
