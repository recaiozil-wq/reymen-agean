# -*- coding: utf-8 -*-
"""
provider_abstraction.py — ReYMeN Sağlayıcı Soyutlama Katmanı.

Tek satır kullanım:
    provider = get_provider('deepseek')
    cevap = provider.chat(mesajlar)

    # ya da
    for token in provider.chat_stream(mesajlar):
        print(token, end='')

Desteklenen sağlayıcılar:
    deepseek, openai, anthropic, groq, xiaomi, xai, openrouter, lmstudio

Özellikler:
    * Thread-safe başlatma ve çağrı yönetimi
    * Exponential backoff ile otomatik yeniden deneme (retry)
    * Rate-limit (429), yetkilendirme (401/403), kredi (402) hata yönetimi
    * config.yaml -> fallback_providers listesinden otomatik yapılandırma
    * Beyin.py ile tam uyumlu — birlikte veya yanında çalışabilir

Tüm docstring'ler Türkçe'dir.
"""

from __future__ import annotations

import abc
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Generator, Optional

import requests

logger = logging.getLogger(__name__)

# ── Sabitler ────────────────────────────────────────────────────────────────
_TIMEOUT_SANIYE: int = 300
_VARSAYILAN_MAX_TOKEN: int = 4096
_VARSAYILAN_SICAKLIK: float = 0.7
_MAKS_DENEME: int = 3
_ILK_BEKLEME: float = 1.0
_BEKLEME_CARPAN: float = 2.0


# ── Veri Yapıları ──────────────────────────────────────────────────────────

@dataclass
class ProviderYanit:
    """Sağlayıcıdan dönen yanıtı temsil eder.

    Args:
        metin:         LLM'den gelen yanıt metni.
        provider:      Kullanılan sağlayıcı adı.
        model:         Kullanılan model adı.
        sure_sn:       İsteğin tamamlanma süresi (saniye).
        basarili:      İsteğin başarılı olup olmadığı.
        hata:          Hata mesajı (varsa).
        tahmini_token: Tahmini token sayısı.
    """
    metin: str = ""
    provider: str = ""
    model: str = ""
    sure_sn: float = 0.0
    basarili: bool = True
    hata: str = ""
    tahmini_token: int = 0


@dataclass
class ProviderYapilandirma:
    """Bir sağlayıcının yapılandırma bilgilerini tutar.

    config.yaml -> fallback_providers listesindeki her girdi bu yapıya dönüşür.
    """
    provider: str
    model: str
    base_url: str = ""
    api_key: str = ""
    api_mode: str = "chat_completions"


# ── Hata Sınıfları ─────────────────────────────────────────────────────────

class ProviderHatasi(Exception):
    """Sağlayıcı çağrıları sırasında oluşan genel hata."""
    pass


class ProviderGecersizKey(ProviderHatasi):
    """API anahtarı geçersiz (401/403)."""
    pass


class ProviderKrediBitti(ProviderHatasi):
    """Sağlayıcı kredisi bitti (402 Payment Required)."""
    pass


class ProviderRateLimit(ProviderHatasi):
    """Hız sınırı aşıldı (429)."""
    pass


class ProviderZamanAsimi(ProviderHatasi):
    """İstek zaman aşımına uğradı."""
    pass


# ── Temel Sınıf ────────────────────────────────────────────────────────────

