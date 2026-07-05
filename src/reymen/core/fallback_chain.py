# -*- coding: utf-8 -*-
"""FallbackChain — provider1 hata → provider2 → ... → son.

Ornek:
    chain = FallbackChain([
        ("deepseek", DeepSeekAdapter(key, "deepseek-chat")),
        ("openrouter", OpenRouterAdapter(key, "openai/gpt-4o-mini")),
        ("lmstudio", LMStudioAdapter()),
    ])
    sonuc = chain.cagri_yap(messages)
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

log = logging.getLogger(__name__)


class FallbackChain:
    """Provider zinciri — sirayla dene, ilk basarili donene kadar devam et."""

    def __init__(self, provider_list: List[Tuple[str, Any]]):
        """
        Args:
            provider_list: [(etiket, adapter_nesnesi), ...]
                Her adapter'da .cagri_yap(messages, **kwargs) -> dict
                ve .kontrol() -> bool olmali.
        """
        self.providers = provider_list

    def cagri_yap(self, messages: list, **kwargs) -> Dict[str, Any]:
        """Provider'lari sirayla dene. Ilk basarili sonucu don."""
        son_hata = None
        for etiket, adapter in self.providers:
            try:
                log.info("FallbackChain: %s deneniyor...", etiket)
                sonuc = adapter.cagri_yap(messages, **kwargs)
                if sonuc.get("basarili"):
                    log.info("FallbackChain: %s basarili", etiket)
                    sonuc["provider"] = etiket
                    return sonuc
                else:
                    kod = sonuc.get("kod", "?")
                    hata = sonuc.get("hata", "bilinmiyor")
                    log.warning("FallbackChain: %s basarisiz (kod=%s): %s", etiket, kod, hata)
                    son_hata = sonuc
            except Exception as e:
                log.warning("FallbackChain: %s exception: %s", etiket, e)
                son_hata = {"basarili": False, "hata": str(e), "provider": etiket}

        log.error("FallbackChain: TUM provider'lar basarisiz")
        return son_hata or {"basarili": False, "hata": "tum_providerlar_basarisiz"}

    def saglik_kontrolu(self) -> List[Tuple[str, bool]]:
        """Tum provider'lari kontrol et, (etiket, calisiyor_mu) listesi don."""
        sonuclar = []
        for etiket, adapter in self.providers:
            try:
                calisiyor = adapter.kontrol()
            except Exception:
                calisiyor = False
            sonuclar.append((etiket, calisiyor))
        return sonuclar
