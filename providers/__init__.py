# -*- coding: utf-8 -*-
"""
providers/__init__.py — 20+ LLM provider registry + plugin sistemi.

Kullanim (klasik, geriye uyumlu):
    from providers import get_provider, list_providers
import logging
logger = logging.getLogger(__name__)
    profil = get_provider("deepseek")
    profil = get_provider("claude")   # alias ile de calisir
    print(list_providers())

Kullanim (plugin sistemi):
    from providers import plugin_al, plugin_listele, plugin_ping
    ok, mesaj = plugin_ping("lmstudio")
    plugin = plugin_al("openai")
    plugin.test()
"""

__all__ = ['AnthropicPlugin', 'CoherePlugin', 'DeepSeekPlugin', 'FireworksPlugin', 'GooglePlugin', 'GroqPlugin', 'LMStudioPlugin', 'MistralPlugin', 'OllamaPlugin', 'OpenAIPlugin', 'OpenRouterPlugin', 'Path', 'PerplexityPlugin', 'ProviderPlugin', 'ProviderProfile', 'TogetherPlugin', 'XAIPlugin', 'get_provider', 'list_providers', 'mevcut_providerlar', 'plugin_al', 'plugin_kaydet', 'plugin_listele', 'plugin_ping', 'plugin_test_hepsi', 'provider_kaydet', 'register_provider']
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))

from providers.base import ProviderProfile  # noqa: E402

# ── Plugin Sistemi ────────────────────────────────────────────────────

from providers.plugin_base import ProviderPlugin  # noqa: E402

# Tüm plugin sınıflarını import et
_PLUGIN_IMPORT_HATA = ""
try:
    from providers.lmstudio_plugin import LMStudioPlugin
    from providers.ollama_plugin import OllamaPlugin
    from providers.deepseek_plugin import DeepSeekPlugin
    from providers.openai_plugin import OpenAIPlugin
    from providers.anthropic_plugin import AnthropicPlugin
    from providers.groq_plugin import GroqPlugin
    from providers.google_plugin import GooglePlugin
    from providers.openrouter_plugin import OpenRouterPlugin
    from providers.together_plugin import TogetherPlugin
    from providers.fireworks_plugin import FireworksPlugin
    from providers.xai_plugin import XAIPlugin
    from providers.mistral_plugin import MistralPlugin
    from providers.cohere_plugin import CoherePlugin
    from providers.perplexity_plugin import PerplexityPlugin
    _PLUGIN_IMPORT_OK = True
except ImportError as _e:
    _PLUGIN_IMPORT_OK = False
    _PLUGIN_IMPORT_HATA = str(_e)

_PLUGIN_REGISTRY: dict[str, ProviderPlugin] = {}


def plugin_kaydet(plugin: ProviderPlugin) -> None:
    """Yeni bir plugin'i kayıt defterine ekle."""
    try:
        _PLUGIN_REGISTRY[plugin.provider_adi] = plugin
        if hasattr(plugin, "aliases"):
            for alias in plugin.aliases:
                _PLUGIN_REGISTRY[alias] = plugin
    except Exception as e:
        print(f"Plugin kayıt hatası ({plugin}): {e}")


def plugin_al(ad: str) -> ProviderPlugin | None:
    """Ada göre plugin döndür; bulunamazsa None."""
    try:
        return _PLUGIN_REGISTRY.get(ad)
    except Exception:
        return None


def plugin_listele() -> list[str]:
    """Kayıtlı plugin adlarını sıralı listele."""
    try:
        return sorted(_PLUGIN_REGISTRY.keys())
    except Exception:
        return []


def plugin_ping(ad: str) -> tuple[bool, str]:
    """Belirtilen provider plugin'ini ping'le."""
    try:
        plugin = plugin_al(ad)
        if not plugin:
            return False, f"Plugin bulunamadı: {ad}"
        return plugin.ping()
    except Exception as e:
        return False, f"Plugin ping hatası: {e}"