class ProviderBase(abc.ABC):
    """Tüm sağlayıcıların türemesi gereken soyut temel sınıf.

    Alt sınıflar şu metotları sağlamalıdır:
        * _api_istek():    Ham API çağrısını gerçekleştirir.
        * _api_istek_stream(): Streaming API çağrısını gerçekleştirir.
        * _modelleri_getir(): Kullanılabilir modelleri listeler.
        * _ping_kontrol():  Sağlayıcı erişilebilirliğini kontrol eder.

    Kullanıma hazır metotlar (override gerekmez):
        * chat():          Retry + hata yönetimi ile API çağrısı.
        * chat_stream():   Streaming API çağrısı.
        * models():        Model listesi (cache'li).
        * ping():          Erişilebilirlik kontrolü.
    """

    # ── Sınıf öznitelikleri (alt sınıflar tanımlamalı) ──────────────────
    ad: str = ""
    """Sağlayıcının kısa adı (ör. 'deepseek', 'openai')."""

    varsayilan_model: str = ""
    """Bu sağlayıcı için varsayılan model adı."""

    varsayilan_base_url: str = ""
    """Bu sağlayıcı için varsayılan API temel URL'i."""

    api_key_env: str = ""
    """API anahtarı için ortam değişkeni adı (ör. 'DEEPSEEK_API_KEY')."""

    api_key_gerekli: bool = True
    """API anahtarı zorunlu mu? (LM Studio gibi yerellerde False)."""

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        """Sağlayıcı örneğini başlatır.

        Args:
            model:    Model adı (None = varsayılan).
            base_url: API temel URL'i (None = varsayılan).
            api_key:  API anahtarı (None = env'den okunur).
        """
        self._model = model or self.varsayilan_model
        self._base_url = (base_url or self.varsayilan_base_url).rstrip("/")
        self._api_key = api_key or os.environ.get(self.api_key_env, "")
        self._lock = threading.Lock()
        self._model_cache: Optional[list[dict]] = None
        self._model_cache_zamani: float = 0.0
        self._model_cache_omru: float = 300.0  # 5 dakika

    # ── Öznitelikler ────────────────────────────────────────────────────

    @property
    def model(self) -> str:
        """Aktif model adı."""
        return self._model

    @model.setter
    def model(self, deger: str) -> None:
        """Model adını değiştirir (thread-safe)."""
        with self._lock:
            self._model = deger

    @property
    def base_url(self) -> str:
        """Aktif API temel URL'i."""
        return self._base_url

    @property
    def api_key(self) -> str:
        """Aktif API anahtarı."""
        return self._api_key

    # ── Hazırlık kontrolü ───────────────────────────────────────────────

    def hazir_mi(self) -> bool:
        """Sağlayıcının kullanıma hazır olup olmadığını kontrol eder.

        Returns:
            True:  API anahtarı mevcut (veya gerekmiyor).
            False: API anahtarı eksik.
        """
        if self.api_key_gerekli and not self._api_key:
            logger.debug("[%s] API anahtari eksik (env: %s)", self.ad, self.api_key_env)
            return False
        return True

    def hazir_mi_veya_uyari(self) -> bool:
        """hazir_mi() gibi çalışır ama eksikse uyarı loglar.

        Returns:
            Sağlayıcı hazırsa True, değilse False.
        """
        if not self.hazir_mi():
            logger.warning(
                "[%s] API anahtari eksik — sağlayıcı kullanilamaz. "
                "Ortam değişkeni: %s", self.ad, self.api_key_env,
            )
            return False
        return True

    # ── Soyut metotlar (alt sınıflar uygulamalı) ────────────────────────

    @abc.abstractmethod
    def _api_istek(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """Ham API çağrısını gerçekleştirir.

        Args:
            mesajlar:      Konuşma mesajları listesi.
            sistem_prompt: Sistem talimatı (opsiyonel).
            **kwargs:      Ek parametreler (temperature, max_tokens, vs.).

        Returns:
            ProviderYanit — yanıt metni, süre, hata bilgisi.
        """
        ...

    @abc.abstractmethod
    def _api_istek_stream(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> Generator[str, None, ProviderYanit]:
        """Streaming API çağrısını gerçekleştirir.

        Args:
            mesajlar:      Konuşma mesajları listesi.
            sistem_prompt: Sistem talimatı (opsiyonel).
            **kwargs:      Ek parametreler.

        Yields:
            str: Her token veya metin parçası.

        Returns:
            ProviderYanit — son yanıt bilgisi (generator bitince).
        """
        ...  # noqa: WPS428  — abstract, intentional empty

    @abc.abstractmethod
    def _modelleri_getir(self) -> list[dict]:
        """Kullanılabilir modelleri API'den getirir.

        Returns:
            Model bilgisi içeren sözlükler listesi:
            [{"id": "model-adi", "object": "model", ...}, ...]
        """
        ...

    @abc.abstractmethod
    def _ping_kontrol(self) -> bool:
        """Sağlayıcı erişilebilirliğini kontrol eder.

        Returns:
            True:  Sağlayıcı erişilebilir.
            False: Erişilemez veya hata var.
        """
        ...

    # ── Hata sınıflandırma ──────────────────────────────────────────────

    @staticmethod
    def _hatayi_siniflandir(hata: Exception) -> ProviderHatasi:
        """Genel bir hatayı sağlayıcı hata türüne dönüştürür.

        Args:
            hata: Yakalanan istisna.

        Returns:
            Uygun ProviderHatasi alt sınıfı.
        """
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
                    return ProviderGecersizKey(f"Erişim reddedildi (403): {hata}")
                elif kod == 429:
                    return ProviderRateLimit(f"Hız sınırı (429): {hata}")
        except Exception as _e:
            log.warning(f"[src.core.provider_abstraction] Exception at L309")
            pass

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

    @staticmethod
    def _yeniden_denenebilir_mi(hata: Exception) -> bool:
        """Bu hatanın yeniden denenip denenemeyeceğini belirler.

        401/402/403 yeniden denenmez (kalıcı hata).
        429 (rate limit) yeniden denenebilir.
        Diğer hatalar (500, ağ, vs.) yeniden denenebilir.

        Returns:
            True:  Yeniden dene.
            False: Hemen hata fırlat.
        """
        siniflandirilmis = ProviderBase._hatayi_siniflandir(hata)
        if isinstance(siniflandirilmis, (ProviderGecersizKey, ProviderKrediBitti)):
            return False
        return True

    # ── Retry mantığı ───────────────────────────────────────────────────

    def _retry_ile_cagir(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """Exponential backoff ile yeniden deneme yapar.

        Sadece rate-limit (429) ve geçici hatalar yeniden denenir.
        401/402/403 gibi kalıcı hatalar hemen fırlatılır.

        Args:
            mesajlar:      Konuşma mesajları.
            sistem_prompt: Sistem talimatı.
            **kwargs:      Ek parametreler.

        Returns:
            Başarılı yanıt.

        Raises:
            ProviderGecersizKey: API anahtarı geçersiz.
            ProviderKrediBitti:  Kredi bitti.
            ProviderHatasi:      Diğer hatalar (tüm denemeler başarısız).
        """
        bekleme = _ILK_BEKLEME
        son_hata: Optional[Exception] = None

        for deneme in range(1, _MAKS_DENEME + 1):
            try:
                t0 = time.monotonic()
                yanit = self._api_istek(mesajlar, sistem_prompt, **kwargs)
                yanit.sure_sn = time.monotonic() - t0
                return yanit
            except Exception as hata:
                son_hata = hata
                siniflandirilmis = self._hatayi_siniflandir(hata)

                if isinstance(siniflandirilmis, ProviderGecersizKey):
                    logger.warning(
                        "[%s] Yetki hatasi — retry edilmiyor: %s",
                        self.ad, siniflandirilmis,
                    )
                    raise siniflandirilmis

                if isinstance(siniflandirilmis, ProviderKrediBitti):
                    logger.warning(
                        "[%s] Kredi bitti — retry edilmiyor: %s",
                        self.ad, siniflandirilmis,
                    )
                    raise siniflandirilmis

                if isinstance(siniflandirilmis, ProviderRateLimit) and deneme < _MAKS_DENEME:
                    logger.warning(
                        "[%s] Rate limit — %.1fs bekleniyor (%d/%d)…",
                        self.ad, bekleme, deneme, _MAKS_DENEME,
                    )
                    time.sleep(bekleme)
                    bekleme *= _BEKLEME_CARPAN
                elif deneme < _MAKS_DENEME:
                    logger.warning(
                        "[%s] Hata — %.1fs sonra yeniden deneniyor (%d/%d): %s",
                        self.ad, bekleme, deneme, _MAKS_DENEME, hata,
                    )
                    time.sleep(bekleme)
                    bekleme *= _BEKLEME_CARPAN
                else:
                    # Son deneme de başarısız
                    raise ProviderHatasi(
                        f"[{self.ad}] Tüm denemeler başarısız ({_MAKS_DENEME}/{_MAKS_DENEME}): {hata}"
                    ) from hata

        # Buraya ulaşılmamalı — yukarıdaki döngü ya return eder ya da raise
        raise ProviderHatasi(
            f"[{self.ad}] Beklenmeyen durum — retry döngüsü sonu."
        ) from son_hata

    # ── Yüksek seviye API ───────────────────────────────────────────────

    def chat(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """LLM'den yanıt üretir (retry + hata yönetimi ile).

        Thread-safe çağrı — aynı anda birden fazla thread çağırabilir.

        Args:
            mesajlar:      Konuşma mesajları listesi.
                           Örn: [{"role": "user", "content": "Merhaba"}]
            sistem_prompt: Sistem talimatı (opsiyonel).
            **kwargs:      Ek parametreler:
                temperature (float):  Sıcaklık (0.0-2.0). Varsayılan: 0.7.
                max_tokens (int):    Maksimum token. Varsayılan: 4096.
                model (str):         Model adı geçersiz kılma.

        Returns:
            ProviderYanit — yanıt metni, süre, hata bilgisi.

        Örnek:
            >>> provider = get_provider('deepseek')
            >>> yanit = provider.chat(
            ...     [{"role": "user", "content": "2+2 nedir?"}],
            ...     sistem_prompt="yardimci ol",
            ... )
            >>> print(yanit.metin)
            2+2 = 4
        """
        if not self.hazir_mi_veya_uyari():
            return ProviderYanit(
                metin="",
                provider=self.ad,
                model=self._model,
                basarili=False,
                hata=f"{self.ad}: API anahtari eksik",
            )

        try:
            return self._retry_ile_cagir(mesajlar, sistem_prompt, **kwargs)
        except (ProviderGecersizKey, ProviderKrediBitti, ProviderHatasi) as e:
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
        """Streaming LLM yanıtı — token token yield eder.

        Thread-safe çağrı. Sağlayıcı streaming desteklemiyorsa
        tam yanıt tek seferde yield edilir (graceful degrade).

        Args:
            mesajlar:      Konuşma mesajları listesi.
            sistem_prompt: Sistem talimatı (opsiyonel).
            **kwargs:      Ek parametreler.

        Yields:
            str: Bir token veya küçük metin parçası.

        Returns:
            ProviderYanit — son yanıt bilgisi (generator bitince).

        Örnek:
            >>> provider = get_provider('deepseek')
            >>> for token in provider.chat_stream(
            ...     [{"role": "user", "content": "Merhaba"}],
            ... ):
            ...     print(token, end="", flush=True)
        """
        if not self.hazir_mi_veya_uyari():
            yield ""
            return ProviderYanit(
                metin="",
                provider=self.ad,
                model=self._model,
                basarili=False,
                hata=f"{self.ad}: API anahtari eksik",
            )

        try:
            generator = self._api_istek_stream(mesajlar, sistem_prompt, **kwargs)
            son_yanit = ProviderYanit(provider=self.ad, model=self._model)

            for token in generator:
                son_yanit.metin += token
                yield token

            # Generator'un dönüş değerini al
            try:
                donus = generator.throw(StopIteration)
                if isinstance(donus, ProviderYanit):
                    son_yanit = donus
            except StopIteration as si:
                if si.value and isinstance(si.value, ProviderYanit):
                    son_yanit = si.value

            son_yanit.provider = self.ad
            son_yanit.model = self._model
            return son_yanit

        except Exception as e:
            hata_yanit = ProviderYanit(
                metin="",
                provider=self.ad,
                model=self._model,
                basarili=False,
                hata=str(e),
            )
            yield ""
            return hata_yanit

    def models(self) -> list[dict]:
        """Kullanılabilir modelleri listeler (cache'li).

        Sonuçlar 5 dakika boyunca önbellekte tutulur.
        Cache süresi dolunca API'den yeniden getirilir.

        Returns:
            Model bilgisi içeren sözlükler listesi.

        Örnek:
            >>> provider = get_provider('lmstudio')
            >>> for m in provider.models():
            ...     print(m['id'])
            cognitivecomputations/dolphin3.0-llama3.1-8b
        """
        simdi = time.time()
        with self._lock:
            if self._model_cache is not None and (simdi - self._model_cache_zamani) < self._model_cache_omru:
                return self._model_cache

            try:
                modeller = self._modelleri_getir()
                self._model_cache = modeller
                self._model_cache_zamani = simdi
                return modeller
            except Exception as e:
                logger.warning("[%s] Model listesi alinamadi: %s", self.ad, e)
                return self._model_cache or []

    def ping(self) -> bool:
        """Sağlayıcı erişilebilirliğini kontrol eder.

        Returns:
            True:  Sağlayıcı erişilebilir.
            False: Erişilemez.

        Örnek:
            >>> provider = get_provider('lmstudio')
            >>> if provider.ping():
            ...     print("LM Studio çalişiyor!")
        """
        try:
            return self._ping_kontrol()
        except Exception as e:
            logger.debug("[%s] Ping hatasi: %s", self.ad, e)
            return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ad={self.ad!r} model={self._model!r}>"


# ═══════════════════════════════════════════════════════════════════════════
# OpenAI Uyumlu Sağlayıcılar (DeepSeek, OpenAI, Groq, xAI, OpenRouter, LM Studio)
# ═══════════════════════════════════════════════════════════════════════════

class OpenAIUyumluProvider(ProviderBase):
    """OpenAI-uyumlu /v1/chat/completions API'sine sahip sağlayıcılar için temel sınıf.

    Bu sınıf, DeepSeek, OpenAI, Groq, xAI, OpenRouter ve LM Studio
    gibi OpenAI API formatını kullanan tüm sağlayıcılar için ortak
    implementasyon sağlar.

    Alt sınıflar sadece sınıf özniteliklerini tanımlamalıdır.
    """

    ad: str = "openai_compat"
    varsayilan_model: str = ""
    varsayilan_base_url: str = ""
    api_key_env: str = ""
    api_key_gerekli: bool = True

    def _api_url(self) -> str:
        """Chat completions endpoint URL'ini döndürür.

        base_url sondaki /v1 varsa temizlenir,
        kod sabit /v1/chat/completions ekler.
        """
        temiz_url = self._base_url.rstrip("/")
        if temiz_url.endswith("/v1"):
            temiz_url = temiz_url[:-3]
        return f"{temiz_url}/v1/chat/completions"

    def _api_istek(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """OpenAI-uyumlu /v1/chat/completions çağrısı.

        Args:
            mesajlar:      Konuşma mesajları.
            sistem_prompt: Sistem talimatı.
            **kwargs:      temperature, max_tokens, model.

        Returns:
            ProviderYanit.
        """
        url = self._api_url()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        model = kwargs.get("model") or self._model
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar if sistem_prompt else mesajlar,
            "stream": False,
            "temperature": kwargs.get("temperature", _VARSAYILAN_SICAKLIK),
            "max_tokens": kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN),
        }

        t0 = time.monotonic()
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=_TIMEOUT_SANIYE)
            r.raise_for_status()
            veri = r.json()
            metin = veri["choices"][0]["message"]["content"] or ""
            sure = time.monotonic() - t0
            return ProviderYanit(
                metin=metin,
                provider=self.ad,
                model=model,
                sure_sn=sure,
                basarili=True,
                tahmini_token=len(metin.split()),
            )
        except requests.exceptions.Timeout as e:
            raise ProviderZamanAsimi(f"[{self.ad}] Zaman aşimi: {e}") from e
        except requests.exceptions.HTTPError as e:
            # Hata kodunu _hatayi_siniflandir ile siniflandirmasi icin
            # yeniden firlat
            raise ProviderHatasi(str(e)) from e
        except requests.exceptions.ConnectionError as e:
            raise ProviderHatasi(f"[{self.ad}] Bağlanti hatasi: {e}") from e
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ProviderHatasi(f"[{self.ad}] Yanit cozulemedi: {e}") from e

    def _api_istek_stream(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> Generator[str, None, ProviderYanit]:
        """OpenAI-uyumlu streaming /v1/chat/completions çağrısı.

        Args:
            mesajlar:      Konuşma mesajları.
            sistem_prompt: Sistem talimatı.
            **kwargs:      temperature, max_tokens, model.

        Yields:
            str: Her SSE event'inden bir token.

        Returns:
            ProviderYanit.
        """
        url = self._api_url()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        model = kwargs.get("model") or self._model
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar if sistem_prompt else mesajlar,
            "stream": True,
            "temperature": kwargs.get("temperature", _VARSAYILAN_SICAKLIK),
            "max_tokens": kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN),
        }

        t0 = time.monotonic()
        metin_parcalari: list[str] = []

        try:
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=_TIMEOUT_SANIYE
            ) as r:
                r.raise_for_status()
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

            sure = time.monotonic() - t0
            return ProviderYanit(
                metin="".join(metin_parcalari),
                provider=self.ad,
                model=model,
                sure_sn=sure,
                basarili=True,
                tahmini_token=len(metin_parcalari),
            )
        except Exception as e:
            # Stream basarisiz — graceful degrade: tam yanit dondur
            try:
                tam_yanit = self._api_istek(mesajlar, sistem_prompt, **kwargs)
                yield tam_yanit.metin
                return tam_yanit
            except Exception as e2:
                return ProviderYanit(
                    metin="",
                    provider=self.ad,
                    model=model,
                    basarili=False,
                    hata=str(e2),
                )

    def _modelleri_getir(self) -> list[dict]:
        """OpenAI-uyumlu /v1/models endpoint'inden model listesi alır."""
        temiz_url = self._base_url.rstrip("/")
        if temiz_url.endswith("/v1"):
            temiz_url = temiz_url[:-3]
        url = f"{temiz_url}/v1/models"

        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json().get("data", [])

    def _ping_kontrol(self) -> bool:
        """OpenAI-uyumlu /v1/models ile erişilebilirliği kontrol eder."""
        try:
            temiz_url = self._base_url.rstrip("/")
            if temiz_url.endswith("/v1"):
                temiz_url = temiz_url[:-3]
            url = f"{temiz_url}/v1/models"

            headers = {}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            r = requests.get(url, headers=headers, timeout=5)
            return r.status_code < 500
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════════════════
# Sağlayıcı Alt Sınıfları
# ═══════════════════════════════════════════════════════════════════════════

