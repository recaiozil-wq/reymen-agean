"""Test: vector_memory."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestVectorMemory:
    def test_import(self):
        from reymen.core.vector_memory import VectorMemory

        assert VectorMemory is not None

    def test_class(self):
        from reymen.core.vector_memory import VectorMemory

        vm = VectorMemory()
        assert vm is not None
