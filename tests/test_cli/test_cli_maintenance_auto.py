"""Auto-generated tests for reymen.sistem.cli_maintenance."""

import pytest
from src.reymen.sistem.cli_maintenance import (
    _normalize_git_bash_path,
    _git_repo_root,
    _path_is_within_root,
    _setup_worktree,
    _worktree_has_unpushed_commits,
    _cleanup_worktree,
    _run_state_db_auto_maintenance,
    _run_checkpoint_auto_maintenance,
    _prune_stale_worktrees,
    _prune_orphaned_branches,
)


class TestMaintenance:
    """Auto-generated tests — her fonksiyonun import + call edilebilirliğini kontrol eder."""

    def test__normalize_git_bash_path_importable(self):
        assert callable(_normalize_git_bash_path)

    def test__git_repo_root_importable(self):
        assert callable(_git_repo_root)

    def test__path_is_within_root_importable(self):
        assert callable(_path_is_within_root)

    def test__setup_worktree_importable(self):
        assert callable(_setup_worktree)

    def test__worktree_has_unpushed_commits_importable(self):
        assert callable(_worktree_has_unpushed_commits)

    def test__cleanup_worktree_importable(self):
        assert callable(_cleanup_worktree)

    def test__run_state_db_auto_maintenance_importable(self):
        assert callable(_run_state_db_auto_maintenance)

    def test__run_checkpoint_auto_maintenance_importable(self):
        assert callable(_run_checkpoint_auto_maintenance)

    def test__prune_stale_worktrees_importable(self):
        assert callable(_prune_stale_worktrees)

    def test__prune_orphaned_branches_importable(self):
        assert callable(_prune_orphaned_branches)