class DeepSeekProvider(OpenAIUyumluProvider):
    """DeepSeek API sağlayıcısı.

    API: https://api.deepseek.com/v1/chat/completions
    Ortam değişkeni: DEEPSEEK_API_KEY
    Varsayılan model: deepseek-chat
    """
    ad: str = "deepseek"
    varsayilan_model: str = "deepseek-chat"
    varsayilan_base_url: str = "https://api.deepseek.com"
    api_key_env: str = "DEEPSEEK_API_KEY"


class OpenAIProvider(OpenAIUyumluProvider):
    """OpenAI API sağlayıcısı.

    API: https://api.openai.com/v1/chat/completions
    Ortam değişkeni: OPENAI_API_KEY
    Varsayılan model: gpt-4o-mini
    """
    ad: str = "openai"
    varsayilan_model: str = "gpt-4o-mini"
    varsayilan_base_url: str = "https://api.openai.com"
    api_key_env: str = "OPENAI_API_KEY"


class GroqProvider(OpenAIUyumluProvider):
    """Groq API sağlayıcısı.

    API: https://api.groq.com/openai/v1/chat/completions
    Ortam değişkeni: GROQ_API_KEY
    Varsayılan model: llama-3.1-8b-instant
    """
    ad: str = "groq"
    varsayilan_model: str = "llama-3.1-8b-instant"
    varsayilan_base_url: str = "https://api.groq.com/openai/v1"
    api_key_env: str = "GROQ_API_KEY"


