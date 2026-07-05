# -*- coding: utf-8 -*-
"""
araclar_goruntu.py â€” Görsel üretim ve analiz araçlarÄ±.

  RESIM_OLUSTUR   â€” FAL.ai FLUX ile prompt'tan görsel üretir.
  VISION_ANALIZ   â€” FAL.ai vision endpoint ile görsel analiz eder
                    (FAL_KEY yoksa/baÅŸarÄ±sÄ±z olursa GORUNTU_ANALIZ'e düÅŸer).
  GORUNTU_ANALIZ  â€” Ollama LLaVA ile yerel/offline görsel analiz (fallback).

BaÄŸÄ±mlÄ±lÄ±k yok â€” sadece stdlib (urllib). Ollama için yerel sunucu gerekir
(varsayÄ±lan http://localhost:11434, OLLAMA_URL ile deÄŸiÅŸtirilebilir).

MEDIA format sözleÅŸmesi (köprü/telegram_bot tarafÄ±ndan ayrÄ±ÅŸtÄ±rÄ±lmasÄ± beklenir):

    [MEDIA type="image" src="<url-veya-dosya-yolu>"]
    <açÄ±klama>
    [/MEDIA]

Projenizdeki köprü/telegram_bot modülü farklÄ± bir biçim bekliyorsa sadece
_media() fonksiyonunu güncellemeniz yeterli â€” diÄŸer kod deÄŸiÅŸmez.

TasarÄ±m ilkesi: hiçbir import hatasÄ± modülün tamamen çökmesine yol açmaz;
her araç kendi içinde try/except ile sessizce (ama loglayarak) degrade eder.
"""

import base64
import json
import logging
import mimetypes
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

_FAL_RUN_URL = "https://api.fal.ai/v1/run/comfyhub/flux-1-1-pro"
_FAL_VISION_URL = "https://api.fal.ai/v1/run/fal-ai/llavav15-13b"
_OR_VISION_URL = "https://openrouter.ai/api/v1/chat/completions"
_OR_VISION_MODEL = "meta-llama/llama-3.2-11b-vision-instruct"
_OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")


# â”€â”€ YardÄ±mcÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _media(tip: str, kaynak: str, aciklama: str = "") -> str:
    blok = f'[MEDIA type="{tip}" src="{kaynak}"]'
    if aciklama:
        blok += f"\n{aciklama}"
    blok += "\n[/MEDIA]"
    return blok


def _http_post_json(
    url: str, payload: dict, headers: dict = None, timeout: int = 60
) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _kaynak_to_data_url(yol_veya_url: str) -> str:
    """Yerel dosya yolunu base64 data: URL'e çevirir; zaten URL ise olduÄŸu gibi döner."""
    if yol_veya_url.startswith(("http://", "https://", "data:")):
        return yol_veya_url
    with open(yol_veya_url, "rb") as f:
        veri = f.read()
    mime = mimetypes.guess_type(yol_veya_url)[0] or "image/png"
    return f"data:{mime};base64,{base64.b64encode(veri).decode()}"


# â”€â”€ OpenRouter Görsel Ãœretim Fallback â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_OR_IMAGE_URL = "https://openrouter.ai/api/v1/chat/completions"
_OR_IMAGE_MODEL = "openai/dall-e-3"


