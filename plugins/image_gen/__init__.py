# -*- coding: utf-8 -*-
"""
plugins/image_gen/__init__.py — Gorsel Uretim Plugin.

Araçlar: GORSEL_URET, GORSEL_DUZENLE, GORSEL_KAYDET
Provider: OpenAI DALL-E (OPENAI_API_KEY) veya Stable Diffusion local (localhost:7860).

.env'de:
    OPENAI_API_KEY=sk-... (DALL-E icin)
    SD_API_URL=http://localhost:7860 (Stable Diffusion icin)
"""

__all__ = ['Path', 'gorsel_kaydet', 'gorsel_uret', 'kaydet']
import json
import os
import re
import urllib.request

PLUGIN_ADI = "image_gen"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Yapay zeka ile gorsel uretimi"


def _dalle_uret(prompt: str, boyut: str = "1024x1024") -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key.startswith("***"):
        return "[ImageGen] OPENAI_API_KEY eksik."
    try:
        veri = json.dumps({
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": boyut,
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/images/generations",
            data=veri,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            sonuc = json.loads(r.read())
        url = sonuc["data"][0]["url"]
        return f"[ImageGen] Gorsel uretildi:\n{url}"
    except Exception as e:
        return f"[ImageGen] DALL-E hatasi: {e}"


def _sd_uret(prompt: str) -> str:
    """Stable Diffusion WebUI API."""
    sd_url = os.environ.get("SD_API_URL", "http://localhost:7860")
    try:
        veri = json.dumps({"prompt": prompt, "steps": 20, "width": 512, "height": 512}).encode()
        req = urllib.request.Request(
            f"{sd_url}/sdapi/v1/txt2img",
            data=veri,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            sonuc = json.loads(r.read())
        # Base64 gorsel kaydet
        import base64
        from pathlib import Path
        gorsel_b64 = sonuc["images"][0]
        gorsel_data = base64.b64decode(gorsel_b64)
        cikti = Path("logs") / "gorsel_cikti.png"
        cikti.parent.mkdir(exist_ok=True)
        cikti.write_bytes(gorsel_data)
        return f"[ImageGen] SD gorsel kaydedildi: {cikti}"
    except Exception as e:
        return f"[ImageGen] SD hatasi: {e}"


def kaydet(motor):
    def gorsel_uret(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        prompt = params[0] if params else ham.strip('"')
        boyut = params[1] if len(params) > 1 else "1024x1024"
        # OpenAI once, SD fallback
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key and not api_key.startswith("***"):
            return _dalle_uret(prompt, boyut)
        return _sd_uret(prompt)

    def gorsel_kaydet(ham: str) -> str:
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        url = params[0] if params else ""
        dosya = params[1] if len(params) > 1 else "gorsel.png"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ReymenAgent/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                veri = r.read()
            from pathlib import Path
            p = Path(dosya)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(veri)
            return f"[ImageGen] Kaydedildi: {dosya} ({len(veri)//1024}KB)"
        except Exception as e:
            return f"[ImageGen] Kayit hatasi: {e}"

    from plugins.kanban import _plugin_arac_kaydet
    _plugin_arac_kaydet(motor, "GORSEL_URET",   gorsel_uret)
    _plugin_arac_kaydet(motor, "GORSEL_KAYDET", gorsel_kaydet)
    print(f"[Plugin:{PLUGIN_ADI}] 2 arac kayit edildi.")
