#!/usr/bin/env python3
"""reymen_cevap_ver.py — ReYMeN conversation_loop'unu Hermes gateway'den cagir.

Kullanim:
    python reymen_cevap_ver.py "kullanici sorusu"

Cikti (stdout):
    [CEVAP] <reymen cevabi>
    veya
    [CEVAP_HATA] <hata mesaji>

Not: Bu script conversation_loop'u her seferinde yeniden baslatir.
Session state korunmaz — sadece anlik sorular icin uygundur.
"""
import json
import os
import sys
from pathlib import Path

# ReYMeN proje yolunu sys.path'e ekle
REYMEN_PROJE = Path(r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan")
REYMEN_SRC = REYMEN_PROJE / "src"
sys.path.insert(0, str(REYMEN_SRC))
sys.path.insert(0, str(REYMEN_PROJE))


def _sistem_prompu_al() -> str:
    """SOUL.md + MEMORY.md + USER.md + durum.json birlestir."""
    parcalar = ["Sen Turkce konusan bir asistansin. Tum cevaplarin Turkce olmak zorundadir.\n"]

    # SOUL.md
    soul = REYMEN_PROJE / ".hermes" / "REYMEN_SOUL.md"
    if not soul.exists():
        soul = REYMEN_PROJE / "SOUL.md"
    if soul.exists():
        parcalar.append(soul.read_text(encoding="utf-8"))

    # MEMORY.md
    bellek = REYMEN_PROJE / "MEMORY.md"
    if bellek.exists():
        parcalar.append(f"\n## BELIEK (hafiza)\n{bellek.read_text(encoding='utf-8')[:3000]}")

    # USER.md
    kullanici = REYMEN_PROJE / "USER.md"
    if kullanici.exists():
        parcalar.append(f"\n## KULLANICI\n{kullanici.read_text(encoding='utf-8')[:3000]}")

    # durum.json
    durum = REYMEN_PROJE / "durum.json"
    if durum.exists():
        try:
            with open(durum, encoding="utf-8") as f:
                parcalar.append(f"\n## DURUM (ham JSON)\n{f.read()[:2000]}")
        except Exception:
            pass

    return "\n\n".join(parcalar)


def reymen_cevapla(soru: str) -> str:
    """ReYMeN conversation_loop'unu calistir ve cevabi al."""
    try:
        from reymen.cereyan.beyin import Beyin
        from reymen.cereyan.motor import Motor
        from reymen.cereyan.conversation_loop import ConversationLoop
    except ImportError as e:
        return f"[CEVAP_HATA] ReYMeN import basarisiz: {e}"

    try:
        system_prompt = _sistem_prompu_al()

        # Config: .env'den provider/model oku veya varsayilan kullan
        config = {
            "system_prompt": system_prompt,
            "provider": os.environ.get("REYMEN_PROVIDER", "deepseek"),
            "model": os.environ.get("REYMEN_MODEL", "deepseek-v4-flash"),
        }

        beyin = Beyin(config=config)
        motor = Motor()
        motor._plugin_moduller_yukle()

        cl = ConversationLoop(motor=motor, beyin=beyin, max_tur=15)
        sonuc = cl.run_conversation(hedef=soru, provider=config["provider"])

        if sonuc.get("basarili"):
            return f"[CEVAP] {sonuc.get('yanit') or sonuc.get('sonuc', '')}"
        else:
            return f"[CEVAP_HATA] {sonuc.get('hata', 'Bilinmeyen hata')}"
    except Exception as e:
        return f"[CEVAP_HATA] {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[CEVAP_HATA] Kullanim: python reymen_cevap_ver.py \"soru\"")
        sys.exit(1)

    soru = " ".join(sys.argv[1:])
    cevap = reymen_cevapla(soru)
    print(cevap)
