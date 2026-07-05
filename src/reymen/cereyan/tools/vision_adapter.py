# -*- coding: utf-8 -*-
"""VisionAdapter — conversation_loop.py'deki _vision_analiz'e kopru.

Motor'daki vision_tools.py, ConversationLoop._vision_analiz metodunu
bu adapter üzerinden çağırır.
"""
from __future__ import annotations
from typing import Optional


class VisionAdapter:
    """Vision tool wrapper — conversation_loop.py'deki _vision_analiz'e kopru."""

    def __init__(self):
        self._loop_ref = None

    def _vision_analiz(self, sorgu: str) -> Optional[str]:
        if self._loop_ref is None:
            return "[VISION] ConversationLoop referansi yok."
        return self._loop_ref._vision_analiz(sorgu)


# ── Bagimsiz vision analiz fonksiyonu ───────────────────────────────

def vision_analiz_yap(sorgu: str) -> Optional[str]:
    """Gorsel/resim analizi. Sorguda URL/dosya yolu varsa analiz et.
    Once DeepSeek V4 Flash (multimodal) dene, olmazsa OpenRouter vision.
    """
    import re as _re

    url_match = _re.search(
        r"https?://[^\s]+\.(jpg|jpeg|png|gif|webp|bmp)", sorgu, _re.IGNORECASE
    )
    dosya_match = None
    if not url_match:
        dosya_match = _re.search(
            r"([a-zA-Z]:\\[^\s]+\.(jpg|jpeg|png|gif|webp|bmp))",
            sorgu, _re.IGNORECASE,
        )
    if not url_match and not dosya_match:
        dosya_match = _re.search(
            r"(\.\.?/[^\s]+\.(jpg|jpeg|png|gif|webp|bmp))", sorgu, _re.IGNORECASE
        )

    if not url_match and not dosya_match:
        gorsel_kelimeler = ["foto", "fotograf", "resim", "gorsel", "goruntu",
                            "ekran", "ss", "screenshot", "image", "photo",
                            "picture", "capture", "snapshot", "ne var",
                            "bak", "goster", "analiz et", "incele"]
        if not any(k in sorgu.lower() for k in gorsel_kelimeler):
            return None
        return None

    try:
        from openai import OpenAI
        import base64, os as _os

        api_key = _os.environ.get("DEEPSEEK_API_KEY", "")
        base_url = "https://api.deepseek.com"
        model = "deepseek-v4-flash"

        resim_url = url_match.group(0) if url_match else ""
        if dosya_match:
            dosya_yol = dosya_match.group(1)
            if _os.path.exists(dosya_yol):
                with open(dosya_yol, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                resim_url = f"data:image/jpeg;base64,{img_b64}"
            else:
                return f"Dosya bulunamadi: {dosya_yol}"

        client = OpenAI(api_key=api_key, base_url=base_url)
        r = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Bu gorseli Turkce analiz et, detayli acikla."},
                        {"type": "image_url", "image_url": {"url": resim_url}},
                    ],
                }
            ],
            max_tokens=1024,
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        try:
            or_key = _os.environ.get("OPENROUTER_API_KEY", "")
            if not or_key:
                return f"DeepSeek vision hatasi: {e}.\nOPENROUTER_API_KEY ile Qwen-VL dene."
            client = OpenAI(api_key=or_key, base_url="https://openrouter.ai/api/v1")
            r = client.chat.completions.create(
                model="qwen/qwen-vl-plus:free",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Bu gorseli Turkce analiz et."},
                            {"type": "image_url", "image_url": {"url": resim_url}},
                        ],
                    }
                ],
                max_tokens=1024,
            )
            return r.choices[0].message.content.strip()
        except Exception as e2:
            return f"Gorsel analiz hatasi: {e2}"
