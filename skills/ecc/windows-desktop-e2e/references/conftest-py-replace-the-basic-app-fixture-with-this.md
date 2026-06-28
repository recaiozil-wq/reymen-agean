---
skill_id: b80550fd0acd
usage_count: 1
last_used: 2026-06-16
---
# conftest.py — replace the basic `app` fixture with this
import os, subprocess, pytest
from pywinauto import Application
from config import APP_PATH, APP_ARGS, APP_TITLE, LAUNCH_TIMEOUT, ACTION_TIMEOUT, ARTIFACT_DIR

@pytest.fixture(scope="function")
def app(request, tmp_path):
    """Fresh process + isolated user-data dirs per test."""
    if not APP_PATH:
        pytest.exit("APP_PATH not set", returncode=1)