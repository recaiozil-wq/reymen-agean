"""Test reymen.core.model_adapter — 7 provider, auto-detect."""

import pytest


class TestModelAdapter:
    def test_import(self):
        from reymen.core import model_adapter

        assert hasattr(model_adapter, "ModelAdapter")
        assert hasattr(model_adapter, "AnthropicAdapter")
        assert hasattr(model_adapter, "OllamaAdapter")
        assert hasattr(model_adapter, "OpenAICompatAdapter")
        assert hasattr(model_adapter, "get_active_adapter")

    def test_anthropic_adapter(self):
        from reymen.core.model_adapter import AnthropicAdapter

        adapter = AnthropicAdapter(model="claude-3-5-sonnet-20241022")
        assert adapter is not None

    def test_ollama_adapter(self):
        from reymen.core.model_adapter import OllamaAdapter

        adapter = OllamaAdapter(model="llama3")
        assert adapter is not None

    def test_openai_compat_adapter(self):
        from reymen.core.model_adapter import OpenAICompatAdapter

        adapter = OpenAICompatAdapter(
            base_url="http://localhost:1234", model="test-model"
        )
        assert adapter is not None
