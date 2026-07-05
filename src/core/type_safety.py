# -*- coding: utf-8 -*-
"""
type_safety.py â€” ReYMeN Tip GÃ¼venliÄŸi KatmanÄ± (Pydantic AI).

Pydantic AI (pydantic-ai) paketi Ã¼zerine inÅŸa edilmiÅŸ, araÃ§ (tool)
Ã§aÄŸrÄ±larÄ± ve LLM yanÄ±tlarÄ± iÃ§in giriÅŸ/Ã§Ä±kÄ±ÅŸ doÄŸrulama (validation)
altyapÄ±sÄ±.

SaÄŸladÄ±klarÄ±:
  * @validated_tool(schema=...)  â†’ AraÃ§ giriÅŸ/Ã§Ä±kÄ±ÅŸ validasyonu
  * StructuredOutput             â†’ LLM'den yapÄ±landÄ±rÄ±lmÄ±ÅŸ (Pydantic model) Ã§Ä±ktÄ±
  * ToolResult                   â†’ Standart araÃ§ dÃ¶nÃ¼ÅŸ sarmalayÄ±cÄ±sÄ±
  * json_schema_al              â†’ Pydantic model â†’ JSON ÅŸema
  * model_al                    â†’ JSON veri â†’ Pydantic model (doÄŸrulamalÄ±)

KullanÄ±m:
    from reymen.core.type_safety import validated_tool, ToolResult

    # 1) Basit validasyon
    @validated_tool
    def topla(a: int, b: int) -> int:
        return a + b

    # 2) Pydantic model ile giriÅŸ validasyonu
    class KullaniciMesaji(BaseModel):
        kullanici_id: str
        mesaj: str
        dil: str = "tr"

    @validated_tool(schema=KullaniciMesaji)
    def mesaj_gonder(veri: KullaniciMesaji) -> ToolResult:
        # veri.kullanici_id, veri.mesaj doÄŸrulanmÄ±ÅŸ ÅŸekilde gelir
        return ToolResult(
            basarili=True,
            veri={"mesaj": veri.mesaj, "hedef": veri.kullanici_id}
        )

    # 3) LLM yapÄ±landÄ±rÄ±lmÄ±ÅŸ Ã§Ä±ktÄ±
    class AnalizSonucu(BaseModel):
        konu: str
        duygu: Literal["pozitif", "negatif", "notr"]
        puan: int = Field(ge=0, le=100)

    sonuc: AnalizSonucu = StructuredOutput.coerce({"konu": "test", ...}, AnalizSonucu)

TÃ¼m dokÃ¼mantasyon TÃ¼rkÃ§e'dir.
"""

from __future__ import annotations

import inspect
import logging
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    TypeVar,
    get_type_hints,
)

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

# â”€â”€ Genel Tip Sabitleri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

T = TypeVar("T")
"""Genel tip deÄŸiÅŸkeni â€” herhangi bir tip."""

