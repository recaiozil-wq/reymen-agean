# -*- coding: utf-8 -*-
"""image_generation_tool.py — Resim Uretme Araci (Image Gen).

LM Studio (llava) ile gorsel analiz, DeepSeek V4 Flash ile base64
goruntu isleme. Gerektiginde Stable Diffusion API cagrisi yapar.
"""

import base64
import json
import os
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

GORSEL_DIZINI = Path(__file__).parent.parent / "output" / "gorseller"
GORSEL_DIZINI.mkdir(parents=True, exist_ok=True)


def gorsel_analiz_et(gorsel_yolu: str, soru: str = "") -> str:
    """Bir gorseli LM Studio ile analiz et.

    Args:
        gorsel_yolu: Gorsel dosyasi yolu
        soru: Gorselle ilgili soru (bos = "Bunu acikla")

    Returns:
        Analiz sonucu
    """
    dosya = Path(gorsel_yolu)
    if not dosya.exists():
        return f"[Gorsel]: Dosya bulunamadi: {gorsel_yolu}"

    if not soru:
        soru = "Bu goruntuyu detayli acikla."

    try:
        import requests

        lm_url = os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234")
        with open(dosya, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        r = requests.post(
            f"{lm_url}/v1/chat/completions",
            json={
                "model": "llava",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": soru},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"},
                        ],
                    }
                ],
                "max_tokens": 1024,
            },
            timeout=60,
        )
        if r.status_code == 200:
            return f"[Gorsel]: {r.json()['choices'][0]['message']['content']}"
        return f"[Gorsel]: Hata {r.status_code}"
    except ImportError:
        return "[Gorsel]: requests kutuphanesi yok."
    except Exception as e:
        return f"[Gorsel]: Hata: {e}"


def resim_uret(prompt: str, boyut: str = "1024x1024") -> str:
    """Yapay zeka ile resim uret.

    Args:
        prompt: Resim aciklamasi
        boyut: Cozunurluk (ornek: 1024x1024)

    Returns:
        Resim dosyasi yolu
    """
    if not prompt:
        return "[Image]: Prompt gerekli."

    from datetime import datetime
    dosya_adi = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    dosya_yolu = GORSEL_DIZINI / dosya_adi

    # Once DeepSeek V4 Flash ile dene (vision yetenegi yoksa fallback)
    try:
        import requests
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if api_key and not api_key.startswith("***"):
            r = requests.post(
                "https://api.deepseek.com/v1/images/generations",
                json={"prompt": prompt, "size": boyut},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60,
            )
            if r.status_code == 200:
                data = r.json()
                img_url = data["data"][0]["url"]
                img_data = requests.get(img_url, timeout=30).content
                dosya_yolu.write_bytes(img_data)
                return f"[Image]: Uretildi -> {dosya_yolu}"
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")

    return "[Image]: Resim uretimi icin API anahtari gerekli."


if __name__ == "__main__":
    print(resim_uret("test prompt"))
