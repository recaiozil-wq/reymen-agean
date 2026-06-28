# -*- coding: utf-8 -*-
"""tests/test_core.py — Cekirdek modul testleri (hafif, bagimsiz)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCore:
    """Ana modulleri dogrudan import etmeden, parca parca test et."""

    def test_config_dict_yapisi(self):
        """CONFIG benzeri bir dict yapisini dogrula."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {
                "lmstudio": {"base_url": "http://localhost:1234", "api_key": "test"},
                "ollama": {"base_url": "http://localhost:11434", "api_key": ""},
                "openai": {"api_key": "test"},
                "anthropic": {"api_key": "test"},
            }
        }
        assert "default_provider" in cfg
        assert "providers" in cfg
        assert len(cfg["providers"]) >= 4

    def test_agent_creation(self):
        """AIAgentOrchestrator import et ve hafif configle olustur."""
        from main import AIAgentOrchestrator
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {"lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"}},
            "skills_dir": ".ReYMeN/skills",
            "max_tur": 2,
        }
        agent = AIAgentOrchestrator(config=cfg, max_tur=2)
        assert agent is not None
        assert agent.budget is not None

    def test_providers_list(self):
        """list_providers en az 20 saglayici donmeli."""
        from providers import list_providers
        saglayicilar = list_providers()
        assert len(saglayicilar) >= 20

    def test_motor_creation(self):
        """Motor olusturma."""
        from motor import Motor
        m = Motor(backend_mode="local")
        assert m is not None

    def test_beyin_creation(self):
        """Beyin olusturma."""
        from beyin import Beyin
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {"lmstudio": {"base_url": "http://localhost:1234", "api_key": "not-needed"}},
        }
        b = Beyin(cfg)
        assert b is not None
