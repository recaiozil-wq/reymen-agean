# -*- coding: utf-8 -*-
"""
apps/kod_analizi.py — Python Kod Analiz Uygulamasi.

Araçlar:
  analiz_et(dosya)      — AST tabanli metrik: fonksiyon/sinif/import sayisi
  sorunlari_bul(dosya)  — Syntax hatalari + basit stil uyarilari
  bagimliliklari_bul(dosya) — import listesi
  karmasiklik(dosya)    — Siklomatik karmasiklik tahmini (if/for/while sayisi)
  ozet_rapor(dizin)     — Tum .py dosyalari icin ozet

CLI:
    python apps/kod_analizi.py analiz main.py
    python apps/kod_analizi.py sorun main.py
    python apps/kod_analizi.py rapor .
"""
import ast
import sys
from pathlib import Path


def analiz_et(dosya: str) -> dict:
    p = Path(dosya)
    if not p.exists():
        return {"hata": f"Dosya bulunamadi: {dosya}"}
    try:
        kod = p.read_text(encoding="utf-8", errors="replace")
        agac = ast.parse(kod, filename=str(p))
    except SyntaxError as e:
        return {"hata": f"Syntax hatasi: {e}"}
    except Exception as e:
        return {"hata": str(e)}

    fonksiyonlar = []
    siniflar = []
    importlar = []

    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.FunctionDef | ast.AsyncFunctionDef):
            fonksiyonlar.append({
                "ad": dugum.name,
                "satir": dugum.lineno,
                "arg_sayisi": len(dugum.args.args),
            })
        elif isinstance(dugum, ast.ClassDef):
            siniflar.append({"ad": dugum.name, "satir": dugum.lineno})
        elif isinstance(dugum, ast.Import):
            for alias in dugum.names:
                importlar.append(alias.name)
        elif isinstance(dugum, ast.ImportFrom):
            if dugum.module:
                importlar.append(dugum.module)

    satirlar = kod.count("\n") + 1
    return {
        "dosya": str(p.resolve()),
        "satir_sayisi": satirlar,
        "fonksiyon_sayisi": len(fonksiyonlar),
        "sinif_sayisi": len(siniflar),
        "import_sayisi": len(set(importlar)),
        "fonksiyonlar": fonksiyonlar[:20],
        "siniflar": siniflar[:10],
        "importlar": list(set(importlar))[:20],
    }


def sorunlari_bul(dosya: str) -> dict:
    p = Path(dosya)
    if not p.exists():
        return {"hata": f"Dosya bulunamadi: {dosya}"}
    sorunlar = []
    try:
        kod = p.read_text(encoding="utf-8", errors="replace")
        ast.parse(kod, filename=str(p))
    except SyntaxError as e:
        sorunlar.append({"tip": "SyntaxError", "satir": e.lineno, "mesaj": str(e.msg)})
        return {"dosya": str(p), "sorunlar": sorunlar}
    except Exception as e:
        return {"hata": str(e)}

    # Stil kontrolleri
    for i, satir in enumerate(kod.splitlines(), 1):
        s = satir.rstrip()
        if len(s) > 120:
            sorunlar.append({"tip": "StilUyarisi", "satir": i,
                             "mesaj": f"Uzun satir ({len(s)} karakter)"})
        if s.endswith("  "):
            sorunlar.append({"tip": "BoslukUyarisi", "satir": i,
                             "mesaj": "Satir sonu fazla bosluk"})
        if "\t" in s and "    " in s:
            sorunlar.append({"tip": "GirdiUyarisi", "satir": i,
                             "mesaj": "Karisik tab/bosluk girintileme"})

    return {"dosya": str(p), "sorunlar": sorunlar, "sorun_sayisi": len(sorunlar)}


def bagimliliklari_bul(dosya: str) -> dict:
    p = Path(dosya)
    if not p.exists():
        return {"hata": f"Dosya bulunamadi: {dosya}"}
    try:
        kod = p.read_text(encoding="utf-8", errors="replace")
        agac = ast.parse(kod)
    except Exception as e:
        return {"hata": str(e)}

    standart = set()
    ucuncu_taraf = set()
    dahili = set()

    import sys as _sys
    stdlib = set(_sys.stdlib_module_names) if hasattr(_sys, "stdlib_module_names") else set()

    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Import):
            for alias in dugum.names:
                kok = alias.name.split(".")[0]
                _siniflandir(kok, stdlib, standart, ucuncu_taraf, dahili)
        elif isinstance(dugum, ast.ImportFrom) and dugum.module:
            kok = dugum.module.split(".")[0]
            _siniflandir(kok, stdlib, standart, ucuncu_taraf, dahili)

    return {
        "dosya": str(p),
        "standart_kutuphaneler": sorted(standart),
        "ucuncu_taraf": sorted(ucuncu_taraf),
        "dahili": sorted(dahili),
    }


