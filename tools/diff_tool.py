# -*- coding: utf-8 -*-
"""diff_tool.py — Metin fark karşılaştırma aracı.

İki metin arasındaki farkları satır bazında gösterir (diff benzeri).
"""

import json
import difflib


TOOL_META = {
    "aciklama": "İki metin arasındaki satır bazında farkları gösterir (diff benzeri).",
    "parametreler": [
        {"ad": "kaynak1", "tip": "str", "aciklama": "Birinci metin veya 'd:' ile dosya yolu."},
        {"ad": "kaynak2", "tip": "str", "aciklama": "İkinci metin veya 'd:' ile dosya yolu."},
        {"ad": "context", "tip": "int", "aciklama": "Her değişiklik etrafında gösterilecek bağlam satır sayısı (varsayılan: 3)."},
        {"ad": "gosterim", "tip": "str", "aciklama": "Gösterim türü: 'unified' (varsayılan), 'context', 'html', 'oran'."},
    ],
    "ornek": 'DIFF_TOOL(kaynak1="eski metin", kaynak2="yeni metin")',
    "kategori": "utility",
}


def run(kaynak1: str = "", kaynak2: str = "", context: int = 3,
        gosterim: str = "unified", *args, **kwargs) -> str:
    """İki metin arasındaki farkları göster.

    Args:
        kaynak1: Birinci metin. 'd:' ile başlarsa dosya yolu.
        kaynak2: İkinci metin. 'd:' ile başlarsa dosya yolu.
        context: Bağlam satır sayısı.
        gosterim: Gösterim türü (unified, context, html, oran).

    Returns:
        JSON veya unified diff çıktısı.
    """
    if not kaynak1 or not kaynak2:
        return json.dumps({"hata": "kaynak1 ve kaynak2 parametreleri zorunludur."}, ensure_ascii=False)

    try:
        # Dosyadan oku
        for i, kaynak in enumerate([kaynak1, kaynak2]):
            if kaynak.startswith(("d:", "D:")):
                from pathlib import Path
                dosya_yolu = kaynak[2:].strip()
                yol = Path(dosya_yolu)
                if not yol.exists():
                    return json.dumps({"hata": f"Dosya bulunamadi: {dosya_yolu}"}, ensure_ascii=False)
                icerik = yol.read_text(encoding="utf-8", errors="replace")
                if i == 0:
                    satir1 = icerik.splitlines()
                    ad1 = dosya_yolu
                else:
                    satir2 = icerik.splitlines()
                    ad2 = dosya_yolu

        if kaynak1.startswith(("d:", "D:")):
            pass  # already set above
        else:
            satir1 = kaynak1.splitlines()
            ad1 = "kaynak1"

        if kaynak2.startswith(("d:", "D:")):
            pass  # already set above
        else:
            satir2 = kaynak2.splitlines()
            ad2 = "kaynak2"

        if gosterim == "unified":
            diff = difflib.unified_diff(
                satir1, satir2,
                fromfile=ad1, tofile=ad2,
                n=context, lineterm=""
            )
            return "\n".join(diff)

        elif gosterim == "context":
            diff = difflib.context_diff(
                satir1, satir2,
                fromfile=ad1, tofile=ad2,
                n=context, lineterm=""
            )
            return "\n".join(diff)

        elif gosterim == "html":
            diff = difflib.HtmlDiff().make_table(
                satir1, satir2,
                fromdesc=ad1, todesc=ad2,
                context=True, numlines=context
            )
            return diff

        elif gosterim == "oran":
            matcher = difflib.SequenceMatcher(None, satir1, satir2)
            benzerlik = matcher.ratio() * 100

            # Ayrıntılı istatistik
            changes = []
            for op, i1, i2, j1, j2 in matcher.get_opcodes():
                if op == "replace":
                    changes.append({
                        "tip": "degistir",
                        "kaynak1": satir1[i1:i2],
                        "kaynak2": satir2[j1:j2],
                    })
                elif op == "delete":
                    changes.append({
                        "tip": "sil",
                        "kaynak1": satir1[i1:i2],
                        "kaynak2": [],
                    })
                elif op == "insert":
                    changes.append({
                        "tip": "ekle",
                        "kaynak1": [],
                        "kaynak2": satir2[j1:j2],
                    })

            return json.dumps({
                "benzerlik_yuzde": round(benzerlik, 2),
                "satir_sayisi_1": len(satir1),
                "satir_sayisi_2": len(satir2),
                "degisiklik_sayisi": len(changes),
                "degisiklikler": changes,
            }, ensure_ascii=False, indent=2)

        else:
            return json.dumps({"hata": f"Geçersiz gösterim: {gosterim}", "desteklenen": ["unified", "context", "html", "oran"]}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    eski = "Merhaba dunya\nBu bir test metnidir\nUcuncu satir\nDorduncu satir"
    yeni = "Merhaba dunya\nBu bir test metnidir (guncel)\nUcuncu satir\nBesinci satir"

    print("=== UNIFIED DIFF ===")
    print(run(eski, yeni, gosterim="unified"))

    print("\n=== ORAN ===")
    print(run(eski, yeni, gosterim="oran"))
