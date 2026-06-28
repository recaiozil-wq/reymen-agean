# -*- coding: utf-8 -*-
"""
tests/test_providers.py — Provider plugin sistemi için birim testleri.

Her plugin'in import edilebilirliğini, ping() metodunun çalışmasını
ve kayıt sisteminin doğru kurulduğunu doğrular. Ağ erişimi olmasa
bile testler geçer (ping başarısız olabilir, hata fırlatmamalı).
"""
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))


# ── Plugin Base ───────────────────────────────────────────────────────

def test_plugin_base_import():
    """plugin_base modülünün ve ProviderPlugin ABC'nin import edildiğini doğrular."""
    try:
        from providers.plugin_base import ProviderPlugin, Renk
        assert ProviderPlugin is not None
        assert Renk.YESIL != ""
        print("  plugin_base: OK")
    except Exception as e:
        assert False, f"plugin_base import hatası: {e}"


# ── Yerel Plugin'ler ──────────────────────────────────────────────────

def test_lmstudio_plugin():
    """LM Studio plugin'ini test eder; her durumda (çevrimdışı dahil) hata fırlatmaz."""
    try:
        from providers.lmstudio_plugin import LMStudioPlugin
        p = LMStudioPlugin()
        assert p.provider_adi == "lmstudio"
        assert "localhost" in p.base_url
        assert isinstance(p.modeller, list) and len(p.modeller) > 0
        assert p.api_key_schema == []
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  LM Studio: {msg}")
    except Exception as e:
        assert False, f"LM Studio plugin hatası: {e}"


def test_ollama_plugin():
    """Ollama plugin'ini test eder; her durumda hata fırlatmaz."""
    try:
        from providers.ollama_plugin import OllamaPlugin
        p = OllamaPlugin()
        assert p.provider_adi == "ollama"
        assert "localhost" in p.base_url
        assert isinstance(p.modeller, list) and len(p.modeller) > 0
        assert p.api_key_schema == []
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  Ollama: {msg}")
    except Exception as e:
        assert False, f"Ollama plugin hatası: {e}"


# ── Bulut Plugin'leri ─────────────────────────────────────────────────

def test_deepseek_plugin():
    """DeepSeek plugin'ini test eder; API anahtarı yoksa False döner, hata fırlatmaz."""
    try:
        from providers.deepseek_plugin import DeepSeekPlugin
        p = DeepSeekPlugin()
        assert p.provider_adi == "deepseek"
        assert "deepseek.com" in p.base_url
        assert len(p.api_key_schema) > 0
        assert p.api_key_schema[0]["key"] == "DEEPSEEK_API_KEY"
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  DeepSeek: {msg}")
    except Exception as e:
        assert False, f"DeepSeek plugin hatası: {e}"


def test_openai_plugin():
    """OpenAI plugin'ini test eder; API anahtarı yoksa False döner, hata fırlatmaz."""
    try:
        from providers.openai_plugin import OpenAIPlugin
        p = OpenAIPlugin()
        assert p.provider_adi == "openai"
        assert "openai.com" in p.base_url
        assert len(p.api_key_schema) > 0
        assert "gpt-4o" in p.modeller
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  OpenAI: {msg}")
    except Exception as e:
        assert False, f"OpenAI plugin hatası: {e}"


def test_anthropic_plugin():
    """Anthropic plugin'ini test eder; özel x-api-key başlığı kullanır."""
    try:
        from providers.anthropic_plugin import AnthropicPlugin
        p = AnthropicPlugin()
        assert p.provider_adi == "anthropic"
        assert "anthropic.com" in p.base_url
        assert p.api_key_schema[0]["key"] == "ANTHROPIC_API_KEY"
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  Anthropic: {msg}")
    except Exception as e:
        assert False, f"Anthropic plugin hatası: {e}"


def test_groq_plugin():
    """Groq plugin'ini test eder; /openai/v1/models endpoint'ini kullanır."""
    try:
        from providers.groq_plugin import GroqPlugin
        p = GroqPlugin()
        assert p.provider_adi == "groq"
        assert "groq.com" in p.base_url
        assert len(p.modeller) > 0
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  Groq: {msg}")
    except Exception as e:
        assert False, f"Groq plugin hatası: {e}"


