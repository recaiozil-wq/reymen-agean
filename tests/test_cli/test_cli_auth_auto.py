"""Auto-generated tests for reymen.sistem.cli_auth."""

import pytest
from src.reymen.sistem.cli_auth import (
    get_job,
    set_sudo_password_callback,
    set_approval_callback,
    set_secret_capture_callback,
    _sync_process_session_id,
    _cleanup_all_terminals,
    _cleanup_all_browsers,
)


class TestAuth:
    """Auto-generated tests — her fonksiyonun import + call edilebilirliğini kontrol eder."""

    def test_get_job_importable(self):
        assert callable(get_job)

    def test_set_sudo_password_callback_importable(self):
        assert callable(set_sudo_password_callback)

    def test_set_approval_callback_importable(self):
        assert callable(set_approval_callback)

    def test_set_secret_capture_callback_importable(self):
        assert callable(set_secret_capture_callback)

    def test__sync_process_session_id_importable(self):
        assert callable(_sync_process_session_id)

    def test__cleanup_all_terminals_importable(self):
        assert callable(_cleanup_all_terminals)

    def test__cleanup_all_browsers_importable(self):
        assert callable(_cleanup_all_browsers)
