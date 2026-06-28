# -*- coding: utf-8 -*-
"""json_transformer.py — JSON dönüşüm aracı (jq benzeri).

JSON verisi üzerinde sorgulama, filtreleme ve dönüşüm işlemleri yapar.
"""

import json


TOOL_META = {
    "aciklama": "JSON verisi üzerinde sorgulama, filtreleme ve dönüşüm (jq benzeri).",
    "parametreler": [
        {"ad": "json_str", "tip": "str", "aciklama": "İşlenecek JSON string'i."},
        {"ad": "sorgu", "tip": "str", "aciklama": "Sorgu ifadesi. '.' = tümü, '.anahtar' = anahtar seç, '.[]' = dizi elemanları."},
    ],
    "ornek": 'JSON_TRANSFORMER(\'{"kullanicilar": [{"ad": "Ali"}]}\', sorgu=".kullanicilar.[].ad")',
    "kategori": "data_processing",
}


def _query_json(data, sorgu: str):
    """Basit JSON sorgulama motoru."""
    if sorgu == "." or sorgu == "":
        return data

    parts = sorgu.strip().lstrip(".").split(".")
    current = data

    for part in parts:
        if part == "[]" and isinstance(current, list):
            return [_query_json(item, ".".join(parts[parts.index("[]") + 1:])) if len(parts) > parts.index("[]") + 1 else item for item in current]
        elif part == "[]":
            return current
        elif isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                return None
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx]
            except (ValueError, IndexError):
                # Listedeki her elemana uygula
                return [_query_json(item, part) for item in current if _query_json(item, part) is not None]
        else:
            return None

    return current


def run(json_str: str = "", sorgu: str = ".", *args, **kwargs) -> str:
    """JSON verisi üzerinde sorgulama/dönüşüm yap.

    Args:
        json_str: İşlenecek JSON string'i.
        sorgu: Sorgu ifadesi (varsayılan: '.' = tüm veri).

    Returns:
        Sorgu sonucu JSON olarak.
    """
    if not json_str:
        return json.dumps({"hata": "json_str parametresi zorunludur."}, ensure_ascii=False)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        return json.dumps({"hata": f"Gecersiz JSON: {str(e)}"}, ensure_ascii=False)

    try:
        sonuc = _query_json(data, sorgu)
        if sonuc is None:
            return json.dumps({"hata": f"Sorgu eslesmedi: {sorgu}"}, ensure_ascii=False)
        return json.dumps(sonuc, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"hata": f"Sorgu hatasi: {str(e)}"}, ensure_ascii=False)


if __name__ == "__main__":
    test_json = '{"kullanicilar": [{"ad": "Ali", "yas": 30}, {"ad": "Ayse", "yas": 25}], "toplam": 2}'

    print("=== TUMU ===")
    print(run(test_json, sorgu="."))

    print("\n=== ANAHTAR SEC ===")
    print(run(test_json, sorgu=".toplam"))

    print("\n=== LISTE ELEMANLARI ===")
    print(run(test_json, sorgu=".kullanicilar"))