def test_google_plugin():
    """Google Gemini plugin'ini test eder; GOOGLE_API_KEY veya GEMINI_API_KEY arar."""
    try:
        from providers.google_plugin import GooglePlugin
        p = GooglePlugin()
        assert p.provider_adi == "google"
        assert "googleapis.com" in p.base_url
        assert "gemini-2.0-flash" in p.modeller
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  Google Gemini: {msg}")
    except Exception as e:
        assert False, f"Google plugin hatası: {e}"


def test_openrouter_plugin():
    """OpenRouter plugin'ini test eder."""
    try:
        from providers.openrouter_plugin import OpenRouterPlugin
        p = OpenRouterPlugin()
        assert p.provider_adi == "openrouter"
        assert "openrouter.ai" in p.base_url
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  OpenRouter: {msg}")
    except Exception as e:
        assert False, f"OpenRouter plugin hatası: {e}"


def test_together_plugin():
    """Together AI plugin'ini test eder."""
    try:
        from providers.together_plugin import TogetherPlugin
        p = TogetherPlugin()
        assert p.provider_adi == "together"
        assert "together.xyz" in p.base_url
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  Together AI: {msg}")
    except Exception as e:
        assert False, f"Together AI plugin hatası: {e}"


def test_fireworks_plugin():
    """Fireworks AI plugin'ini test eder."""
    try:
        from providers.fireworks_plugin import FireworksPlugin
        p = FireworksPlugin()
        assert p.provider_adi == "fireworks"
        assert "fireworks.ai" in p.base_url
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  Fireworks AI: {msg}")
    except Exception as e:
        assert False, f"Fireworks AI plugin hatası: {e}"


def test_xai_plugin():
    """xAI Grok plugin'ini test eder."""
    try:
        from providers.xai_plugin import XAIPlugin
        p = XAIPlugin()
        assert p.provider_adi == "xai"
        assert "x.ai" in p.base_url
        assert "grok-2" in p.modeller
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        assert isinstance(msg, str)
        print(f"  xAI Grok: {msg}")
    except Exception as e:
        assert False, f"xAI plugin hatası: {e}"


def test_mistral_plugin():
    """Mistral AI plugin'ini test eder."""
    try:
        from providers.mistral_plugin import MistralPlugin
        p = MistralPlugin()
        assert p.provider_adi == "mistral"
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        print(f"  Mistral: {msg}")
    except Exception as e:
        assert False, f"Mistral plugin hatası: {e}"


def test_cohere_plugin():
    """Cohere AI plugin'ini test eder."""
    try:
        from providers.cohere_plugin import CoherePlugin
        p = CoherePlugin()
        assert p.provider_adi == "cohere"
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        print(f"  Cohere: {msg}")
    except Exception as e:
        assert False, f"Cohere plugin hatası: {e}"


def test_perplexity_plugin():
    """Perplexity AI plugin'ini test eder."""
    try:
        from providers.perplexity_plugin import PerplexityPlugin
        p = PerplexityPlugin()
        assert p.provider_adi == "perplexity"
        ok, msg = p.ping()
        assert isinstance(ok, bool)
        print(f"  Perplexity: {msg}")
    except Exception as e:
        assert False, f"Perplexity plugin hatası: {e}"


# ── Registry Sistemi ──────────────────────────────────────────────────

def test_plugin_kayit_sistemi():
    """Plugin kayıt sisteminin doğru kurulduğunu doğrular."""
    try:
        from providers import plugin_listele, plugin_al, plugin_ping
        liste = plugin_listele()
        assert isinstance(liste, list)
        assert len(liste) > 0, "Plugin listesi boş olmamalı"
        assert "lmstudio" in liste
        assert "openai" in liste
        assert "anthropic" in liste
        print(f"  Kayıtlı plugin sayısı: {len(liste)}")
        print(f"  Plugin listesi: {liste}")
    except Exception as e:
        assert False, f"Plugin kayıt sistemi hatası: {e}"


