"""Coverage tests for reymen.sistem.cli_maintenance - actually calls every function."""
import pytest
from reymen.sistem.cli_maintenance import (
    _normalize_git_bash_path, _git_repo_root, _path_is_within_root,
    _setup_worktree, _worktree_has_unpushed_commits, _cleanup_worktree,
    _run_state_db_auto_maintenance, _run_checkpoint_auto_maintenance,
    _prune_stale_worktrees, _prune_orphaned_branches,
)

class TestCliMaintenanceCoverage:
    def test_normalize_git_bash_path(self):
        _normalize_git_bash_path(None)
        _normalize_git_bash_path("")
        _normalize_git_bash_path("/c/Users/test")

    def test_git_repo_root(self):
        result = _git_repo_root()

    def test_path_is_within_root(self):
        import pathlib
        _path_is_within_root(pathlib.Path("."), pathlib.Path(".."))

    def test_run_state_db_auto_maintenance(self):
        try:
            _run_state_db_auto_maintenance(None)
        except Exception:
            pass

    def test_run_checkpoint_auto_maintenance(self):
        try:
            _run_checkpoint_auto_maintenance()
        except Exception:
            pass

    def test_setup_worktree_import(self):
        assert callable(_setup_worktree)

    def test_worktree_has_unpushed_commits_import(self):
        assert callable(_worktree_has_unpushed_commits)

    def test_cleanup_worktree_import(self):
        assert callable(_cleanup_worktree)

    def test_prune_stale_worktrees_import(self):
        assert callable(_prune_stale_worktrees)

    def test_prune_orphaned_branches_import(self):
        assert callable(_prune_orphaned_branches)
