# -*- coding: utf-8 -*-
"""
provider_plugin_base.py — ReYMeN Provider Plugin Base.

Soyut temel sinif (ABC): `ProviderPluginBase`.

Provider plugin'leri, bir dis hizmete (API, veritabani, model,
donanim vb.) erisim saglayan eklentilerdir. Bu sinif, tum provider
plugin'lerinin uymasi gereken asgari ara yuzu (contract) tanimlar.

Kullanim:
    class MyProvider(ProviderPluginBase):
        name = "my_provider"
        version = "1.0.0"

        def init(self, config: dict | None = None) -> bool:
            ...
        def health_check(self) -> dict:
            ...
        def shutdown(self) -> None:
            ...
"""

from __future__ import annotations

import abc
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ProviderPluginBase(abc.ABC):
    """Provider plugin'leri icin soyut temel sinif.

    Tum provider plugin'leri bu siniftan turemelidir ve asagidaki
    ozellik/metotlari uygulamalidir.

    Attributes:
        name: Provider'in benzersiz adi (ornek: "openai", "postgresql").
        version: Provider surum numarasi.
    """

    # ── Zorunlu sinif ozellikleri (override edilmelidir) ──────────────────
    name: str = ""
    version: str = ""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Alt sinif olusturulurken name ve version kontrolu."""
        super().__init_subclass__(**kwargs)
        if not cls.name:
            raise TypeError(
                f"{cls.__name__} must define a non-empty 'name' class attribute."
            )
        if not cls.version:
            raise TypeError(
                f"{cls.__name__} must define a non-empty 'version' class attribute."
        )

    # ── Zorunlu metotlar ──────────────────────────────────────────────────

    @abc.abstractmethod
    def init(self, config: dict | None = None) -> bool:
        """Provider'i baslat / yapilandir.

        Args:
            config: Yapilandirma sozlugu (API anahtari, URL, timeout vb.).

        Returns:
            Basarili ise True, basarisiz ise False.
        """
        ...

    @abc.abstractmethod
    def health_check(self) -> dict:
        """Provider'in saglik kontrolu.

        Returns:
            En az su anahtarlari iceren bir sozluk:
              - "status": "ok", "degraded" veya "down"
              - "latency_ms": Yanit suresi (milisaniye, mumkunse)
              - "message": Aciklama (opsiyonel)
        """
        ...

    @abc.abstractmethod
    def shutdown(self) -> None:
        """Provider'i guvenli sekilde kapat.

        Kaynaklari serbest birakir, baglantilari kapatir.
        """
        ...

    # ── Opsiyonel yardimci metotlar ───────────────────────────────────────

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r} version={self.version!r}>"

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"
