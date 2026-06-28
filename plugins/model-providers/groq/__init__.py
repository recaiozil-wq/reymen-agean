"""Native Groq provider profile."""


__all__ = ['GroqProfile', 'ProviderProfile', 'fetch_models', 'register_provider']
import json
import logging
import urllib.request

from providers import register_provider
from providers.base import ProviderProfile

logger = logging.getLogger(__name__)

_CACHE: list[str] | None = None


class GroqProfile(ProviderProfile):
    """Groq provider profile."""

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        """Fetch models from Groq API; fall back to fallback_models on failure."""
        global _CACHE  # noqa: PLW0603
        if _CACHE is not None:
            return _CACHE
        if not api_key:
            return list(self.fallback_models) if self.fallback_models else None
        try:
            req = urllib.request.Request("https://api.groq.com/openai/v1/models")
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
            logger.debug("fetch_models(groq): %s", exc)

        return list(self.fallback_models) if self.fallback_models else None


groq = GroqProfile(
    name="groq",
    aliases=("groq-cloud",),
    api_mode="chat_completions",
    env_vars=("GROQ_API_KEY",),
    base_url="https://api.groq.com/openai/v1",
    auth_type="api_key",
    display_name="Groq",
    description="Groq — ultra-fast inference",
    signup_url="https://console.groq.com/keys",
    fallback_models=(
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "gemma2-27b-it",
    ),
    default_aux_model="llama3-8b-8192",
)

register_provider(groq)
