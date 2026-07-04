"""Test: cron_manager."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestCronManager:
    def test_import(self):
        from reymen.core.cron_manager import CronJob, CronManager

        assert CronJob is not None

    def test_olusum(self):
        from reymen.core.cron_manager import CronJob

        j = CronJob("test1", "echo hello", "* * * * *")
        assert j is not None

    def test_to_dict(self):
        from reymen.core.cron_manager import CronJob

        j = CronJob("t2", "echo 2", "*/5 * * * *")
        d = j.to_dict()
        assert isinstance(d, dict)

    def test_from_dict(self):
        from reymen.core.cron_manager import CronJob

        j = CronJob.from_dict({"job_id": "d1", "komut": "ls", "zaman": "0 9 * * *"})
        assert j is not None
