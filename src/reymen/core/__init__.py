# src/reymen/core/__init__.py
# Import yonlendirme: reymen.core.* -> src.core.*
# Eski testlerin calismasi icin gerekli (proje yapisindaki degisiklikten sonra)

import importlib
import sys

_CORE_MODULES = [
    "backup_manager",
    "config_manager",
    "credential_pool",
    "cron_manager",
    "delegation_manager",
    "gateway_manager",
    "guardrails_manager",
    "langgraph_export",
    "mcp_server",
    "model_provider",
    "oauth_manager",
    "orchestrator",
    "provider_abstraction",
    "schema_manager",
    "session_search",
    "skills_hub",
    "vector_memory",
]

def __getattr__(name):
    """reymen.core.XYZ -> src.core.XYZ yonlendirmesi"""
    if name in _CORE_MODULES:
        mod = importlib.import_module(f"src.core.{name}")
        sys.modules[f"reymen.core.{name}"] = mod
        return mod
    raise AttributeError(f"module 'reymen.core' has no attribute '{name}'")
