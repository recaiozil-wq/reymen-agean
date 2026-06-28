# -*- coding: utf-8 -*-
"""tools/vision_tools.py — Görsel Analiz Aracı.

ReYMeN: LM Studio LLaVA modeline görsel gönderip analiz ettirir.
REST API çağrısı ile localhost:1234 üzerinden çalışır.
"""

import json
import base64
import os
from typing import Any


def run(**kwargs) -> str:
    """Görsel analiz yap.

    Args:
        gorsel_yolu (str): Zorunlu. Analiz edilecek görsel dosyasının yolu.
        soru (str, optional): Görsel hakkında sorulacak soru. Varsayılan: "Bu görselde ne görüyorsun?"

    Returns:
        str: Analiz sonucu metni.
    """
    try:
        gorsel_yolu = kwargs.get("gorsel_yolu")
        if not gorsel_yolu:
            return "[Vision]: 'gorsel_yolu' parametresi zorunludur."

        soru = kwargs.get("soru", "Bu görselde ne görüyorsun?")

        # Dosyayı kontrol et
        if not os.path.exists(gorsel_yolu):
            return f"[Vision]: Dosya bulunamadı: {gorsel_yolu}"

        # Görseli base64'e çevir
        try:
            with open(gorsel_yolu, "rb") as f:
                gorsel_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return f"[Vision]: Görsel okunamadı: {e}"

        # Dosya uzantısına göre MIME tipi belirle
        uzanti = os.path.splitext(gorsel_yolu)[1].lower()
        mime_turleri = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp"
        }
        mime_turu = mime_turleri.get(uzanti, "image/png")

        # LM Studio API'ye çağrı yap
        try:
            import requests
            payload = {
                "model": "local-model",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": soru},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_turu};base64,{gorsel_data}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 1024
            }
            r = requests.post(
                "http://localhost:1234/v1/chat/completions",
                json=payload,
                timeout=120
            )
            if r.status_code != 200:
                return f"[Vision]: API hatası (HTTP {r.status_code}): {r.text[:500]}"

            data = r.json()
            yanit = data["choices"][0]["message"]["content"]

            # Özet bilgi döndür
            rapor = {
                "gorsel": gorsel_yolu,
                "soru": soru,
                "analiz": yanit
            }
            return json.dumps(rapor, ensure_ascii=False, indent=2)

        except ImportError:
            return "[Vision]: 'requests' kütüphanesi gerekli. pip install requests"
        except requests.exceptions.ConnectionError:
            return "[Vision]: LM Studio bağlantısı kurulamadı. localhost:1234 çalışıyor mu?"
        except requests.exceptions.Timeout:
            return "[Vision]: LM Studio zaman aşımı. Model çok mu yavaş?"
        except Exception as e:
            return f"[Vision]: API çağrı hatası: {e}"

    except Exception as e:
        return f"[Vision]: Beklenmeyen hata: {e}"


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run(gorsel_yolu="ornek.png", soru="Bu görselde hangi nesneler var?"))


# ── Upstream Hermes uyumluluk stublari ─────────────────────────────────


def _determine_mime_type(path: str) -> str:
    """Dosya uzantisindan MIME tipi belirle — upstream Hermes uyumluluk."""
    ext = os.path.splitext(path)[1].lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
                ".mp4": "video/mp4", ".webm": "video/webm"}
    return mime_map.get(ext, "image/png")


def _validate_image_url(url: str) -> bool:
    """URL gecerliligini kontrol et — upstream Hermes uyumluluk."""
    return bool(url and url.startswith(("http://", "https://", "data:")))


def _detect_video_mime_type(path: str) -> str:
    """Video MIME tipi belirle — upstream Hermes uyumluluk."""
    ext = os.path.splitext(path)[1].lower()
    mime_map = {".mp4": "video/mp4", ".webm": "video/webm", ".avi": "video/x-msvideo"}
    return mime_map.get(ext, "video/mp4")


def vision_analyze_tool(image_url: str, prompt: str = "", **kwargs) -> str:
    """Gorsel analiz araci — upstream Hermes uyumluluk."""
    return run(gorsel_yolu=image_url, soru=prompt)


VIDEO_ANALYZE_SCHEMA: dict = {}
_EMBED_TARGET_BYTES: int = 4 * 1024 * 1024
_EMBED_MAX_DIMENSION: int = 2048
_MAX_BASE64_BYTES: int = 20 * 1024 * 1024
_RESIZE_TARGET_BYTES: int = 4 * 1024 * 1024
_MAX_VIDEO_BASE64_BYTES: int = 50 * 1024 * 1024