ModelTipi = TypeVar("ModelTipi", bound=BaseModel)
"""Pydantic BaseModel alt sÄ±nÄ±flarÄ± iÃ§in tip deÄŸiÅŸkeni."""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ToolResult â€” Standart AraÃ§ DÃ¶nÃ¼ÅŸ SarmalayÄ±cÄ±sÄ±
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@dataclass
class ToolResult(Generic[T]):
    """Bir araÃ§ Ã§aÄŸrÄ±sÄ±nÄ±n standart dÃ¶nÃ¼ÅŸ sarmalayÄ±cÄ±sÄ±.

    TÃ¼m araÃ§lar (validated_tool ile sarmalanmÄ±ÅŸ olsun ya da olmasÄ±n)
    bu yapÄ±yÄ± dÃ¶nebilir. BÃ¶ylece Ã¼st katman (motor, conversation_loop)
    her araÃ§tan aynÄ± ÅŸablonda yanÄ±t alÄ±r.

    Args:
        basarili:  Ä°ÅŸlem baÅŸarÄ±lÄ± mÄ±?
        veri:      BaÅŸarÄ±lÄ± yanÄ±t verisi (T tipi).
        hata:      Hata mesajÄ± (baÅŸarÄ±sÄ±z ise doldurulur).
        model:     KullanÄ±lan validasyon modeli adÄ± (opsiyonel).
    """

    basarili: bool = True
    veri: Optional[T] = None
    hata: str = ""
    model: str = ""

    def __bool__(self) -> bool:
        """DoÄŸrudan if kontrolÃ¼: ``if sonuc:`` ÅŸeklinde kullanÄ±m.

        Returns:
            ``basarili`` deÄŸerini dÃ¶ndÃ¼rÃ¼r.
        """
        return self.basarili


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# JSON Åema â†” Pydantic Model DÃ¶nÃ¼ÅŸÃ¼mleri
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def json_schema_al(model: type[BaseModel]) -> dict[str, Any]:
    """Bir Pydantic modelinden JSON Schema (draft-07) Ã¼retir.

    Bu ÅŸema, LLM'e tool parametresi veya yanÄ±t formatÄ± olarak
    gÃ¶nderilebilir. Pydantic-ai'nin ``Agent`` sÄ±nÄ±fÄ± bu ÅŸemayÄ±
    otomatik olarak tool tanÄ±mÄ±na ekler; bu fonksiyon elle kullanÄ±m
    veya harici sistemlerle entegrasyon iÃ§indir.

    Args:
        model: Pydantic BaseModel alt sÄ±nÄ±fÄ± (Ã¶r. ``KullaniciMesaji``).

    Returns:
        JSON Schema sÃ¶zlÃ¼ÄŸÃ¼.

    Ã–rnek:
        >>> json_schema_al(KullaniciMesaji)
        {
            "properties": {
                "kullanici_id": {"title": "Kullanici Id", "type": "string"},
                "mesaj": {"title": "Mesaj", "type": "string"},
                "dil": {"default": "tr", "title": "Dil", "type": "string"}
            },
            "required": ["kullanici_id", "mesaj"],
            "title": "KullaniciMesaji",
            "type": "object"
        }
    """
    return model.model_json_schema()


