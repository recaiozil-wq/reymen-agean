# -*- coding: utf-8 -*-
"""dizin_listele.py — Dizin listeleme aracı.

Verilen dizin veya mevcut dizini listeler.
"""

import json
import os
from pathlib import Path


def run(dizin: str = ".", *args, **kwargs) -> str:
    """Dizin içeriğini listele.

    Args:
        dizin: Listelenecek dizin yolu (varsayılan: ".")

    Returns:
        JSON formatında dosya ve klasör listesi
    """
    try:
        yol = Path(dizin or ".").resolve()
        if not yol.exists():
            return json.dumps({"hata": f"Dizin bulunamadı: {dizin}"}, ensure_ascii=False)
        if not yol.is_dir():
            return json.dumps({"hata": f"Dizin değil: {dizin}"}, ensure_ascii=False)

        dosyalar = []
        klasorler = []
        for entry in sorted(yol.iterdir()):
            if entry.is_dir():
                klasorler.append(entry.name)
            else:
                try:
                    boyut = entry.stat().st_size
                except OSError:
                    boyut = -1
                dosyalar.append({"ad": entry.name, "boyut": boyut})

        return json.dumps({
            "dizin": str(yol),
            "klasorler": klasorler,
            "dosyalar": dosyalar,
            "toplam_klasor": len(klasorler),
            "toplam_dosya": len(dosyalar),
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("."))