class XAIProvider(OpenAIUyumluProvider):
    """xAI (Grok) API sağlayıcısı.

    API: https://api.x.ai/v1/chat/completions
    Ortam değişkeni: XAI_API_KEY
    Varsayılan model: grok-2-latest
    """
    ad: str = "xai"
    varsayilan_model: str = "grok-2-latest"
    varsayilan_base_url: str = "https://api.x.ai"
    api_key_env: str = "XAI_API_KEY"


class OpenRouterProvider(OpenAIUyumluProvider):
    """OpenRouter API sağlayıcısı.

    API: https://openrouter.ai/api/v1/chat/completions
    Ortam değişkeni: OPENROUTER_API_KEY
    Varsayılan model: deepseek/deepseek-chat
    """
    ad: str = "openrouter"
    varsayilan_model: str = "deepseek/deepseek-chat"
    varsayilan_base_url: str = "https://openrouter.ai/api"
    api_key_env: str = "OPENROUTER_API_KEY"


class LMStudioProvider(OpenAIUyumluProvider):
    """Yerel LM Studio sağlayıcısı.

    API anahtarı gerekmez.
    API: http://localhost:1234/v1/chat/completions
    Varsayılan model: local-model
    """
    ad: str = "lmstudio"
    varsayilan_model: str = "local-model"
    varsayilan_base_url: str = "http://localhost:1234"
    api_key_env: str = ""
    api_key_gerekli: bool = False

    def _api_istek(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """LM Studio: sistem mesaji [SISTEM]: on eki ile user rolune cevrilir.

        LM Studio sistem mesajini dogrudan desteklemez; bu nedenle
        sistem prompt'u user mesajina donusturulur.
        """
        url = self._api_url()
        donusturulmus: list[dict] = []

        if sistem_prompt:
            donusturulmus.append({"role": "user", "content": f"[SISTEM]: {sistem_prompt}"})
        for m in mesajlar:
            if m.get("role") == "system":
                donusturulmus.append({"role": "user", "content": f"[SISTEM]: {m['content']}"})
            else:
                donusturulmus.append(m)

        model = kwargs.get("model") or self._model
        payload = {
            "model": model,
            "messages": donusturulmus,
            "stream": False,
            "temperature": kwargs.get("temperature", _VARSAYILAN_SICAKLIK),
            "max_tokens": kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN),
        }

        t0 = time.monotonic()
        try:
            r = requests.post(url, json=payload, timeout=_TIMEOUT_SANIYE)
            r.raise_for_status()
            metin = r.json()["choices"][0]["message"]["content"] or ""
            sure = time.monotonic() - t0
            return ProviderYanit(
                metin=metin,
                provider=self.ad,
                model=model,
                sure_sn=sure,
                basarili=True,
                tahmini_token=len(metin.split()),
            )
        except requests.exceptions.Timeout as e:
            raise ProviderZamanAsimi(f"[{self.ad}] Zaman asimi: {e}") from e
        except Exception as e:
            raise ProviderHatasi(f"[{self.ad}] Hata: {e}") from e


