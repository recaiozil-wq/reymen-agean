# -*- coding: utf-8 -*-
"""
apps/dosya_duzenleyici.py — Dosya Duzenleyici Uygulamasi.

Araçlar:
  oku(dosya)                    — Dosya oku
  yaz(dosya, icerik)            — Dosya yaz (yedek alir)
  ekle(dosya, icerik)           — Dosya sonuna ekle
  ara(dizin, sorgu)             — Dosyalarda metin ara
  yedekle(dosya)                — .bak uzantisi ile yedek al
  listele(dizin, uzanti)        — Dizin listele
  sil(dosya)                    — Dosya sil (yedek alarak)
  yeniden_adlandir(eski, yeni)  — Yeniden adlandir

CLI:
    python apps/dosya_duzenleyici.py oku C:/tmp/dosya.txt
    python apps/dosya_duzenleyici.py ara C:/tmp ".py"
"""
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def oku(dosya: str, kodlama: str = "utf-8") -> dict:
    p = Path(dosya)
    if not p.exists():
        return {"hata": f"Dosya bulunamadi: {dosya}"}
    try:
        icerik = p.read_text(encoding=kodlama, errors="replace")
        return {
            "dosya": str(p.resolve()),
            "icerik": icerik,
            "satir_sayisi": icerik.count("\n") + 1,
            "karakter_sayisi": len(icerik),
        }
    except Exception as e:
        return {"hata": str(e)}


def yaz(dosya: str, icerik: str, yedekle_once: bool = True,
        kodlama: str = "utf-8") -> dict:
    p = Path(dosya)
    yedek = None
    if yedekle_once and p.exists():
        sonuc = yedekle(dosya)
        yedek = sonuc.get("yedek")
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(icerik, encoding=kodlama)
        return {"dosya": str(p.resolve()), "yazildi": True, "yedek": yedek}
    except Exception as e:
        return {"hata": str(e)}


def ekle(dosya: str, icerik: str, kodlama: str = "utf-8") -> dict:
    p = Path(dosya)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding=kodlama) as f:
            f.write(icerik)
        return {"dosya": str(p.resolve()), "eklendi": True}
    except Exception as e:
        return {"hata": str(e)}


def ara(dizin: str, sorgu: str, uzanti: str = "", limit: int = 50) -> dict:
    """Dizinde metin ara (basit string match)."""
    kok = Path(dizin)
    if not kok.exists():
        return {"hata": f"Dizin bulunamadi: {dizin}"}
    eslesme = []
    desen = re.compile(re.escape(sorgu), re.IGNORECASE)
    try:
        for dosya in kok.rglob("*"):
            if not dosya.is_file():
                continue
            if uzanti and dosya.suffix != uzanti:
                continue
            if len(eslesme) >= limit:
                break
            try:
                for i, satir in enumerate(dosya.read_text(encoding="utf-8",
                                                           errors="replace").splitlines(), 1):
                    if desen.search(satir):
                        eslesme.append({
                            "dosya": str(dosya),
                            "satir": i,
                            "icerik": satir.strip()[:120],
                        })
                        if len(eslesme) >= limit:
                            break
            except Exception:
                continue
        return {"sorgu": sorgu, "bulunanlar": eslesme, "toplam": len(eslesme)}
    except Exception as e:
        return {"hata": str(e)}


def yedekle(dosya: str) -> dict:
    p = Path(dosya)
    if not p.exists():
        return {"hata": f"Dosya bulunamadi: {dosya}"}
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    yedek_yolu = p.with_suffix(f".{zaman}.bak")
    try:
        shutil.copy2(str(p), str(yedek_yolu))
        return {"dosya": str(p), "yedek": str(yedek_yolu)}
    except Exception as e:
        return {"hata": str(e)}


def listele(dizin: str, uzanti: str = "", gizli: bool = False) -> dict:
    kok = Path(dizin)
    if not kok.exists():
        return {"hata": f"Dizin bulunamadi: {dizin}"}
    try:
        dosyalar = []
        for p in sorted(kok.iterdir()):
            if not gizli and p.name.startswith("."):
                continue
            if uzanti and p.is_file() and p.suffix != uzanti:
                continue
            dosyalar.append({
                "ad": p.name,
                "tip": "dizin" if p.is_dir() else "dosya",
                "boyut": p.stat().st_size if p.is_file() else 0,
            })
        return {"dizin": str(kok.resolve()), "icerik": dosyalar}
    except Exception as e:
        return {"hata": str(e)}


def sil(dosya: str, yedekle_once: bool = True) -> dict:
    p = Path(dosya)
    if not p.exists():
        return {"hata": f"Dosya bulunamadi: {dosya}"}
    yedek = None
    if yedekle_once:
        sonuc = yedekle(dosya)
        yedek = sonuc.get("yedek")
    try:
        p.unlink()
        return {"dosya": str(p), "silindi": True, "yedek": yedek}
    except Exception as e:
        return {"hata": str(e)}


def yeniden_adlandir(eski: str, yeni: str) -> dict:
    src = Path(eski)
    dst = Path(yeni)
    if not src.exists():
        return {"hata": f"Kaynak bulunamadi: {eski}"}
    try:
        src.rename(dst)
        return {"eski": str(src), "yeni": str(dst), "basarili": True}
    except Exception as e:
        return {"hata": str(e)}


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    if len(sys.argv) < 3:
        print("Kullanim: python dosya_duzenleyici.py [oku|ara|listele|yedekle|sil] <hedef> [...]")
        sys.exit(1)

    komut = sys.argv[1]
    hedef = sys.argv[2]

    if komut == "oku":
        r = oku(hedef)
        print(r.get("icerik", r.get("hata", "")))
    elif komut == "ara":
        sorgu = sys.argv[3] if len(sys.argv) > 3 else ""
        r = ara(hedef, sorgu)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif komut == "listele":
        r = listele(hedef)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif komut == "yedekle":
        r = yedekle(hedef)
        print(json.dumps(r, ensure_ascii=False))
    elif komut == "sil":
        r = sil(hedef)
        print(json.dumps(r, ensure_ascii=False))
    else:
        print(f"Bilinmeyen komut: {komut}")
