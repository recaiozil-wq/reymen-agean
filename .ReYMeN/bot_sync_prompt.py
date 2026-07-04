#!/usr/bin/env python3
"""Tum bot ai_bot_*.json dosyalarinin sistem_prompt'una ortak durum.json yonlendirmesi ekle."""

import json
from pathlib import Path

ORTAK_YONLENDIRME = """

## ORTAK DURUM DOSYASI (TUM BOTLAR OKUR)
Proje durumu icin SU KAYNAGI kullan, kendi hafizandan degil:
- dosya: durum.json (proje kokunde)
- komut: python -m reymen.sistem.durum_paylas --rapor
- komut: python -m reymen.sistem.durum_paylas --oku

'ReYMeN vs ReYMeN eksik yonler' sorulursa:
1. ONCE durum.json'u oku (python -m reymen.sistem.durum_paylas --rapor)
2. Guncel veriye gore cevap ver
3. ORNEK: '24/29 ozellik tamam (%83). Eksikler: Image Gen, Voice/TTS/STT, Video Gen, Plugin Hot-reload, ACP, HITL, Skills Marketplace, Docker.'
"""

REYDIR = Path(__file__).resolve().parent  # .ReYMeN dizini

for bot_dosya in REYDIR.glob("ai_bot_*.json"):
    print(f"\n=== {bot_dosya.name} ===")
    try:
        with open(bot_dosya, "r", encoding="utf-8") as f:
            data = json.load(f)

        eski_prompt = data.get("sistem_prompt", "")
        print(f"ESKI prompt sonu: ...{eski_prompt[-100:]}")

        if "ORTAK DURUM DOSYASI" not in eski_prompt:
            data["sistem_prompt"] = eski_prompt + ORTAK_YONLENDIRME
            with open(bot_dosya, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ GUNCELLENDI")
        else:
            print("⏭️ Zaten var, atlandi")
    except Exception as e:
        print(f"❌ HATA: {e}")
