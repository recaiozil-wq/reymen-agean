# -*- coding: utf-8 -*-
"""plugins/teams_pipeline/__init__.py — Teams Toplanti Pipeline Plugin.

Toplanti transkripti, ozet, aksiyon maddeleri.
"""


__all__ = ['Path', 'kaydet', 'pipe_calistir', 'pipe_durum']
plugin_adi = "teams_pipeline"
plugin_aciklamasi = "Teams toplanti transkripti, ozet ve aksiyon maddeleri cikarma"


def kaydet(motor):
    try:
        import json
        import time
        from pathlib import Path

        PIPE_DIZINI = Path(__file__).parent.parent / "data" / "pipeline"

        def pipe_calistir(args):
            """Pipeline'i calistir: transkript al, ozet cikar, aksiyon maddeleri olustur."""
            PIPE_DIZINI.mkdir(parents=True, exist_ok=True)
            kayit = {
                "id": str(int(time.time())),
                "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "ham_metin": args.strip(),
                "durum": "isleniyor",
            }
            # Basit ozet cikarma
            kelimeler = args.strip().split()
            kayit["ozet"] = " ".join(kelimeler[:50]) + ("..." if len(kelimeler) > 50 else "")
            # Basit aksiyon maddeleri tespiti
            aksiyonlar = [w for w in kelimeler if w.lower().startswith(("yap", "gerceklestir", "tamamla", "gönder", "hazirla"))]
            kayit["aksiyon_maddeleri"] = aksiyonlar[:10]
            kayit["durum"] = "tamamlandi"
            dosya = PIPE_DIZINI / f"pipeline_{kayit['id']}.json"
            dosya.write_text(json.dumps(kayit, ensure_ascii=False, indent=2), encoding="utf-8")
            return f"[Pipe] Pipeline calisti: {kayit['id']} | {len(aksiyonlar)} aksiyon maddesi"

        def pipe_durum(args):
            """Pipeline calisma durumunu goster."""
            if not PIPE_DIZINI.exists():
                return "[Pipe] Henuz pipeline kaydi yok."
            dosyalar = list(PIPE_DIZINI.glob("pipeline_*.json"))
            if not dosyalar:
                return "[Pipe] Henuz pipeline kaydi yok."
            son = sorted(dosyalar)[-1]
            veri = json.loads(son.read_text(encoding="utf-8"))
            return (
                f"[Pipe] Son pipeline: {veri['id']} | Durum: {veri['durum']} | "
                f"Ozet: {veri.get('ozet', '')[:80]}"
            )

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("PIPE_CALISTIR", pipe_calistir)
            motor._registry.kaydet("PIPE_DURUM", pipe_durum)
    except Exception:
        pass
