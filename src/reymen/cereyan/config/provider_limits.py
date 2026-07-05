# -*- coding: utf-8 -*-
"""Provider token limitleri.

Provider'a göre token limitleri (modern modeller için).
Envs: PROVIDER_LIMIT_<UPPER_NAME>=<TOKEN>
"""
from __future__ import annotations

import os

PROVIDER_LIMITS: dict[str, int] = {
    "deepseek": int(os.environ.get("PROVIDER_LIMIT_DEEPSEEK", "128000")),
    "claude": int(os.environ.get("PROVIDER_LIMIT_CLAUDE", "200000")),
    "sonnet": int(os.environ.get("PROVIDER_LIMIT_SONNET", "200000")),
    "anthropic": int(os.environ.get("PROVIDER_LIMIT_ANTHROPIC", "200000")),
    "gpt4": int(os.environ.get("PROVIDER_LIMIT_GPT4", "128000")),
    "gpt4o": int(os.environ.get("PROVIDER_LIMIT_GPT4O", "128000")),
    "gemini": int(os.environ.get("PROVIDER_LIMIT_GEMINI", "128000")),
    "codex": int(os.environ.get("PROVIDER_LIMIT_CODEX", "200000")),
    "openrouter": int(os.environ.get("PROVIDER_LIMIT_OPENROUTER", "128000")),
}

# Varsayilan limit (hic eslesmezse)
PROVIDER_LIMIT_VARSAYILAN: int = int(os.environ.get("PROVIDER_LIMIT_DEFAULT", "128000"))
