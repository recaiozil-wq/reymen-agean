"""Test: schema_manager."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestSchemaManager:
    def test_import(self):
        from reymen.core.schema_manager import SchemaManager

        assert SchemaManager is not None

    def test_class(self):
        from reymen.core.schema_manager import SchemaManager

        sm = SchemaManager()
        assert sm is not None
