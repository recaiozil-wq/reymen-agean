# -*- coding: utf-8 -*-
"""tests/test_yardimci.py — Yardimci modul testleri (zaman asimi yok)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLogging:
    def test_logger_kurulum(self):
        """Logger kurulumu ve alt logger olusturma."""
        from ReYMeN_logging import kur, get_logger

        log = kur()
        assert log is not None
        alt = get_logger("test")
        assert alt is not None


class TestSkillUtils:
    def test_skill_sayisi_var(self):
        """skill_sayisi fonksiyonu integer donmeli."""
        from skill_utils import skill_sayisi, kategorileri_listele

        sayi = skill_sayisi()
        assert isinstance(sayi, int)
        kat = kategorileri_listele()
        assert isinstance(kat, list)

    def test_skill_ara(self):
        """skill_ara en az list donmeli."""
        from skill_utils import skill_ara

        sonuc = skill_ara("windows")
        assert isinstance(sonuc, list)


class TestMessageSanitization:
    def test_temizleme(self):
        """Mesaj temizleme ve dogrulama."""
        from message_sanitization import temizle, dogrula

        t = temizle("Merhaba")
        assert "Merhaba" in t
        t = temizle("rm -rf /")
        assert "ENGELLENDI" in t
        d = dogrula("test")
        assert d["gecerli"]