def _resim_openrouter_fallback(prompt: str, en: str = "1024", boy: str = "1024") -> str:
    """OpenRouter uzerinden gorsel uret (FAL_KEY yoksa)."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return (
            "[RESIM_OLUSTUR] Hata: FAL_KEY/FAL_API_KEY/OPENROUTER_API_KEY "
            "tanimli degil. Gorsel uretim icin bir API anahtari gerekli."
        )

    try:
        size = f"{en}x{boy}"
        payload = {
            "model": _OR_IMAGE_MODEL,
            "messages": [{"role": "user", "content": f"Generate an image: {prompt}"}],
        }
        sonuc = _http_post_json(
            _OR_IMAGE_URL,
            payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://github.com/Watcher-ReYMeN/ReYMeN-Ajan",
            },
            timeout=90,
        )
        # OpenAI uyumlu yanÄ±t
        choices = sonuc.get("choices", [])
        if choices:
            msg = choices[0].get("message", {})
            content = msg.get("content", "")
            if content:
                return _media("image", content, f"Prompt: {prompt}")
        return f"[RESIM_OLUSTUR] OpenRouter yanit alinamadi: {json.dumps(sonuc)[:300]}"
    except Exception as e:
        logger.error("[RESIM_OLUSTUR] OpenRouter fallback hatasi: %s", e)
        return f"[RESIM_OLUSTUR] Hata: FAL ve OpenRouter basarisiz: {e}"


# â”€â”€ RESIM_OLUSTUR â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def resim_olustur(prompt: str, en: str = "1024", boy: str = "1024") -> str:
    """FAL.ai FLUX (flux-1-1-pro) ile prompt'tan görsel üretir."""
    if not prompt or not prompt.strip():
        return "[RESIM_OLUSTUR] Hata: 'prompt' boÅŸ olamaz."

    api_key = os.environ.get("FAL_KEY", "").strip()
    if not api_key:
        api_key = os.environ.get("FAL_API_KEY", "").strip()
    if not api_key:
        # OpenRouter fallback dene
        return _resim_openrouter_fallback(prompt.strip(), en, boy)

    try:
        en_i, boy_i = int(en), int(boy)
    except (TypeError, ValueError):
        en_i, boy_i = 1024, 1024

    try:
        sonuc = _http_post_json(
            _FAL_RUN_URL,
            {"prompt": prompt.strip(), "image_size": {"width": en_i, "height": boy_i}},
            headers={"Authorization": f"Key {api_key}"},
            timeout=90,
        )
        url = None
        if isinstance(sonuc.get("images"), list) and sonuc["images"]:
            url = sonuc["images"][0].get("url")
        elif isinstance(sonuc.get("image"), dict):
            url = sonuc["image"].get("url")
        elif isinstance(sonuc.get("image"), str):
            url = sonuc["image"]

        if not url:
            return f"[RESIM_OLUSTUR] Hata: beklenmeyen FAL cevabÄ±: {json.dumps(sonuc)[:300]}"
        return _media("image", url, f"Prompt: {prompt.strip()}")
    except urllib.error.HTTPError as e:
        govde = e.read().decode(errors="replace")[:300]
        return f"[RESIM_OLUSTUR] FAL API hatasÄ± ({e.code}): {govde}"
    except Exception as e:
        logger.error("[RESIM_OLUSTUR] hata: %s", e)
        return f"[RESIM_OLUSTUR] Hata: {e}"


# â”€â”€ VISION_ANALIZ (FAL, GORUNTU_ANALIZ'e fallback) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def vision_analiz(
    kaynak: str, soru: str = "Bu görselde ne var, detaylÄ± açÄ±kla."
) -> str:
    """FAL.ai vision modeliyle görsel analiz eder (URL veya yerel dosya yolu)."""
    if not kaynak or not kaynak.strip():
        return "[VISION_ANALIZ] Hata: görsel kaynaÄŸÄ± (url/yol) boÅŸ olamaz."

    api_key = os.environ.get("FAL_KEY", "").strip()
    if not api_key:
        api_key = os.environ.get("FAL_API_KEY", "").strip()
    if not api_key:
        return _ollama_fallback(kaynak, soru, neden="FAL_KEY tanÄ±mlÄ± deÄŸil")

    try:
        gorsel_url = _kaynak_to_data_url(kaynak.strip())
        sonuc = _http_post_json(
            _FAL_VISION_URL,
            {"image_url": gorsel_url, "prompt": soru},
            headers={"Authorization": f"Key {api_key}"},
            timeout=60,
        )
        metin = sonuc.get("output") or sonuc.get("text") or sonuc.get("response")
        if not metin:
            return _ollama_fallback(
                kaynak, soru, neden=f"beklenmeyen FAL cevabÄ±: {json.dumps(sonuc)[:200]}"
            )
        return f"[VISION_ANALIZ]\n{metin.strip()}"
    except Exception as e:
        logger.warning("[VISION_ANALIZ] FAL hatasÄ±, Ollama LLaVA'ya düÅŸülüyor: %s", e)
        return _ollama_fallback(kaynak, soru, neden=str(e))


