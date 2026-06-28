# -*- coding: utf-8 -*-
"""
apps/not_defteri.py — Markdown Not Defteri.

Araçlar:
  not_ekle(baslik, icerik, etiketler)  — Yeni not olustur
  not_oku(not_id_veya_baslik)          — Not oku
  not_ara(sorgu)                       — Baslik/icerik arama
  not_listele(etiket)                  — Not listesi (filtrelenebilir)
  not_sil(not_id)                      — Not sil
  notlari_disa_aktar()                 — Tum notlar JSON

Notlar .ReYMeN/notlar/ klasorunde .md olarak saklanir.
Her not YAML frontmatter ile baslar:
    ---
    id: 1
    baslik: ...
    etiketler: python, arastirma
    olusturma: 2025-01-01T12:00:00Z
    ---

CLI:
    python apps/not_defteri.py ekle "Test notu" "Bu bir test"
    python apps/not_defteri.py listele
    python apps/not_defteri.py ara "python"
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
NOT_DIZINI = ROOT / ".ReYMeN" / "notlar"
NOT_DIZINI.mkdir(parents=True, exist_ok=True)
SAYAC_DOSYASI = NOT_DIZINI / ".sayac"


def _sonraki_id() -> int:
    if SAYAC_DOSYASI.exists():
        try:
            n = int(SAYAC_DOSYASI.read_text().strip())
        except Exception:
            n = 0
    else:
        n = 0
    n += 1
    SAYAC_DOSYASI.write_text(str(n))
    return n


def _frontmatter_ayristir(metin: str) -> tuple[dict, str]:
    """YAML frontmatter -> dict, geri kalan metin."""
    if not metin.startswith("---"):
        return {}, metin
    parcalar = metin.split("---", 2)
    if len(parcalar) < 3:
        return {}, metin
    meta: dict = {}
    for satir in parcalar[1].splitlines():
        if ":" in satir:
            k, v = satir.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, parcalar[2].strip()


def _frontmatter_olustur(meta: dict) -> str:
    satirlar = ["---"]
    for k, v in meta.items():
        satirlar.append(f"{k}: {v}")
    satirlar.append("---")
    return "\n".join(satirlar)


def not_ekle(baslik: str, icerik: str = "", etiketler: str = "") -> dict:
    not_id = _sonraki_id()
    zaman = datetime.now(timezone.utc).isoformat()
    guvenli_ad = re.sub(r"[^\w\-]", "_", baslik)[:40]
    dosya_adi = f"{not_id:04d}_{guvenli_ad}.md"
    dosya = NOT_DIZINI / dosya_adi

    meta = {
        "id": not_id,
        "baslik": baslik,
        "etiketler": etiketler,
        "olusturma": zaman,
        "guncelleme": zaman,
    }
    tam_icerik = _frontmatter_olustur(meta) + "\n\n" + icerik
    dosya.write_text(tam_icerik, encoding="utf-8")
    return {"id": not_id, "dosya": str(dosya), "baslik": baslik, "olusturma": zaman}


def not_oku(not_id: int | str) -> dict:
    hedef = _id_bul(not_id)
    if not hedef:
        return {"hata": f"Not bulunamadi: {not_id}"}
    metin = hedef.read_text(encoding="utf-8")
    meta, icerik = _frontmatter_ayristir(metin)
    return {
        "id": meta.get("id", ""),
        "baslik": meta.get("baslik", ""),
        "etiketler": meta.get("etiketler", ""),
        "olusturma": meta.get("olusturma", ""),
        "guncelleme": meta.get("guncelleme", ""),
        "icerik": icerik,
        "dosya": str(hedef),
    }


def not_guncelle(not_id: int | str, yeni_icerik: str = None, baslik: str = None,
                 etiketler: str = None) -> dict:
    hedef = _id_bul(not_id)
    if not hedef:
        return {"hata": f"Not bulunamadi: {not_id}"}
    metin = hedef.read_text(encoding="utf-8")
    meta, icerik = _frontmatter_ayristir(metin)
    meta["guncelleme"] = datetime.now(timezone.utc).isoformat()
    if baslik is not None:
        meta["baslik"] = baslik
    if etiketler is not None:
        meta["etiketler"] = etiketler
    yeni_icerik_son = yeni_icerik if yeni_icerik is not None else icerik
    tam = _frontmatter_olustur(meta) + "\n\n" + yeni_icerik_son
    hedef.write_text(tam, encoding="utf-8")
    return {"id": meta.get("id"), "guncellendi": True}


def not_ara(sorgu: str) -> list[dict]:
    desen = re.compile(re.escape(sorgu), re.IGNORECASE)
    sonuclar = []
    for dosya in sorted(NOT_DIZINI.glob("*.md")):
        metin = dosya.read_text(encoding="utf-8", errors="replace")
        meta, icerik = _frontmatter_ayristir(metin)
        if desen.search(metin):
            sonuclar.append({
                "id": meta.get("id", ""),
                "baslik": meta.get("baslik", ""),
                "etiketler": meta.get("etiketler", ""),
                "ozet": icerik[:150],
            })
    return sonuclar


def not_listele(etiket: str = "") -> list[dict]:
    notlar = []
    for dosya in sorted(NOT_DIZINI.glob("*.md")):
        metin = dosya.read_text(encoding="utf-8", errors="replace")
        meta, _ = _frontmatter_ayristir(metin)
        if etiket and etiket.lower() not in meta.get("etiketler", "").lower():
            continue
        notlar.append({
            "id": meta.get("id", ""),
            "baslik": meta.get("baslik", ""),
            "etiketler": meta.get("etiketler", ""),
            "olusturma": meta.get("olusturma", ""),
            "dosya": str(dosya),
        })
    return notlar


def not_sil(not_id: int | str) -> dict:
    hedef = _id_bul(not_id)
    if not hedef:
        return {"hata": f"Not bulunamadi: {not_id}"}
    hedef.unlink()
    return {"id": not_id, "silindi": True}


def notlari_disa_aktar() -> list[dict]:
    return [not_oku(d.stem.split("_")[0]) for d in sorted(NOT_DIZINI.glob("*.md"))]


def _id_bul(not_id: int | str) -> Path | None:
    """ID numarasina veya basliga gore dosya bul."""
    id_str = str(not_id)
    for dosya in NOT_DIZINI.glob("*.md"):
        if dosya.name.startswith(f"{id_str.zfill(4)}_"):
            return dosya
    # Baslik eslesimi
    for dosya in NOT_DIZINI.glob("*.md"):
        metin = dosya.read_text(encoding="utf-8", errors="replace")
        meta, _ = _frontmatter_ayristir(metin)
        if meta.get("baslik", "").lower() == str(not_id).lower():
            return dosya
    return None


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanim: python not_defteri.py [ekle|oku|ara|listele|sil] [...]")
        sys.exit(1)

    komut = sys.argv[1]
    if komut == "ekle":
        baslik = sys.argv[2] if len(sys.argv) > 2 else "Yeni Not"
        icerik = sys.argv[3] if len(sys.argv) > 3 else ""
        etiket = sys.argv[4] if len(sys.argv) > 4 else ""
        print(json.dumps(not_ekle(baslik, icerik, etiket), ensure_ascii=False, indent=2))
    elif komut == "oku":
        hedef = sys.argv[2] if len(sys.argv) > 2 else "1"
        r = not_oku(hedef)
        if "icerik" in r:
            print(f"# {r['baslik']}\n\n{r['icerik']}")
        else:
            print(r.get("hata"))
    elif komut == "ara":
        sorgu = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(not_ara(sorgu), ensure_ascii=False, indent=2))
    elif komut == "listele":
        etiket = sys.argv[2] if len(sys.argv) > 2 else ""
        notlar = not_listele(etiket)
        for n in notlar:
            print(f"#{n['id']}  {n['baslik']}  [{n['etiketler']}]  {n['olusturma'][:10]}")
    elif komut == "sil":
        hedef = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(not_sil(hedef), ensure_ascii=False))
    else:
        print(f"Bilinmeyen komut: {komut}")