def plugin_test_hepsi() -> dict[str, tuple[bool, str]]:
    """Tüm kayıtlı plugin'leri test eder; {ad: (ok, mesaj)} sözlüğü döner."""
    try:
        sonuclar = {}
        for ad, plugin in _PLUGIN_REGISTRY.items():
            try:
                sonuclar[ad] = plugin.ping()
            except Exception as e:
                sonuclar[ad] = (False, str(e))
        return sonuclar
    except Exception as e:
        return {"hata": (False, str(e))}


def _plugin_sistemini_kur() -> None:
    """Yerleşik plugin'leri kayıt defterine ekle."""
    if not _PLUGIN_IMPORT_OK:
        print(f"Plugin sistemi devre dışı — import hatası: {_PLUGIN_IMPORT_HATA}")
        return
    for sinif in [
        LMStudioPlugin, OllamaPlugin, DeepSeekPlugin, OpenAIPlugin,
        AnthropicPlugin, GroqPlugin, GooglePlugin, OpenRouterPlugin,
        TogetherPlugin, FireworksPlugin, XAIPlugin, MistralPlugin,
        CoherePlugin, PerplexityPlugin,
    ]:
        try:
            plugin_kaydet(sinif())
        except Exception as e:
            print(f"Plugin kurulamadı ({sinif.__name__}): {e}")


_plugin_sistemini_kur()

# ── Provider Tanimlari ────────────────────────────────────────────────

