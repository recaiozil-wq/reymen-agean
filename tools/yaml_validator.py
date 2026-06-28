# -*- coding: utf-8 -*-
"""yaml_validator.py — YAML geçerlilik kontrolü ve formatlama aracı.

YAML string'ini doğrular ve opsiyonel olarak JSON'a dönüştürür.
"""

import json

# Opsiyonel: PyYAML
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


TOOL_META = {
    "aciklama": "YAML string'ini doğrular ve opsiyonel olarak JSON'a dönüştürür.",
    "parametreler": [
        {"ad": "yaml_str", "tip": "str", "aciklama": "Kontrol edilecek YAML string'i."},
        {"ad": "format", "tip": "str", "aciklama": "'dogrula' (varsayılan) veya 'jsona_cevir'."},
    ],
    "ornek": 'YAML_VALIDATOR("ad: Ali\\nyas: 30", format="jsona_cevir")',
    "kategori": "code_execution",
}


def run(yaml_str: str = "", format: str = "dogrula", *args, **kwargs) -> str:
    """YAML string'ini doğrula.

    Args:
        yaml_str: Kontrol edilecek YAML string'i.
        format: 'dogrula' (varsayılan) veya 'jsona_cevir'.

    Returns:
        Doğrulama sonucu veya JSON dönüşümü.
    """
    if not HAS_YAML:
        return json.dumps({
            "hata": "PyYAML kurulu degil. 'pip install pyyaml' ile kurun.",
            "cozum": "Alternatif: manuel YAML kontrolü yapilamiyor."
        }, ensure_ascii=False)

    if not yaml_str:
        return json.dumps({"hata": "yaml_str parametresi zorunludur."}, ensure_ascii=False)

    try:
        parsed = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        return json.dumps({
            "durum": "gecersiz",
            "hata": str(e),
        }, ensure_ascii=False)

    if parsed is None:
        return json.dumps({
            "durum": "gecersiz",
            "hata": "YAML bos veya yalnizca null deger iceriyor."
        }, ensure_ascii=False)

    if format == "jsona_cevir":
        try:
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except (TypeError, ValueError) as e:
            return json.dumps({
                "durum": "donusum_hatasi",
                "hata": f"JSON'a donusturulemiyor: {str(e)}",
            }, ensure_ascii=False)
    else:
        tip = type(parsed).__name__
        return json.dumps({
            "durum": "gecerli",
            "tip": tip,
            "anahtar_sayisi": len(parsed) if isinstance(parsed, dict) else None,
            "eleman_sayisi": len(parsed) if isinstance(parsed, (list, tuple)) else None,
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    test_yaml = """
ad: Ali
yas: 30
sehir: Istanbul
beceriler:
  - Python
  - JavaScript
"""
    print("=== DOGRULA ===")
    print(run(test_yaml, format="dogrula"))
    print("\n=== JSON'A CEVIR ===")
    print(run(test_yaml, format="jsona_cevir"))
    if not HAS_YAML:
        print("\n[PyYAML kurulu degil, yalnizca hata mesaji test edildi.]")
