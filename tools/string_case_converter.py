# -*- coding: utf-8 -*-
"""string_case_converter.py — String büyük/küçük harf dönüşüm aracı.

Metin dönüşümleri: büyük harf, küçük harf, başlık, camelCase, snake_case, ters çevirme.
"""

import json
import re


TOOL_META = {
    "aciklama": "String dönüşümleri: büyük/küçük harf, camelCase, snake_case, başlık, ters çevirme.",
    "parametreler": [
        {"ad": "metin", "tip": "str", "aciklama": "Dönüştürülecek metin."},
        {"ad": "islem", "tip": "str", "aciklama": "Dönüşüm türü: buyuk, kucuk, baslik, camel, snake, kebab, pascal, ters, alternatif."},
    ],
    "ornek": 'STRING_CASE("merhaba dunya", islem="baslik")',
    "kategori": "utility",
}


def _to_camel(metin: str) -> str:
    """snake_case veya normal metni camelCase'e çevir."""
    kelimeler = re.split(r'[\s_\-]+', metin)
    if not kelimeler:
        return metin
    return kelimeler[0].lower() + ''.join(k.capitalize() for k in kelimeler[1:])


def _to_snake(metin: str) -> str:
    """camelCase veya normal metni snake_case'e çevir."""
    metin = re.sub(r'([A-Z])', r'_\1', metin)
    metin = re.sub(r'[\s\-]+', '_', metin)
    return metin.strip('_').lower()


def _to_kebab(metin: str) -> str:
    """camelCase veya normal metni kebab-case'e çevir."""
    metin = re.sub(r'([A-Z])', r'-\1', metin)
    metin = re.sub(r'[\s_]+', '-', metin)
    return metin.strip('-').lower()


def _to_pascal(metin: str) -> str:
    """camelCase veya normal metni PascalCase'e çevir."""
    kelimeler = re.split(r'[\s_\-]+', metin)
    return ''.join(k.capitalize() for k in kelimeler)


def _alternating(metin: str) -> str:
    """Alternatif büyük/küçük harf (AlTeRnAtInG)."""
    sonuc = []
    for i, c in enumerate(metin):
        sonuc.append(c.upper() if i % 2 == 0 else c.lower())
    return ''.join(sonuc)


def run(metin: str = "", islem: str = "buyuk", *args, **kwargs) -> str:
    """String dönüşümü yap.

    Args:
        metin: Dönüştürülecek metin.
        islem: Dönüşüm türü (buyuk, kucuk, baslik, camel, snake, kebab, pascal, ters, alternatif).

    Returns:
        JSON: dönüşüm sonucu.
    """
    if not metin:
        return json.dumps({"hata": "metin parametresi zorunludur."}, ensure_ascii=False)

    try:
        islemler = {
            "buyuk": lambda m: m.upper(),
            "kucuk": lambda m: m.lower(),
            "baslik": lambda m: m.title(),
            "camel": _to_camel,
            "snake": _to_snake,
            "kebab": _to_kebab,
            "pascal": _to_pascal,
            "ters": lambda m: m[::-1],
            "alternatif": _alternating,
        }

        if islem not in islemler:
            return json.dumps({
                "hata": f"Geçersiz işlem: {islem}",
                "desteklenen": list(islemler.keys()),
            }, ensure_ascii=False)

        sonuc = islemler[islem](metin)

        return json.dumps({
            "islem": islem,
            "giris": metin,
            "giris_uzunluk": len(metin),
            "cikti": sonuc,
            "cikti_uzunluk": len(sonuc),
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== BUYUK HARF ===")
    print(run("merhaba dunya", islem="buyuk"))
    print("\n=== BASLIK ===")
    print(run("merhaba dunya", islem="baslik"))
    print("\n=== CAMEL CASE ===")
    print(run("merhaba_dunya", islem="camel"))
    print("\n=== TERS ===")
    print(run("merhaba", islem="ters"))
    print("\n=== ALTERNATIF ===")
    print(run("merhaba", islem="alternatif"))
