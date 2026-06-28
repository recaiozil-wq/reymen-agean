"""Native Mistral provider profile."""


__all__ = ['MistralProfile', 'ProviderProfile', 'fetch_models', 'register_provider']
import json
import logging
import urllib.request

from providers import register_provider
from providers.base import ProviderProfile

logger = logging.getLogger(__name__)

_CACHE: list[str] | None = None


class MistralProfile(ProviderProfile):
    """Mistral provider profile."""

    def fetch_models(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 8.0,
    ) -> list[str] | None:
        """Fetch models from Mistral API; fall back to fallback_models on failure."""
        global _CACHE  # noqa: PLW0603
        if _CACHE is not None:
            return _CACHE
        if not api_key:
            return list(self.fallback_models) if self.fallback_models else None
        try:
            req = urllib.request.Request("https://api.mistral.ai/v1/models")
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
            logger.debug("fetch_models(mistral): %s", exc)

        return list(self.fallback_models) if self.fallback_models else None


mistral = MistralProfile(
    name="mistral",
    aliases=("mistralai", "mistral-ai"),
    api_mode="chat_completions",
    env_vars=("MISTRAL_API_KEY",),
    base_url="https://api.mistral.ai",
    auth_type="api_key",
    display_name="Mistral",
    description="Mistral AI — open-weight frontier models",
    signup_url="https://console.mistral.ai/api-keys/",
    fallback_models=(
        "mistral-large-latest",
        "mistral-medium-latest",
        "mistral-small-latest",
        "open-mistral-7b",
        "open-mixtral-8x7b",
        "open-mixtral-8x22b",
    ),
    default_aux_model="mistral-small-latest",
)

register_provider(mistral)
