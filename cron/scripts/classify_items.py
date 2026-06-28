# -*- coding: utf-8 -*-
"""cron/scripts/classify_items.py — Ogeleri Siniflandirici.

Bu betik, cron islerinde ogeleri (e-posta, bildirim vb.) siniflandirmak
icin kullanilir. ``cron.scripts.classify_items`` modul yoluyla referans
edilir; asla mutlak dosya yoluyla degil.

Kullanim:
    python -m cron.scripts.classify_items [--input FILE] [--threshold 0.7]
"""


def classify_items(items: list, threshold: float = 0.7) -> list:
    """Bir liste oge icinden onemli olanlari filtrele.

    Args:
        items: Siniflandirilacak ogeler (dict listesi)
        threshold: Onem esigi (0-1 arasi)

    Returns:
        Onemli olarak isaretlenen ogeler listesi
    """
    results = []
    for item in items:
        score = item.get("score", 0.0)
        if score >= threshold:
            results.append({**item, "important": True})
    return results


if __name__ == "__main__":
    import json
    import sys

    sample = [
        {"id": "1", "subject": "Acil toplanti", "score": 0.9},
        {"id": "2", "subject": "Haber bulteni", "score": 0.3},
        {"id": "3", "subject": "Proje guncelleme", "score": 0.8},
    ]
    print(json.dumps(classify_items(sample), ensure_ascii=False, indent=2))