# ═══════════════════════════════════════════════════════════════════════════
# Anthropic Sağlayıcısı (farklı API formatı)
# ═══════════════════════════════════════════════════════════════════════════

class AnthropicProvider(ProviderBase):
    """Anthropic (Claude) API sağlayıcısı.

    Anthropic Messages API (/v1/messages) kullanir.
    OpenAI uyumlu degildir — kendi API formati vardir.

    API: https://api.anthropic.com/v1/messages
    Ortam değişkeni: ANTHROPIC_API_KEY
    Varsayılan model: claude-haiku-4-5-20251001
    """
    ad: str = "anthropic"
    varsayilan_model: str = "claude-haiku-4-5-20251001"
    varsayilan_base_url: str = "https://api.anthropic.com"
    api_key_env: str = "ANTHROPIC_API_KEY"

    def _api_url(self) -> str:
        """Anthropic Messages API URL'i."""
        temiz_url = self._base_url.rstrip("/")
        return f"{temiz_url}/v1/messages"

    def _api_istek(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """Anthropic /v1/messages API çağrısı.

        Not: Anthropic, OpenAI'dan farkli bir mesaj formati kullanir.
        """
        url = self._api_url()
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        model = kwargs.get("model") or self._model
        # Anthropic sadece "user" ve "assistant" rollerini kabul eder
        ant_mesajlar = [m for m in mesajlar if m.get("role") in ("user", "assistant")]

        payload: dict[str, Any] = {
            "model": model,
            "messages": ant_mesajlar,
            "max_tokens": kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN),
        }
        if sistem_prompt:
            payload["system"] = sistem_prompt
        if "temperature" in kwargs:
            payload["temperature"] = kwargs["temperature"]

        t0 = time.monotonic()
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=_TIMEOUT_SANIYE)
            r.raise_for_status()
            veri = r.json()
            # Anthropic yanit formati: content[{type: "text", text: "..."}]
            metin = ""
            for blok in veri.get("content", []):
                if blok.get("type") == "text":
                    metin += blok.get("text", "")
            sure = time.monotonic() - t0
            return ProviderYanit(
                metin=metin,
                provider=self.ad,
                model=model,
                sure_sn=sure,
                basarili=True,
                tahmini_token=len(metin.split()),
            )
        except requests.exceptions.Timeout as e:
            raise ProviderZamanAsimi(f"[{self.ad}] Zaman asimi: {e}") from e
        except requests.exceptions.HTTPError as e:
            raise ProviderHatasi(str(e)) from e
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ProviderHatasi(f"[{self.ad}] Yanit cozulemedi: {e}") from e

    def _api_istek_stream(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> Generator[str, None, ProviderYanit]:
        """Anthropic streaming — text_delta olaylarini yield eder."""
        url = self._api_url()
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        model = kwargs.get("model") or self._model
        ant_mesajlar = [m for m in mesajlar if m.get("role") in ("user", "assistant")]

        payload: dict[str, Any] = {
            "model": model,
            "messages": ant_mesajlar,
            "max_tokens": kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN),
            "stream": True,
        }
        if sistem_prompt:
            payload["system"] = sistem_prompt

        t0 = time.monotonic()
        metin_parcalari: list[str] = []

        try:
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=_TIMEOUT_SANIYE
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

            sure = time.monotonic() - t0
            return ProviderYanit(
                metin="".join(metin_parcalari),
                provider=self.ad,
                model=model,
                sure_sn=sure,
                basarili=True,
                tahmini_token=len(metin_parcalari),
            )
        except Exception as e:
            try:
                tam_yanit = self._api_istek(mesajlar, sistem_prompt, **kwargs)
                yield tam_yanit.metin
                return tam_yanit
            except Exception as e2:
                return ProviderYanit(
                    metin="",
                    provider=self.ad,
                    model=model,
                    basarili=False,
                    hata=str(e2),
                )

    def _modelleri_getir(self) -> list[dict]:
        """Anthropic model listesi (sabit, API'si yok)."""
        return [
            {"id": "claude-haiku-4-5-20251001", "object": "model"},
            {"id": "claude-sonnet-4-5-20251001", "object": "model"},
            {"id": "claude-opus-4-5-20251001", "object": "model"},
        ]

    def _ping_kontrol(self) -> bool:
        """Anthropic erişilebilirlik kontrolü."""
        try:
            url = self._api_url()
            r = requests.post(
                url,
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={"model": self._model, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1},
                timeout=5,
            )
            return r.status_code < 500
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════════════════
# Xiaomi (MiniMax) Sağlayıcısı
# ═══════════════════════════════════════════════════════════════════════════

