# -*- coding: utf-8 -*-
"""
provider_abstraction.py â€” ReYMeN SaÄŸlayÄ±cÄ± Soyutlama KatmanÄ± (cereyan).

KullanÄ±cÄ± config.yaml'da sadece:
    model:
      provider: deepseek  # deepseek|openai|anthropic|xai|openrouter
      model: deepseek-v4-flash

ile tek satÄ±rda model saÄŸlayÄ±cÄ± deÄŸiÅŸtirebilir.

SaÄŸlayÄ±cÄ±lar:
    DeepSeek  â†’ api.deepseek.com
    OpenAI    â†’ api.openai.com
    Anthropic â†’ api.anthropic.com  (Messages API)
    xAI       â†’ api.x.ai
    OpenRouter â†’ openrouter.ai/api

API anahtarÄ± arama sÄ±rasÄ± (provider_abstraction.py):
    1. .env / os.environ
    2. config.yaml providers.<name>.api_key
    3. credential_pool (reymen.sistem.credential_persistence)
    4. Her profil .env'si (AppData/Local/reymen/profiles/<profil>/.env)

TÃ¼m dokÃ¼mantasyon TÃ¼rkÃ§e'dir.
"""

from __future__ import annotations

import abc
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Generator, Optional

import requests

logger = logging.getLogger(__name__)

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_TIMEOUT_SANIYE: int = 300
_VARSAYILAN_MAX_TOKEN: int = 4096
_VARSAYILAN_SICAKLIK: float = 0.7


# â”€â”€ Veri YapÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class ProviderYanit:
    """SaÄŸlayÄ±cÄ±dan dÃ¶nen yanÄ±t.

    Attributes:
        metin:      LLM yanÄ±t metni.
        provider:   KullanÄ±lan saÄŸlayÄ±cÄ± adÄ±.
        model:      KullanÄ±lan model adÄ±.
        sure_sn:    Ä°stek sÃ¼resi (saniye).
        basarili:   BaÅŸarÄ±lÄ± mÄ±?
        hata:       Hata mesajÄ± (baÅŸarÄ±sÄ±zsa).
    """

    metin: str = ""
    provider: str = ""
    model: str = ""
    sure_sn: float = 0.0
    basarili: bool = True
    hata: str = ""


# â”€â”€ Hata SÄ±nÄ±flarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class ProviderHatasi(Exception):
    """SaÄŸlayÄ±cÄ± Ã§aÄŸrÄ±larÄ± sÄ±rasÄ±nda oluÅŸan genel hata."""

    pass


class ProviderGecersizKey(ProviderHatasi):
    """API anahtarÄ± geÃ§ersiz (401/403)."""

    pass


class ProviderKrediBitti(ProviderHatasi):
    """402 Payment Required â€” kredi bitti."""

    pass


class ProviderRateLimit(ProviderHatasi):
    """429 â€” hÄ±z sÄ±nÄ±rÄ± aÅŸÄ±ldÄ±."""

    pass


class ProviderZamanAsimi(ProviderHatasi):
    """Ä°stek zaman aÅŸÄ±mÄ±."""

    pass


