"""Test: reymen/core/backup_manager.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestBackup:
    def test_import(self):
        import reymen.core.backup_manager

        assert reymen.core.backup_manager is not None

    def test_class(self):
        from reymen.core.backup_manager import BackupManager

        assert BackupManager is not None
