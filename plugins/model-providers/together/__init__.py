"""Native Together AI provider profile."""


__all__ = ['ProviderProfile', 'TogetherProfile', 'fetch_models', 'register_provider']
import json
import logging
import urllib.request

from providers import register_provider
from providers.base import ProviderProfile

logger = logging.getLogger(__name__)

_CACHE: list[str] | None = None


class TogetherProfile(ProviderProfile):
    """Together AI provider profile."""

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        """Fetch models from Together AI API; fall back to fallback_models on failure."""
        global _CACHE  # noqa: PLW0603
        if _CACHE is not None:
            return _CACHE
        if not api_key:
            return list(self.fallback_models) if self.fallback_models else None
        try:
            req = urllib.request.Request("https://api.together.xyz/v1/models")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            models = [
                m["id"]
                for m in data if isinstance(m, dict) and "id" in m
            ]
            if models:
                _CACHE = models
                return models
        except Exception as exc:
            logger.debug("fetch_models(together): %s", exc)

        return list(self.fallback_models) if self.fallback_models else None


together = TogetherProfile(
    name="together",
    aliases=("togetherai", "together-ai"),
    api_mode="chat_completions",
    env_vars=("TOGETHER_API_KEY",),
    base_url="https://api.together.xyz",
    auth_type="api_key",
    display_name="Together AI",
    description="Together AI — hosted open-source models",
    signup_url="https://api.together.xyz/settings/api-keys",
    fallback_models=(
        "meta-llama/Llama-3-70b-chat-hf",
        "meta-llama/Llama-3-8b-chat-hf",
        "mistralai/Mixtral-8x22B-Instruct-v0.1",
        "google/gemma-2-27b-it",
        "Qwen/Qwen2-72B-Instruct",
        "deepseek-ai/deepseek-llm-67b-chat",
    ),
    default_aux_model="meta-llama/Llama-3-8b-chat-hf",
)

register_provider(together)