def test_plugin_al():
    """plugin_al() fonksiyonunun doğru plugin döndürdüğünü doğrular."""
    try:
        from providers import plugin_al
        plugin = plugin_al("lmstudio")
        assert plugin is not None, "lmstudio plugin'i bulunamadı"
        assert plugin.provider_adi == "lmstudio"

        yok = plugin_al("var_olmayan_provider")
        assert yok is None, "Var olmayan provider None döndürmeli"
        print("  plugin_al(): OK")
    except Exception as e:
        assert False, f"plugin_al() hatası: {e}"


def test_plugin_ping():
    """plugin_ping() fonksiyonunun hata fırlatmadığını doğrular."""
    try:
        from providers import plugin_ping
        ok, msg = plugin_ping("lmstudio")
        assert isinstance(ok, bool)
        assert isinstance(msg, str)

        ok2, msg2 = plugin_ping("var_olmayan")
        assert ok2 is False
        assert "bulunamadı" in msg2 or "not found" in msg2.lower()
        print(f"  plugin_ping('lmstudio'): {ok}, '{msg}'")
    except Exception as e:
        assert False, f"plugin_ping() hatası: {e}"


def test_eski_api_geriye_uyumluluk():
    """Eski statik provider API'sinin hâlâ çalıştığını doğrular (geriye uyumluluk)."""
    try:
        from providers import get_provider, list_providers, mevcut_providerlar
        liste = list_providers()
        assert len(liste) >= 20, f"Provider sayısı düşük: {len(liste)}"
        profil = get_provider("lmstudio")
        assert profil is not None
        assert profil.name == "lmstudio"
        profil2 = get_provider("claude")  # alias testi
        assert profil2 is not None
        assert profil2.name == "anthropic"
        print(f"  Eski API: {len(liste)} provider, alias 'claude' → anthropic OK")
    except Exception as e:
        assert False, f"Geriye uyumluluk hatası: {e}"


def test_plugin_test_metodu():
    """Her plugin'in test() metodunun renkli çıktı döndürdüğünü doğrular."""
    try:
        from providers.lmstudio_plugin import LMStudioPlugin
        from providers.ollama_plugin import OllamaPlugin
        for sinif in [LMStudioPlugin, OllamaPlugin]:
            p = sinif()
            ok, msg = p.test()
            assert isinstance(ok, bool)
            assert isinstance(msg, str)
            assert len(msg) > 0
        print("  test() metotları: OK")
    except Exception as e:
        assert False, f"test() metodu hatası: {e}"


# ── Manuel çalıştırma ─────────────────────────────────────────────────

if __name__ == "__main__":
    from providers.plugin_base import Renk

    testler = [
        test_plugin_base_import,
        test_lmstudio_plugin,
        test_ollama_plugin,
        test_deepseek_plugin,
        test_openai_plugin,
        test_anthropic_plugin,
        test_groq_plugin,
        test_google_plugin,
        test_openrouter_plugin,
        test_together_plugin,
        test_fireworks_plugin,
        test_xai_plugin,
        test_mistral_plugin,
        test_cohere_plugin,
        test_perplexity_plugin,
        test_plugin_kayit_sistemi,
        test_plugin_al,
        test_plugin_ping,
        test_eski_api_geriye_uyumluluk,
        test_plugin_test_metodu,
    ]

    gecen = 0
    kalan = 0
    print(f"\n{Renk.BOLD}Provider Plugin Testleri{Renk.RESET}")
    print("=" * 50)
    for test_fn in testler:
        isim = test_fn.__name__.replace("test_", "").replace("_", " ")
        try:
            test_fn()
            print(f"{Renk.YESIL}✓{Renk.RESET} {isim}")
            gecen += 1
        except AssertionError as e:
            print(f"{Renk.KIRMIZI}✗{Renk.RESET} {isim}: {e}")
            kalan += 1
        except Exception as e:
            print(f"{Renk.KIRMIZI}✗{Renk.RESET} {isim}: {e}")
            kalan += 1
    print("=" * 50)
    print(f"Sonuç: {Renk.YESIL}{gecen} geçti{Renk.RESET}, {Renk.KIRMIZI}{kalan} kaldı{Renk.RESET}")
