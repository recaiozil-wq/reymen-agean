# -*- coding: utf-8 -*-
"""
type_safety.py — ReYMeN Tip Güvenliği Katmanı (Pydantic AI).

Pydantic AI (pydantic-ai) paketi üzerine inşa edilmiş, araç (tool)
çağrıları ve LLM yanıtları için giriş/çıkış doğrulama (validation)
altyapısı.

Sağladıkları:
  * @validated_tool(schema=...)  → Araç giriş/çıkış validasyonu
  * StructuredOutput             → LLM'den yapılandırılmış (Pydantic model) çıktı
  * ToolResult                   → Standart araç dönüş sarmalayıcısı
  * json_schema_al              → Pydantic model → JSON şema
  * model_al                    → JSON veri → Pydantic model (doğrulamalı)

Kullanım:
    from reymen.core.type_safety import validated_tool, ToolResult

    # 1) Basit validasyon
    @validated_tool
    def topla(a: int, b: int) -> int:
        return a + b

    # 2) Pydantic model ile giriş validasyonu
    class KullaniciMesaji(BaseModel):
        kullanici_id: str
        mesaj: str
        dil: str = "tr"

    @validated_tool(schema=KullaniciMesaji)
    def mesaj_gonder(veri: KullaniciMesaji) -> ToolResult:
        # veri.kullanici_id, veri.mesaj doğrulanmış şekilde gelir
        return ToolResult(
            basarili=True,
            veri={"mesaj": veri.mesaj, "hedef": veri.kullanici_id}
        )

    # 3) LLM yapılandırılmış çıktı
    class AnalizSonucu(BaseModel):
        konu: str
        duygu: Literal["pozitif", "negatif", "notr"]
        puan: int = Field(ge=0, le=100)

    sonuc: AnalizSonucu = StructuredOutput.coerce({"konu": "test", ...}, AnalizSonucu)

Tüm dokümantasyon Türkçe'dir.
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

# ── Genel Tip Sabitleri ───────────────────────────────────────────────

T = TypeVar("T")
"""Genel tip değişkeni — herhangi bir tip."""

ModelTipi = TypeVar("ModelTipi", bound=BaseModel)
"""Pydantic BaseModel alt sınıfları için tip değişkeni."""


# ═══════════════════════════════════════════════════════════════════════
# ToolResult — Standart Araç Dönüş Sarmalayıcısı
# ═══════════════════════════════════════════════════════════════════════


@dataclass
class ToolResult(Generic[T]):
    """Bir araç çağrısının standart dönüş sarmalayıcısı.

    Tüm araçlar (validated_tool ile sarmalanmış olsun ya da olmasın)
    bu yapıyı dönebilir. Böylece üst katman (motor, conversation_loop)
    her araçtan aynı şablonda yanıt alır.

    Args:
        basarili:  İşlem başarılı mı?
        veri:      Başarılı yanıt verisi (T tipi).
        hata:      Hata mesajı (başarısız ise doldurulur).
        model:     Kullanılan validasyon modeli adı (opsiyonel).
    """

    basarili: bool = True
    veri: Optional[T] = None
    hata: str = ""
    model: str = ""

    def __bool__(self) -> bool:
        """Doğrudan if kontrolü: ``if sonuc:`` şeklinde kullanım.

        Returns:
            ``basarili`` değerini döndürür.
        """
        return self.basarili


# ═══════════════════════════════════════════════════════════════════════
# JSON Şema ↔ Pydantic Model Dönüşümleri
# ═══════════════════════════════════════════════════════════════════════


def json_schema_al(model: type[BaseModel]) -> dict[str, Any]:
    """Bir Pydantic modelinden JSON Schema (draft-07) üretir.

    Bu şema, LLM'e tool parametresi veya yanıt formatı olarak
    gönderilebilir. Pydantic-ai'nin ``Agent`` sınıfı bu şemayı
    otomatik olarak tool tanımına ekler; bu fonksiyon elle kullanım
    veya harici sistemlerle entegrasyon içindir.

    Args:
        model: Pydantic BaseModel alt sınıfı (ör. ``KullaniciMesaji``).

    Returns:
        JSON Schema sözlüğü.

    Örnek:
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
    """Ham veriyi (dict veya JSON) Pydantic modeline dönüştürür ve doğrular.

    ``veri`` zaten bir ``BaseModel`` örneği ise olduğu gibi döner
    (tekrar doğrulama yapılmaz). Aksi halde ``model.model_validate()``
    ile doğrulama yapılır.

    Args:
        veri:   Doğrulanacak ham veri (dict, JSON string, veya BaseModel).
        model:  Hedef Pydantic modeli.
        strict: Katı mod (tip dönüşümü yapma). Varsayılan: False.

    Returns:
        Doğrulanmış Pydantic model örneği.

    Raises:
        ValidationError: Veri modele uymuyorsa.

    Örnek:
        >>> sonuc = model_al({"konu": "test", "duygu": "pozitif"}, AnalizSonucu)
        >>> sonuc.duygu
        'pozitif'
    """
    if isinstance(veri, BaseModel):
        return veri  # type: ignore[return-value]
    return model.model_validate(veri, strict=strict)


