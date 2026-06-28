# -*- coding: utf-8 -*-
"""plugins/observability/__init__.py — Gozlemlenebilirlik Plugin.

Token sayimi, latency olcumu, log toplama. JSONL log formati.
"""


__all__ = ['Path', 'kaydet', 'obs_log', 'obs_metrik', 'obs_rapor']
plugin_adi = "observability"
plugin_aciklamasi = "Token sayimi, latency olcumu ve log toplama"


def kaydet(motor):
    try:
        import json
        import time
        from pathlib import Path

        LOG_DOSYASI = Path(__file__).parent.parent / "logs" / "observability.jsonl"

        def obs_log(args):
            """Bir log kaydi ekle (JSONL formatinda)."""
            LOG_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
            kayit = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "message": args.strip(),
                "level": "INFO",
            }
            with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
                f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
            return f"[OBS] Log kaydedildi: {len(args.strip())} karakter"

        def obs_metrik(args):
            """Token sayimi ve latency metrigi ekle."""
            import time
            LOG_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
            try:
                veri = json.loads(args) if args.strip() else {}
            except Exception:
                veri = {"raw": args.strip()}
            veri["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
            veri["type"] = "metric"
            with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
                f.write(json.dumps(veri, ensure_ascii=False) + "\n")
            return f"[OBS] Metrik kaydedildi: {len(veri)} alan"

        def obs_rapor(args):
            """Loglardan ozet rapor olustur."""
            if not LOG_DOSYASI.exists():
                return "[OBS] Henuz log kaydi yok."
            satirlar = LOG_DOSYASI.read_text(encoding="utf-8").strip().split("\n")
            toplam = len(satirlar)
            metrikler = [s for s in satirlar if '"metric"' in s]
            return f"[OBS] Rapor: {toplam} kayit (metrik: {len(metrikler)})"

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("OBS_LOG", obs_log)
            motor._registry.kaydet("OBS_METRIK", obs_metrik)
            motor._registry.kaydet("OBS_RAPOR", obs_rapor)
    except Exception:
        pass
