# -*- coding: utf-8 -*-
"""
backup_manager.py — Basit Git tabanli yedekleme sistemi.

BackupManager sinifi:
    - create()   -> str (backup commit hash) veya None
    - list()     -> list[dict]  (git log --oneline)
    - list_v2()  -> list[dict]  (detayli git log)
    - restore()  -> bool

Git repo yoksa veya git calismiyorsa guvenli sekilde None/list doner.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BackupManager:
    """Basit Git tabanli yedekleme yoneticisi.

    create() -> commit atar, hash doner.
    list()   -> git log --oneline ile commit listesi.
    list_v2() -> detayli commit bilgisi.
    restore() -> git checkout ile geri yukleme.
    """

    def __init__(self, repo_path: Optional[str] = None):
        self._repo_path = Path(repo_path or Path.cwd()).resolve()

    # ------------------------------------------------------------------
    # Yardimci: git calisiyor mu?
    # ------------------------------------------------------------------
    def _git_var_mi(self) -> bool:
        """Git kurulu ve repo_path'te bir git repo'su var mi?"""
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return r.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return False

    # ------------------------------------------------------------------
    #  create()
    # ------------------------------------------------------------------
    def create(self) -> Optional[str]:
        """Git add + commit yap.

        Returns:
            Commit hash (str) basariliysa, None basarisizsa.
        """
        if not self._git_var_mi():
            logger.warning("[BackupManager] Git repo bulunamadi: %s", self._repo_path)
            return None

        try:
            # git add -A
            r = subprocess.run(
                ["git", "add", "-A"],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if r.returncode != 0:
                logger.error("[BackupManager] git add basarisiz: %s", r.stderr.strip())
                return None

            # git commit
            r = subprocess.run(
                ["git", "commit", "--allow-empty", "-m", f"Backup {self._timestamp()}"],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if r.returncode != 0:
                # "nothing to commit" — hata degil
                if "nothing to commit" in r.stderr:
                    logger.info("[BackupManager] Yedeklenecek yeni dosya yok.")
                    # Yine de son commit hash'ini don
                    return self._son_commit_hash()
                logger.error("[BackupManager] git commit basarisiz: %s", r.stderr.strip())
                return None

            # commit hash'ini al
            return self._son_commit_hash()

        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
            logger.error("[BackupManager] create() hatasi: %s", e)
            return None

    def _son_commit_hash(self) -> Optional[str]:
        """Son commit'in hash'ini don."""
        try:
            r = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()[:12]  # kisa hash
            return None
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            return None

    @staticmethod
    def _timestamp() -> str:
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    #  list()
    # ------------------------------------------------------------------
    def list(self) -> List[Dict[str, Any]]:
        """Git log --oneline ile commit listesi.

        Returns:
            [{"hash": "...", "message": "...", "tarih": "..."}, ...]
            Git yoksa bos liste.
        """
        if not self._git_var_mi():
            return []

        try:
            r = subprocess.run(
                ["git", "log", "--oneline", "--all", "--max-count=50"],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=15,
            )
            if r.returncode != 0:
                return []

            commits = []
            for line in r.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                # hash + message
                parts = line.split(" ", 1)
                commits.append({
                    "hash": parts[0],
                    "message": parts[1] if len(parts) > 1 else "",
                })
            return commits

        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
            logger.error("[BackupManager] list() hatasi: %s", e)
            return []

    # ------------------------------------------------------------------
    #  list_v2()
    # ------------------------------------------------------------------
    def list_v2(self) -> List[Dict[str, Any]]:
        """Detayli commit listesi: hash + message + author + tarih.

        Returns:
            [{"hash": ..., "message": ..., "author": ..., "tarih": ..., "kisa_hash": ...}, ...]
            Git yoksa bos liste.
        """
        if not self._git_var_mi():
            return []

        try:
            r = subprocess.run(
                [
                    "git", "log", "--all", "--max-count=50",
                    "--format=%H|%h|%an|%ai|%s",
                ],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=15,
            )
            if r.returncode != 0:
                return []

            commits = []
            for line in r.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split("|", 4)
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "kisa_hash": parts[1],
                        "author": parts[2],
                        "tarih": parts[3],
                        "message": parts[4],
                    })
                elif len(parts) >= 1:
                    commits.append({"hash": parts[0]})
            return commits

        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
            logger.error("[BackupManager] list_v2() hatasi: %s", e)
            return []

    # ------------------------------------------------------------------
    #  restore(path)
    # ------------------------------------------------------------------
    def restore(self, path: str) -> bool:
        """Git checkout ile commit veya branch'e geri yukle.

        Args:
            path: Commit hash, branch adi, veya tag.

        Returns:
            True basariliysa, False basarisizsa.
        """
        if not self._git_var_mi():
            logger.warning("[BackupManager] Git repo bulunamadi, restore imkansiz.")
            return False

        if not path or not path.strip():
            logger.error("[BackupManager] restore() icin gecerli bir hedef gerekli.")
            return False

        ref = path.strip()

        try:
            # once stash yap (calisma alani kirli olabilir)
            subprocess.run(
                ["git", "stash", "--allow-empty"],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=15,
            )

            # checkout
            r = subprocess.run(
                ["git", "checkout", ref, "--"],
                cwd=str(self._repo_path),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if r.returncode == 0:
                logger.info("[BackupManager] Geri yukleme basarili: %s", ref)
                return True
            else:
                logger.error("[BackupManager] checkout basarisiz (%s): %s", ref, r.stderr.strip())
                return False

        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as e:
            logger.error("[BackupManager] restore() hatasi: %s", e)
            return False