_PROVIDERS: list[ProviderProfile] = [

    # Yerel (API anahtari gerekmez)
    ProviderProfile(
        name="lmstudio",
        aliases=("lm-studio", "lm_studio", "local"),
        base_url="http://localhost:1234",
        default_model="cognitivecomputations.dolphin3.0-llama3.1-8b",
        notes="LM Studio yerel sunucu. system→user cevirmesi gerekir.",
    ),
    ProviderProfile(
        name="ollama",
        aliases=("ollama-local",),
        base_url="http://localhost:11434",
        default_model="llama3.1:8b",
        notes="Ollama yerel sunucu.",
    ),
    ProviderProfile(
        name="vllm",
        aliases=("vllm-local",),
        base_url="http://localhost:8000",
        default_model="meta-llama/Llama-3.1-8B-Instruct",
        notes="vLLM OpenAI uyumlu endpoint.",
    ),
    ProviderProfile(
        name="xinference",
        aliases=("xorbits",),
        base_url="http://localhost:9997",
        default_model="qwen2-instruct",
        notes="Xinference yerel inference sunucu.",
    ),
    ProviderProfile(
        name="litellm",
        aliases=("litellm-proxy",),
        base_url="http://localhost:4000",
        default_model="gpt-3.5-turbo",
        notes="LiteLLM proxy gateway.",
    ),

    # Bulut (API anahtari gerekli)
    ProviderProfile(
        name="deepseek",
        aliases=("ds",),
        base_url="https://api.deepseek.com",
        env_vars=("DEEPSEEK_API_KEY",),
        default_model="deepseek-chat",
    ),
    ProviderProfile(
        name="openai",
        aliases=("gpt", "chatgpt"),
        base_url="https://api.openai.com",
        env_vars=("OPENAI_API_KEY",),
        default_model="gpt-4o-mini",
    ),
    ProviderProfile(
        name="anthropic",
        aliases=("claude",),
        base_url="https://api.anthropic.com",
        env_vars=("ANTHROPIC_API_KEY",),
        default_model="claude-haiku-4-5-20251001",
        openai_compat=False,
        api_key_header="x-api-key",
        api_key_prefix="",
        notes="Anthropic Messages API — openai_compat=False.",
    ),
    ProviderProfile(
        name="groq",
        aliases=("groq-cloud",),
        base_url="https://api.groq.com/openai/v1",
        env_vars=("GROQ_API_KEY",),
        default_model="llama-3.1-8b-instant",
    ),
    ProviderProfile(
        name="together",
        aliases=("togetherai", "together-ai"),
        base_url="https://api.together.xyz",
        env_vars=("TOGETHER_API_KEY",),
        default_model="meta-llama/Llama-3-8b-chat-hf",
    ),
    ProviderProfile(
        name="mistral",
        aliases=("mistralai",),
        base_url="https://api.mistral.ai",
        env_vars=("MISTRAL_API_KEY",),
        default_model="mistral-small-latest",
    ),
    ProviderProfile(
        name="cohere",
        aliases=("cohere-ai",),
        base_url="https://api.cohere.ai",
        env_vars=("COHERE_API_KEY",),
        default_model="command-r",
        notes="Cohere Command modelleri.",
    ),
    ProviderProfile(
        name="perplexity",
        aliases=("pplx",),
        base_url="https://api.perplexity.ai",
        env_vars=("PERPLEXITY_API_KEY",),
        default_model="llama-3.1-sonar-small-128k-online",
        notes="Web aramali modeller.",
    ),
    ProviderProfile(
        name="fireworks",
        aliases=("fireworks-ai",),
        base_url="https://api.fireworks.ai/inference",
        env_vars=("FIREWORKS_API_KEY",),
        default_model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    ),
    ProviderProfile(
        name="openrouter",
        aliases=("or", "open-router"),
        base_url="https://openrouter.ai/api",
        env_vars=("OPENROUTER_API_KEY",),
        default_model="meta-llama/llama-3.1-8b-instruct:free",
        notes="Ucretsiz modeller mevcut (free tier).",
    ),
    ProviderProfile(
        name="google",
        aliases=("gemini", "google-ai"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        env_vars=("GOOGLE_API_KEY", "GEMINI_API_KEY"),
        default_model="gemini-2.0-flash",
    ),
    ProviderProfile(
        name="azure",
        aliases=("azure-openai", "aoai"),
        base_url="",
        env_vars=("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"),
        default_model="gpt-4o-mini",
        notes=(
            "base_url bos — kullanim oncesi AZURE_OPENAI_ENDPOINT "
            "degerini okuyup profili guncelleyin (orn. provider_kaydet "
            "ile yeni bir ProviderProfile kaydedin)."
        ),
    ),
    ProviderProfile(
        name="huggingface",
        aliases=("hf", "hugging-face"),
        base_url="https://api-inference.huggingface.co",
        env_vars=("HUGGINGFACE_API_KEY", "HF_TOKEN"),
        default_model="meta-llama/Llama-3.1-8B-Instruct",
        notes="HuggingFace Inference API.",
    ),
    ProviderProfile(
        name="nvidia",
        aliases=("nvidia-ai",),
        base_url="https://integrate.api.nvidia.com",
        env_vars=("NVIDIA_API_KEY",),
        default_model="meta/llama-3.1-8b-instruct",
    ),
    ProviderProfile(
        name="alibaba",
        aliases=("dashscope", "qwen"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        env_vars=("DASHSCOPE_API_KEY",),
        default_model="qwen-plus",
        notes="Alibaba DashScope / Qwen modelleri.",
    ),
    ProviderProfile(
        name="moonshot",
        aliases=("kimi",),
        base_url="https://api.moonshot.cn",
        env_vars=("MOONSHOT_API_KEY",),
        default_model="moonshot-v1-8k",
    ),
    ProviderProfile(
        name="zhipu",
        aliases=("glm", "zhipuai"),
        base_url="https://open.bigmodel.cn/api/paas",
        env_vars=("ZHIPU_API_KEY",),
        default_model="glm-4-flash",
    ),
    ProviderProfile(
        name="anyscale",
        aliases=("anyscale-endpoints",),
        base_url="https://api.endpoints.anyscale.com",
        env_vars=("ANYSCALE_API_KEY",),
        default_model="meta-llama/Llama-3-8b-chat-hf",
    ),
]

# ── Registry ─────────────────────────────────────────────────────────

_BY_NAME: dict[str, ProviderProfile] = {}


def _build_registry() -> None:
    for p in _PROVIDERS:
        _BY_NAME[p.name] = p
        for alias in p.aliases:
            _BY_NAME[alias] = p


_build_registry()


def get_provider(name: str) -> ProviderProfile | None:
    """Isme veya alias'a gore provider profili dondur."""
    return _BY_NAME.get(name.lower().strip())


def list_providers() -> list[str]:
    """Kayitli provider isimlerini listele (alias haric)."""
    return sorted(p.name for p in _PROVIDERS)


def mevcut_providerlar() -> list[str]:
    """API anahtari olan veya yerel providerlar."""
    return [p.name for p in _PROVIDERS if p.mevcut_mu()]


def provider_kaydet(profil: ProviderProfile) -> None:
    """Runtime'da yeni bir provider kaydet (varolan ayni isimli profili gunceller)."""
    mevcut = _BY_NAME.get(profil.name)
    if mevcut is None:
        _PROVIDERS.append(profil)
    else:
        idx = _PROVIDERS.index(mevcut)
        _PROVIDERS[idx] = profil
    _BY_NAME[profil.name] = profil
    for alias in profil.aliases:
        _BY_NAME[alias] = profil


def register_provider(
    provider: ProviderProfile | type[ProviderProfile] | str | ProviderPlugin | None = None,
    provider_class: type | None = None,
    **kwargs,
) -> None:
    """Provider kaydet — 33 model-provider plugin'inin kullandigi arayuz.

    Kullanim (en yaygin):
        register_provider(profile_instance)

    Kullanim (alternatif — sinif + kwargs):
        class MyProvider(ProviderProfile): ...
        register_provider("myprovider", MyProvider, env_vars=("MY_KEY",), base_url="...")
        register_provider(MyProvider)  # sinifin varsayilan kurucusuyla

    1. ``ProviderProfile`` ornegi gonderilirse -> ``provider_kaydet`` ile kaydeder.
    2. ``ProviderPlugin`` ornegi gonderilirse -> ``plugin_kaydet`` ile kaydeder.
    3. ``str`` + ``provider_class`` gonderilirse -> sinifi kurup kaydeder.
    4. ``provider_class`` tek basina gonderilirse -> varsayilan kurucuyla kurar.
    """
    # ── Durum 1: ProviderProfile ornegi ───────────────────────────────
    if isinstance(provider, ProviderProfile):
        provider_kaydet(provider)
        return

    # ── Durum 2: ProviderPlugin ornegi ────────────────────────────────
    if isinstance(provider, ProviderPlugin):
        plugin_kaydet(provider)
        return

    # ── Durum 3: Sinif (ProviderProfile alt sinifi) ───────────────────
    if isinstance(provider, type) and issubclass(provider, ProviderProfile):
        instance = provider(**kwargs)
        provider_kaydet(instance)
        return

    if isinstance(provider, type) and hasattr(provider, "provider_adi"):
        # ProviderPlugin alt sinifi
        instance = provider(**kwargs)
        plugin_kaydet(instance)
        return

    # ── Durum 4: isim + sinif (provider_class parametresi) ────────────
    if isinstance(provider, str) and provider_class is not None:
        if isinstance(provider_class, type) and issubclass(provider_class, ProviderProfile):
            instance = provider_class(name=provider, **kwargs)
            provider_kaydet(instance)
            return
        if isinstance(provider_class, type) and hasattr(provider_class, "provider_adi"):
            instance = provider_class(**kwargs)
            plugin_kaydet(instance)
            return

    # ── Durum 5: Sadece kwargs — ProviderProfile kurup kaydet ────────
    if provider is None and provider_class is not None:
        if isinstance(provider_class, type) and issubclass(provider_class, ProviderProfile):
            instance = provider_class(**kwargs)
            provider_kaydet(instance)
            return

    # ── Bilinmeyen / desteklenmeyen kullanim ──────────────────────────
    raise TypeError(
        f"register_provider() beklenmeyen arguman: provider={provider!r}, "
        f"provider_class={provider_class!r}, kwargs={kwargs}. "
        f"Beklenen: ProviderProfile ornegi, ProviderPlugin ornegi, "
        f"veya ProviderProfile alt sinifi."
    )


if __name__ == "__main__":
    print(f"Toplam provider: {len(list_providers())}")
    print(f"Provider listesi: {list_providers()}")
    print(f"\nMevcut providerlar: {mevcut_providerlar()}")
    p = get_provider("claude")
    if p:
        print(f"\nAnthropic profili: {p.name} -> {p.base_url}")