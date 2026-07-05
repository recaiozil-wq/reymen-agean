# -*- coding: utf-8 -*-
"""key_validate.py â€” API anahtarÄ± doÄŸrulama modÃ¼lÃ¼.

Kurulum sÄ±rasÄ±nda ve her baÅŸlangÄ±Ã§ta API key'lerinin
varlÄ±ÄŸÄ±nÄ± ve formatÄ±nÄ± kontrol eder.

KullanÄ±m:
    from reymen.guvenlik.key_validate import key_kontrol, KEY_TANIMLARI
    eksikler = key_kontrol()
    if eksikler:
        print(f"Eksik key'ler: {eksikler}")
"""

import os
import re
from typing import Dict, List, Optional, Tuple

# Provider key tanÄ±mlarÄ±: (env_adÄ±, zorunlu mu?, format_regex, aÃ§Ä±klama)
KEY_TANIMLARI: Dict[str, Tuple[bool, Optional[str], str]] = {
    # (zorunlu, format_regex, aÃ§Ä±klama)
    "DEEPSEEK_API_KEY": (
        True,
        r"^sk-[A-Za-z0-9]{20,}$",
        "DeepSeek API anahtarÄ± (sk- ile baÅŸlar)",
    ),
    "OPENAI_API_KEY": (
        False,
        r"^sk-[A-Za-z0-9]{20,}$",
        "OpenAI API anahtarÄ± (sk- ile baÅŸlar)",
    ),
    "ANTHROPIC_API_KEY": (
        False,
        r"^sk-ant-[A-Za-z0-9]{20,}$",
        "Anthropic API anahtarÄ± (sk-ant- ile baÅŸlar)",
    ),
    "OPENROUTER_API_KEY": (
        False,
        None,
        "OpenRouter API anahtarÄ±",
    ),
    "GROQ_API_KEY": (
        False,
        r"^gsk_[A-Za-z0-9]{20,}$",
        "Groq API anahtarÄ± (gsk_ ile baÅŸlar)",
    ),
    "XAI_API_KEY": (
        False,
        None,
        "xAI (Grok) API anahtarÄ±",
    ),
    "XIAOMI_API_KEY": (
        False,
        None,
        "Xiaomi/MiMo API anahtarÄ±",
    ),
}

# Telegram bot token'larÄ± (opsiyonel, format kontrollÃ¼)
BOT_TOKEN_TANIMLARI: Dict[str, Tuple[bool, str]] = {
    "BOT_TOKEN_REYMEN": (False, "ReYMeN Ana Bot"),
    "BOT_TOKEN_PASA": (False, "Pasa_38 Bot"),
    "BOT_TOKEN_KRAL": (False, "Kiral38 Bot"),
    "TELEGRAM_BOT_TOKEN": (False, "Genel Telegram Bot"),
}

# Format: 1234567890:ABCdefGHIjklmNOPqrstUVWXyz
BOT_TOKEN_REGEX = re.compile(r"^\d{8,10}:[A-Za-z0-9_-]{30,}$")


def key_format_kontrol(key: str, regex: Optional[str]) -> bool:
    """Key formatÄ±nÄ± kontrol et. regex=None ise sadece boÅŸ kontrolÃ¼ yap."""
    if not key or key == "buraya_yaz":
        return False
    if regex is None:
        return bool(key.strip())
    return bool(re.match(regex, key.strip()))


def key_kontrol() -> Dict[str, List[str]]:
    """TÃ¼m API anahtarlarÄ±nÄ± kontrol et.

    Returns:
        {
            "eksik_zorunlu": ["DEEPSEEK_API_KEY"],   # HiÃ§ yok veya buraya_yaz
            "format_hatali": ["OPENAI_API_KEY"],      # Var ama format yanlÄ±ÅŸ
            "eksik_opsiyonel": ["GROQ_API_KEY"],      # Opsiyonel ama yok
            "uyari": ["BOT_TOKEN_PASA"]               # Bot token formatÄ± hatalÄ±
        }
    """
    sonuc: Dict[str, List[str]] = {
        "eksik_zorunlu": [],
        "format_hatali": [],
        "eksik_opsiyonel": [],
        "uyari": [],
    }

    # LLM key'leri
    for env_ad, (zorunlu, regex, aciklama) in KEY_TANIMLARI.items():
        value = os.environ.get(env_ad, "") or ""
        if not value or value == "buraya_yaz":
            if zorunlu:
                sonuc["eksik_zorunlu"].append(f"{env_ad} ({aciklama})")
            else:
                sonuc["eksik_opsiyonel"].append(env_ad)
        elif regex and not key_format_kontrol(value, regex):
            sonuc["format_hatali"].append(f"{env_ad} â€” beklenen format: {regex}")

    # Bot token'larÄ±
    for env_ad, (zorunlu, aciklama) in BOT_TOKEN_TANIMLARI.items():
        value = os.environ.get(env_ad, "") or ""
        if value and value != "buraya_yaz":
            if not BOT_TOKEN_REGEX.match(value.strip()):
                sonuc["uyari"].append(
                    f"{env_ad} ({aciklama}) â€” format: 1234567890:ABCdef..."
                )

    return sonuc


def ozet_ver(kontrol_sonuc: Dict[str, List[str]]) -> str:
    """Kontrol sonucunu okunabilir metne Ã§evir."""
    satirlar = []

    if kontrol_sonuc["eksik_zorunlu"]:
        satirlar.append("âŒ EKSÄ°K ZORUNLU KEY'LER:")
        for k in kontrol_sonuc["eksik_zorunlu"]:
            satirlar.append(f"   â€¢ {k}")

    if kontrol_sonuc["format_hatali"]:
        satirlar.append("âš ï¸ FORMAT HATALI KEY'LER:")
        for k in kontrol_sonuc["format_hatali"]:
            satirlar.append(f"   â€¢ {k}")

    if kontrol_sonuc["eksik_opsiyonel"]:
        satirlar.append("â„¹ï¸ EKSÄ°K OPSÄ°YONEL KEY'LER (pasif kalacak):")
        for k in kontrol_sonuc["eksik_opsiyonel"]:
            satirlar.append(f"   â€¢ {k}")

    if kontrol_sonuc["uyari"]:
        satirlar.append("âš ï¸ BOT TOKEN UYARILARI:")
        for k in kontrol_sonuc["uyari"]:
            satirlar.append(f"   â€¢ {k} â€” format kontrolÃ¼ baÅŸarÄ±sÄ±z")

    if not any(kontrol_sonuc.values()):
        satirlar.append("âœ… TÃ¼m API anahtarlarÄ± tamam ve formatlarÄ± doÄŸru.")

    return "\n".join(satirlar)


def env_dogrula(env_path: str) -> Optional[str]:
    """.env dosyasÄ±nÄ± oku ve doÄŸrula. Hata varsa mesaj dÃ¶ndÃ¼r."""
    if not os.path.isfile(env_path):
        return (
            f".env dosyasÄ± bulunamadÄ±: {env_path}\n"
            "Ã‡Ã¶zÃ¼m: cp .env.example .env (Linux) veya copy .env.example .env (Windows)"
        )
    return None


if __name__ == "__main__":
    from dotenv import load_dotenv
    from pathlib import Path

    env_path = Path(__file__).parent.parent.parent / ".env"
    hata = env_dogrula(str(env_path))
    if hata:
        print(hata)
    else:
        load_dotenv(env_path, override=True)

    sonuc = key_kontrol()
    print(ozet_ver(sonuc))