class XiaomiProvider(ProviderBase):
    """Xiaomi (MiniMax) API sağlayıcısı.

    OpenAI uyumlu degildir — /v1/text/chatcompletion_v2 endpoint'ini kullanir.

    API: https://api.minimax.chat/v1/text/chatcompletion_v2
    Ortam değişkeni: XIAOMI_API_KEY
    Varsayılan model: MiniMax-Text-01
    """
    ad: str = "xiaomi"
    varsayilan_model: str = "mimo-v2.5-pro"
    varsayilan_base_url: str = "https://api.xiaomimimo.com/v1"
    api_key_env: str = "XIAOMI_API_KEY"

    def _api_url(self) -> str:
        """MiniMax chat completion URL'i."""
        if "/chat/completions" in self._base_url:
            return self._base_url
        # Xiaomi/MiniMax bazen OpenAI uyumlu endpoint de kullanabilir
        temiz_url = self._base_url.rstrip("/")
        if temiz_url.endswith("/v1"):
            return f"{temiz_url}/chat/completions"
        return f"{temiz_url}/v1/chat/completions"

    def _api_istek(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> ProviderYanit:
        """Xiaomi/MiniMax API çağrısı — OpenAI uyumlu endpoint."""
        url = self._api_url()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        model = kwargs.get("model") or self._model
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar if sistem_prompt else mesajlar,
            "stream": False,
            "temperature": kwargs.get("temperature", _VARSAYILAN_SICAKLIK),
            "max_tokens": kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN),
        }

        t0 = time.monotonic()
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=_TIMEOUT_SANIYE)
            r.raise_for_status()
            veri = r.json()
            metin = veri["choices"][0]["message"]["content"] or ""
            sure = time.monotonic() - t0
            return ProviderYanit(
                metin=metin,
                provider=self.ad,
                model=model,
                sure_sn=sure,
                basarili=True,
                tahmini_token=len(metin.split()),
            )
        except requests.exceptions.Timeout as e:
            raise ProviderZamanAsimi(f"[{self.ad}] Zaman asimi: {e}") from e
        except Exception as e:
            raise ProviderHatasi(f"[{self.ad}] Hata: {e}") from e

    def _api_istek_stream(
        self,
        mesajlar: list[dict],
        sistem_prompt: str = "",
        **kwargs: Any,
    ) -> Generator[str, None, ProviderYanit]:
        """Xiaomi/MiniMax streaming — OpenAI uyumlu."""
        url = self._api_url()
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        model = kwargs.get("model") or self._model
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sistem_prompt}] + mesajlar if sistem_prompt else mesajlar,
            "stream": True,
            "temperature": kwargs.get("temperature", _VARSAYILAN_SICAKLIK),
            "max_tokens": kwargs.get("max_tokens", _VARSAYILAN_MAX_TOKEN),
        }

        t0 = time.monotonic()
        metin_parcalari: list[str] = []

        try:
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=_TIMEOUT_SANIYE
            ) as r:
                r.raise_for_status()
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

            sure = time.monotonic() - t0
            return ProviderYanit(
                metin="".join(metin_parcalari),
                provider=self.ad,
                model=model,
                sure_sn=sure,
                basarili=True,
                tahmini_token=len(metin_parcalari),
            )
        except Exception as e:
            try:
                tam_yanit = self._api_istek(mesajlar, sistem_prompt, **kwargs)
                yield tam_yanit.metin
                return tam_yanit
            except Exception as e2:
                return ProviderYanit(
                    metin="",
                    provider=self.ad,
                    model=model,
                    basarili=False,
                    hata=str(e2),
                )

    def _modelleri_getir(self) -> list[dict]:
        """Xiaomi/MiniMax model listesi (sabit)."""
        return [
            {"id": "mimo-v2.5-pro", "object": "model"},
            {"id": "MiniMax-Text-01", "object": "model"},
        ]

    def _ping_kontrol(self) -> bool:
        """Xiaomi/MiniMax erişilebilirlik kontrolü."""
        try:
            url = self._api_url()
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                json={"model": self._model, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1},
                timeout=5,
            )
            return r.status_code < 500
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════════════════
# Sağlayıcı Fabrikası
# ═══════════════════════════════════════════════════════════════════════════

