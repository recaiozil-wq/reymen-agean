# -*- coding: utf-8 -*-
"""tools/tool_dispatch_helpers.py — Parametre dogrulama ve donusum.

Uc ana fonksiyon:
  validate_params  — JSON schema benzeri dogrulama
  coerce_types     — Tip donusumu
  filter_sensitive_params — Hassas alanlari logdan gizle
"""

import json
from typing import Any
import logging
logger = logging.getLogger(__name__)

# ANSI renk kodlari
_Y = "\033[92m"   # yesil
_S = "\033[93m"   # sari
_K = "\033[91m"   # kirmizi
_M = "\033[94m"   # mavi
_R = "\033[0m"    # sifirla

_VARSAYILAN_HASSAS = frozenset({
    "api_key", "token", "password", "secret",
    "authorization", "auth", "passwd", "credential",
    "private_key", "access_key", "refresh_token",
})

_JSON_TIP_ESLEME: dict[str, type | tuple] = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}

_GUVENLI_TIPLER: dict[str, type] = {
    "str": str, "int": int, "float": float,
    "bool": bool, "list": list, "dict": dict,
}


def validate_params(schema: dict, args: dict) -> tuple:
    """JSON schema benzeri parametre dogrulama.

    'required' listesi ve 'properties' icindeki type / minLength / enum
    kurallari kontrol edilir. Tam JSON Schema standardi degil; temel
    alan dogrulamasi icin yeterlidir.

    Args:
        schema: {'required': [...], 'properties': {alan: {type, minLength, enum}}}
        args: Dogrulanacak parametre dict'i.

    Returns:
        (gecerli: bool, hatalar: list[str])
    """
    hatalar: list[str] = []

    for alan in schema.get("required", []):
        if alan not in args:
            hatalar.append(f"{_K}Eksik zorunlu parametre: '{alan}'{_R}")

    for alan, tanim in schema.get("properties", {}).items():
        if alan not in args:
            continue
        deger = args[alan]

        beklenen = tanim.get("type")
        if beklenen and not isinstance(deger, _JSON_TIP_ESLEME.get(beklenen, object)):
            hatalar.append(
                f"{_S}'{alan}' tip hatasi: beklenen={beklenen}, "
                f"gelen={type(deger).__name__}{_R}"
            )

        min_uzunluk = tanim.get("minLength")
        if min_uzunluk is not None and isinstance(deger, str) and len(deger) < min_uzunluk:
            hatalar.append(f"{_S}'{alan}' cok kisa (min {min_uzunluk} karakter){_R}")

        enum = tanim.get("enum")
        if enum is not None and deger not in enum:
            hatalar.append(f"{_S}'{alan}' gecersiz deger '{deger}', izinliler: {enum}{_R}")

    if hatalar:
        print(f"{_K}[DISPATCH] {len(hatalar)} dogrulama hatasi{_R}")
    else:
        print(f"{_Y}[DISPATCH] Parametreler gecerli ({len(args)} alan){_R}")

    return len(hatalar) == 0, hatalar


def coerce_types(args: dict, expected_types: dict) -> dict:
    """Parametre degerlerini hedef tiplere donustur.

    Bool donusumu icin 'true'/'1'/'evet'/'yes' dizelerini tanir.
    Liste donusumu icin JSON dizisi veya virgul ayirici denemeleri yapar.

    Args:
        args: Donusturulacak parametreler.
        expected_types: {parametre_adi: hedef_tip} (ornegin {'port': int}).

    Returns:
        dict: Donusturulmus parametreler (orijinal dict degistirilmez).
    """
    cikti = dict(args)

    for alan, hedef in expected_types.items():
        if alan not in cikti:
            continue
        deger = cikti[alan]
        if isinstance(deger, hedef):
            continue
        try:
            if hedef is bool and isinstance(deger, str):
                cikti[alan] = deger.strip().lower() in ("true", "1", "evet", "yes")
            elif hedef is list and isinstance(deger, str):
                cikti[alan] = json.loads(deger) if deger.lstrip().startswith("[") else [x.strip() for x in deger.split(",")]
            elif hedef is dict and isinstance(deger, str):
                cikti[alan] = json.loads(deger)
            else:
                cikti[alan] = hedef(deger)
            print(f"{_M}[DISPATCH] COERCE '{alan}': {type(deger).__name__} → {hedef.__name__}{_R}")
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            print(f"{_S}[DISPATCH] COERCE '{alan}' donusturulamadi: {exc}{_R}")

    return cikti


def filter_sensitive_params(args: dict, sensitive_keys: set | None = None) -> dict:
    """Hassas parametreleri log guvenligi icin maskele.

    Orijinal args degistirilmez; maskelenmis kopya dondurulur.
    Karsilastirma kucuk harf ile yapilir (API_KEY == api_key).

    Args:
        args: Maskelenecek parametreler.
        sensitive_keys: Hassas anahtar isimleri (None ise varsayilan set kullanilir).

    Returns:
        dict: Hassas degerleri '***REDACTED***' ile degistirilmis kopya.
    """
    hassas = {k.lower() for k in (sensitive_keys or _VARSAYILAN_HASSAS)}
    gizlenen = 0
    cikti: dict = {}

    for k, v in args.items():
        if k.lower() in hassas:
            cikti[k] = "***REDACTED***"
            gizlenen += 1
        else:
            cikti[k] = v

    if gizlenen:
        print(f"{_S}[DISPATCH] {gizlenen} hassas parametre maskelendi{_R}")

    return cikti


def run(islem: str = "validate", schema=None, args=None,
        expected_types=None, sensitive_keys=None) -> str:
    """Dispatch helpers harici arayuzu (tool_registry uyumu icin).

    Args:
        islem: 'validate' | 'coerce' | 'filter'
        schema: JSON schema dict veya JSON string (validate icin).
        args: Parametre dict veya JSON string.
        expected_types: {alan: tip_adi} dict veya JSON string (coerce icin).
        sensitive_keys: Hassas anahtar listesi (filter icin).

    Returns:
        str: JSON formatinda sonuc.
    """
    def _parse(x, varsayilan):
        if x is None:
            return varsayilan
        if isinstance(x, str):
            try:
                return json.loads(x)
            except json.JSONDecodeError:
                return varsayilan
        return x

    schema = _parse(schema, {})
    args = _parse(args, {})
    expected_types = _parse(expected_types, {})

    try:
        if islem == "validate":
            gecerli, hatalar = validate_params(schema, args)
            return json.dumps({"gecerli": gecerli, "hatalar": hatalar}, ensure_ascii=False)

        elif islem == "coerce":
            tip_esle = {
                k: _GUVENLI_TIPLER[v]
                for k, v in expected_types.items()
                if v in _GUVENLI_TIPLER
            }
            return json.dumps(coerce_types(args, tip_esle), ensure_ascii=False, default=str)

        elif islem == "filter":
            keys = set(sensitive_keys) if sensitive_keys else None
            return json.dumps(filter_sensitive_params(args, keys), ensure_ascii=False)

        return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen islem: {islem}"}, ensure_ascii=False)

    except Exception as exc:
        return json.dumps({"durum": "hata", "mesaj": str(exc)}, ensure_ascii=False)


if __name__ == "__main__":
    schema = {"required": ["ad"], "properties": {"ad": {"type": "string", "minLength": 2}}}
    print(run("validate", schema=schema, args={"ad": "Al"}))
    print(run("coerce", args={"port": "8080", "aktif": "true"}, expected_types={"port": "int", "aktif": "bool"}))
    print(run("filter", args={"kullanici": "ahmet", "api_key": "gizli123"}))
