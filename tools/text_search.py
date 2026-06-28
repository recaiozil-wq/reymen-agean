# -*- coding: utf-8 -*-
"""text_search.py — Metin içinde regex arama ve dosya desen bulma aracı.

Dosya veya string içinde regex ile arama yapar.
"""

import json
import re
from pathlib import Path


TOOL_META = {
    "aciklama": "Metin/dosya içinde regex araması yapar ve eşleşmeleri döndürür.",
    "parametreler": [
        {"ad": "kaynak", "tip": "str", "aciklama": "Aranacak metin veya dosya yolu (d: ile başlarsa dosya yolu olarak alınır)."},
        {"ad": "desen", "tip": "str", "aciklama": "Regex deseni."},
        {"ad": "ignore_case", "tip": "bool", "aciklama": "Büyük/küçük harf duyarsız (varsayılan: false)."},
    ],
    "ornek": 'TEXT_SEARCH(kaynak="d:veri.txt", desen="hata.*kritik", ignore_case=true)',
    "kategori": "data_processing",
}


def run(kaynak: str = "", desen: str = "", ignore_case: bool = False, *args, **kwargs) -> str:
    """Metin veya dosyada regex araması yap.

    Args:
        kaynak: Aranacak metin. 'd:' ile başlarsa dosya yolu.
        desen: Regex deseni.
        ignore_case: Büyük/küçük harf duyarsız arama.

    Returns:
        JSON: eşleşme sayısı ve detaylar.
    """
    if not desen:
        return json.dumps({"hata": "desen parametresi zorunludur."}, ensure_ascii=False)
    if not kaynak:
        return json.dumps({"hata": "kaynak parametresi zorunludur."}, ensure_ascii=False)

    try:
        flags = re.IGNORECASE if ignore_case else 0
        pattern = re.compile(desen, flags)
    except re.error as e:
        return json.dumps({"hata": f"Gecersiz regex: {str(e)}"}, ensure_ascii=False)

    # Dosyadan oku
    if kaynak.startswith("d:") or kaynak.startswith("D:"):
        dosya_yolu = kaynak[2:].strip()
        yol = Path(dosya_yolu)
        if not yol.exists():
            return json.dumps({"hata": f"Dosya bulunamadi: {dosya_yolu}"}, ensure_ascii=False)
        try:
            icerik = yol.read_text(encoding="utf-8", errors="replace")
            satirlar = icerik.split("\n")
        except Exception as e:
            return json.dumps({"hata": f"Dosya okuma hatasi: {str(e)}"}, ensure_ascii=False)
    else:
        icerik = kaynak
        satirlar = icerik.split("\n")

    eslesmeler = []
    for i, satir in enumerate(satirlar, 1):
        for match in pattern.finditer(satir):
            eslesmeler.append({
                "satir": i,
                "eslesen": match.group(),
                "konum": match.start(),
                "satir_icerik": satir.strip()[:200],
            })

    return json.dumps({
        "desen": desen,
        "ignore_case": ignore_case,
        "toplam_satir": len(satirlar),
        "eslesme_sayisi": len(eslesmeler),
        "eslesmeler": eslesmeler[:100],  # Maks 100 sonuç
        "daha_fazla": len(eslesmeler) > 100,
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("=== METINDE ARA ===")
    print(run(
        kaynak="Merhaba dunya\nBu bir test metnidir\nHATA: kritik sorun\nuyari: onemsiz",
        desen="(HATA|hata|Hata)",
        ignore_case=False
    ))

    print("\n=== BUYUK/KUCUK HARF DUYARSIZ ===")
    print(run(
        kaynak="Merhaba dunya\nBu bir test metnidir\nHATA: kritik sorun\nuyari: onemsiz",
        desen="hata",
        ignore_case=True
    ))