_PROVIDER_SINIFLARI: dict[str, type[ProviderBase]] = {
    "deepseek":   DeepSeekProvider,
    "openai":     OpenAIProvider,
    "openai-api": OpenAIProvider,  # config.yaml'daki "openai-api" icin alias
    "anthropic":  AnthropicProvider,
    "groq":       GroqProvider,
    "xiaomi":     XiaomiProvider,
    "xai":        XAIProvider,
    "openrouter": OpenRouterProvider,
    "lmstudio":   LMStudioProvider,
}

# Global instance cache (thread-safe)
_provider_cache: dict[str, ProviderBase] = {}
_provider_cache_lock = threading.Lock()

# Global config referansi (get_provider ile set edilir)
_global_config: Optional[dict[str, Any]] = None
_global_config_lock = threading.Lock()


def _provider_adi_duzelt(ad: str) -> str:
    """Config'deki provider adlarini normalize eder.

    Ornegin "openai-api" -> "openai" gibi.
    """
    eslesmeler = {
        "openai-api": "openai",
        "openai": "openai",
    }
    return eslesmeler.get(ad, ad)


def get_provider(
    ad: str,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    config: Optional[dict[str, Any]] = None,
) -> ProviderBase:
    """Tek satirlik provider fabrikasi.

    Provider adina gore uygun instance'i dondurur.
    Instance'lar thread-safe cache'de tutulur — ayni provider tekrar
    olusturulmaz.

    Args:
        ad:       Sağlayıcı adı.
                  Desteklenenler: deepseek, openai, openai-api, anthropic,
                  groq, xiaomi, xai, openrouter, lmstudio.
        model:    Model adi (None = varsayilan).
        base_url: API temel URL'i (None = varsayilan).
        api_key:  API anahtari (None = env'den okunur).
        config:   Config sozlugu. Verilirse config.yaml'daki
                  fallback_providers listesinden yapilandirma
                  bilgileri otomatik alinir.

    Returns:
        ProviderBase alt sinifi ornegi.

    Raises:
        ValueError: Bilinmeyen provider adi.

    Örnek:
        >>> provider = get_provider('deepseek')
        >>> yanit = provider.chat([{"role": "user", "content": "Merhaba"}])
        >>> print(yanit.metin)

        >>> # Config'den yapilandirma ile
        >>> provider = get_provider('deepseek', config=config_dict)
    """
    # Config'den yapilandirma bilgilerini al
    if config is not None:
        with _global_config_lock:
            global _global_config
            _global_config = config

    # Config'de fallback_providers varsa, oradan yapilandirma oku
    if config and _provider_adi_duzelt(ad) in [p.get("provider", "") for p in config.get("fallback_providers", [])]:
        for pconf in config.get("fallback_providers", []):
            if _provider_adi_duzelt(pconf.get("provider", "")) == _provider_adi_duzelt(ad):
                model = model or pconf.get("model")
                base_url = base_url or pconf.get("base_url")
                break

    duzeltilmis_ad = _provider_adi_duzelt(ad)
    sinif = _PROVIDER_SINIFLARI.get(duzeltilmis_ad)

    if sinif is None:
        raise ValueError(
            f"Bilinmeyen sağlayıcı: {ad!r}. "
            f"Desteklenenler: {', '.join(_PROVIDER_SINIFLARI.keys())}"
        )

    # Cache anahtari: ad + model + base_url
    cache_key = f"{duzeltilmis_ad}:{model or ''}:{base_url or ''}"

    with _provider_cache_lock:
        mevcut = _provider_cache.get(cache_key)
        if mevcut is not None:
            return mevcut

        instance = sinif(model=model, base_url=base_url, api_key=api_key)
        _provider_cache[cache_key] = instance
        logger.debug("[ProviderFabrikasi] %s olusturuldu (cache anahtari: %s)", duzeltilmis_ad, cache_key)
        return instance


