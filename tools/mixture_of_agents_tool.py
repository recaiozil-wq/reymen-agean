# -*- coding: utf-8 -*-
"""tools/mixture_of_agents_tool.py — Çoklu Model Harmanlama Aracı.

ReYMeN: Birden çok LLM provider'a aynı soruyu gönderir,
en tutarlı cevabı seçer. Async çağrı ile çalışır.
"""

import json
import asyncio
from difflib import SequenceMatcher
from typing import List


async def _deepseek_sor(soru: str) -> str:
    """DeepSeek API'ye soru gönder (örnek implementasyon)."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": soru}],
                "temperature": 0.3
            }
            r = await client.post("https://api.deepseek.com/v1/chat/completions", json=payload)
            data = r.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[DeepSeek Hata]: {e}"


async def _lmstudio_sor(soru: str) -> str:
    """LM Studio'ya soru gönder (localhost:1234)."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            payload = {
                "model": "local-model",
                "messages": [{"role": "user", "content": soru}],
                "temperature": 0.3
            }
            r = await client.post("http://localhost:1234/v1/chat/completions", json=payload)
            data = r.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[LMStudio Hata]: {e}"


async def _ollama_sor(soru: str) -> str:
    """Ollama'ya soru gönder (localhost:11434)."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            payload = {
                "model": "llama3",
                "messages": [{"role": "user", "content": soru}],
                "stream": False
            }
            r = await client.post("http://localhost:11434/api/chat", json=payload)
            data = r.json()
            return data["message"]["content"]
    except Exception as e:
        return f"[Ollama Hata]: {e}"


def _benzerlik_skoru(metin1: str, metin2: str) -> float:
    """İki metin arasındaki benzerlik oranını hesapla."""
    return SequenceMatcher(None, metin1, metin2).ratio()


def _en_tutarli_sec(yanitlar: dict) -> str:
    """En tutarlı yanıtı seç (diğerlerine en çok benzeyen)."""
    if not yanitlar:
        return "Hiçbir modelden yanıt alınamadı."
    if len(yanitlar) == 1:
        return list(yanitlar.values())[0]

    toplam_skor = {}
    for model1, y1 in yanitlar.items():
        toplam_skor[model1] = 0
        for model2, y2 in yanitlar.items():
            if model1 != model2:
                toplam_skor[model1] += _benzerlik_skoru(y1, y2)

    en_iyi = max(toplam_skor, key=toplam_skor.get)
    return yanitlar[en_iyi]


async def _sorulari_gonder(soru: str, modeller: list) -> dict:
    """Tüm modellere async soru gönder."""
    model_map = {
        "deepseek": _deepseek_sor,
        "lmstudio": _lmstudio_sor,
        "ollama": _ollama_sor,
    }

    gorevler = {}
    for m in modeller:
        m_adi = m.lower()
        if m_adi in model_map:
            gorevler[m_adi] = model_map[m_adi](soru)

    if not gorevler:
        return {}

    sonuclar = await asyncio.gather(*gorevler.values(), return_exceptions=True)
    yanitlar = {}
    for i, (model_adi, _) in enumerate(gorevler.items()):
        sonuc = sonuclar[i]
        if isinstance(sonuc, Exception):
            yanitlar[model_adi] = f"[Hata]: {sonuc}"
        else:
            yanitlar[model_adi] = sonuc
    return yanitlar


def run(**kwargs) -> str:
    """Çoklu model harmanlama çalıştır.

    Args:
        soru (str): Zorunlu. Gönderilecek soru.
        modeller (list, optional): Kullanılacak modeller. Varsayılan: ["deepseek", "lmstudio"]

    Returns:
        str: En tutarlı yanıt metni.
    """
    try:
        soru = kwargs.get("soru")
        if not soru:
            return "[MixtureOfAgents]: 'soru' parametresi zorunludur."

        modeller = kwargs.get("modeller", ["deepseek", "lmstudio"])

        yanitlar = asyncio.run(_sorulari_gonder(soru, modeller))

        rapor = {}
        for model, yanit in yanitlar.items():
            rapor[model] = yanit[:200] + "..." if len(yanit) > 200 else yanit

        en_tutarli = _en_tutarli_sec(yanitlar)

        sonuc = {
            "tum_yanitlar": rapor,
            "secim": en_tutarli,
            "modeller": modeller
        }
        return json.dumps(sonuc, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"[MixtureOfAgents]: Beklenmeyen hata: {e}"


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run(soru="Türkiye'nin başkenti neresidir?", modeller=["deepseek", "lmstudio"]))
