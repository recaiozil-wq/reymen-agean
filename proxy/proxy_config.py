# -*- coding: utf-8 -*-
"""proxy/proxy_config.py — Proxy yapilandirma yonetimi."""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Optional
import logging
logger = logging.getLogger(__name__)


class ProxyConfig:
    """Proxy yapilandirmasi. JSON dosyasi + env override ile beslenir."""

    DEFAULTS: dict[str, Any] = {
        "port": 8080,
        "auth": None,
        "whitelist": [],
        "upstream": None,
        "timeout": 30,
        "ssl": False,
    }

    def __init__(self, config_path: Optional[str] = None):
        self._cfg: dict[str, Any] = dict(self.DEFAULTS)
        if config_path and Path(config_path).exists():
            with open(config_path, encoding="utf-8") as f:
                self._cfg.update(json.load(f))
        for env_key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
            val = os.environ.get(env_key)
            if val:
                self._cfg["upstream"] = val
                break

    def __getattr__(self, key: str) -> Any:
        try:
            return self._cfg[key]
        except KeyError:
            raise AttributeError(f"ProxyConfig has no attribute '{key}'")

    def to_dict(self) -> dict[str, Any]:
        return dict(self._cfg)
