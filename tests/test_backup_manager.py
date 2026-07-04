# -*- coding: utf-8 -*-
"""
Test: reymen.core.backup_manager (git-based)

Actual API:
  BackupManager(repo_path=None)
    .create() -> str | None  (commit hash)
    .list() -> list[dict]    (git log --oneline)
    .list_v2() -> list[dict] (detailed git log)
    .restore(path) -> bool
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from reymen.core.backup_manager import BackupManager


class TestBackupManagerInit:
    """BackupManager baslatma."""

    def test_default_repo_path(self):
        bm = BackupManager()
        assert bm._repo_path == Path.cwd().resolve()

    def test_custom_repo_path(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        assert bm._repo_path == tmp_path.resolve()

    def test_none_repo_path_uses_cwd(self):
        bm = BackupManager(None)
        assert bm._repo_path == Path.cwd().resolve()


class TestGitVarMi:
    """_git_var_mi — git kurulu mu kontrolu."""

    def test_git_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert bm._git_var_mi() is False

    def test_git_var_dizin_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        mock_r = MagicMock(returncode=1)
        with patch("subprocess.run", return_value=mock_r):
            assert bm._git_var_mi() is False

    def test_git_var_basarili(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        mock_r = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_r):
            assert bm._git_var_mi() is True

    def test_git_timeout(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 10)):
            assert bm._git_var_mi() is False


class TestCreate:
    """create() — git add + commit."""

    def test_create_git_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=False):
            assert bm.create() is None

    def test_create_basarili(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        mock_hash = "abc123def456"
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run") as mock_run:
                # git add success, git commit success
                mock_run.side_effect = [
                    MagicMock(returncode=0),
                    MagicMock(returncode=0),
                    MagicMock(returncode=0, stdout=mock_hash + "\n"),
                ]
                result = bm.create()
                assert result == mock_hash

    def test_create_git_add_basarisiz(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", return_value=MagicMock(returncode=1, stderr="add error")):
                assert bm.create() is None

    def test_create_nothing_to_commit(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        mock_hash = "abc123"
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(returncode=0),  # git add
                    MagicMock(returncode=1, stderr="nothing to commit"),  # git commit
                    MagicMock(returncode=0, stdout=mock_hash + "\n"),  # git rev-parse
                ]
                result = bm.create()
                assert result == mock_hash

    def test_create_oserror(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", side_effect=OSError("disk error")):
                assert bm.create() is None


class TestList:
    """list() — git log --oneline."""

    def test_list_git_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=False):
            assert bm.list() == []

    def test_list_bos(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="")):
                assert bm.list() == []

    def test_list_commit_var(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        log_output = "abc1234 first commit\ndef5678 second commit"
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=log_output)):
                commits = bm.list()
                assert len(commits) == 2
                assert commits[0]["hash"] == "abc1234"
                assert commits[0]["message"] == "first commit"
                assert commits[1]["hash"] == "def5678"

    def test_list_git_hata(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", return_value=MagicMock(returncode=1)):
                assert bm.list() == []

    def test_list_oserror(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", side_effect=OSError("error")):
                assert bm.list() == []


class TestListV2:
    """list_v2() — detayli git log."""

    def test_list_v2_git_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=False):
            assert bm.list_v2() == []

    def test_list_v2_bos(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="")):
                assert bm.list_v2() == []

    def test_list_v2_commit_var(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        log_output = "fullhash|shorthash|Author|2026-01-01|test message"
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout=log_output)):
                commits = bm.list_v2()
                assert len(commits) == 1
                assert commits[0]["hash"] == "fullhash"
                assert commits[0]["kisa_hash"] == "shorthash"
                assert commits[0]["author"] == "Author"
                assert commits[0]["message"] == "test message"


class TestRestore:
    """restore() — git checkout ile geri yukleme."""

    def test_restore_git_yok(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=False):
            assert bm.restore("abc123") is False

    def test_restore_bos_path(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            assert bm.restore("") is False
            assert bm.restore("  ") is False

    def test_restore_basarili(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(),  # git stash
                    MagicMock(returncode=0),  # git checkout
                ]
                assert bm.restore("abc123") is True

    def test_restore_basarisiz(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(),  # git stash
                    MagicMock(returncode=1, stderr="checkout failed"),  # git checkout
                ]
                assert bm.restore("abc123") is False

    def test_restore_oserror(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch.object(bm, "_git_var_mi", return_value=True):
            with patch("subprocess.run", side_effect=OSError("error")):
                assert bm.restore("abc123") is False


class TestTimestamp:
    """_timestamp() — zaman damgasi uretimi."""

    def test_timestamp_format(self):
        ts = BackupManager._timestamp()
        # Format: "YYYY-MM-DD HH:MM:SS"
        parts = ts.split(" ")
        assert len(parts) == 2
        assert len(parts[0].split("-")) == 3
        assert len(parts[1].split(":")) == 3


class TestSonCommitHash:
    """_son_commit_hash() — son commit hash'i."""

    def test_hash_alindi(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="abc123def456\n")):
            assert bm._son_commit_hash() == "abc123def456"

    def test_hash_basarisiz(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", return_value=MagicMock(returncode=1)):
            assert bm._son_commit_hash() is None

    def test_hash_oserror(self, tmp_path):
        bm = BackupManager(str(tmp_path))
        with patch("subprocess.run", side_effect=OSError("error")):
            assert bm._son_commit_hash() is None
