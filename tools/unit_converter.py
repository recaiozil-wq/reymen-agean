# -*- coding: utf-8 -*-
"""unit_converter.py — Birim dönüşümü aracı.

Bayt, zaman, sıcaklık, uzunluk, ağırlık birimleri arasında dönüşüm yapar.
"""

import json


# Dönüşüm katsayıları
BOYUT_BIRIMLERI = {
    "B": 1,
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
    "TB": 1024**4,
    "PB": 1024**5,
}

SICAKLIK_DONUSUM = {
    "celsius": lambda v, h: v if h == "celsius" else v * 9/5 + 32 if h == "fahrenheit" else v + 273.15,
    "fahrenheit": lambda v, h: v if h == "fahrenheit" else (v - 32) * 5/9 if h == "celsius" else (v - 32) * 5/9 + 273.15,
    "kelvin": lambda v, h: v if h == "kelvin" else v - 273.15 if h == "celsius" else (v - 273.15) * 9/5 + 32,
}

UZUNLUK_BIRIMLERI = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
}

AGIRLIK_BIRIMLERI = {
    "mg": 0.000001, "g": 0.001, "kg": 1.0, "ton": 1000.0,
    "oz": 0.0283495, "lb": 0.453592, "st": 6.35029,
}

ZAMAN_BIRIMLERI = {
    "sn": 1.0, "dk": 60.0, "saat": 3600.0,
    "gun": 86400.0, "hafta": 604800.0, "ay": 2592000.0, "yil": 31536000.0,
}


TOOL_META = {
    "aciklama": "Birim dönüşümü: bayt, sıcaklık, uzunluk, ağırlık, zaman.",
    "parametreler": [
        {"ad": "kategori", "tip": "str", "aciklama": "Dönüşüm kategorisi: boyut, sicaklik, uzunluk, agirlik, zaman."},
        {"ad": "deger", "tip": "float", "aciklama": "Dönüştürülecek değer."},
        {"ad": "kaynak_birim", "tip": "str", "aciklama": "Kaynak birim (örn: MB, celsius, km, kg, saat)."},
        {"ad": "hedef_birim", "tip": "str", "aciklama": "Hedef birim (örn: GB, fahrenheit, mil, lb, dk)."},
    ],
    "ornek": 'UNIT_CONVERTER(kategori="boyut", deger=1024, kaynak_birim="MB", hedef_birim="GB")',
    "kategori": "conversion",
}


def run(kategori: str = "", deger: float = 0.0, kaynak_birim: str = "", hedef_birim: str = "", *args, **kwargs) -> str:
    """Birim dönüşümü yap.

    Args:
        kategori: Dönüşüm kategorisi (boyut, sicaklik, uzunluk, agirlik, zaman).
        deger: Dönüştürülecek değer.
        kaynak_birim: Kaynak birim adı.
        hedef_birim: Hedef birim adı.

    Returns:
        JSON: dönüşüm sonucu.
    """
    if not kategori:
        return json.dumps({"hata": "kategori parametresi zorunludur.", "kategoriler": ["boyut", "sicaklik", "uzunluk", "agirlik", "zaman"]}, ensure_ascii=False)
    if not kaynak_birim:
        return json.dumps({"hata": "kaynak_birim parametresi zorunludur."}, ensure_ascii=False)
    if not hedef_birim:
        return json.dumps({"hata": "hedef_birim parametresi zorunludur."}, ensure_ascii=False)

    kategori = kategori.lower()
    kaynak = kaynak_birim.lower().strip()
    hedef = hedef_birim.lower().strip()

    try:
        if kategori == "boyut":
            return _convert_boyut(deger, kaynak, hedef)
        elif kategori == "sicaklik":
            return _convert_sicaklik(deger, kaynak, hedef)
        elif kategori == "uzunluk":
            return _convert_uzunluk(deger, kaynak, hedef)
        elif kategori == "agirlik":
            return _convert_agirlik(deger, kaynak, hedef)
        elif kategori == "zaman":
            return _convert_zaman(deger, kaynak, hedef)
        else:
            return json.dumps({"hata": f"Geçersiz kategori: {kategori}", "kategoriler": ["boyut", "sicaklik", "uzunluk", "agirlik", "zaman"]}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"hata": f"Dönüşüm hatası: {str(e)}"}, ensure_ascii=False)


def _convert_boyut(deger: float, kaynak: str, hedef: str) -> str:
    if kaynak.upper() not in BOYUT_BIRIMLERI:
        return json.dumps({"hata": f"Geçersiz birim: {kaynak}. Desteklenen: {list(BOYUT_BIRIMLERI.keys())}"}, ensure_ascii=False)
    if hedef.upper() not in BOYUT_BIRIMLERI:
        return json.dumps({"hata": f"Geçersiz birim: {hedef}. Desteklenen: {list(BOYUT_BIRIMLERI.keys())}"}, ensure_ascii=False)

    kaynak_k = kaynak.upper()
    hedef_k = hedef.upper()
    bayt = deger * BOYUT_BIRIMLERI[kaynak_k]
    sonuc = bayt / BOYUT_BIRIMLERI[hedef_k]

    return json.dumps({
        "kategori": "boyut",
        "giris": {"deger": deger, "birim": kaynak_k},
        "cikti": {"deger": round(sonuc, 6), "birim": hedef_k},
        "bayt": round(bayt, 2),
    }, ensure_ascii=False, indent=2)


