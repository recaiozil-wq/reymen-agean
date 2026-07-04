# -*- coding: utf-8 -*-
"""
Test: reymen.core.backup_manager — mock-based integration tests.
Tests the actual git-based BackupManager API.
"""

import os, sys, tempfile, json, zipfile, time, shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
import subprocess
import pytest

from reymen.core.backup_manager import BackupManager


class TestBackupCreate:
    """create() — temel git yedekleme."""

    def test_create_with_repo_path(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        assert bm._repo_path == tmp_path.resolve()

    def test_create_git_yok_returns_none(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=False):
            assert bm.create() is None

    def test_create_git_var_cagri(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(returncode=0),  # git add
                    MagicMock(returncode=0),  # git commit
                    MagicMock(returncode=0, stdout="abc123def456\n"),  # rev-parse
                ]
                result = bm.create()
                assert result == "abc123def456"
                assert mock_run.call_count == 3


class TestBackupList:
    """list() — commit listesi."""

    def test_list_returns_list(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=False):
            assert bm.list() == []

    def test_list_with_commits(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout="abc1234 first\ndef5678 second"
                )
                commits = bm.list()
                assert len(commits) == 2


class TestBackupListV2:
    """list_v2() — detayli commit listesi."""

    def test_list_v2_git_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=False):
            assert bm.list_v2() == []


class TestBackupRestore:
    """restore() — geri yukleme."""

    def test_restore_git_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=False):
            assert bm.restore("abc123") is False

    def test_restore_bos(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            assert bm.restore("") is False


class TestBackupTimestamp:
    """_timestamp() — zaman damgasi."""

    def test_timestamp_olusturulur(self):
        ts = BackupManager._timestamp()
        assert isinstance(ts, str)
        assert len(ts) > 0


class TestBackupGitVarMi:
    """_git_var_mi — git kontrol."""

    def test_git_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert bm._git_var_mi() is False

    def test_git_oserror(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", side_effect=OSError("permission denied")):
            assert bm._git_var_mi() is False

    def test_git_timeout(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10)):
            assert bm._git_var_mi() is False

    def test_git_var(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", return_value=MagicMock(returncode=0)):
            assert bm._git_var_mi() is True


class TestBackupMetadata:
    """Yardimci fonksiyon testleri."""

    def test_son_commit_hash_basari(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="abc123\n")):
            assert bm._son_commit_hash() == "abc123"

    def test_son_commit_hash_kisa(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        long_hash = "a" * 40
        with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=long_hash + "\n")):
            result = bm._son_commit_hash()
            assert len(result) == 12
