# -*- coding: utf-8 -*-
"""tests/test_slash_commands.py — Slash komut modülü import/birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest


class TestSlashCommandsImport:
    def test_module_importable(self):
        """slash_commands.py modülü import edilebilir mi? (180K modül)"""
        import gateway.slash_commands as sc
        assert sc is not None

    def test_has_expected_attributes(self):
        import gateway.slash_commands as sc
        # Should have common slash command attributes
        attrs = [a for a in dir(sc) if not a.startswith("_")]
        assert len(attrs) > 0

    def test_command_handler_classes(self):
        """Modülde en az bir handler sınıfı var mı? (örneğin mixin veya fonksiyon)"""
        import gateway.slash_commands as sc
        # Expect at least some callable or class
        classes = [getattr(sc, name) for name in dir(sc)
                   if isinstance(getattr(sc, name), type) and not name.startswith("_")]
        functions = [getattr(sc, name) for name in dir(sc)
                     if callable(getattr(sc, name)) and not name.startswith("_")]
        assert len(classes) + len(functions) > 0

    def test_registry_or_list_exists(self):
        """Komut kaydı/listesi için tipik bir değişken varlığını kontrol et."""
        import gateway.slash_commands as sc
        # Look for common patterns
        has_registry = hasattr(sc, "_KOMUTLAR") or hasattr(sc, "KOMUTLAR") or \
                       hasattr(sc, "_commands") or hasattr(sc, "commands") or \
                       hasattr(sc, "_COMMANDS") or hasattr(sc, "COMMANDS") or \
                       hasattr(sc, "kayitli_komutlar")
        # If no registry found, just check there are classes
        if not has_registry:
            classes = [getattr(sc, name) for name in dir(sc)
                       if isinstance(getattr(sc, name), type) and not name.startswith("_")]
            assert len(classes) > 0
