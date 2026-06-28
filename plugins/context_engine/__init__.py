# -*- coding: utf-8 -*-
"""plugins/context_engine/__init__.py — Baglam Motoru Plugin.

Konusma baglamini yonetir, ozet cikarir.
"""


__all__ = ['Path', 'baglam_al', 'baglam_guncelle', 'kaydet']
plugin_adi = "context_engine"
plugin_aciklamasi = "Konusma baglamini yonetme ve ozet cikarma"


def kaydet(motor):
    try:
        def baglam_al(args):
            """Mevcut konusma baglamini getir."""
            import json
            dosya = Path(__file__).parent.parent / "context" / "session_context.json"
            if dosya.exists():
                return dosya.read_text(encoding="utf-8")
            return json.dumps({"context": {}, "ozet": ""}, ensure_ascii=False, indent=2)

        def baglam_guncelle(args):
            """Konusma baglamini guncelle."""
            import json
            from pathlib import Path
            dosya = Path(__file__).parent.parent / "context" / "session_context.json"
            dosya.parent.mkdir(parents=True, exist_ok=True)
            try:
                mevcut = json.loads(dosya.read_text(encoding="utf-8"))
            except Exception:
                mevcut = {"context": {}, "ozet": ""}
            if "|" in args:
                anahtar, deger = args.split("|", 1)
                mevcut["context"][anahtar.strip()] = deger.strip()
            else:
                mevcut["ozet"] = args.strip()
            dosya.write_text(json.dumps(mevcut, ensure_ascii=False, indent=2), encoding="utf-8")
            return f"[Baglam] Guncellendi: {len(mevcut['context'])} anahtar"

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("BAGLAM_AL", baglam_al)
            motor._registry.kaydet("BAGLAM_GUNCELLE", baglam_guncelle)
    except Exception:
        pass
