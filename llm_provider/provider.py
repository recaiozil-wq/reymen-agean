"""
Unified LLM Provider Interface.

BaseLLMProvider — ABC (modeller, api_key zorunlu)
Concrete: OpenAIProvider, AnthropicProvider, GroqProvider, OllamaProvider
LLMProvider  — config.yaml tabanlı dispatcher (geri uyum)
"""

import os
from abc import ABC, abstractmethod
from typing import Optional

import yaml
from dotenv import load_dotenv

from .models import LLMResponse
from .token_sayac import global_sayac
from .rate_limiter import global_limiter

load_dotenv()


# ---------------------------------------------------------------------------
# ABC
# ---------------------------------------------------------------------------

class BaseLLMProvider(ABC):
    """Her LLM provider'ının uyması gereken soyut temel sınıf."""

    def __init__(self, api_key: str, base_url: str = ""):
        self._api_key = api_key
        if base_url:
            self._base_url = base_url
        else:
            self._base_url = ""

    @property
    @abstractmethod
    def modeller(self) -> list[str]:
        """Provider'ın desteklediği model adları listesi."""
        ...

    @property
    @abstractmethod
    def api_key(self) -> str:
        """Kimlik doğrulama anahtarı."""
        ...

    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        """Sohbet tamamlama isteği gönder."""
        ...

    @property
    def base_url(self) -> str:
        return self._base_url


# ---------------------------------------------------------------------------
# Concrete providers
# ---------------------------------------------------------------------------

class OpenAIProvider(BaseLLMProvider):
    """OpenAI Chat Completions (gpt-4o, gpt-4-turbo, ...)."""

    _MODELLER = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

    def __init__(self, api_key: str, base_url: str = "", model: str = "gpt-4o",
                 max_tokens: int = 4096, temperature: float = 0.7):
        super().__init__(api_key, base_url)
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    @property
    def modeller(self) -> list[str]:
        return self._MODELLER

    @property
    def api_key(self) -> str:
        return self._api_key

    def _istemci(self):
        if self._client is None:
            from openai import OpenAI
            kwargs = {"api_key": self._api_key}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        model = kwargs.pop("model", self._model)
        max_tokens = kwargs.pop("max_tokens", self.max_tokens)
        temperature = kwargs.pop("temperature", self.temperature)
        response = self._istemci().chat.completions.create(
            model=model, messages=messages,
            max_tokens=max_tokens, temperature=temperature, **kwargs,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content,
            model=model,
            provider="openai",
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            },
            raw=response,
        )


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Messages API (claude-*)."""

    _MODELLER = [
        "claude-sonnet-4-6", "claude-opus-4-8",
        "claude-haiku-4-5-20251001", "claude-3-5-sonnet-20241022",
    ]

    def __init__(self, api_key: str, base_url: str = "",
                 model: str = "claude-sonnet-4-6",
                 max_tokens: int = 4096, temperature: float = 0.7):
        super().__init__(api_key, base_url)
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    @property
    def modeller(self) -> list[str]:
        return self._MODELLER

    @property
    def api_key(self) -> str:
        return self._api_key

    def _istemci(self):
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self._api_key)
        return self._client

    def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        model = kwargs.pop("model", self._model)
        max_tokens = kwargs.pop("max_tokens", self.max_tokens)
        temperature = kwargs.pop("temperature", self.temperature)

        system_msg = None
        anthropic_msgs = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                anthropic_msgs.append({"role": m["role"], "content": m["content"]})

        response = self._istemci().messages.create(
            model=model, max_tokens=max_tokens, temperature=temperature,
            system=system_msg, messages=anthropic_msgs, **kwargs,
        )
        content = "".join(b.text for b in response.content if hasattr(b, "text"))
        return LLMResponse(
            content=content,
            model=model,
            provider="anthropic",
            usage={
                "input_tokens": response.usage.input_tokens if response.usage else 0,
                "output_tokens": response.usage.output_tokens if response.usage else 0,
            },
            raw=response,
        )


class GroqProvider(BaseLLMProvider):
    """Groq (OpenAI-uyumlu API)."""

    _MODELLER = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]

    def __init__(self, api_key: str, base_url: str = "https://api.groq.com/openai/v1",
                 model: str = "llama-3.3-70b-versatile",
                 max_tokens: int = 4096, temperature: float = 0.7):
        super().__init__(api_key, base_url)
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    @property
    def modeller(self) -> list[str]:
        return self._MODELLER

    @property
    def api_key(self) -> str:
        return self._api_key

    def _istemci(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        return self._client

    def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        model = kwargs.pop("model", self._model)
        max_tokens = kwargs.pop("max_tokens", self.max_tokens)
        temperature = kwargs.pop("temperature", self.temperature)
        response = self._istemci().chat.completions.create(
            model=model, messages=messages,
            max_tokens=max_tokens, temperature=temperature, **kwargs,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content,
            model=model,
            provider="groq",
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            },
            raw=response,
        )


class OllamaProvider(BaseLLMProvider):
    """Ollama (yerel OpenAI-uyumlu sunucu)."""

    _MODELLER = ["llama3", "mistral", "phi3", "gemma2"]

    def __init__(self, api_key: str = "ollama",
                 base_url: str = "http://localhost:11434/v1",
                 model: str = "llama3",
                 max_tokens: int = 4096, temperature: float = 0.7):
        super().__init__(api_key, base_url)
        self._model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    @property
    def modeller(self) -> list[str]:
        return self._MODELLER

    @property
    def api_key(self) -> str:
        return self._api_key

    def _istemci(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        return self._client

    def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        model = kwargs.pop("model", self._model)
        max_tokens = kwargs.pop("max_tokens", self.max_tokens)
        temperature = kwargs.pop("temperature", self.temperature)
        response = self._istemci().chat.completions.create(
            model=model, messages=messages,
            max_tokens=max_tokens, temperature=temperature, **kwargs,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content,
            model=model,
            provider="ollama",
            raw=response,
        )


# ---------------------------------------------------------------------------
# Config yardımcısı
# ---------------------------------------------------------------------------

def load_config(config_path: Optional[str] = None) -> dict:
    """config.yaml'ı yükle."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _env_anahtar(key: str) -> str:
    """Env değişkenini oku; boşluk ve çevreleyen tırnakları temizle."""
    v = os.getenv(key, "")
    if v:
        return v.strip().strip('"').strip("'")
    return ""


