"""Tests for the Nous-ReYMeN-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"ReYMeN"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``ReYMeN-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "ReYMeN" tag namespace.

``is_nous_ReYMeN_non_agentic`` should only match the actual Nous Research
ReYMeN-3 / ReYMeN-4 chat family.
"""

from __future__ import annotations

import pytest

from ReYMeN_cli.model_switch import (
    _ReYMeN_MODEL_WARNING,
    _check_ReYMeN_model_warning,
    is_nous_ReYMeN_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "NousResearch/ReYMeN-3-Llama-3.1-70B",
        "NousResearch/ReYMeN-3-Llama-3.1-405B",
        "ReYMeN-3",
        "ReYMeN-3",
        "ReYMeN-4",
        "ReYMeN-4-405b",
        "ReYMeN_4_70b",
        "openrouter/ReYMeN3:70b",
        "openrouter/nousresearch/ReYMeN-4-405b",
        "NousResearch/ReYMeN3",
        "ReYMeN-3.1",
    ],
)
def test_matches_real_nous_ReYMeN_chat_models(model_name: str) -> None:
    assert is_nous_ReYMeN_non_agentic(
        model_name
    ), f"expected {model_name!r} to be flagged as Nous ReYMeN 3/4"
    assert _check_ReYMeN_model_warning(model_name) == _ReYMeN_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "ReYMeN-brain:qwen3-14b-ctx16k",
        "ReYMeN-brain:qwen3-14b-ctx32k",
        "ReYMeN-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat ReYMeN models we don't warn about
        "ReYMeN-llm-2",
        "ReYMeN2-pro",
        "nous-ReYMeN-2-mistral",
        # Edge cases
        "",
        "ReYMeN",  # bare "ReYMeN" isn't the 3/4 family
        "ReYMeN-brain",
        "brain-ReYMeN-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_ReYMeN_non_agentic(
        model_name
    ), f"expected {model_name!r} NOT to be flagged as Nous ReYMeN 3/4"
    assert _check_ReYMeN_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_ReYMeN_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_ReYMeN_model_warning("") == ""