# â”€â”€ API AnahtarÄ± Bulucu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Provider â†’ env deÄŸiÅŸken adlarÄ± (beyin.py ile uyumlu)
_PROVIDER_ENV: dict[str, str] = {
    "deepseek": "DEEPSEEK_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "xai": "XAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def _anahtar_bul(provider: str, config: dict[str, Any]) -> str:
    """API anahtarÄ±nÄ± sÄ±rayla dener: os.environ â†’ config â†’ credential_pool.

    Args:
        provider: SaÄŸlayÄ±cÄ± adÄ± (Ã¶r. "deepseek").
        config:   config.yaml'nin tamamÄ± (veya providers sÃ¶zlÃ¼ÄŸÃ¼).

    Returns:
        Bulunan anahtar ya da "".
    """
    env_adi = _PROVIDER_ENV.get(provider)

    # 1. os.environ / .env
    if env_adi:
        deger = os.environ.get(env_adi, "")
        if deger and not deger.startswith("***"):
            return deger

    # 2. config.yaml providers.<name>.api_key
    prov_conf = (config.get("providers", {}) if isinstance(config, dict) else {}).get(
        provider, {}
    )
    deger = prov_conf.get("api_key", "")
    if deger and not deger.startswith("***"):
        return deger

    # 3. credential_pool (opsiyonel)
    try:
        from reymen.sistem.credential_persistence import credential_pool  # type: ignore[import]

        if env_adi and hasattr(credential_pool, "anahtar_al"):
            deger = credential_pool.anahtar_al(env_adi)  # type: ignore[union-attr]
            if deger:
                return deger
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")

    try:
        from reymen.sistem.credential_pool import credential_pool  # type: ignore[import]

        if env_adi and hasattr(credential_pool, "anahtar_al"):
            deger = credential_pool.anahtar_al(env_adi)  # type: ignore[union-attr]
            if deger:
                return deger
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")

    # 4. WCM / profil .env'si â€” zaten os.environ'a yÃ¼klenmiÅŸ olmalÄ±
    # (profil .env'si ReYMeN tarafÄ±ndan os.environ'a eklenir)

    return ""


# â”€â”€ Temel SÄ±nÄ±f â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class ProviderBase(abc.ABC):
    """TÃ¼m saÄŸlayÄ±cÄ±larÄ±n tÃ¼remesi gereken soyut temel sÄ±nÄ±f.

    Alt sÄ±nÄ±flar tanÄ±mlamalÄ±:
        ad:               SaÄŸlayÄ±cÄ± kÄ±sa adÄ± (Ã¶r. "deepseek").
        varsayilan_model: VarsayÄ±lan model adÄ±.
        varsayilan_url:   VarsayÄ±lan API base URL.
        api_key_env:      Ortam deÄŸiÅŸkeni adÄ±.

    KullanÄ±ma hazÄ±r:
        chat(mesajlar, sistem_prompt) â†’ ProviderYanit
        chat_stream(...) â†’ Generator[str, None, ProviderYanit]
    """

    ad: str = ""
    varsayilan_model: str = ""
    varsayilan_url: str = ""
    api_key_env: str = ""
    api_key_gerekli: bool = True

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        """SaÄŸlayÄ±cÄ± Ã¶rneÄŸini baÅŸlatÄ±r.

        Args:
            model:    Model adÄ± (None = varsayÄ±lan).
            base_url: API base URL (None = varsayÄ±lan).
            api_key:  API anahtarÄ± (None = otomatik bul).
            config:   config.yaml sÃ¶zlÃ¼ÄŸÃ¼ (anahtar aramasÄ± iÃ§in).
        """
        self._model = model or self.varsayilan_model
        self._base_url = (base_url or self.varsayilan_url).rstrip("/")
        self._config = config or {}

        if api_key:
            self._api_key = api_key
        else:
            self._api_key = _anahtar_bul(self.ad, self._config)

    @property
    def model(self) -> str:
        return self._model

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def api_key(self) -> str:
        return self._api_key

    def hazir_mi(self) -> bool:
        """API anahtarÄ± mevcut mu?"""
        if self.api_key_gerekli and not self._api_key:
            logger.debug("[%s] API anahtari eksik (env: %s)", self.ad, self.api_key_env)
            return False
        return True

    # â”€â”€ Soyut metotlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @abc.abstractmethod
    def _api_istek(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """Ham API Ã§aÄŸrÄ±sÄ± â€” alt sÄ±nÄ±flar uygulamalÄ±."""
        ...

    @abc.abstractmethod
    def _api_istek_stream(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> Generator[str, None, ProviderYanit]:
        """Streaming API Ã§aÄŸrÄ±sÄ± â€” alt sÄ±nÄ±flar uygulamalÄ±."""
        ...
        # yield ''  # noqa  â€” Generator olduÄŸu iÃ§in dummy yield
        if False:
            yield ""

    # â”€â”€ Hata sÄ±nÄ±flandÄ±rma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @staticmethod
    def _hatayi_siniflandir(hata: Exception) -> ProviderHatasi:
        """HTTP hatasÄ±nÄ± tÃ¼rÃ¼ne gÃ¶re sÄ±nÄ±flandÄ±rÄ±r."""
        mesaj = str(hata).lower()
        try:
            resp = getattr(hata, "response", None)
            if resp is not None:
                kod = resp.status_code
                if kod == 401:
                    return ProviderGecersizKey(f"Yetkisiz (401): {hata}")
                elif kod == 402:
                    return ProviderKrediBitti(f"Kredi bitti (402): {hata}")
                elif kod == 403:
                    return ProviderGecersizKey(f"EriÅŸim reddedildi (403): {hata}")
                elif kod == 429:
                    return ProviderRateLimit(f"HÄ±z sÄ±nÄ±rÄ± (429): {hata}")
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        if "401" in mesaj or "unauthorized" in mesaj:
            return ProviderGecersizKey(str(hata))
        elif "402" in mesaj or "payment required" in mesaj:
            return ProviderKrediBitti(str(hata))
        elif "403" in mesaj or "forbidden" in mesaj:
            return ProviderGecersizKey(str(hata))
        elif "429" in mesaj or "rate limit" in mesaj or "too many requests" in mesaj:
            return ProviderRateLimit(str(hata))
        elif "timeout" in mesaj or "timed out" in mesaj:
            return ProviderZamanAsimi(str(hata))
        return ProviderHatasi(str(hata))

    # â”€â”€ YÃ¼ksek seviye API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def chat(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """LLM'den yanÄ±t Ã¼retir.

        Args:
            mesajlar:      [{"role": "user", "content": "..."}, ...]
            sistem_prompt: Sistem talimatÄ±.
            **kwargs:      temperature, max_tokens, model override.

        Returns:
            ProviderYanit.
        """
        if not self.hazir_mi():
            return ProviderYanit(
                metin="",
                provider=self.ad,
                model=self._model,
                basarili=False,
                hata=f"{self.ad}: API anahtari eksik",
            )
        try:
            t0 = time.monotonic()
            yanit = self._api_istek(mesajlar, sistem_prompt, **kwargs)
            yanit.sure_sn = time.monotonic() - t0
            return yanit
        except Exception as e:
            return ProviderYanit(
                metin="",
                provider=self.ad,
                model=self._model,
                basarili=False,
                hata=str(e),
            )

    def chat_stream(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> Generator[str, None, ProviderYanit]:
        """Streaming LLM yanÄ±tÄ± â€” token token yield eder."""
        if not self.hazir_mi():
            yield ProviderYanit(
                metin="",
                provider=self.ad,
                model=self._model,
                basarili=False,
                hata=f"{self.ad}: API anahtari eksik",
            )
            return
        try:
            yield from self._api_istek_stream(mesajlar, sistem_prompt, **kwargs)
        except Exception as e:
            yanit = ProviderYanit(
                metin="",
                provider=self.ad,
                model=self._model,
                basarili=False,
                hata=str(e),
            )
            return yanit


# â”€â”€ OpenAI-uyumlu SaÄŸlayÄ±cÄ± (ortak taban) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class OpenAIUyumluProvider(ProviderBase):
    """OpenAI /v1/chat/completions endpoint'ine istek atan ortak sÄ±nÄ±f.

    deepseek, openai, xai, openrouter gibi tÃ¼m OpenAI-uyumlu saÄŸlayÄ±cÄ±lar
    bu sÄ±nÄ±fÄ± kullanÄ±r â€” sadece ad, varsayilan_model, varsayilan_url ve
    api_key_env deÄŸerlerini tanÄ±mlarlar.
    """

    api_key_gerekli = True

    def _api_istek(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        model = kwargs.get("model", self._model)
        temperature = kwargs.get("temperature", _VARSAYILAN_SICAKLIK)
        max_tokens = kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN)

        url = f"{self._base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar,
            "stream": False,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=_TIMEOUT_SANIYE)
        r.raise_for_status()
        veri = r.json()
        metin = veri["choices"][0]["message"]["content"] or ""
        return ProviderYanit(
            metin=metin,
            provider=self.ad,
            model=model,
        )

    def _api_istek_stream(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> Generator[str, None, ProviderYanit]:
        model = kwargs.get("model", self._model)
        temperature = kwargs.get("temperature", _VARSAYILAN_SICAKLIK)
        max_tokens = kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN)

        url = f"{self._base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        son_yanit = ProviderYanit(provider=self.ad, model=model)
        with requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=_TIMEOUT_SANIYE,
        ) as r:
            r.raise_for_status()
            metin_parcalari: list[str] = []
            for satir in r.iter_lines():
                if not satir:
                    continue
                satir_str = satir.decode("utf-8", errors="replace")
                if not satir_str.startswith("data: "):
                    continue
                veri = satir_str[6:]
                if veri.strip() == "[DONE]":
                    break
                try:
                    parcali = json.loads(veri)
                    delta = parcali["choices"][0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        metin_parcalari.append(token)
                        yield token
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
        son_yanit.metin = "".join(metin_parcalari)
        return son_yanit


# â”€â”€ SaÄŸlayÄ±cÄ± SÄ±nÄ±flarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class DeepseekProvider(OpenAIUyumluProvider):
    ad = "deepseek"
    varsayilan_model = "deepseek-chat"
    varsayilan_url = "https://api.deepseek.com"
    api_key_env = "DEEPSEEK_API_KEY"


class OpenAIProvider(OpenAIUyumluProvider):
    ad = "openai"
    varsayilan_model = "gpt-4o-mini"
    varsayilan_url = "https://api.openai.com"
    api_key_env = "OPENAI_API_KEY"


class XAIProvider(OpenAIUyumluProvider):
    ad = "xai"
    varsayilan_model = "grok-2-latest"
    varsayilan_url = "https://api.x.ai"
    api_key_env = "XAI_API_KEY"


class OpenRouterProvider(OpenAIUyumluProvider):
    ad = "openrouter"
    varsayilan_model = "deepseek/deepseek-chat"
    varsayilan_url = "https://openrouter.ai/api"
    api_key_env = "OPENROUTER_API_KEY"


class AnthropicProvider(ProviderBase):
    """Anthropic Messages API kullanÄ±r (OpenAI uyumlu deÄŸil)."""

    ad = "anthropic"
    varsayilan_model = "claude-haiku-4-5-20251001"
    varsayilan_url = "https://api.anthropic.com"
    api_key_env = "ANTHROPIC_API_KEY"
    api_key_gerekli = True

    def _api_istek(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        model = kwargs.get("model", self._model)
        max_tokens = kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN)

        url = f"{self._base_url}/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        ant_mesajlar = [m for m in mesajlar if m["role"] in ("user", "assistant")]
        payload = {
            "model": model,
            "system": sistem_prompt,
            "messages": ant_mesajlar,
            "max_tokens": max_tokens,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=_TIMEOUT_SANIYE)
        r.raise_for_status()
        veri = r.json()
        metin = veri["content"][0]["text"]
        return ProviderYanit(
            metin=metin,
            provider=self.ad,
            model=model,
        )

    def _api_istek_stream(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> Generator[str, None, ProviderYanit]:
        model = kwargs.get("model", self._model)
        max_tokens = kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN)

        url = f"{self._base_url}/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        ant_mesajlar = [m for m in mesajlar if m["role"] in ("user", "assistant")]
        payload = {
            "model": model,
            "system": sistem_prompt,
            "messages": ant_mesajlar,
            "max_tokens": max_tokens,
            "stream": True,
        }
        son_yanit = ProviderYanit(provider=self.ad, model=model)
        metin_parcalari: list[str] = []
        with requests.post(
            url,
            headers=headers,
            json=payload,
            stream=True,
            timeout=_TIMEOUT_SANIYE,
        ) as r:
            r.raise_for_status()
            for satir in r.iter_lines():
                if not satir:
                    continue
                satir_str = satir.decode("utf-8", errors="replace")
                if not satir_str.startswith("data: "):
                    continue
                try:
                    olay = json.loads(satir_str[6:])
                    if olay.get("type") == "content_block_delta":
                        delta = olay.get("delta", {})
                        if delta.get("type") == "text_delta":
                            token = delta.get("text", "")
                            if token:
                                metin_parcalari.append(token)
                                yield token
                except json.JSONDecodeError:
                    continue
        son_yanit.metin = "".join(metin_parcalari)
        return son_yanit


# â”€â”€ SaÄŸlayÄ±cÄ± KaydÄ± (Registry) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_PROVIDER_SINIFLAR: dict[str, type[ProviderBase]] = {
    "deepseek": DeepseekProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "xai": XAIProvider,
    "openrouter": OpenRouterProvider,
}

# Fallback sÄ±rasÄ± (birincil baÅŸarÄ±sÄ±z olursa)
_FALLBACK_SIRASI: list[str] = [
    "deepseek",
    "openai",
    "openrouter",
    "xai",
    "anthropic",
]

# VarsayÄ±lan model adlarÄ± (config'de model belirtilmemiÅŸse kullanÄ±lÄ±r)
_VARSAYILAN_MODELLER: dict[str, str] = {
    "deepseek": "deepseek-chat",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "xai": "grok-2-latest",
    "openrouter": "deepseek/deepseek-chat",
}


def get_provider(
    name: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    config: Optional[dict[str, Any]] = None,
) -> Optional[ProviderBase]:
    """SaÄŸlayÄ±cÄ± Ã¶rneÄŸi dÃ¶ndÃ¼rÃ¼r.

    Args:
        name:     SaÄŸlayÄ±cÄ± adÄ± (deepseek|openai|anthropic|xai|openrouter).
        model:    Model adÄ± (None = varsayÄ±lan).
        api_key:  API anahtarÄ± (None = otomatik bul).
        base_url: API base URL (None = varsayÄ±lan).
        config:   config.yaml sÃ¶zlÃ¼ÄŸÃ¼ (anahtar aramasÄ± iÃ§in).

    Returns:
        ProviderBase Ã¶rneÄŸi veya None (bilinmeyen saÄŸlayÄ±cÄ±).
    """
    sinif = _PROVIDER_SINIFLAR.get(name)
    if sinif is None:
        logger.warning("[get_provider] Bilinmeyen saÄŸlayÄ±cÄ±: %s", name)
        return None

    return sinif(
        model=model,
        api_key=api_key,
        base_url=base_url,
        config=config,
    )


def get_fallback_zinciri(
    birincil: str,
    config: Optional[dict[str, Any]] = None,
) -> list[ProviderBase]:
    """Fallback zinciri oluÅŸturur: birincil â†’ diÄŸerleri.

    SÄ±ra: birincil â†’ _FALLBACK_SIRASI'ndaki diÄŸer saÄŸlayÄ±cÄ±lar (API anahtarÄ± olanlar).

    Args:
        birincil: Birincil saÄŸlayÄ±cÄ± adÄ±.
        config:   config.yaml sÃ¶zlÃ¼ÄŸÃ¼.

    Returns:
        KullanÄ±ma hazÄ±r ProviderBase Ã¶rnekleri listesi.
    """
    zincir: list[ProviderBase] = []
    eklenen: set[str] = set()

    # Birincil
    p = get_provider(birincil, config=config)
    if p and p.hazir_mi():
        zincir.append(p)
        eklenen.add(birincil)

    # Fallback sÄ±rasÄ±
    for ad in _FALLBACK_SIRASI:
        if ad in eklenen:
            continue
        p = get_provider(ad, config=config)
        if p and p.hazir_mi():
            zincir.append(p)
            eklenen.add(ad)

    return zincir


def saglayiciyi_yapilandir(
    config: dict[str, Any],
) -> dict[str, Any]:
    """config.yaml'daki model.provider deÄŸerini okuyarak
    get_provider iÃ§in hazÄ±r config sÃ¶zlÃ¼ÄŸÃ¼ dÃ¶ndÃ¼rÃ¼r.

    config.yaml beklenen yapÄ±:
        model:
          provider: deepseek  # deepseek|openai|anthropic|xai|openrouter
          model: deepseek-v4-flash

    Returns:
        {
            "provider": "deepseek",
            "model": "deepseek-v4-flash",
            "config": { ... }  # orijinal config
        }
    """
    model_blok = config.get("model", {})
    if isinstance(model_blok, dict):
        provider_adi = model_blok.get("provider", "deepseek")
        model_adi = model_blok.get("model") or model_blok.get("default", "")
    else:
        provider_adi = config.get("provider", "deepseek")
        model_adi = (
            config.get("model", {}).get("default", "")
            if isinstance(config.get("model"), dict)
            else ""
        )

    if not model_adi:
        model_adi = _VARSAYILAN_MODELLER.get(provider_adi, "deepseek-chat")

    return {
        "provider": provider_adi,
        "model": model_adi,
        "config": config,
    }


# â”€â”€ HÄ±zlÄ± test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # Test: get_provider
    p = get_provider("deepseek")
    print(f"DeepSeek: ad={p.ad}, model={p.model}, hazir={p.hazir_mi()}")

    p = get_provider("openai")
    print(f"OpenAI: ad={p.ad}, model={p.model}, hazir={p.hazir_mi()}")

    p = get_provider("anthropic")
    print(f"Anthropic: ad={p.ad}, model={p.model}, hazir={p.hazir_mi()}")

    p = get_provider("xai")
    print(f"xAI: ad={p.ad}, model={p.model}, hazir={p.hazir_mi()}")

    p = get_provider("openrouter")
    print(f"OpenRouter: ad={p.ad}, model={p.model}, hazir={p.hazir_mi()}")

    # Test: fallback zinciri
    zincir = get_fallback_zinciri("deepseek")
    print(f"\nFallback zinciri ({len(zincir)} adet):")
    for p in zincir:
        print(f"  - {p.ad} ({p.model}) [hazir={p.hazir_mi()}]")
