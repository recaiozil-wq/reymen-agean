# -*- coding: utf-8 -*-
"""json_validator.py — JSON geçerlilik kontrolü ve formatlama aracı.

JSON string'ini doğrular, güzel formatlar veya sıkıştırır.
"""

import json


TOOL_META = {
    "aciklama": "JSON string'ini doğrular, güzel formatlar veya sıkıştırır.",
    "parametreler": [
        {"ad": "json_str", "tip": "str", "aciklama": "Kontrol edilecek JSON string'i."},
        {"ad": "islem", "tip": "str", "aciklama": "'dogrula', 'formatla' veya 'sikistir' (varsayılan: dogrula)."},
    ],
    "ornek": 'JSON_VALIDATOR(\'{"ad": "test"}\', islem="formatla")',
    "kategori": "code_execution",
}


def run(json_str: str = "", islem: str = "dogrula", *args, **kwargs) -> str:
    """JSON string'ini doğrula ve/veya formatla.

    Args:
        json_str: Kontrol edilecek JSON string'i.
        islem: 'dogrula' (varsayılan), 'formatla' veya 'sikistir'.

    Returns:
        JSON formatında doğrulama sonucu veya formatlanmış JSON.
    """
    if not json_str:
        return json.dumps({"hata": "json_str parametresi zorunludur."}, ensure_ascii=False)

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        return json.dumps({
            "durum": "gecersiz",
            "hata": str(e),
            "konum": e.pos,
            "satir": e.lineno,
            "kolon": e.colno,
        }, ensure_ascii=False)

    if islem == "formatla":
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    elif islem == "sikistir":
        return json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
    else:  # dogrula
        tip = type(parsed).__name__
        try:
            boyut = len(json_str.encode("utf-8"))
        except Exception:
            boyut = len(json_str)
        return json.dumps({
            "durum": "gecerli",
            "tip": tip,
            "boyut_bytes": boyut,
            "anahtar_sayisi": len(parsed) if isinstance(parsed, dict) else None,
            "eleman_sayisi": len(parsed) if isinstance(parsed, (list, tuple)) else None,
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("=== DOGRULA ===")
    print(run('{"ad": "Ali", "yas": 30}', islem="dogrula"))
    print("\n=== FORMATLA ===")
    print(run('{"ad":"Ali","yas":30}', islem="formatla"))
    print("\n=== SIKISTIR ===")
    print(run('{"ad": "Ali", "yas": 30}', islem="sikistir"))
    print("\n=== GECERSIZ ===")
    print(run('{ad: Ali}', islem="dogrula"))
