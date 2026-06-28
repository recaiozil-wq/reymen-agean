# -*- coding: utf-8 -*-
"""test_gateway_persistence.py — ai_bot.py kalıcı ayar testleri."""
import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Proje kökünü ekle
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
sys.path.insert(0, str(PROJE_KOK / "telegram_bot"))

# ── Fixture ─────────────────────────────────────────────────────────────────

@pytest.fixture
def ayar_dosyasi(tmp_path):
    return tmp_path / "ai_bot_ayarlari.json"


@pytest.fixture
def yoneticisi(ayar_dosyasi):
    from telegram_bot.ai_bot import AyarYoneticisi, VARSAYILAN_AYARLAR
    return AyarYoneticisi(ayar_dosyasi)


# ── AyarYoneticisi Testleri ───────────────────────────────────────────────────

class TestAyarYoneticisi:
    def test_varsayilan_ayarlar(self, yoneticisi):
        assert yoneticisi.al("model") == "deepseek-chat"
        assert yoneticisi.al("provider") == "deepseek"
        assert yoneticisi.al("offset") == 0
        assert yoneticisi.al("bilinen_chatler") == []

    def test_dosya_yoksa_varsayilan_kullanir(self, ayar_dosyasi):
        from telegram_bot.ai_bot import AyarYoneticisi
        y = AyarYoneticisi(ayar_dosyasi)
        assert y.al("model") == "deepseek-chat"
        assert not ayar_dosyasi.exists()  # okuma yok → dosya oluşmadı

    def test_ayarla_ve_kaydet(self, yoneticisi, ayar_dosyasi):
        yoneticisi.ayarla("model", "gpt-4o-mini")
        assert ayar_dosyasi.exists()
        data = json.loads(ayar_dosyasi.read_text(encoding="utf-8"))
        assert data["model"] == "gpt-4o-mini"

    def test_ayarla_kalici_olarak_okunur(self, ayar_dosyasi):
        from telegram_bot.ai_bot import AyarYoneticisi
        y1 = AyarYoneticisi(ayar_dosyasi)
        y1.ayarla("provider", "openrouter")
        y2 = AyarYoneticisi(ayar_dosyasi)
        assert y2.al("provider") == "openrouter"

    def test_offset_artarak_guncellenir(self, yoneticisi, ayar_dosyasi):
        yoneticisi.offset_guncelle(1001)
        assert yoneticisi.al("offset") == 1001
        data = json.loads(ayar_dosyasi.read_text(encoding="utf-8"))
        assert data["offset"] == 1001

    def test_offset_geriye_gitmez(self, yoneticisi):
        yoneticisi.offset_guncelle(500)
        yoneticisi.offset_guncelle(300)  # küçük → görmezden gel
        assert yoneticisi.al("offset") == 500

    def test_offset_restart_sonrasi_korunur(self, ayar_dosyasi):
        from telegram_bot.ai_bot import AyarYoneticisi
        y1 = AyarYoneticisi(ayar_dosyasi)
        y1.offset_guncelle(9999)
        y2 = AyarYoneticisi(ayar_dosyasi)
        assert y2.al("offset") == 9999

    def test_chat_ekle(self, yoneticisi):
        yoneticisi.chat_ekle(123456)
        assert 123456 in yoneticisi.al("bilinen_chatler")

    def test_chat_tekrar_eklenmez(self, yoneticisi):
        yoneticisi.chat_ekle(123456)
        yoneticisi.chat_ekle(123456)
        assert yoneticisi.al("bilinen_chatler").count(123456) == 1

    def test_chat_kalici_olarak_okunur(self, ayar_dosyasi):
        from telegram_bot.ai_bot import AyarYoneticisi
        y1 = AyarYoneticisi(ayar_dosyasi)
        y1.chat_ekle(111111)
        y2 = AyarYoneticisi(ayar_dosyasi)
        assert 111111 in y2.al("bilinen_chatler")

    def test_sifirla_ayarlari_korumaz(self, yoneticisi, ayar_dosyasi):
        yoneticisi.ayarla("model", "ozel-model")
        yoneticisi.offset_guncelle(777)
        yoneticisi.sifirla()
        assert yoneticisi.al("model") == "deepseek-chat"  # sıfırlandı
        assert yoneticisi.al("offset") == 777  # offset korundu

    def test_sifirla_kalici(self, ayar_dosyasi):
        from telegram_bot.ai_bot import AyarYoneticisi
        y1 = AyarYoneticisi(ayar_dosyasi)
        y1.ayarla("provider", "ozel-prov")
        y1.sifirla()
        y2 = AyarYoneticisi(ayar_dosyasi)
        assert y2.al("provider") == "deepseek"

    def test_ozet_doner(self, yoneticisi):
        ozet = yoneticisi.ozet()
        assert "Model:" in ozet
        assert "Provider:" in ozet
        assert "Offset:" in ozet

    def test_bozuk_dosya_varsayilana_duner(self, ayar_dosyasi):
        from telegram_bot.ai_bot import AyarYoneticisi
        ayar_dosyasi.parent.mkdir(parents=True, exist_ok=True)
        ayar_dosyasi.write_text("bu gecersiz json{{{{", encoding="utf-8")
        y = AyarYoneticisi(ayar_dosyasi)
        assert y.al("model") == "deepseek-chat"


