# -*- coding: utf-8 -*-
"""tests/test_model.py — Model modulu testleri."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModelMetadata:
    def test_model_listele(self):
        from model_metadata import model_listele

        m = model_listele()
        assert len(m) >= 5

    def test_model_bilgisi(self):
        from model_metadata import model_bilgisi

        b = model_bilgisi("deepseek-chat")
        assert b.get("provider") == "deepseek"

    def test_model_oner(self):
        from model_metadata import modele_gore_sec

        oneriler = modele_gore_sec("resim analiz et")
        assert isinstance(oneriler, list)


class TestModelTools:
    def test_benchmark_raporu(self):
        from model_tools import benchmark_raporu

        rapor = benchmark_raporu([])
        assert isinstance(rapor, str)
