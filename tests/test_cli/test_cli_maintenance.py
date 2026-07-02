"""Tests for reymen.sistem.cli_maintenance."""
import pytest
from unittest.mock import patch


class TestGitRepoRoot:
    def test_importable(self):
        from reymen.sistem.cli_maintenance import _git_repo_root
        assert callable(_git_repo_root)

    def test_returns_string_or_none(self):
        from reymen.sistem.cli_maintenance import _git_repo_root
        result = _git_repo_root()
        assert result is None or isinstance(result, str)


class TestPathIsWithinRoot:
    def test_importable(self):
        from reymen.sistem.cli_maintenance import _path_is_within_root
        assert callable(_path_is_within_root)


class TestSetupWorktree:
    def test_importable(self):
        from reymen.sistem.cli_maintenance import _setup_worktree
        assert callable(_setup_worktree)


class TestCleanupWorktree:
    def test_importable(self):
        from reymen.sistem.cli_maintenance import _cleanup_worktree
        assert callable(_cleanup_worktree)


class TestPruneOrphanedBranches:
    def test_importable(self):
        from reymen.sistem.cli_maintenance import _prune_orphaned_branches
        assert callable(_prune_orphaned_branches)
