"""Native OpenAI (generic) provider profile.

Generic OpenAI — distinct from openai-codex (Responses API).
Uses the standard Chat Completions API with Bearer auth.
"""


__all__ = ['OpenAIProfile', 'ProviderProfile', 'fetch_models', 'register_provider']
import json
import logging
import urllib.request

from providers import register_provider
from providers.base import ProviderProfile

logger = logging.getLogger(__name__)

_CACHE: list[str] | None = None


class OpenAIProfile(ProviderProfile):
    """Generic OpenAI provider profile."""

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        """Fetch models from OpenAI API; fall back to fallback_models on failure."""
        global _CACHE  # noqa: PLW0603
        if _CACHE is not None:
            return _CACHE
        if not api_key:
            return list(self.fallback_models) if self.fallback_models else None
        try:
            req = urllib.request.Request("https://api.openai.com/v1/models")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            models = [
                m["id"]
                for m in data.get("data", [])
                if isinstance(m, dict) and "id" in m
            ]
            if models:
                _CACHE = models
                return models
        except Exception as exc:
            logger.debug("fetch_models(openai): %s", exc)

        return list(self.fallback_models) if self.fallback_models else None


openai = OpenAIProfile(
    name="openai",
    aliases=("gpt", "chatgpt", "openai-chat"),
    api_mode="chat_completions",
    env_vars=("OPENAI_API_KEY",),
    base_url="https://api.openai.com",
    auth_type="api_key",
    display_name="OpenAI",
    description="OpenAI — GPT-4o, GPT-4, GPT-3.5 (Chat Completions API)",
    signup_url="https://platform.openai.com/api-keys",
    fallback_models=(
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ),
    default_aux_model="gpt-4o-mini",
)

register_provider(openai)
