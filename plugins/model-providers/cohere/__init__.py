"""Native Cohere provider profile."""


__all__ = ['CohereProfile', 'ProviderProfile', 'fetch_models', 'register_provider']
import json
import logging
import urllib.request

from providers import register_provider
from providers.base import ProviderProfile

logger = logging.getLogger(__name__)

_CACHE: list[str] | None = None


class CohereProfile(ProviderProfile):
    """Cohere provider profile."""

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        """Fetch models from Cohere API; fall back to fallback_models on failure."""
        global _CACHE  # noqa: PLW0603
        if _CACHE is not None:
            return _CACHE
        if not api_key:
            return list(self.fallback_models) if self.fallback_models else None
        try:
            req = urllib.request.Request("https://api.cohere.ai/v1/models")
            req.add_header("Authorization", f"Bearer {api_key}")
            req.add_header("Accept", "application/json")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode())
            models = [m["id"] for m in data if isinstance(m, dict) and "id" in m]
            if models:
                _CACHE = models
                return models
        except Exception as exc:
            logger.debug("fetch_models(cohere): %s", exc)

        return list(self.fallback_models) if self.fallback_models else None


cohere = CohereProfile(
    name="cohere",
    aliases=("cohere-ai", "command"),
    api_mode="chat_completions",
    env_vars=("COHERE_API_KEY",),
    base_url="https://api.cohere.ai",
    auth_type="api_key",
    display_name="Cohere",
    description="Cohere — Command & Embed models",
    signup_url="https://dashboard.cohere.com/api-keys",
    fallback_models=(
        "command-r",
        "command-r-plus",
        "command",
        "command-light",
        "embed-english-v3.0",
        "embed-multilingual-v3.0",
    ),
    default_aux_model="command-r",
)

register_provider(cohere)