def get_all_providers(
    config: Optional[dict[str, Any]] = None,
) -> dict[str, ProviderBase]:
    """Config.yaml'daki fallback_providers listesindeki tum saglayicilari yukler.

    Args:
        config: Config sozlugu. None ise _global_config kullanilir.

    Returns:
        {provider_adi: ProviderBase ornegi} sozlugu.

    Örnek:
        >>> providers = get_all_providers(config)
        >>> for ad, p in providers.items():
        ...     print(f"{ad}: {p.ping()}")
    """
    cfg = config or _global_config
    if cfg is None:
        logger.warning("[get_all_providers] Config bulunamadi — bos sozluk donuluyor.")
        return {}

    saglayicilar: dict[str, ProviderBase] = {}
    for pconf in cfg.get("fallback_providers", []):
        ad = pconf.get("provider", "")
        if not ad:
            continue
        try:
            instance = get_provider(
                ad=ad,
                model=pconf.get("model"),
                base_url=pconf.get("base_url"),
                config=cfg,
            )
            saglayicilar[ad] = instance
        except ValueError as e:
            logger.warning("[get_all_providers] %s atlandi: %s", ad, e)
            continue

    return saglayicilar


def provideri_temizle(ad: Optional[str] = None) -> None:
    """Provider instance cache'ini temizler.

    Args:
        ad: Temizlenecek provider adi. None = tumunu temizle.

    Örnek:
        >>> provideri_temizle('deepseek')  # Sadece deepseek cache'ini temizle
        >>> provideri_temizle()            # Tum cache'i temizle
    """
    with _provider_cache_lock:
        if ad is None:
            _provider_cache.clear()
            logger.info("[ProviderFabrikasi] Tum provider cache'i temizlendi.")
        else:
            duzeltilmis_ad = _provider_adi_duzelt(ad)
            silinecek = [k for k in _provider_cache if k.startswith(duzeltilmis_ad)]
            for k in silinecek:
                del _provider_cache[k]
            logger.info(
                "[ProviderFabrikasi] %s cache'i temizlendi (%d girdi).",
                duzeltilmis_ad, len(silinecek),
            )


# ═══════════════════════════════════════════════════════════════════════════
# Beyin.py ile uyumluluk
# ═══════════════════════════════════════════════════════════════════════════

def beyin_icin_provider_olustur(
    beyin_config: dict[str, Any],
    provider_adi: Optional[str] = None,
) -> ProviderBase:
    """Beyin.py config formati ile uyumlu provider olusturur.

    Beyin'in su formattaki config'ini kabul eder:
        {
            "default_provider": "lmstudio",
            "default_model": "model-adi",
            "providers": {
                "lmstudio": {"base_url": "http://localhost:1234", "api_key": ""},
                "deepseek": {"base_url": "https://api.deepseek.com", "api_key": "sk-..."},
            },
        }

    Args:
        beyin_config: Beyin.py formatinda config sozlugu.
        provider_adi: Kullanilacak provider adi. None = default_provider.

    Returns:
        ProviderBase ornegi.

    Örnek:
        >>> cfg = {
        ...     "default_provider": "deepseek",
        ...     "default_model": "deepseek-chat",
        ...     "providers": {
        ...         "deepseek": {"base_url": "https://api.deepseek.com"},
        ...     },
        ... }
        >>> provider = beyin_icin_provider_olustur(cfg)
        >>> yanit = provider.chat([{"role": "user", "content": "Merhaba"}])
    """
    ad = provider_adi or beyin_config.get("default_provider", "lmstudio")
    model = beyin_config.get("default_model")

    # providers alt yapilandirmasini oku
    prov_conf = beyin_config.get("providers", {}).get(ad, {})
    base_url = prov_conf.get("base_url")
    api_key = prov_conf.get("api_key")

    return get_provider(ad=ad, model=model, base_url=base_url, api_key=api_key)


# ═══════════════════════════════════════════════════════════════════════════
# Hizli Test
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

    print("=" * 60)
    print("Provider Abstraction Katmani — Test")
    print("=" * 60)

    # 1. Temel provider olusturma
    print("\n--- 1. Provider olusturma ---")
    for ad in ("deepseek", "openai", "anthropic", "groq", "xiaomi", "xai", "openrouter", "lmstudio"):
        try:
            p = get_provider(ad)
            print(f"  ✅ {p}")
        except ValueError as e:
            print(f"  ❌ {ad}: {e}")

    # 2. hazir_mi kontrolu
    print("\n--- 2. hazir_mi kontrolleri ---")
    for ad in ("deepseek", "openai", "lmstudio"):
        p = get_provider(ad)
        print(f"  {ad}: hazir={p.hazir_mi()}, api_key={'var' if p.api_key else 'yok'}")

    # 3. Ping testi
    print("\n--- 3. Ping testi ---")
    lm = get_provider("lmstudio")
    print(f"  LM Studio ping: {lm.ping()}")

    # 4. Thread guvenligi testi
    print("\n--- 4. Thread guvenligi ---")
    import threading as _th

    def _thread_test(ad: str) -> None:
        p = get_provider(ad)
        print(f"  Thread {_th.current_thread().name}: {p}")

    threads = [
        _th.Thread(target=_thread_test, args=("deepseek",), name=f"T{i}")
        for i in range(5)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("  Thread test tamam.")

    # 5. Config'den yukleme
    print("\n--- 5. Config'den yukleme (ornek) ---")
    ornek_config = {
        "fallback_providers": [
            {"provider": "deepseek", "model": "deepseek-v4-flash", "base_url": "https://api.deepseek.com"},
            {"provider": "lmstudio", "model": "local-model", "base_url": "http://localhost:1234"},
        ]
    }
    tumu = get_all_providers(ornek_config)
    for ad, p in tumu.items():
        print(f"  {ad}: {p}")

    # 6. Provider olusturma dogrulama
    print("\n--- 6. Provider sinif dogrulama ---")
    for ad, sinif in _PROVIDER_SINIFLARI.items():
        instance = sinif()
        required = ["chat", "chat_stream", "models", "ping"]
        eksik = [m for m in required if not hasattr(instance, m)]
        if eksik:
            print(f"  ❌ {ad}: EKSIK metotlar: {eksik}")
        else:
            print(f"  ✅ {ad}: tum gereken metotlar mevcut")

    print("\n" + "=" * 60)
    print("Test tamam.")
