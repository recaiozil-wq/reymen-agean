"""Test reymen.core.session_search — Session Search FTS5."""
import pytest


@pytest.fixture(autouse=True)
def _temp_db(monkeypatch, tmp_path):
    """Her testte geçici DB kullan."""
    db_path = tmp_path / "test_session.db"
    monkeypatch.setattr("reymen.core.session_search.DB_PATH", db_path)


class TestSessionSearch:
    def test_import(self):
        from reymen.core import session_search
        assert hasattr(session_search, "session_ara")
        assert hasattr(session_search, "session_listele")
        assert hasattr(session_search, "session_istatistik")

    def test_session_ara_empty(self):
        from reymen.core.session_search import session_ara
        results = session_ara("test query")
        assert isinstance(results, list)

    def test_session_listele(self):
        from reymen.core.session_search import session_listele
        results = session_listele()
        assert isinstance(results, list)

    def test_session_istatistik(self):
        from reymen.core.session_search import session_istatistik
        stats = session_istatistik()
        assert isinstance(stats, dict)