# ── Komut İşleyici Testleri ───────────────────────────────────────────────────

class TestKomutIsleme:
    def _gonder_mock(self):
        return MagicMock(return_value=True)

    def test_model_komutu_degistirir(self, yoneticisi):
        gonder = self._gonder_mock()
        with patch("telegram_bot.ai_bot.mesaj_gonder", gonder):
            from telegram_bot.ai_bot import komut_isle
            komut_isle("TOK", 100, "/model gpt-4o-mini", yoneticisi)
        assert yoneticisi.al("model") == "gpt-4o-mini"

    def test_provider_komutu_degistirir(self, yoneticisi):
        gonder = self._gonder_mock()
        with patch("telegram_bot.ai_bot.mesaj_gonder", gonder):
            from telegram_bot.ai_bot import komut_isle
            komut_isle("TOK", 100, "/provider openrouter", yoneticisi)
        assert yoneticisi.al("provider") == "openrouter"

    def test_sistem_komutu_degistirir(self, yoneticisi):
        gonder = self._gonder_mock()
        with patch("telegram_bot.ai_bot.mesaj_gonder", gonder):
            from telegram_bot.ai_bot import komut_isle
            komut_isle("TOK", 100, "/sistem Yeni sistem prompt", yoneticisi)
        assert yoneticisi.al("sistem_prompt") == "Yeni sistem prompt"

    def test_sifirla_komutu(self, yoneticisi):
        yoneticisi.ayarla("model", "ozel")
        gonder = self._gonder_mock()
        with patch("telegram_bot.ai_bot.mesaj_gonder", gonder):
            from telegram_bot.ai_bot import komut_isle
            komut_isle("TOK", 100, "/sifirla", yoneticisi)
        assert yoneticisi.al("model") == "deepseek-chat"

    def test_ayarlar_komutu_cevap_doner(self, yoneticisi):
        gonder = self._gonder_mock()
        with patch("telegram_bot.ai_bot.mesaj_gonder", gonder):
            from telegram_bot.ai_bot import komut_isle
            komut_isle("TOK", 100, "/ayarlar", yoneticisi)
        gonder.assert_called_once()

    def test_start_komutu(self, yoneticisi):
        gonder = self._gonder_mock()
        with patch("telegram_bot.ai_bot.mesaj_gonder", gonder):
            from telegram_bot.ai_bot import komut_isle
            komut_isle("TOK", 100, "/start", yoneticisi)
        gonder.assert_called_once()

    def test_bilinmeyen_komut_false_doner(self, yoneticisi):
        from telegram_bot.ai_bot import komut_isle
        sonuc = komut_isle("TOK", 100, "/bilinmeyenkomut", yoneticisi)
        assert sonuc is False

    def test_normal_mesaj_false_doner(self, yoneticisi):
        from telegram_bot.ai_bot import komut_isle
        sonuc = komut_isle("TOK", 100, "merhaba nasılsın", yoneticisi)
        assert sonuc is False

    def test_model_argumansiz_gosterir(self, yoneticisi):
        gonder = self._gonder_mock()
        with patch("telegram_bot.ai_bot.mesaj_gonder", gonder):
            from telegram_bot.ai_bot import komut_isle
            komut_isle("TOK", 100, "/model", yoneticisi)
        gonder.assert_called_once()
        assert "deepseek-chat" in str(gonder.call_args)

    def test_komut_true_doner(self, yoneticisi):
        gonder = self._gonder_mock()
        with patch("telegram_bot.ai_bot.mesaj_gonder", gonder):
            from telegram_bot.ai_bot import komut_isle
            sonuc = komut_isle("TOK", 100, "/start", yoneticisi)
        assert sonuc is True
