from __future__ import annotations

import sys, os
# ReYMeN's AIAgent lives in reymen/sistem/run_agent.py
_reymen_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_sistem_path = os.path.join(_reymen_root, "reymen", "sistem")
if _sistem_path not in sys.path:
    sys.path.insert(0, _sistem_path)
from run_agent import AIAgent


def _agent_with_base_url(base_url: str) -> AIAgent:
    agent = object.__new__(AIAgent)
    agent.base_url = base_url
    return agent


def test_direct_openai_url_requires_openai_host():
    agent = _agent_with_base_url("https://api.openai.com.example/v1")

    assert agent._is_direct_openai_url() is False


def test_direct_openai_url_ignores_path_segment_match():
    agent = _agent_with_base_url("https://proxy.example.test/api.openai.com/v1")

    assert agent._is_direct_openai_url() is False


def test_direct_openai_url_accepts_native_host():
    agent = _agent_with_base_url("https://api.openai.com/v1")

    assert agent._is_direct_openai_url() is True
