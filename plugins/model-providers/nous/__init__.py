"""Nous Portal provider profile."""


__all__ = ['Any', 'NousProfile', 'ProviderProfile', 'build_api_kwargs_extras', 'build_extra_body', 'nous_portal_tags', 'register_provider']
from typing import Any

from agent.portal_tags import nous_portal_tags
from providers import register_provider
from providers.base import ProviderProfile


class NousProfile(ProviderProfile):
    """Nous Portal — product tags, reasoning with Nous-specific omission."""

    def build_extra_body(
        self, *, session_id: str | None = None, **context
    ) -> dict[str, Any]:
        return {"tags": nous_portal_tags()}

    def build_api_kwargs_extras(
        self,
        *,
        reasoning_config: dict | None = None,
        supports_reasoning: bool = False,
        **context,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Nous: passes full reasoning_config, but OMITS when disabled."""
        extra_body = {}
        if supports_reasoning:
            if reasoning_config is not None:
                rc = dict(reasoning_config)
                if rc.get("enabled") is False:
                    pass  # Nous omits reasoning when disabled
                else:
                    extra_body["reasoning"] = rc
            else:
                extra_body["reasoning"] = {"enabled": True, "effort": "medium"}
        return extra_body, {}


nous = NousProfile(
    name="nous",
    aliases=("nous-portal", "nousresearch"),
    env_vars=("NOUS_API_KEY",),
    display_name="Nous Research",
    description="Nous Research — ReYMeN model family",
    signup_url="https://nousresearch.com/",
    fallback_models=(
        "ReYMeN-3-405b",
        "ReYMeN-3-70b",
    ),
    base_url="https://inference.nousresearch.com/v1",
    auth_type="oauth_device_code",
)

register_provider(nous)
