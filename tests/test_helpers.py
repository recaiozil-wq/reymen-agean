# -*- coding: utf-8 -*-
"""gateway/platforms/helpers.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestRetry:
    def test_retry_success_first_try(self):
        from gateway.platforms.helpers import retry
        call_count = 0
        def my_func():
            nonlocal call_count
            call_count += 1
            return "basarili"
        decorated = retry(max_deneme=3)(my_func)
        result = decorated()
        assert result == "basarili"
        assert call_count == 1

    def test_retry_fails_then_succeeds(self):
        from gateway.platforms.helpers import retry
        call_count = 0
        def my_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("hata")
            return "basarili"
        decorated = retry(max_deneme=3, bekle=0.01)(my_func)
        result = decorated()
        assert result == "basarili"
        assert call_count == 3

    def test_retry_all_fail(self):
        from gateway.platforms.helpers import retry
        call_count = 0
        def my_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("hep hata")
        decorated = retry(max_deneme=3, bekle=0.01)(my_func)
        with pytest.raises(ValueError, match="hep hata"):
            decorated()
        assert call_count == 3

    def test_retry_custom_exceptions(self):
        from gateway.platforms.helpers import retry
        call_count = 0
        def my_func():
            nonlocal call_count
            call_count += 1
            raise TypeError("tip hatasi")
        decorated = retry(max_deneme=2, bekle=0.01, hata_tipleri=(TypeError,))(my_func)
        with pytest.raises(TypeError):
            decorated()
        assert call_count == 2

    def test_retry_send_message_success(self):
        from gateway.platforms.helpers import retry_send_message
        send_func = MagicMock(return_value={"durum": "basarili"})
        result = retry_send_message(send_func, "hedef", "mesaj", max_deneme=2)
        assert result["durum"] == "basarili"
        send_func.assert_called_once()

    def test_retry_send_message_fails_then_succeeds(self):
        from gateway.platforms.helpers import retry_send_message
        send_func = MagicMock(side_effect=[{"durum": "hata"}, {"durum": "basarili"}])
        result = retry_send_message(send_func, "hedef", "mesaj", max_deneme=2)
        assert result["durum"] == "basarili"
        assert send_func.call_count == 2

    def test_retry_send_message_fails_all(self):
        from gateway.platforms.helpers import retry_send_message
        send_func = MagicMock(return_value={"durum": "hata", "hata": "olmadi"})
        result = retry_send_message(send_func, "hedef", "mesaj", max_deneme=3)
        assert result["durum"] == "hata"
        assert send_func.call_count == 3


class TestMesajFormatlama:
    def test_mesaj_kisalt_short(self):
        from gateway.platforms.helpers import mesaj_kisalt
        assert mesaj_kisalt("kisa") == "kisa"

    def test_mesaj_kisalt_long(self):
        from gateway.platforms.helpers import mesaj_kisalt
        uzun = "a" * 5000
        kisaltilmis = mesaj_kisalt(uzun, max_uzunluk=100)
        assert len(kisaltilmis) <= 100
        assert kisaltilmis.endswith("...")

    def test_mesaj_istege_cevir_plain(self):
        from gateway.platforms.helpers import mesaj_istege_cevir
        result = mesaj_istege_cevir("**bold** _italic_", tur="plain")
        assert "**" not in result
        assert "_" not in result

    def test_mesaj_istege_cevir_html(self):
        from gateway.platforms.helpers import mesaj_istege_cevir
        result = mesaj_istege_cevir("**bold** `code`", tur="html")
        assert "<b>" in result
        assert "<code>" in result

    def test_mesaj_istege_cevir_markdown(self):
        from gateway.platforms.helpers import mesaj_istege_cevir
        result = mesaj_istege_cevir("**bold**", tur="md")
        assert result == "**bold**"

    def test_mesaj_parcala_short(self):
        from gateway.platforms.helpers import mesaj_parcala
        result = mesaj_parcala("kisa", max_parca=100)
        assert result == ["kisa"]

    def test_mesaj_parcala_long(self):
        from gateway.platforms.helpers import mesaj_parcala
        result = mesaj_parcala("a" * 1000, max_parca=300)
        assert len(result) == 4
        assert all(len(p) <= 300 for p in result)

    def test_mesaj_birlestir(self):
        from gateway.platforms.helpers import mesaj_birlestir
        result = mesaj_birlestir(["a", "b", "c"], ayrac="\n")
        assert result == "a\nb\nc"

    def test_mesaj_birlestir_empty(self):
        from gateway.platforms.helpers import mesaj_birlestir
        assert mesaj_birlestir([]) == ""
        assert mesaj_birlestir(["a", None, "b"]) == "a\n\nb"


class TestMedya:
    def test_medya_yukle_no_requests(self):
        with patch("gateway.platforms.helpers._REQUESTS_OK", False):
            from gateway.platforms.helpers import medya_yukle
            result = medya_yukle("http://example.com/img.jpg")
            assert result["durum"] == "hata"

    def test_medya_yukle_no_url(self):
        with patch("gateway.platforms.helpers._REQUESTS_OK", True):
            from gateway.platforms.helpers import medya_yukle
            result = medya_yukle("")
            assert result["durum"] == "hata"
            assert "URL" in result["hata"]

    def test_medya_yukle_error(self):
        with patch("gateway.platforms.helpers._REQUESTS_OK", True):
            with patch("requests.get", side_effect=Exception("indirme hatasi")):
                from gateway.platforms.helpers import medya_yukle
                result = medya_yukle("http://example.com/img.jpg")
                assert result["durum"] == "hata"
                assert "indirme" in result["hata"]

    def test_medya_sil_nonexistent(self):
        from gateway.platforms.helpers import medya_sil
        assert medya_sil("/nonexistent/path") is False

    def test_medya_sil_success(self):
        from gateway.platforms.helpers import medya_sil
        with patch("os.path.isfile", return_value=True):
            with patch("os.remove", return_value=None):
                assert medya_sil("/tmp/test.txt") is True


class TestPlatformDogrulama:
    def test_platform_dogrula_success(self):
        from gateway.platforms.helpers import platform_dogrula
        with patch("os.environ.get", return_value="var"):
            result = platform_dogrula(["API_KEY", "TOKEN"])
            assert result["durum"] == "basarili"

    def test_platform_dogrula_eksik(self):
        from gateway.platforms.helpers import platform_dogrula
        with patch("os.environ.get", return_value=""):
            result = platform_dogrula(["API_KEY", "TOKEN"])
            assert result["durum"] == "hata"
            assert "API_KEY" in result["eksikler"]

    def test_env_al(self):
        from gateway.platforms.helpers import env_al
        with patch("os.environ.get", return_value="deger"):
            assert env_al("TEST") == "deger"
        with patch("os.environ.get", return_value=""):
            assert env_al("YOK") == ""

    def test_ping(self):
        from gateway.platforms.helpers import ping
        assert ping() is True


class TestMessageDeduplicator:
    def test_deduplicator(self):
        from gateway.platforms.helpers import MessageDeduplicator
        md = MessageDeduplicator()
        assert md.is_duplicate("a") is False
        assert md.is_duplicate("a") is True
        assert md.is_duplicate("b") is False
        assert md.is_duplicate("b") is True


class TestThreadParticipationTracker:
    def test_init(self):
        from gateway.platforms.helpers import ThreadParticipationTracker
        tracker = ThreadParticipationTracker(platform="test")
        assert tracker._platform == "test"
        assert len(tracker) == 0

    def test_mark_and_contains(self):
        with patch("os.environ.get", return_value="/tmp"):
            from gateway.platforms.helpers import ThreadParticipationTracker
            tracker = ThreadParticipationTracker(platform="test")
            tracker.mark("thread_1")
            assert "thread_1" in tracker
            assert len(tracker) == 1

    def test_state_path(self):
        with patch("os.environ.get", return_value="/tmp"):
            from gateway.platforms.helpers import ThreadParticipationTracker
            tracker = ThreadParticipationTracker(platform="test")
            path = tracker._state_path()
            assert "test_threads.json" in str(path)


class TestStripMarkdown:
    def test_strip_markdown_bold(self):
        from gateway.platforms.helpers import strip_markdown
        result = strip_markdown("**bold** text")
        assert "bold" in result

    def test_strip_markdown_links(self):
        from gateway.platforms.helpers import strip_markdown
        result = strip_markdown("[link](http://example.com)")
        assert "link" in result

    def test_strip_markdown_headers(self):
        from gateway.platforms.helpers import strip_markdown
        result = strip_markdown("# Baslik\n## Alt")
        assert "Baslik" in result

    def test_strip_markdown_empty(self):
        from gateway.platforms.helpers import strip_markdown
        assert strip_markdown("") == ""

    def test_strip_markdown_code_block(self):
        from gateway.platforms.helpers import strip_markdown
        result = strip_markdown("```\nkod\n```")
        assert "kod" in result