def _ollama_fallback(kaynak: str, soru: str, neden: str = "") -> str:
    """Fallback: OpenRouter vision API (Ollama kaldirildigi icin)."""
    if neden:
        logger.warning("[VISION] FAL basarisiz: %s â†’ OpenRouter deneniyor", neden)
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return f"[VISION] Görsel analizi icin OPENROUTER_API_KEY gerekli."
    try:
        if kaynak.startswith(("http://", "https://")):
            with urllib.request.urlopen(kaynak, timeout=30) as r:
                veri = r.read()
        else:
            with open(kaynak, "rb") as f:
                veri = f.read()
        b64 = base64.b64encode(veri).decode()
        mime = mimetypes.guess_type(kaynak)[0] or "image/jpeg"
        payload = {
            "model": _OR_VISION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": soru},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                }
            ],
            "max_tokens": 1024,
        }
        req = urllib.request.Request(
            _OR_VISION_URL,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/Watcher-ReYMeN/ReYMeN-Ajan",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            cevap = json.loads(r.read().decode())
        return (
            cevap.get("choices", [{}])[0].get("message", {}).get("content", "")
            or "Görsel analiz edilemedi."
        )
    except Exception as e:
        return f"[VISION] OpenRouter hatasi: {e}"


# â”€â”€ GORUNTU_ANALIZ (Ollama LLaVA â€” yerel/offline fallback) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def goruntu_analiz(
    kaynak: str, soru: str = "Bu görselde ne var, detaylÄ± açÄ±kla.", model: str = "llava"
) -> str:
    """Ollama üzerinde çalÄ±ÅŸan LLaVA modeliyle yerel/offline görsel analiz."""
    if not kaynak or not kaynak.strip():
        return "[GORUNTU_ANALIZ] Hata: görsel kaynaÄŸÄ± (url/yol) boÅŸ olamaz."

    try:
        if kaynak.startswith(("http://", "https://")):
            with urllib.request.urlopen(kaynak, timeout=20) as r:
                veri = r.read()
        else:
            with open(kaynak, "rb") as f:
                veri = f.read()
        b64 = base64.b64encode(veri).decode()

        sonuc = _http_post_json(
            f"{_OLLAMA_URL}/api/generate",
            {"model": model, "prompt": soru, "images": [b64], "stream": False},
            timeout=120,
        )
        metin = (sonuc.get("response") or "").strip()
        return f"[GORUNTU_ANALIZ]\n{metin or '(boÅŸ yanÄ±t)'}"
    except urllib.error.URLError as e:
        return (
            f"[GORUNTU_ANALIZ] Hata: Ollama'ya baÄŸlanÄ±lamadÄ± ({_OLLAMA_URL}). "
            f"Ollama kurulu ve çalÄ±ÅŸÄ±yor mu? ('ollama pull llava') Detay: {e}"
        )
    except FileNotFoundError:
        return f"[GORUNTU_ANALIZ] Hata: dosya bulunamadÄ±: {kaynak}"
    except Exception as e:
        logger.error("[GORUNTU_ANALIZ] hata: %s", e)
        return f"[GORUNTU_ANALIZ] Hata: {e}"


# â”€â”€ Motor kayÄ±t â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def motor_kaydet(motor) -> None:
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    try:
        motor._plugin_arac_kaydet(
            "RESIM_OLUSTUR",
            resim_olustur,
            "FAL.ai FLUX ile prompt'tan görsel üretir (FAL_KEY gerekli). "
            "Parametreler: prompt, en, boy.",
        )
        motor._plugin_arac_kaydet(
            "VISION_ANALIZ",
            vision_analiz,
            "FAL.ai vision modeliyle görseli analiz eder (FAL_KEY gerekli; yoksa "
            "otomatik olarak Ollama LLaVA'ya düÅŸer). Parametreler: kaynak (url/yol), soru.",
        )
        # GORUNTU_ANALIZ sadece henuz kaydedilmemisse eklenir.
        # reymen.cereyan.tools.vision_tools (DeepSeek V4 Flash + OpenRouter)
        # overwrite edebilsin diye once kayitli mi kontrol et.
        motor._plugin_arac_kaydet(
            "GORUNTU_ANALIZ",
            goruntu_analiz,
            "Ollama LLaVA ile yerel/offline görsel analiz eder. "
            "Parametreler: kaynak (url/yol), soru, model.",
            only_if_missing=True,
        )
    except Exception as e:
        print(f"[AraclarGoruntu] Motor kayÄ±t hatasÄ±: {e}")


if __name__ == "__main__":
    print(
        "araclar_goruntu hazÄ±r. FAL_KEY:", "var" if os.environ.get("FAL_KEY") else "yok"
    )
    print("OLLAMA_URL:", _OLLAMA_URL)