def _siniflandir(kok, stdlib, standart, ucuncu_taraf, dahili):
    if kok in stdlib:
        standart.add(kok)
    elif kok.startswith(".") or (Path(__file__).parent.parent / (kok + ".py")).exists():
        dahili.add(kok)
    else:
        ucuncu_taraf.add(kok)


def karmasiklik(dosya: str) -> dict:
    p = Path(dosya)
    if not p.exists():
        return {"hata": f"Dosya bulunamadi: {dosya}"}
    try:
        kod = p.read_text(encoding="utf-8", errors="replace")
        agac = ast.parse(kod)
    except Exception as e:
        return {"hata": str(e)}

    fonksiyon_karmasikliklari = []
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.FunctionDef | ast.AsyncFunctionDef):
            skor = 1  # Temel
            for alt in ast.walk(dugum):
                if isinstance(alt, ast.If | ast.For | ast.While | ast.ExceptHandler
                               | ast.With | ast.Assert | ast.BoolOp):
                    skor += 1
            fonksiyon_karmasikliklari.append({
                "fonksiyon": dugum.name,
                "satir": dugum.lineno,
                "karmasiklik": skor,
                "seviye": "dusuk" if skor <= 5 else "orta" if skor <= 10 else "yuksek",
            })

    ortalama = (sum(f["karmasiklik"] for f in fonksiyon_karmasikliklari) /
                len(fonksiyon_karmasikliklari)) if fonksiyon_karmasikliklari else 0
    return {
        "dosya": str(p),
        "fonksiyon_sayisi": len(fonksiyon_karmasikliklari),
        "ortalama_karmasiklik": round(ortalama, 2),
        "en_karmasik": sorted(fonksiyon_karmasikliklari,
                              key=lambda x: -x["karmasiklik"])[:5],
    }


def ozet_rapor(dizin: str) -> dict:
    kok = Path(dizin)
    if not kok.exists():
        return {"hata": f"Dizin bulunamadi: {dizin}"}

    toplam = {"dosya": 0, "satir": 0, "fonksiyon": 0, "sinif": 0}
    sorunlu: list[str] = []
    buyuk_fonksiyonlar: list[dict] = []

    for dosya in kok.rglob("*.py"):
        if "venv" in dosya.parts or "__pycache__" in dosya.parts:
            continue
        toplam["dosya"] += 1
        a = analiz_et(str(dosya))
        if "hata" in a:
            sorunlu.append(str(dosya))
            continue
        toplam["satir"] += a.get("satir_sayisi", 0)
        toplam["fonksiyon"] += a.get("fonksiyon_sayisi", 0)
        toplam["sinif"] += a.get("sinif_sayisi", 0)

        k = karmasiklik(str(dosya))
        for f in k.get("en_karmasik", []):
            if f["karmasiklik"] >= 8:
                buyuk_fonksiyonlar.append({"dosya": str(dosya), **f})

    return {
        "dizin": str(kok.resolve()),
        "ozet": toplam,
        "sorunlu_dosyalar": sorunlu,
        "en_karmasik_fonksiyonlar": sorted(
            buyuk_fonksiyonlar, key=lambda x: -x["karmasiklik"])[:10],
    }


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    if len(sys.argv) < 3:
        print("Kullanim: python kod_analizi.py [analiz|sorun|bagimlilik|karmasiklik|rapor] <hedef>")
        sys.exit(1)

    komut, hedef = sys.argv[1], sys.argv[2]
    KOMUTLAR = {
        "analiz": analiz_et,
        "sorun": sorunlari_bul,
        "bagimlilik": bagimliliklari_bul,
        "karmasiklik": karmasiklik,
        "rapor": ozet_rapor,
    }
    fn = KOMUTLAR.get(komut)
    if not fn:
        print(f"Bilinmeyen komut: {komut}. Mevcut: {list(KOMUTLAR)}")
        sys.exit(1)
    print(json.dumps(fn(hedef), ensure_ascii=False, indent=2))
