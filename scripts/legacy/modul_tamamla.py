#!/usr/bin/env python3
"""modul_tamamla.py — coverage_durumu.core TEK kaynak.
tamamlanan_moduller otomatik senkron.

Kullanim:
    python modul_tamamla.py <modul> <coverage> <test_sayisi> <aciklama>
    python modul_tamamla.py --sync
    python modul_tamamla.py --list
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

DURUM = Path(__file__).resolve().parent / "durum.json"


def _yukle():
    with open(DURUM, encoding="utf-8") as f:
        return json.load(f)


def _kaydet(data):
    data["son_guncelleme"] = datetime.now(timezone.utc).astimezone().isoformat()
    with open(DURUM, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _sync(data):
    """tamamlanan_moduller'i coverage_durumu.core'dan yeniden olustur."""
    core = data.get("coverage_durumu", {}).get("core", {})
    data["tamamlanan_moduller"] = {}
    for mod, info in core.items():
        if isinstance(info, dict) and "coverage" in info:
            data["tamamlanan_moduller"][mod] = {
                "tamamlandi": True,
                "tarih": info.get("guncelleme", "")[:10],
                "coverage": info["coverage"],
                "test_sayisi": info.get("test_sayisi", 0),
                "core_durumu": info.get("core_durumu", "AKTIF"),
                "aciklama": info.get("eksik_analizi", {}).get("not", ""),
            }
    return data


def modul_ekle(modul, coverage, test_sayisi, aciklama):
    """coverage_durumu.core'a yazar, tamamlanan_moduller otomatik senkron."""
    data = _yukle()
    if "coverage_durumu" not in data:
        data["coverage_durumu"] = {"genel": {}, "core": {}}
    if "core" not in data["coverage_durumu"]:
        data["coverage_durumu"]["core"] = {}

    data["coverage_durumu"]["core"][modul] = {
        "coverage": f"{coverage}%",
        "durum": "TAMAMLANDI",
        "test_sayisi": test_sayisi,
        "core_durumu": "KAPANDI",
        "guncelleme": datetime.now(timezone.utc).astimezone().isoformat(),
    }

    data = _sync(data)
    _kaydet(data)
    print(f"OK {modul}: coverage_durumu.core -> tamamlanan_moduller senkron (%{coverage}, {test_sayisi} test)")
    return True


def sync():
    data = _yukle()
    once = len(data.get("tamamlanan_moduller", {}))
    data = _sync(data)
    son = len(data["tamamlanan_moduller"])
    _kaydet(data)
    print(f"OK sync: {once} -> {son} modul")


def listele():
    data = _yukle()
    core = data.get("coverage_durumu", {}).get("core", {})
    tm = data.get("tamamlanan_moduller", {})
    print("coverage_durumu.core (KAYNAK):")
    for mod in sorted(core):
        i = core[mod]
        print(f"  {mod:25s} %{i.get('coverage','?'):>8s}  {i.get('test_sayisi',0)} test")
    print()
    print("tamamlanan_moduller (SENKRON):")
    for mod in sorted(tm):
        i = tm[mod]
        print(f"  {mod:25s} %{i.get('coverage','?'):>8s}  {i.get('test_sayisi',0)} test")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--sync":
        sync()
    elif len(sys.argv) >= 2 and sys.argv[1] == "--list":
        listele()
    elif len(sys.argv) >= 5:
        modul_ekle(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
    else:
        print(__doc__.strip())
        sys.exit(1)