def _convert_sicaklik(deger: float, kaynak: str, hedef: str) -> str:
    if kaynak not in SICAKLIK_DONUSUM:
        return json.dumps({"hata": f"Gecersiz birim: {kaynak}. Desteklenen: celsius, fahrenheit, kelvin"}, ensure_ascii=False)
    if hedef not in SICAKLIK_DONUSUM:
        return json.dumps({"hata": f"Gecersiz birim: {hedef}. Desteklenen: celsius, fahrenheit, kelvin"}, ensure_ascii=False)

    # Önce celsius'a çevir
    if kaynak == "celsius":
        celsius = deger
    elif kaynak == "fahrenheit":
        celsius = (deger - 32) * 5 / 9
    elif kaynak == "kelvin":
        celsius = deger - 273.15
    else:
        return json.dumps({"hata": f"Bilinmeyen sıcaklık birimi: {kaynak}"}, ensure_ascii=False)

    if hedef == "celsius":
        sonuc = celsius
    elif hedef == "fahrenheit":
        sonuc = celsius * 9 / 5 + 32
    elif hedef == "kelvin":
        sonuc = celsius + 273.15
    else:
        return json.dumps({"hata": f"Bilinmeyen sıcaklık birimi: {hedef}"}, ensure_ascii=False)

    return json.dumps({
        "kategori": "sicaklik",
        "giris": {"deger": deger, "birim": kaynak.capitalize()},
        "cikti": {"deger": round(sonuc, 2), "birim": hedef.capitalize()},
    }, ensure_ascii=False, indent=2)


def _convert_uzunluk(deger: float, kaynak: str, hedef: str) -> str:
    if kaynak not in UZUNLUK_BIRIMLERI:
        return json.dumps({"hata": f"Geçersiz birim: {kaynak}. Desteklenen: {list(UZUNLUK_BIRIMLERI.keys())}"}, ensure_ascii=False)
    if hedef not in UZUNLUK_BIRIMLERI:
        return json.dumps({"hata": f"Geçersiz birim: {hedef}. Desteklenen: {list(UZUNLUK_BIRIMLERI.keys())}"}, ensure_ascii=False)

    metre = deger * UZUNLUK_BIRIMLERI[kaynak]
    sonuc = metre / UZUNLUK_BIRIMLERI[hedef]

    return json.dumps({
        "kategori": "uzunluk",
        "giris": {"deger": deger, "birim": kaynak},
        "cikti": {"deger": round(sonuc, 6), "birim": hedef},
        "metre": round(metre, 6),
    }, ensure_ascii=False, indent=2)


def _convert_agirlik(deger: float, kaynak: str, hedef: str) -> str:
    if kaynak not in AGIRLIK_BIRIMLERI:
        return json.dumps({"hata": f"Geçersiz birim: {kaynak}. Desteklenen: {list(AGIRLIK_BIRIMLERI.keys())}"}, ensure_ascii=False)
    if hedef not in AGIRLIK_BIRIMLERI:
        return json.dumps({"hata": f"Geçersiz birim: {hedef}. Desteklenen: {list(AGIRLIK_BIRIMLERI.keys())}"}, ensure_ascii=False)

    kg = deger * AGIRLIK_BIRIMLERI[kaynak]
    sonuc = kg / AGIRLIK_BIRIMLERI[hedef]

    return json.dumps({
        "kategori": "agirlik",
        "giris": {"deger": deger, "birim": kaynak},
        "cikti": {"deger": round(sonuc, 6), "birim": hedef},
        "kg": round(kg, 6),
    }, ensure_ascii=False, indent=2)


def _convert_zaman(deger: float, kaynak: str, hedef: str) -> str:
    if kaynak not in ZAMAN_BIRIMLERI:
        return json.dumps({"hata": f"Geçersiz birim: {kaynak}. Desteklenen: {list(ZAMAN_BIRIMLERI.keys())}"}, ensure_ascii=False)
    if hedef not in ZAMAN_BIRIMLERI:
        return json.dumps({"hata": f"Geçersiz birim: {hedef}. Desteklenen: {list(ZAMAN_BIRIMLERI.keys())}"}, ensure_ascii=False)

    saniye = deger * ZAMAN_BIRIMLERI[kaynak]
    sonuc = saniye / ZAMAN_BIRIMLERI[hedef]

    return json.dumps({
        "kategori": "zaman",
        "giris": {"deger": deger, "birim": kaynak},
        "cikti": {"deger": round(sonuc, 6), "birim": hedef},
        "saniye": round(saniye, 2),
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("=== BOYUT ===")
    print(run(kategori="boyut", deger=1024, kaynak_birim="MB", hedef_birim="GB"))

    print("\n=== SICAKLIK ===")
    print(run(kategori="sicaklik", deger=100, kaynak_birim="celsius", hedef_birim="fahrenheit"))

    print("\n=== UZUNLUK ===")
    print(run(kategori="uzunluk", deger=10, kaynak_birim="km", hedef_birim="mi"))

    print("\n=== ZAMAN ===")
    print(run(kategori="zaman", deger=2, kaynak_birim="gun", hedef_birim="saat"))