def model_al(
    veri: dict[str, Any] | Any,
    model: type[ModelTipi],
    strict: bool = False,
) -> ModelTipi:
    """Ham veriyi (dict veya JSON) Pydantic modeline dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r ve doÄŸrular.

    ``veri`` zaten bir ``BaseModel`` Ã¶rneÄŸi ise olduÄŸu gibi dÃ¶ner
    (tekrar doÄŸrulama yapÄ±lmaz). Aksi halde ``model.model_validate()``
    ile doÄŸrulama yapÄ±lÄ±r.

    Args:
        veri:   DoÄŸrulanacak ham veri (dict, JSON string, veya BaseModel).
        model:  Hedef Pydantic modeli.
        strict: KatÄ± mod (tip dÃ¶nÃ¼ÅŸÃ¼mÃ¼ yapma). VarsayÄ±lan: False.

    Returns:
        DoÄŸrulanmÄ±ÅŸ Pydantic model Ã¶rneÄŸi.

    Raises:
        ValidationError: Veri modele uymuyorsa.

    Ã–rnek:
        >>> sonuc = model_al({"konu": "test", "duygu": "pozitif"}, AnalizSonucu)
        >>> sonuc.duygu
        'pozitif'
    """
    if isinstance(veri, BaseModel):
        return veri  # type: ignore[return-value]
    return model.model_validate(veri, strict=strict)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# validated_tool â€” Pydantic ile DoÄŸrulayan AraÃ§ DekoratÃ¶rÃ¼
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ValidatedTool:
    """``@validated_tool`` dekoratÃ¶rÃ¼nÃ¼n dÃ¶ndÃ¼rdÃ¼ÄŸÃ¼ sarmalayÄ±cÄ± nesne.

    Bu sÄ±nÄ±f, bir fonksiyonu Pydantic doÄŸrulama ile sarmalar.
    ``schema`` parametresi verilmiÅŸse, fonksiyon Ã§aÄŸrÄ±lmadan Ã¶nce
    giriÅŸ parametreleri modele gÃ¶re doÄŸrulanÄ±r. ``output_schema``
    verilmiÅŸse, dÃ¶nÃ¼ÅŸ deÄŸeri modele gÃ¶re doÄŸrulanÄ±r.

    KullanÄ±cÄ± doÄŸrudan bu sÄ±nÄ±fla deÄŸil, ``@validated_tool``
    dekoratÃ¶rÃ¼ ile etkileÅŸir.
    """

    def __init__(
        self,
        fn: Callable[..., Any],
        schema: Optional[type[BaseModel]] = None,
        output_schema: Optional[type[BaseModel]] = None,
        arac_adi: Optional[str] = None,
        arac_aciklamasi: Optional[str] = None,
    ) -> None:
        """ValidatedTool baÅŸlatÄ±cÄ±.

        Args:
            fn:               SarÄ±lacak fonksiyon.
            schema:           GiriÅŸ validasyonu iÃ§in Pydantic modeli (opsiyonel).
            output_schema:    Ã‡Ä±kÄ±ÅŸ validasyonu iÃ§in Pydantic modeli (opsiyonel).
            arac_adi:         AraÃ§ adÄ± (None = fn.__name__).
            arac_aciklamasi:  AraÃ§ aÃ§Ä±klamasÄ± (None = fn.__doc__).
        """
        self._fn = fn
        self._schema = schema
        self._output_schema = output_schema
        self._arac_adi = arac_adi or fn.__name__
        self._arac_aciklamasi = arac_aciklamasi or fn.__doc__ or ""

        # Fonksiyon tip ipuÃ§larÄ±nÄ± oto-Ã§Ä±kar
        if schema is None:
            self._auto_schema: Optional[type[BaseModel]] = (
                self._tip_ipuclarindan_schema_olustur()
            )
        else:
            self._auto_schema = None

    @property
    def ad(self) -> str:
        """AraÃ§ adÄ±."""
        return self._arac_adi

    @property
    def aciklama(self) -> str:
        """AraÃ§ aÃ§Ä±klamasÄ±."""
        return self._arac_aciklamasi

    @property
    def schema(self) -> Optional[type[BaseModel]]:
        """KullanÄ±lan giriÅŸ validasyon modeli (varsa)."""
        return self._schema or self._auto_schema

    @property
    def output_schema(self) -> Optional[type[BaseModel]]:
        """KullanÄ±lan Ã§Ä±kÄ±ÅŸ validasyon modeli (varsa)."""
        return self._output_schema

    @property
    def json_schema(self) -> Optional[dict[str, Any]]:
        """GiriÅŸ validasyon ÅŸemasÄ± (JSON Schema formatÄ±nda)."""
        if self.schema:
            return json_schema_al(self.schema)
        return None

    @property
    def output_json_schema(self) -> Optional[dict[str, Any]]:
        """Ã‡Ä±kÄ±ÅŸ validasyon ÅŸemasÄ± (JSON Schema formatÄ±nda)."""
        if self._output_schema:
            return json_schema_al(self._output_schema)
        return None

    # â”€â”€ Oto-ÅŸema (tip ipuÃ§larÄ±ndan dinamik model) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _tip_ipuclarindan_schema_olustur(self) -> Optional[type[BaseModel]]:
        """Fonksiyon tip ipuÃ§larÄ±ndan otomatik Pydantic modeli oluÅŸturur.

        ``schema`` parametresi verilmemiÅŸse, fonksiyonun parametre
        tiplerinden (type hints) dinamik bir Pydantic modeli Ã¼retir.
        BÃ¶ylece ``@validated_tool`` sade dekoratÃ¶r olarak
        (parantezsiz) kullanÄ±ldÄ±ÄŸÄ±nda bile temel tip doÄŸrulamasÄ±
        yapÄ±labilir.

        Returns:
            Dinamik oluÅŸturulmuÅŸ Pydantic modeli veya None
            (tip ipuÃ§larÄ± yoksa veya Ã§Ä±karÄ±lamazsa).
        """
        try:
            hints = get_type_hints(self._fn)
        except Exception:
            return None

        # 'return' tipini Ã§Ä±kar
        hints.pop("return", None)

        if not hints:
            return None

        # Pydantic'nin create_model() fonksiyonu ile dinamik model
        from pydantic import create_model

        alanlar: dict[str, Any] = {}
        for param_ad, param_tip in hints.items():
            # Parametrenin varsayÄ±lan deÄŸeri var mÄ± kontrol et
            imza = inspect.signature(self._fn)
            param = imza.parameters.get(param_ad)
            if param is not None and param.default is not inspect.Parameter.empty:
                # VarsayÄ±lan deÄŸerli â†’ opsiyonel alan
                alanlar[param_ad] = (Optional[param_tip], param.default)  # noqa: UP045
            else:
                alanlar[param_ad] = (param_tip, ...)

        return create_model(
            f"{self._arac_adi.capitalize()}Parametre",
            **alanlar,
        )

    # â”€â”€ Ã‡aÄŸrÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Fonksiyonu doÄŸrulayarak Ã§aÄŸÄ±rÄ±r.

        1. GiriÅŸ validasyonu (schema varsa)
        2. AsÄ±l fonksiyon Ã§aÄŸrÄ±sÄ±
        3. Ã‡Ä±kÄ±ÅŸ validasyonu (output_schema varsa)
        4. ToolResult sarmalama

        Args:
            *args:   Pozisyonel argÃ¼manlar.
            **kwargs: Anahtar-deÄŸer argÃ¼manlarÄ±.

        Returns:
            ``ToolResult[T]`` â€” baÅŸarÄ±lÄ±/baÅŸarÄ±sÄ±z durum bilgisiyle.

        Raises:
            ValidationError: GiriÅŸ doÄŸrulamasÄ± baÅŸarÄ±sÄ±zsa (sadece
                             ``schema`` verilmiÅŸ ve ``raise_on_error=True``
                             ise; normalde hata ToolResult iÃ§inde dÃ¶ner).
        """
        # â”€â”€ 1. GiriÅŸ validasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        aktif_schema = self._schema or self._auto_schema

        if aktif_schema is not None:
            try:
                # kwargs iÃ§inden schema alanlarÄ±nÄ± filtrele
                # (sadece modelde tanÄ±mlÄ± alanlarÄ± geÃ§)
                model_alanlari = set(aktif_schema.model_fields.keys())
                uygun_kwargs = {k: v for k, v in kwargs.items() if k in model_alanlari}

                # EÄŸer hiÃ§ uygun kwargs yoksa ve tek bir pozisyonel
                # argÃ¼man varsa, onu doÄŸrudan model girdisi olarak al
                if not uygun_kwargs and len(args) == 1 and isinstance(args[0], dict):
                    uygun_kwargs = args[0]  # type: ignore[assignment]

                dogrulanmis = model_al(uygun_kwargs, aktif_schema)

                # DoÄŸrulanmÄ±ÅŸ veriyi kwargs'a dÃ¶nÃ¼ÅŸtÃ¼r
                # (model_validate dict dÃ¶ndÃ¼rmÃ¼yor, model Ã¶rneÄŸi dÃ¶ndÃ¼rÃ¼yor)
                kwargs.update(dogrulanmis.model_dump())
            except ValidationError as exc:
                logger.warning(
                    "[ValidatedTool:%s] GiriÅŸ validasyonu baÅŸarÄ±sÄ±z: %s",
                    self._arac_adi,
                    exc,
                )
                return ToolResult(
                    basarili=False,
                    hata=f"GiriÅŸ validasyonu baÅŸarÄ±sÄ±z: {exc}",
                    model=aktif_schema.__name__,
                )

        # â”€â”€ 2. AsÄ±l fonksiyon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        try:
            sonuc = self._fn(*args, **kwargs)
        except Exception as exc:
            logger.error(
                "[ValidatedTool:%s] Ã‡alÄ±ÅŸma hatasÄ±: %s",
                self._arac_adi,
                exc,
                exc_info=True,
            )
            return ToolResult(
                basarili=False,
                hata=str(exc),
                model=aktif_schema.__name__ if aktif_schema else "",
            )

        # â”€â”€ 3. Ã‡Ä±kÄ±ÅŸ validasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if self._output_schema is not None:
            try:
                # sonuÃ§ dict deÄŸilse doÄŸrudan model_validate ile dene
                if isinstance(sonuc, dict):
                    sonuc = model_al(sonuc, self._output_schema)
                elif not isinstance(sonuc, self._output_schema):
                    sonuc = self._output_schema.model_validate({"veri": sonuc})
            except ValidationError as exc:
                logger.warning(
                    "[ValidatedTool:%s] Ã‡Ä±kÄ±ÅŸ validasyonu baÅŸarÄ±sÄ±z: %s",
                    self._arac_adi,
                    exc,
                )
                return ToolResult(
                    basarili=False,
                    hata=f"Ã‡Ä±kÄ±ÅŸ validasyonu baÅŸarÄ±sÄ±z: {exc}",
                    model=self._output_schema.__name__,
                )

        # â”€â”€ 4. ToolResult sarmala â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if isinstance(sonuc, ToolResult):
            return sonuc

        return ToolResult(
            basarili=True,
            veri=sonuc,
            model=aktif_schema.__name__ if aktif_schema else "",
        )

    # â”€â”€ Pydantic-ai ile entegrasyon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def pydantic_ai_tool(self) -> dict[str, Any]:
        """Pydantic-ai ``Agent`` sÄ±nÄ±fÄ±na kaydedilebilir tool tanÄ±mÄ± Ã¼retir.

        Bu metot, ``@validated_tool`` ile sarmalanmÄ±ÅŸ bir fonksiyonu
        pydantic-ai'nin ``agent.tool()`` veya ``agent.register_tool()``
        mantÄ±ÄŸÄ±na uygun bir sÃ¶zlÃ¼ÄŸe dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r. Elle kayÄ±t iÃ§in
        kullanÄ±lÄ±r.

        Returns:
            ``{"name": ..., "description": ..., "parameters": ...}``
            ÅŸeklinde tool tanÄ±m sÃ¶zlÃ¼ÄŸÃ¼.
        """
        tool_def: dict[str, Any] = {
            "name": self._arac_adi,
            "description": self._arac_aciklamasi,
        }

        if self.json_schema:
            tool_def["parameters"] = self.json_schema

        return tool_def

    def __repr__(self) -> str:
        return (
            f"ValidatedTool(ad={self._arac_adi!r}, "
            f"schema={self._schema.__name__ if self._schema else 'auto'}, "
            f"output_schema={self._output_schema.__name__ if self._output_schema else None})"
        )


def validated_tool(
    fn: Optional[Callable[..., Any]] = None,
    *,
    schema: Optional[type[BaseModel]] = None,
    output_schema: Optional[type[BaseModel]] = None,
    arac_adi: Optional[str] = None,
    arac_aciklamasi: Optional[str] = None,
) -> Callable[..., Any]:
    """Pydantic validasyonu ekleyen araÃ§ (tool) dekoratÃ¶rÃ¼.

    ÃœÃ§ kullanÄ±m ÅŸekli vardÄ±r:

    **1) Sade dekoratÃ¶r (parantezsiz):**
        Fonksiyonun kendi tip ipuÃ§larÄ±ndan otomatik ÅŸema oluÅŸturur.

        .. code-block:: python

            @validated_tool
            def topla(a: int, b: int) -> int:
                return a + b

    **2) Parametreli dekoratÃ¶r:**
        Belli bir Pydantic modelini giriÅŸ ÅŸemasÄ± olarak kullanÄ±r.

        .. code-block:: python

            @validated_tool(schema=KullaniciMesaji)
            def mesaj_gonder(veri: KullaniciMesaji) -> ToolResult:
                ...

    **3) GiriÅŸ + Ã§Ä±kÄ±ÅŸ validasyonu:**
        Hem giriÅŸ hem Ã§Ä±kÄ±ÅŸ iÃ§in Pydantic modeli verilir.

        .. code-block:: python

            @validated_tool(schema=Sorgu, output_schema=Yanit)
            def sorgula(veri: Sorgu) -> Yanit:
                ...

    Args:
        fn:               SarÄ±lacak fonksiyon (sade dekoratÃ¶r modu).
        schema:           GiriÅŸ validasyon modeli (opsiyonel).
        output_schema:    Ã‡Ä±kÄ±ÅŸ validasyon modeli (opsiyonel).
        arac_adi:         AraÃ§ adÄ± (None = fn.__name__).
        arac_aciklamasi:  AraÃ§ aÃ§Ä±klamasÄ± (None = fn.__doc__).

    Returns:
        ``ValidatedTool`` Ã¶rneÄŸi (sarmalanmÄ±ÅŸ fonksiyon).
    """
    if fn is not None:
        # KullanÄ±m: @validated_tool  (parantezsiz)
        return ValidatedTool(fn)

    # KullanÄ±m: @validated_tool(schema=..., output_schema=...)
    def decorator(real_fn: Callable[..., Any]) -> ValidatedTool:
        return ValidatedTool(
            real_fn,
            schema=schema,
            output_schema=output_schema,
            arac_adi=arac_adi,
            arac_aciklamasi=arac_aciklamasi,
        )

    return decorator


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# StructuredOutput â€” LLM YapÄ±landÄ±rÄ±lmÄ±ÅŸ Ã‡Ä±ktÄ± YardÄ±mcÄ±sÄ±
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class StructuredOutput(Generic[ModelTipi]):
    """LLM'den yapÄ±landÄ±rÄ±lmÄ±ÅŸ (structured) Ã§Ä±ktÄ± almayÄ± kolaylaÅŸtÄ±rÄ±r.

    Pydantic AI'nÄ±n ``result_type`` parametresiyle uyumlu Ã§alÄ±ÅŸÄ±r:
    ``Agent(result_type=AnalizSonucu)`` ÅŸeklinde kullanÄ±ldÄ±ÄŸÄ±nda LLM,
    doÄŸrudan belirtilen Pydantic modeline uygun JSON Ã§Ä±ktÄ±sÄ± Ã¼retir.

    Bu sÄ±nÄ±f, manuel doÄŸrulama, dÃ¶nÃ¼ÅŸÃ¼m ve ÅŸema oluÅŸturma iÅŸlemlerini
    tek bir noktada toplar.

    KullanÄ±m:
        .. code-block:: python

            from pydantic import BaseModel, Field
            from typing import Literal

            class AnalizSonucu(BaseModel):
                konu: str
                duygu: Literal["pozitif", "negatif", "notr"]
                puan: int = Field(ge=0, le=100)

            # SeÃ§enek 1: Pydantic AI Agent ile
            # agent = Agent(..., result_type=AnalizSonucu)
            # yanit = agent.run("metni analiz et")

            # SeÃ§enek 2: Manuel doÄŸrulama
            ham_json = {"konu": "ReYMeN", "duygu": "pozitif", "puan": 95}
            sonuc = StructuredOutput.coerce(ham_json, AnalizSonucu)

            # SeÃ§enek 3: Åema bilgisi
            schema = StructuredOutput.schema_al(AnalizSonucu)
    """

    def __init__(self, model: ModelTipi):
        """StructuredOutput Ã¶rneÄŸi.

        Args:
            model: DoÄŸrulanmÄ±ÅŸ Pydantic model Ã¶rneÄŸi.
        """
        self._model = model

    @property
    def model(self) -> ModelTipi:
        """DoÄŸrulanmÄ±ÅŸ Pydantic model Ã¶rneÄŸi."""
        return self._model

    @property
    def dict(self) -> dict[str, Any]:
        """Model verisini sÃ¶zlÃ¼k olarak dÃ¶ndÃ¼rÃ¼r."""
        return self._model.model_dump()

    @property
    def json(self) -> str:
        """Model verisini JSON string olarak dÃ¶ndÃ¼rÃ¼r."""
        return self._model.model_dump_json()

    @classmethod
    def coerce(
        cls,
        veri: dict[str, Any] | Any,
        model: type[ModelTipi],
        strict: bool = False,
    ) -> StructuredOutput[ModelTipi]:
        """Ham veriyi doÄŸrular ve ``StructuredOutput`` olarak sarar.

        Args:
            veri:   Ham veri (dict, JSON, veya BaseModel).
            model:  Hedef Pydantic model sÄ±nÄ±fÄ±.
            strict: KatÄ± mod (tip dÃ¶nÃ¼ÅŸÃ¼mÃ¼ yapma).

        Returns:
            ``StructuredOutput[ModelTipi]`` Ã¶rneÄŸi.

        Raises:
            ValidationError: DoÄŸrulama baÅŸarÄ±sÄ±zsa.

        Ã–rnek:
            >>> sonuc = StructuredOutput.coerce(
            ...     {"konu": "test", "duygu": "pozitif", "puan": 90},
            ...     AnalizSonucu,
            ... )
            >>> sonuc.model.duygu
            'pozitif'
        """
        dogrulanmis = model_al(veri, model, strict=strict)
        return cls(dogrulanmis)

    @staticmethod
    def schema_al(model: type[BaseModel]) -> dict[str, Any]:
        """Bir Pydantic modelinin JSON Schema'sÄ±nÄ± dÃ¶ndÃ¼rÃ¼r.

        Bu ÅŸema, LLM'e ``response_format`` veya tool parametresi olarak
        gÃ¶nderilebilir.

        Args:
            model: Pydantic BaseModel alt sÄ±nÄ±fÄ±.

        Returns:
            JSON Schema sÃ¶zlÃ¼ÄŸÃ¼.
        """
        return json_schema_al(model)

    def __repr__(self) -> str:
        return f"StructuredOutput(model={self._model!r})"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Pydantic-ai Agent Entegrasyonu
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def build_pydantic_ai_tool(
    validated: ValidatedTool,
) -> dict[str, Any]:
    """``ValidatedTool`` Ã¶rneÄŸini pydantic-ai tool tanÄ±mÄ±na dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r.

    Pydantic-ai'nin ``Agent`` sÄ±nÄ±fÄ±na tool kaydetmek iÃ§in kullanÄ±lÄ±r:

    .. code-block:: python

        from pydantic_ai import Agent
        from reymen.core.type_safety import build_pydantic_ai_tool

        agent = Agent("openai:gpt-4o")
        tool_def = build_pydantic_ai_tool(mesaj_gonder)
        agent.register_tool(tool_def)  # (pydantic-ai API'sine baÄŸlÄ±)

    Args:
        validated: ``@validated_tool`` ile sarmalanmÄ±ÅŸ fonksiyon.

    Returns:
        Pydantic-ai uyumlu tool tanÄ±m sÃ¶zlÃ¼ÄŸÃ¼:
        ``{"name": ..., "description": ..., "parameters": ...}``
    """
    return validated.pydantic_ai_tool()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Test / Demo
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _demo() -> None:
    """``type_safety.py`` modÃ¼lÃ¼nÃ¼n temel iÅŸlevlerini test eder."""
    from pydantic import Field
    from typing import Literal

    print("â•â•â• ReYMeN Tip GÃ¼venliÄŸi (type_safety.py) Demo â•â•â•")
    print()

    # â”€â”€ 1. Sade dekoratÃ¶r â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    @validated_tool
    def topla(a: int, b: int) -> int:
        """Ä°ki sayÄ±yÄ± toplar."""
        return a + b

    print(f"[1] Sade dekoratÃ¶r: topla(3, 5) = {topla(3, 5)}")

    # â”€â”€ 2. Model ile validasyon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    class KullaniciMesaji(BaseModel):
        kullanici_id: str
        mesaj: str
        dil: str = "tr"

    @validated_tool(schema=KullaniciMesaji)
    def mesaj_gonder(kullanici_id: str, mesaj: str, dil: str = "tr") -> ToolResult:
        """KullanÄ±cÄ±ya mesaj gÃ¶nderir."""
        logger.info("Mesaj gonderiliyor: %s -> %s (%s)", mesaj, kullanici_id, dil)
        return ToolResult(
            basarili=True,
            veri={"hedef": kullanici_id, "mesaj": mesaj, "dil": dil},
        )

    sonuc = mesaj_gonder(kullanici_id="user_123", mesaj="Merhaba!")
    print(f"[2] Model validasyon: {sonuc}")

    # â”€â”€ 3. HatalÄ± giriÅŸ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    hata_sonuc = mesaj_gonder(mesaj="Eksik parametre")
    print(f"[3] Hata yakalama: {hata_sonuc}")

    # â”€â”€ 4. JSON ÅŸema â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    class AnalizSonucu(BaseModel):
        konu: str
        duygu: Literal["pozitif", "negatif", "notr"]
        puan: int = Field(ge=0, le=100)

    schema = json_schema_al(AnalizSonucu)
    print(f"[4] JSON Schema: {schema}")

    # â”€â”€ 5. StructuredOutput â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    ham_veri = {"konu": "ReYMeN", "duygu": "pozitif", "puan": 95}
    so = StructuredOutput.coerce(ham_veri, AnalizSonucu)
    print(f"[5] StructuredOutput: {so.model}")
    print(f"    JSON: {so.json}")
    print()

    print("â•â•â• Demo baÅŸarÄ±yla tamamlandÄ± â•â•â•")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _demo()
