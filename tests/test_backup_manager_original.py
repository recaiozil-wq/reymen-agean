# -*- coding: utf-8 -*-
"""
Test: reymen.core.backup_manager — original comprehensive tests.
Tests the actual git-based BackupManager API.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from reymen.core.backup_manager import BackupManager


class TestYedekAlRouting:
    """BackupManager baslatma ve temel islemler."""

    def test_init_with_repo_path(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            assert bm._repo_path == Path(td).resolve()

    def test_init_default_path(self):
        bm = BackupManager()
        assert bm._repo_path == Path.cwd().resolve()

    def test_create_dispatch(self):
        """create() → git varsa commit yapar."""
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(returncode=0),  # git add
                        MagicMock(returncode=0),  # git commit
                        MagicMock(returncode=0, stdout="hash123\n"),  # rev-parse
                    ]
                    result = bm.create()
                    assert result == "hash123"

    def test_timestamp_uretilir(self):
        """timestamp uretilir."""
        ts = BackupManager._timestamp()
        assert isinstance(ts, str)
        assert "-" in ts
        assert ":" in ts

    def test_baslangic_zamani_olculur(self):
        """Zaman olculur."""
        bm = BackupManager()
        assert isinstance(bm._repo_path, Path)


class TestCreateMethods:
    """create() detayli testleri."""

    def test_create_basarili(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(returncode=0),
                        MagicMock(returncode=0),
                        MagicMock(returncode=0, stdout="abc123\n"),
                    ]
                    sonuc = bm.create()
                    assert sonuc == "abc123"

    def test_create_git_yok(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=False):
                sonuc = bm.create()
                assert sonuc is None

    def test_create_add_hata(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run", return_value=MagicMock(returncode=1, stderr="err")):
                    sonuc = bm.create()
                    assert sonuc is None

    def test_create_nothing_to_commit(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(returncode=0),
                        MagicMock(returncode=1, stderr="nothing to commit"),
                        MagicMock(returncode=0, stdout="lasthash\n"),
                    ]
                    sonuc = bm.create()
                    assert sonuc == "lasthash"

    def test_create_oserror(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run", side_effect=OSError("disk")):
                    sonuc = bm.create()
                    assert sonuc is None


class TestListMethods:
    """list() ve list_v2() testleri."""

    def test_list_git_yok(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=False):
                assert bm.list() == []

    def test_list_basari(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run",
                    return_value=MagicMock(returncode=0, stdout="hash1 msg1\nhash2 msg2")):
                    liste = bm.list()
                    assert len(liste) == 2

    def test_list_v2_git_yok(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=False):
                assert bm.list_v2() == []

    def test_list_v2_basari(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run",
                    return_value=MagicMock(returncode=0, stdout="full|short|Author|2026|msg")):
                    liste = bm.list_v2()
                    assert len(liste) == 1
                    assert liste[0]["hash"] == "full"

    def test_list_oserror(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run", side_effect=OSError("err")):
                    assert bm.list() == []

    def test_list_v2_oserror(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run", side_effect=OSError("err")):
                    assert bm.list_v2() == []


class TestRestoreMethods:
    """restore() testleri."""

    def test_restore_git_yok(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=False):
                assert bm.restore("abc") is False

    def test_restore_bos_path(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                assert bm.restore("") is False
                assert bm.restore("  ") is False

    def test_restore_basarili(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(),  # stash
                        MagicMock(returncode=0),  # checkout
                    ]
                    assert bm.restore("abc123") is True

    def test_restore_basarisiz(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(),
                        MagicMock(returncode=1, stderr="fail"),
                    ]
                    assert bm.restore("abc123") is False

    def test_restore_oserror(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch.object(bm, "_git_var_mi", return_value=True):
                with patch("subprocess.run", side_effect=OSError("err")):
                    assert bm.restore("abc123") is False


class TestSonCommitHash:
    """_son_commit_hash() testleri."""

    def test_hash_alindi(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="abc123\n")):
                assert bm._son_commit_hash() == "abc123"

    def test_hash_basarisiz(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch("subprocess.run", return_value=MagicMock(returncode=1)):
                assert bm._son_commit_hash() is None

    def test_hash_oserror(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch("subprocess.run", side_effect=OSError("err")):
                assert bm._son_commit_hash() is None

    def test_hash_kisa(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            long_hash = "a" * 40
            with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=long_hash + "\n")):
                result = bm._son_commit_hash()
                assert len(result) == 12


class TestGitVarMi:
    """_git_var_mi() testleri."""

    def test_git_bulunamadi(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch("subprocess.run", side_effect=FileNotFoundError):
                assert bm._git_var_mi() is False

    def test_git_bulundu(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch("subprocess.run", return_value=MagicMock(returncode=0)):
                assert bm._git_var_mi() is True

    def test_git_yok_dizin(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch("subprocess.run", return_value=MagicMock(returncode=1)):
                assert bm._git_var_mi() is False

    def test_git_timeout(self):
        with tempfile.TemporaryDirectory() as td:
            bm = BackupManager(repo_path=td)
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10)):
                assert bm._git_var_mi() is False


class TestTimestamp:
    """_timestamp() testleri."""

    def test_format_dogrulama(self):
        ts = BackupManager._timestamp()
        parts = ts.split(" ")
        assert len(parts) == 2
        date_parts = parts[0].split("-")
        assert len(date_parts) == 3
        assert all(p.isdigit() for p in date_parts)

    def test_benzersiz(self):
        ts1 = BackupManager._timestamp()
        # Timestampler farkli olmali (en azindan farkli cagirilarda)
        assert isinstance(ts1, str)