# ═══════════════════════════════════════════════════════════════════════
# validated_tool — Pydantic ile Doğrulayan Araç Dekoratörü
# ═══════════════════════════════════════════════════════════════════════


class ValidatedTool:
    """``@validated_tool`` dekoratörünün döndürdüğü sarmalayıcı nesne.

    Bu sınıf, bir fonksiyonu Pydantic doğrulama ile sarmalar.
    ``schema`` parametresi verilmişse, fonksiyon çağrılmadan önce
    giriş parametreleri modele göre doğrulanır. ``output_schema``
    verilmişse, dönüş değeri modele göre doğrulanır.

    Kullanıcı doğrudan bu sınıfla değil, ``@validated_tool``
    dekoratörü ile etkileşir.
    """

    def __init__(
        self,
        fn: Callable[..., Any],
        schema: Optional[type[BaseModel]] = None,
        output_schema: Optional[type[BaseModel]] = None,
        arac_adi: Optional[str] = None,
        arac_aciklamasi: Optional[str] = None,
    ) -> None:
        """ValidatedTool başlatıcı.

        Args:
            fn:               Sarılacak fonksiyon.
            schema:           Giriş validasyonu için Pydantic modeli (opsiyonel).
            output_schema:    Çıkış validasyonu için Pydantic modeli (opsiyonel).
            arac_adi:         Araç adı (None = fn.__name__).
            arac_aciklamasi:  Araç açıklaması (None = fn.__doc__).
        """
        self._fn = fn
        self._schema = schema
        self._output_schema = output_schema
        self._arac_adi = arac_adi or fn.__name__
        self._arac_aciklamasi = arac_aciklamasi or fn.__doc__ or ""

        # Fonksiyon tip ipuçlarını oto-çıkar
        if schema is None:
            self._auto_schema: Optional[type[BaseModel]] = self._tip_ipuclarindan_schema_olustur()
        else:
            self._auto_schema = None

    @property
    def ad(self) -> str:
        """Araç adı."""
        return self._arac_adi

    @property
    def aciklama(self) -> str:
        """Araç açıklaması."""
        return self._arac_aciklamasi

    @property
    def schema(self) -> Optional[type[BaseModel]]:
        """Kullanılan giriş validasyon modeli (varsa)."""
        return self._schema or self._auto_schema

    @property
    def output_schema(self) -> Optional[type[BaseModel]]:
        """Kullanılan çıkış validasyon modeli (varsa)."""
        return self._output_schema

    @property
    def json_schema(self) -> Optional[dict[str, Any]]:
        """Giriş validasyon şeması (JSON Schema formatında)."""
        if self.schema:
            return json_schema_al(self.schema)
        return None

    @property
    def output_json_schema(self) -> Optional[dict[str, Any]]:
        """Çıkış validasyon şeması (JSON Schema formatında)."""
        if self._output_schema:
            return json_schema_al(self._output_schema)
        return None

    # ── Oto-şema (tip ipuçlarından dinamik model) ───────────────────

    def _tip_ipuclarindan_schema_olustur(self) -> Optional[type[BaseModel]]:
        """Fonksiyon tip ipuçlarından otomatik Pydantic modeli oluşturur.

        ``schema`` parametresi verilmemişse, fonksiyonun parametre
        tiplerinden (type hints) dinamik bir Pydantic modeli üretir.
        Böylece ``@validated_tool`` sade dekoratör olarak
        (parantezsiz) kullanıldığında bile temel tip doğrulaması
        yapılabilir.

        Returns:
            Dinamik oluşturulmuş Pydantic modeli veya None
            (tip ipuçları yoksa veya çıkarılamazsa).
        """
        try:
            hints = get_type_hints(self._fn)
        except Exception:
            return None

        # 'return' tipini çıkar
        hints.pop("return", None)

        if not hints:
            return None

        # Pydantic'nin create_model() fonksiyonu ile dinamik model
        from pydantic import create_model

        alanlar: dict[str, Any] = {}
        for param_ad, param_tip in hints.items():
            # Parametrenin varsayılan değeri var mı kontrol et
            imza = inspect.signature(self._fn)
            param = imza.parameters.get(param_ad)
            if param is not None and param.default is not inspect.Parameter.empty:
                # Varsayılan değerli → opsiyonel alan
                alanlar[param_ad] = (Optional[param_tip], param.default)  # noqa: UP045
            else:
                alanlar[param_ad] = (param_tip, ...)

        return create_model(
            f"{self._arac_adi.capitalize()}Parametre",
            **alanlar,
        )

    # ── Çağrı ───────────────────────────────────────────────────────

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Fonksiyonu doğrulayarak çağırır.

        1. Giriş validasyonu (schema varsa)
        2. Asıl fonksiyon çağrısı
        3. Çıkış validasyonu (output_schema varsa)
        4. ToolResult sarmalama

        Args:
            *args:   Pozisyonel argümanlar.
            **kwargs: Anahtar-değer argümanları.

        Returns:
            ``ToolResult[T]`` — başarılı/başarısız durum bilgisiyle.

        Raises:
            ValidationError: Giriş doğrulaması başarısızsa (sadece
                             ``schema`` verilmiş ve ``raise_on_error=True``
                             ise; normalde hata ToolResult içinde döner).
        """
        # ── 1. Giriş validasyonu ────────────────────────────────
        aktif_schema = self._schema or self._auto_schema

        if aktif_schema is not None:
            try:
                # kwargs içinden schema alanlarını filtrele
                # (sadece modelde tanımlı alanları geç)
                model_alanlari = set(aktif_schema.model_fields.keys())
                uygun_kwargs = {
                    k: v for k, v in kwargs.items() if k in model_alanlari
                }

                # Eğer hiç uygun kwargs yoksa ve tek bir pozisyonel
                # argüman varsa, onu doğrudan model girdisi olarak al
                if not uygun_kwargs and len(args) == 1 and isinstance(args[0], dict):
                    uygun_kwargs = args[0]  # type: ignore[assignment]

                dogrulanmis = model_al(uygun_kwargs, aktif_schema)

                # Doğrulanmış veriyi kwargs'a dönüştür
                # (model_validate dict döndürmüyor, model örneği döndürüyor)
                kwargs.update(dogrulanmis.model_dump())
            except ValidationError as exc:
                logger.warning(
                    "[ValidatedTool:%s] Giriş validasyonu başarısız: %s",
                    self._arac_adi, exc,
                )
                return ToolResult(
                    basarili=False,
                    hata=f"Giriş validasyonu başarısız: {exc}",
                    model=aktif_schema.__name__,
                )

        # ── 2. Asıl fonksiyon ───────────────────────────────────
        try:
            sonuc = self._fn(*args, **kwargs)
        except Exception as exc:
            logger.error(
                "[ValidatedTool:%s] Çalışma hatası: %s",
                self._arac_adi, exc, exc_info=True,
            )
            return ToolResult(
                basarili=False,
                hata=str(exc),
                model=aktif_schema.__name__ if aktif_schema else "",
            )

        # ── 3. Çıkış validasyonu ───────────────────────────────
        if self._output_schema is not None:
            try:
                # sonuç dict değilse doğrudan model_validate ile dene
                if isinstance(sonuc, dict):
                    sonuc = model_al(sonuc, self._output_schema)
                elif not isinstance(sonuc, self._output_schema):
                    sonuc = self._output_schema.model_validate({"veri": sonuc})
            except ValidationError as exc:
                logger.warning(
                    "[ValidatedTool:%s] Çıkış validasyonu başarısız: %s",
                    self._arac_adi, exc,
                )
                return ToolResult(
                    basarili=False,
                    hata=f"Çıkış validasyonu başarısız: {exc}",
                    model=self._output_schema.__name__,
                )

        # ── 4. ToolResult sarmala ──────────────────────────────
        if isinstance(sonuc, ToolResult):
            return sonuc

        return ToolResult(
            basarili=True,
            veri=sonuc,
            model=aktif_schema.__name__ if aktif_schema else "",
        )

    # ── Pydantic-ai ile entegrasyon ──────────────────────────────

    def pydantic_ai_tool(self) -> dict[str, Any]:
        """Pydantic-ai ``Agent`` sınıfına kaydedilebilir tool tanımı üretir.

        Bu metot, ``@validated_tool`` ile sarmalanmış bir fonksiyonu
        pydantic-ai'nin ``agent.tool()`` veya ``agent.register_tool()``
        mantığına uygun bir sözlüğe dönüştürür. Elle kayıt için
        kullanılır.

        Returns:
            ``{"name": ..., "description": ..., "parameters": ...}``
            şeklinde tool tanım sözlüğü.
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
    """Pydantic validasyonu ekleyen araç (tool) dekoratörü.

    Üç kullanım şekli vardır:

    **1) Sade dekoratör (parantezsiz):**
        Fonksiyonun kendi tip ipuçlarından otomatik şema oluşturur.

        .. code-block:: python

            @validated_tool
            def topla(a: int, b: int) -> int:
                return a + b

    **2) Parametreli dekoratör:**
        Belli bir Pydantic modelini giriş şeması olarak kullanır.

        .. code-block:: python

            @validated_tool(schema=KullaniciMesaji)
            def mesaj_gonder(veri: KullaniciMesaji) -> ToolResult:
                ...

    **3) Giriş + çıkış validasyonu:**
        Hem giriş hem çıkış için Pydantic modeli verilir.

        .. code-block:: python

            @validated_tool(schema=Sorgu, output_schema=Yanit)
            def sorgula(veri: Sorgu) -> Yanit:
                ...

    Args:
        fn:               Sarılacak fonksiyon (sade dekoratör modu).
        schema:           Giriş validasyon modeli (opsiyonel).
        output_schema:    Çıkış validasyon modeli (opsiyonel).
        arac_adi:         Araç adı (None = fn.__name__).
        arac_aciklamasi:  Araç açıklaması (None = fn.__doc__).

    Returns:
        ``ValidatedTool`` örneği (sarmalanmış fonksiyon).
    """
    if fn is not None:
        # Kullanım: @validated_tool  (parantezsiz)
        return ValidatedTool(fn)

    # Kullanım: @validated_tool(schema=..., output_schema=...)
    def decorator(real_fn: Callable[..., Any]) -> ValidatedTool:
        return ValidatedTool(
            real_fn,
            schema=schema,
            output_schema=output_schema,
            arac_adi=arac_adi,
            arac_aciklamasi=arac_aciklamasi,
        )

    return decorator