_PROVIDER_SINIFLAR: dict[str, type[BaseLLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "groq": GroqProvider,
    "ollama": OllamaProvider,
}


# ---------------------------------------------------------------------------
# Dispatcher (geri uyum + fallback zinciri)
# ---------------------------------------------------------------------------

class LLMProvider:
    """Config.yaml tabanlı dispatcher — fallback zinciri yönetir."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = load_config(config_path)
        self.provider_name = self.config.get("default_provider", "openai")
        self._aktif: BaseLLMProvider = self._olustur(self.provider_name)

    def _olustur(self, isim: str) -> BaseLLMProvider:
        """Config'e göre provider instance oluştur."""
        cfg = self.config["providers"].get(isim, {})
        api_key = _env_anahtar(cfg.get("api_key_env", "")) or ("ollama" if isim == "ollama" else "")
        sinif = _PROVIDER_SINIFLAR.get(isim)
        if sinif is None:
            raise ValueError(f"Desteklenmeyen provider: {isim}")
        return sinif(
            api_key=api_key,
            base_url=cfg.get("base_url", ""),
            model=cfg.get("model", ""),
            max_tokens=cfg.get("max_tokens", 4096),
            temperature=cfg.get("temperature", 0.7),
        )

    def chat(self, messages: list[dict], **kwargs) -> LLMResponse:
        """Sıralı fallback zinciriyle chat gönder."""
        siralama = [self.provider_name] + [
            p for p in self.config["providers"] if p != self.provider_name
        ]
        last_err = None
        for isim in siralama:
            cfg = self.config["providers"].get(isim, {})
            api_key = _env_anahtar(cfg.get("api_key_env", ""))
            if not api_key and isim != "ollama":
                last_err = f"{isim}: API key yok"
                continue
            try:
                # Rate limit kontrolü
                global_limiter().bekle(isim)

                provider = self._olustur(isim)
                sonuc = provider.chat(messages, **kwargs)
                self._aktif = provider
                self.provider_name = isim

                # Token kullanımını kaydet
                if sonuc.usage:
                    giris = sonuc.usage.get("prompt_tokens") or sonuc.usage.get("input_tokens", 0)
                    cikis = sonuc.usage.get("completion_tokens") or sonuc.usage.get("output_tokens", 0)
                    global_sayac().kaydet(isim, sonuc.model, giris, cikis)

                return sonuc
            except Exception as exc:
                last_err = f"{isim}: {exc}"
                print(f"[LLM Fallback] {isim} başarısız → {exc}")
        return LLMResponse(content="", model="", provider=self.provider_name, error=str(last_err))

    def switch_provider(self, provider_name: str) -> None:
        """Runtime'da provider değiştir."""
        self._aktif = self._olustur(provider_name)
        self.provider_name = provider_name

    @property
    def modeller(self) -> list[str]:
        """Aktif provider'ın desteklediği modeller."""
        return self._aktif.modeller

    @property
    def api_key(self) -> str:
        return self._aktif.api_key

    @property
    def current_provider(self) -> str:
        return self.provider_name


def get_provider(config_path: Optional[str] = None) -> LLMProvider:
    """Yapılandırılmış LLMProvider döndür."""
    return LLMProvider(config_path)
