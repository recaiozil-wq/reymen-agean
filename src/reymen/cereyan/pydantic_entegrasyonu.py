# -*- coding: utf-8 -*-
"""
pydantic_entegrasyonu.py â€” Pydantic ile type-safe structured output validation.

Tool Ã§aÄŸrÄ±larÄ±nda giriÅŸ/Ã§Ä±kÄ±ÅŸ ÅŸemalarÄ±nÄ± Pydantic model olarak tanÄ±mlar.
LLM Ã§Ä±ktÄ±sÄ±nÄ± doÄŸrular, hatalÄ± JSON'u otomatik dÃ¼zeltir.
Pydantic yoksa graceful degrade ile eski davranÄ±ÅŸa dÃ¶ner.

KullanÄ±m:
    from reymen.cereyan.pydantic_entegrasyonu import (
        validate_tool_call, validate_llm_output,
        pydantic_aktif, ToolCallModel
    )

    # Tool Ã§aÄŸrÄ±sÄ± doÄŸrulama
    dogrulanmis = validate_tool_call("WEB_ARA", {"sorgu": "test"})
    if dogrulanmis["basarili"]:
        args = dogrulanmis["args"]

    # LLM Ã§Ä±ktÄ±sÄ± doÄŸrulama
    sonuc = validate_llm_output(yanit, WebAraOutput)
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)

# â”€â”€ Pydantic'in mevcut olup olmadÄ±ÄŸÄ±nÄ± kontrol et â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

try:
    from pydantic import BaseModel, Field, ValidationError

    pydantic_aktif = True
    pydantic_version = __import__("pydantic").version.version_info()
except ImportError:
    BaseModel = object  # type: ignore
    # Pydantic yoksa bu field'larÄ± kullanÄ±lamaz yap
    Field = None  # type: ignore
    ValidationError = None  # type: ignore
    pydantic_aktif = False
    pydantic_version = None

    # Sahte field_validator (kullanÄ±lmayacak)
    def field_validator(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 1. Tool Åema Modelleri â€” her tool'un giriÅŸ parametrelerini tanÄ±mlar
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ToolCallModel(BaseModel):
    """TÃ¼m tool Ã§aÄŸrÄ±larÄ± iÃ§in temel Pydantic model."""

    pass


# â”€â”€ Bilinen tool'lar iÃ§in giriÅŸ ÅŸemalarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class WebAraInput(ToolCallModel):
    """WEB_ARA tool girdisi."""

    sorgu: str = Field(..., description="Aranacak kelime veya cÃ¼mle")
    max_sonuc: Optional[int] = Field(
        default=5, ge=1, le=50, description="Maksimum sonuÃ§ sayÄ±sÄ±"
    )


class DosyaOkuInput(ToolCallModel):
    """DOSYA_OKU tool girdisi."""

    dosya_yolu: str = Field(..., min_length=1, description="Okunacak dosyanÄ±n tam yolu")
    satir_bas: Optional[int] = Field(default=None, ge=1, description="BaÅŸlangÄ±Ã§ satÄ±rÄ±")
    satir_limit: Optional[int] = Field(
        default=None, ge=1, le=2000, description="Maksimum satÄ±r sayÄ±sÄ±"
    )


class DosyaYazInput(ToolCallModel):
    """DOSYA_YAZ tool girdisi."""

    dosya_yolu: str = Field(
        ..., min_length=1, description="YazÄ±lacak dosyanÄ±n tam yolu"
    )
    icerik: str = Field(..., description="Dosyaya yazÄ±lacak iÃ§erik")


class PythonCalistirInput(ToolCallModel):
    """PYTHON_CALISTIR tool girdisi."""

    kod: str = Field(..., min_length=1, description="Ã‡alÄ±ÅŸtÄ±rÄ±lacak Python kodu")


class KomutCalistirInput(ToolCallModel):
    """KOMUT_CALISTIR tool girdisi."""

    komut: str = Field(..., min_length=1, description="Ã‡alÄ±ÅŸtÄ±rÄ±lacak shell komutu")
    timeout: Optional[int] = Field(
        default=60, ge=1, le=600, description="Zaman aÅŸÄ±mÄ± saniye"
    )


class GorevBittiInput(ToolCallModel):
    """GOREV_BITTI tool girdisi."""

    ozet: str = Field(
        ..., min_length=1, max_length=1000, description="YapÄ±lanlarÄ±n Ã¶zeti (2â€“5 cÃ¼mle)"
    )


class ProfilDegistirInput(ToolCallModel):
    """PROFIL_DEGISTIR tool girdisi."""

    profil_adi: str = Field(
        ...,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="GeÃ§ilecek profil adÄ±: reyment, dev, test, prod",
    )


class SkillAktivasyonInput(ToolCallModel):
    """SKILL_AKTIVAT tool girdisi."""

    ad: str = Field(..., min_length=1, description="Aktive edilecek skill adÄ±")


class WebAraOutput(ToolCallModel):
    """WEB_ARA tool Ã§Ä±ktÄ±sÄ±."""

    baslik: str = Field(..., description="Sayfa baÅŸlÄ±ÄŸÄ±")
    url: str = Field(..., description="Sayfa URL'si")
    ozet: Optional[str] = Field(default=None, description="Sayfa Ã¶zeti")
    skor: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Alaka skoru"
    )


# â”€â”€ Tool â†’ Schema eÅŸleme sÃ¶zlÃ¼ÄŸÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# GiriÅŸ ÅŸemasÄ± olan tool'lar burada tanÄ±mlanÄ±r.
# Her tool: (input_model, output_model) Ã§ifti.
# output_model=None ise sadece giriÅŸ doÄŸrulamasÄ± yapÄ±lÄ±r.

TOOL_SCHEMALARI: Dict[str, tuple] = {
    "WEB_ARA": (WebAraInput, WebAraOutput),
    "DOSYA_OKU": (DosyaOkuInput, None),
    "DOSYA_YAZ": (DosyaYazInput, None),
    "PYTHON_CALISTIR": (PythonCalistirInput, None),
    "KOMUT_CALISTIR": (KomutCalistirInput, None),
    "GOREV_BITTI": (GorevBittiInput, None),
    "PROFIL_DEGISTIR": (ProfilDegistirInput, None),
    "SKILL_AKTIVAT": (SkillAktivasyonInput, None),
}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 2. JSON DÃ¼zeltme
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _json_duzelt(ham: str) -> str:
    """JSON formatÄ±nÄ± otomatik dÃ¼zelt.

    YaygÄ±n LLM hatalarÄ±nÄ± dÃ¼zeltir:
    - Tek tÄ±rnak -> Ã§ift tÄ±rnak
    - Trailing comma
    - TÄ±rnaksÄ±z anahtar
    - None/null karmaÅŸasÄ±
    - Son sÃ¼slÃ¼ parantez eksikliÄŸi

    Args:
        ham: Ham JSON metni

    Returns:
        DÃ¼zeltilmiÅŸ JSON metni
    """
    if not ham or not isinstance(ham, str):
        return ham

    # BoÅŸluklarÄ± temizle
    metin = ham.strip()

    # JSON deÄŸilse (dÃ¼z metin, tool adÄ± vs.) olduÄŸu gibi dÃ¶ndÃ¼r
    if not (metin.startswith("{") or metin.startswith("[")):
        return ham

    # 1. Tek tÄ±rnak -> Ã§ift tÄ±rnak (sadece JSON anahtarlarÄ± ve string deÄŸerler iÃ§in)
    metin = re.sub(r"(?<!\\)'", '"', metin)

    # 2. Python None -> JSON null
    metin = re.sub(r"\bNone\b", "null", metin)
    metin = re.sub(r"\bTrue\b", "true", metin)
    metin = re.sub(r"\bFalse\b", "false", metin)

    # 3. Trailing comma temizle (}, ] Ã¶ncesi)
    metin = re.sub(r",\s*([}\]])", r"\1", metin)

    # 4. TÄ±rnaksÄ±z anahtar dÃ¼zelt (Ã¶r: {sorgu: "test"} -> {"sorgu": "test"})
    metin = re.sub(r"\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:", r'{"\1":', metin)

    # 5. JSON string iÃ§indeki escape sorunlarÄ±
    metin = metin.replace("\\'", "'")

    # 6. Fazladan sÃ¼slÃ¼ parantez kapatma
    acik_suslu = metin.count("{")
    kapali_suslu = metin.count("}")
    if acik_suslu > kapali_suslu:
        metin += "}" * (acik_suslu - kapali_suslu)

    # 7. Fazladan kÃ¶ÅŸeli parantez kapatma
    acik_koseli = metin.count("[")
    kapali_koseli = metin.count("]")
    if acik_koseli > kapali_koseli:
        metin += "]" * (acik_koseli - kapali_koseli)

    return metin


def _schema_al(tool_adi: str):
    """Bir tool'un giriÅŸ ÅŸemasÄ±nÄ± dÃ¶ndÃ¼rÃ¼r.

    Args:
        tool_adi: Tool adÄ± (bÃ¼yÃ¼k harf)

    Returns:
        Pydantic model sÄ±nÄ±fÄ± veya None
    """
    if not pydantic_aktif:
        return None
    girdiler = TOOL_SCHEMALARI.get(tool_adi)
    if girdiler:
        return girdiler[0]  # input model
    return None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 3. Tool Ã‡aÄŸrÄ±sÄ± DoÄŸrulama
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def validate_tool_call(
    tool_adi: str,
    args: Union[Dict[str, Any], str],
) -> Dict[str, Any]:
    """Tool Ã§aÄŸrÄ±sÄ± parametrelerini Pydantic ile doÄŸrula.

    Args:
        tool_adi: Tool adÄ± (Ã¶rn: "WEB_ARA", "DOSYA_OKU")
        args: Parametre dict'i veya ham string

    Returns:
        {
            "basarili": True/False,
            "args": doÄŸrulanmÄ±ÅŸ dict (basarili=True ise),
            "hata": hata mesajÄ± (basarili=False ise),
            "orijinal_args": orijinal args,
        }

    Not:
        - Pydantic yoksa args olduÄŸu gibi dÃ¶ner (graceful degrade)
        - Åema tanÄ±mlÄ± deÄŸilse args olduÄŸu gibi dÃ¶ner (geÃ§erli)
        - JSON hatalarÄ±nda otomatik dÃ¼zeltme denenir
    """
    sonuc: Dict[str, Any] = {
        "basarili": False,
        "args": {},
        "hata": "",
        "orijinal_args": args,
    }

    # Pydantic yoksa graceful degrade
    if not pydantic_aktif:
        if isinstance(args, dict):
            sonuc["args"] = args
        else:
            sonuc["args"] = {"param": str(args)}
        sonuc["basarili"] = True
        return sonuc

    # Åema kontrolÃ¼ â€” ÅŸema yoksa args olduÄŸu gibi geÃ§er
    schema_model = _schema_al(tool_adi)
    if schema_model is None:
        if isinstance(args, dict):
            sonuc["args"] = args
        else:
            sonuc["args"] = {"param": str(args)}
        sonuc["basarili"] = True
        return sonuc

    # args string ise JSON'a Ã§evirmeyi dene
    if isinstance(args, str):
        try:
            # Ã–nce ham JSON'u dÃ¼zelt
            duzeltilmis = _json_duzelt(args)
            parsed_args = json.loads(duzeltilmis)
            if duzeltilmis != args:
                logger.info("[Pydantic] %s JSON'u otomatik dÃ¼zeltildi.", tool_adi)
            args = parsed_args
        except json.JSONDecodeError as e:
            # Orijinal args'i olduÄŸu gibi kullan (graceful)
            logger.warning(
                "[Pydantic] %s iÃ§in JSON parse hatasÄ±: %s. Orijinal string args kullanÄ±lÄ±yor.",
                tool_adi,
                e,
            )
            sonuc["args"] = {"param": str(args)}
            sonuc["hata"] = f"JSON parse hatasÄ±: {e}"
            sonuc["basarili"] = True  # Graceful degrade
            return sonuc

    # Dict tip kontrolÃ¼
    if not isinstance(args, dict):
        # Dict deÄŸilse stringe Ã§evir ve param olarak ver
        sonuc["args"] = {"param": str(args)}
        sonuc["hata"] = (
            f"Args dict deÄŸil ({type(args).__name__}), string olarak iletiliyor"
        )
        sonuc["basarili"] = True  # Graceful degrade
        return sonuc

    # Pydantic validasyonu
    try:
        validated = schema_model(**args)
        sonuc["args"] = validated.model_dump(exclude_none=True)
        sonuc["basarili"] = True
        logger.debug(
            "[Pydantic] %s validasyonu baÅŸarÄ±lÄ±: %s",
            tool_adi,
            sonuc["args"],
        )
    except ValidationError as e:
        hata_detay = _validation_hata_mesaji(e)
        logger.warning(
            "[Pydantic] %s validasyon hatasÄ±: %s. Args: %s",
            tool_adi,
            hata_detay,
            args,
        )
        sonuc["args"] = args  # Orijinal args'i koru (graceful)
        sonuc["hata"] = hata_detay
        sonuc["basarili"] = True  # Hata bildir ama Ã§alÄ±ÅŸmaya devam et
    except Exception as e:
        logger.error(
            "[Pydantic] %s beklenmeyen hata: %s",
            tool_adi,
            e,
        )
        sonuc["args"] = args
        sonuc["hata"] = f"Beklenmeyen hata: {e}"
        sonuc["basarili"] = True  # Graceful degrade

    return sonuc


def _validation_hata_mesaji(e) -> str:
    """Pydantic ValidationError'dan okunabilir hata mesajÄ± Ã¼retir.

    Args:
        e: Pydantic ValidationError

    Returns:
        Ä°nsan tarafÄ±ndan okunabilir hata mesajÄ±
    """
    hatalar = []
    for hata in e.errors():
        alan = " -> ".join(str(loc) for loc in hata.get("loc", []))
        tip = hata.get("type", "unknown")
        msg = hata.get("msg", "GeÃ§ersiz deÄŸer")
        if alan:
            hatalar.append(f"'{alan}': {msg} (tip: {tip})")
        else:
            hatalar.append(f"{msg} (tip: {tip})")
    return " | ".join(hatalar)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 4. LLM Ã‡Ä±ktÄ±sÄ± DoÄŸrulama
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def validate_llm_output(
    output: Union[str, Dict[str, Any]],
    schema_model,
) -> Dict[str, Any]:
    """LLM Ã§Ä±ktÄ±sÄ±nÄ± Pydantic model ile doÄŸrula.

    Args:
        output: LLM'den gelen ham Ã§Ä±ktÄ± (string veya dict)
        schema_model: DoÄŸrulama iÃ§in Pydantic model sÄ±nÄ±fÄ±

    Returns:
        {
            "basarili": True/False,
            "data": doÄŸrulanmÄ±ÅŸ dict (basarili=True ise),
            "hata": hata mesajÄ± (basarili=False ise),
            "duzeltildi": JSON otomatik dÃ¼zeltme yapÄ±ldÄ± mÄ±,
        }

    Not:
        - Pydantic yoksa output olduÄŸu gibi dÃ¶ner
        - JSON hatalarÄ±nda otomatik dÃ¼zeltme denenir
    """
    sonuc: Dict[str, Any] = {
        "basarili": False,
        "data": {},
        "hata": "",
        "duzeltildi": False,
    }

    # Pydantic yoksa graceful degrade
    if not pydantic_aktif:
        if isinstance(output, dict):
            sonuc["data"] = output
        else:
            sonuc["data"] = {"raw": str(output)}
        sonuc["basarili"] = True
        return sonuc

    # JSON Ã§Ã¶zÃ¼mleme
    if isinstance(output, str):
        try:
            duzeltilmis = _json_duzelt(output)
            if duzeltilmis != output:
                sonuc["duzeltildi"] = True
            parsed = json.loads(duzeltilmis)
        except json.JSONDecodeError as e:
            sonuc["hata"] = f"JSON Ã§Ã¶zÃ¼mleme hatasÄ±: {e}"
            sonuc["data"] = {"raw": output}
            return sonuc
    elif isinstance(output, dict):
        parsed = output
    else:
        sonuc["hata"] = f"Beklenmeyen tip: {type(output).__name__}"
        sonuc["data"] = {"raw": str(output)}
        return sonuc

    # Pydantic validasyonu
    try:
        validated = schema_model(**parsed)
        sonuc["data"] = validated.model_dump(exclude_none=True)
        sonuc["basarili"] = True
    except ValidationError as e:
        sonuc["hata"] = _validation_hata_mesaji(e)
        sonuc["data"] = parsed  # Orijinal parsed veriyi dÃ¶ndÃ¼r
    except Exception as e:
        sonuc["hata"] = f"Beklenmeyen hata: {e}"
        sonuc["data"] = parsed

    return sonuc


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 5. Tools Schema Ãœretici (motor.py iÃ§in yardÄ±mcÄ±)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def schema_to_tool_def(ad: str, input_model, aciklama: str = "") -> Optional[dict]:
    """Pydantic model'den OpenAI-uyumlu tool definition Ã¼retir.

    Args:
        ad: Tool adÄ±
        input_model: Pydantic input modeli
        aciklama: Tool aÃ§Ä±klamasÄ± (boÅŸsa model docstring'inden alÄ±nÄ±r)

    Returns:
        {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}
    """
    if not pydantic_aktif:
        return None

    schema = input_model.model_json_schema()
    props = dict(schema.get("properties", {}))
    required = list(schema.get("required", []))

    # AÃ§Ä±klama
    if not aciklama:
        aciklama = input_model.__doc__ or ad.replace("_", " ").title()

    # Her property'den title'Ä± kaldÄ±r (OpenAI gereksiz bulur)
    for p in props.values():
        p.pop("title", None)

    return {
        "type": "function",
        "function": {
            "name": ad,
            "description": aciklama[:200],
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required,
            },
        },
    }


def tools_schema_pydantic(tool_adi: str, aciklama: str = "") -> Optional[dict]:
    """Pydantic model'den tek bir tool definition Ã¼retir.

    Args:
        tool_adi: Tool adÄ±
        aciklama: AÃ§Ä±klama (opsiyonel)

    Returns:
        Tool definition dict veya None (ÅŸema yoksa/pydantic yoksa)
    """
    if not pydantic_aktif:
        return None
    schema_model = _schema_al(tool_adi)
    if schema_model is None:
        return None
    return schema_to_tool_def(tool_adi, schema_model, aciklama)


def tum_tools_schema() -> Dict[str, Optional[dict]]:
    """TÃ¼m bilinen tool ÅŸemalarÄ±nÄ± Ã¼retir.

    Returns:
        {tool_adi: tool_definition_dict veya None}
    """
    if not pydantic_aktif:
        return {}
    sonuc = {}
    for tool_adi in TOOL_SCHEMALARI:
        sonuc[tool_adi] = tools_schema_pydantic(tool_adi)
    return sonuc


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 6. YardÄ±mcÄ±: String args'ten dict oluÅŸturma (mevcut sistemle uyum)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def ham_param_to_dict(tool_adi: str, ham_param: str) -> Dict[str, Any]:
    """Eski sistemin quoted-string ham_param'Ä±nÄ± Pydantic schema ile dict'e Ã§evir.

    Args:
        tool_adi: Tool adÄ±
        ham_param: Quoted-string parametre (Ã¶rn: '"test.py" "icerik"')

    Returns:
        Parametre dict'i
    """
    if not pydantic_aktif:
        return {"param": ham_param}

    schema_model = _schema_al(tool_adi)
    if schema_model is None:
        return {"param": ham_param}

    # Quoted string'leri parse et
    params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham_param)
    if not params:
        return {"param": ham_param}

    # Model alan adlarÄ±nÄ± al
    alan_adi_listesi = list(schema_model.model_fields.keys())
    if not alan_adi_listesi:
        return {"param": ham_param}

    # Ä°lk N parametreyi model alanlarÄ±na eÅŸle
    result = {}
    for i, deger in enumerate(params):
        if i < len(alan_adi_listesi):
            result[alan_adi_listesi[i]] = deger
        else:
            result[f"param_{i}"] = deger

    return result


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# 7. AraÃ§ Ã‡alÄ±ÅŸtÄ±rma Ã–ncesi/SonrasÄ± Hook
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def tool_cagri_oncesi(tool_adi: str, args: Any) -> Dict[str, Any]:
    """Tool Ã§aÄŸrÄ±lmadan Ã¶nce args doÄŸrulamasÄ± yap.

    Args:
        tool_adi: Tool adÄ±
        args: Ham args (dict veya string)

    Returns:
        DoÄŸrulanmÄ±ÅŸ args bilgisi:
        {
            "basarili": True,
            "args": doÄŸrulanmÄ±ÅŸ dict,
            "hata": varsa uyarÄ± mesajÄ±,
            "hata_var_mi": True/False,
        }
    """
    sonuc = validate_tool_call(tool_adi, args)
    return {
        "basarili": True,
        "args": sonuc.get("args", {}),
        "hata": sonuc.get("hata", ""),
        "hata_var_mi": bool(sonuc.get("hata")),
    }