# ═══════════════════════════════════════════════════════════════════════
# StructuredOutput — LLM Yapılandırılmış Çıktı Yardımcısı
# ═══════════════════════════════════════════════════════════════════════


class StructuredOutput(Generic[ModelTipi]):
    """LLM'den yapılandırılmış (structured) çıktı almayı kolaylaştırır.

    Pydantic AI'nın ``result_type`` parametresiyle uyumlu çalışır:
    ``Agent(result_type=AnalizSonucu)`` şeklinde kullanıldığında LLM,
    doğrudan belirtilen Pydantic modeline uygun JSON çıktısı üretir.

    Bu sınıf, manuel doğrulama, dönüşüm ve şema oluşturma işlemlerini
    tek bir noktada toplar.

    Kullanım:
        .. code-block:: python

            from pydantic import BaseModel, Field
            from typing import Literal

            class AnalizSonucu(BaseModel):
                konu: str
                duygu: Literal["pozitif", "negatif", "notr"]
                puan: int = Field(ge=0, le=100)

            # Seçenek 1: Pydantic AI Agent ile
            # agent = Agent(..., result_type=AnalizSonucu)
            # yanit = agent.run("metni analiz et")

            # Seçenek 2: Manuel doğrulama
            ham_json = {"konu": "ReYMeN", "duygu": "pozitif", "puan": 95}
            sonuc = StructuredOutput.coerce(ham_json, AnalizSonucu)

            # Seçenek 3: Şema bilgisi
            schema = StructuredOutput.schema_al(AnalizSonucu)
    """

    def __init__(self, model: ModelTipi):
        """StructuredOutput örneği.

        Args:
            model: Doğrulanmış Pydantic model örneği.
        """
        self._model = model

    @property
    def model(self) -> ModelTipi:
        """Doğrulanmış Pydantic model örneği."""
        return self._model

    @property
    def dict(self) -> dict[str, Any]:
        """Model verisini sözlük olarak döndürür."""
        return self._model.model_dump()

    @property
    def json(self) -> str:
        """Model verisini JSON string olarak döndürür."""
        return self._model.model_dump_json()

    @classmethod
    def coerce(
        cls,
        veri: dict[str, Any] | Any,
        model: type[ModelTipi],
        strict: bool = False,
    ) -> StructuredOutput[ModelTipi]:
        """Ham veriyi doğrular ve ``StructuredOutput`` olarak sarar.

        Args:
            veri:   Ham veri (dict, JSON, veya BaseModel).
            model:  Hedef Pydantic model sınıfı.
            strict: Katı mod (tip dönüşümü yapma).

        Returns:
            ``StructuredOutput[ModelTipi]`` örneği.

        Raises:
            ValidationError: Doğrulama başarısızsa.

        Örnek:
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
        """Bir Pydantic modelinin JSON Schema'sını döndürür.

        Bu şema, LLM'e ``response_format`` veya tool parametresi olarak
        gönderilebilir.

        Args:
            model: Pydantic BaseModel alt sınıfı.

        Returns:
            JSON Schema sözlüğü.
        """
        return json_schema_al(model)

    def __repr__(self) -> str:
        return f"StructuredOutput(model={self._model!r})"


# ═══════════════════════════════════════════════════════════════════════
# Pydantic-ai Agent Entegrasyonu
# ═══════════════════════════════════════════════════════════════════════


def build_pydantic_ai_tool(
    validated: ValidatedTool,
) -> dict[str, Any]:
    """``ValidatedTool`` örneğini pydantic-ai tool tanımına dönüştürür.

    Pydantic-ai'nin ``Agent`` sınıfına tool kaydetmek için kullanılır:

    .. code-block:: python

        from pydantic_ai import Agent
        from reymen.core.type_safety import build_pydantic_ai_tool

        agent = Agent("openai:gpt-4o")
        tool_def = build_pydantic_ai_tool(mesaj_gonder)
        agent.register_tool(tool_def)  # (pydantic-ai API'sine bağlı)

    Args:
        validated: ``@validated_tool`` ile sarmalanmış fonksiyon.

    Returns:
        Pydantic-ai uyumlu tool tanım sözlüğü:
        ``{"name": ..., "description": ..., "parameters": ...}``
    """
    return validated.pydantic_ai_tool()


# ═══════════════════════════════════════════════════════════════════════
# Test / Demo
# ═══════════════════════════════════════════════════════════════════════


def _demo() -> None:
    """``type_safety.py`` modülünün temel işlevlerini test eder."""
    from pydantic import Field
    from typing import Literal

    print("═══ ReYMeN Tip Güvenliği (type_safety.py) Demo ═══")
    print()

    # ── 1. Sade dekoratör ──────────────────────────────────────
    @validated_tool
    def topla(a: int, b: int) -> int:
        """İki sayıyı toplar."""
        return a + b

    print(f"[1] Sade dekoratör: topla(3, 5) = {topla(3, 5)}")

    # ── 2. Model ile validasyon ────────────────────────────────
    class KullaniciMesaji(BaseModel):
        kullanici_id: str
        mesaj: str
        dil: str = "tr"

    @validated_tool(schema=KullaniciMesaji)
    def mesaj_gonder(kullanici_id: str, mesaj: str, dil: str = "tr") -> ToolResult:
        """Kullanıcıya mesaj gönderir."""
        logger.info("Mesaj gonderiliyor: %s -> %s (%s)", mesaj, kullanici_id, dil)
        return ToolResult(
            basarili=True,
            veri={"hedef": kullanici_id, "mesaj": mesaj, "dil": dil},
        )

    sonuc = mesaj_gonder(kullanici_id="user_123", mesaj="Merhaba!")
    print(f"[2] Model validasyon: {sonuc}")

    # ── 3. Hatalı giriş ────────────────────────────────────────
    hata_sonuc = mesaj_gonder(mesaj="Eksik parametre")
    print(f"[3] Hata yakalama: {hata_sonuc}")

    # ── 4. JSON şema ───────────────────────────────────────────
    class AnalizSonucu(BaseModel):
        konu: str
        duygu: Literal["pozitif", "negatif", "notr"]
        puan: int = Field(ge=0, le=100)

    schema = json_schema_al(AnalizSonucu)
    print(f"[4] JSON Schema: {schema}")

    # ── 5. StructuredOutput ────────────────────────────────────
    ham_veri = {"konu": "ReYMeN", "duygu": "pozitif", "puan": 95}
    so = StructuredOutput.coerce(ham_veri, AnalizSonucu)
    print(f"[5] StructuredOutput: {so.model}")
    print(f"    JSON: {so.json}")
    print()

    print("═══ Demo başarıyla tamamlandı ═══")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _demo()
