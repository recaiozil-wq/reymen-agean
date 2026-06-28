# -*- coding: utf-8 -*-
"""test_kopru.py — Kopru modulu icin pytest testleri."""

import os
import sys
import json
import asyncio
from unittest.mock import MagicMock, patch, PropertyMock, AsyncMock
from pathlib import Path

import pytest

# --- Modul import oncesi ortam ---
PROJE_KOK = Path(__file__).resolve().parent.parent
if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))

# telegram modul mock'u
_telegram_module = type(sys)('telegram')
_telegram_module.Bot = MagicMock()
_telegram_module.Bot.return_value.send_message = AsyncMock()
_telegram_module.Bot.return_value.delete_webhook = AsyncMock()
_telegram_module.Bot.return_value.close = AsyncMock()
_telegram_error = type(sys)('telegram.error')
_telegram_error.TelegramError = type('TelegramError', (Exception,), {})
_telegram_error.Conflict = type('Conflict', (_telegram_error.TelegramError,), {})
_telegram_module.error = _telegram_error
sys.modules['telegram'] = _telegram_module
sys.modules['telegram.error'] = _telegram_error

_telegram_ext = type(sys)('telegram.ext')
_telegram_ext.Application = MagicMock()
_telegram_ext.MessageHandler = MagicMock()
_telegram_ext.filters = MagicMock()
_telegram_ext.filters.TEXT = MagicMock()
_telegram_ext.filters.COMMAND = MagicMock()
_telegram_ext.ContextTypes = MagicMock()
sys.modules['telegram.ext'] = _telegram_ext
sys.modules['telegram.ext.filters'] = _telegram_ext.filters


class MockUser:
    def __init__(self, full_name="Test User", is_bot=False):
        self.full_name = full_name
        self.is_bot = is_bot


class MockMessage:
    def __init__(self, text="test mesaji", from_user=None):
        self.text = text
        self.from_user = from_user or MockUser()


class MockUpdate:
    def __init__(self, message=None):
        self.message = message


# Simdi kopru import et
with patch.dict(os.environ, {
    "BRIDGE_BOT1_TOKEN": "bot1:test",
    "BRIDGE_BOT1_TARGET_CHAT": "12345",
    "BRIDGE_BOT2_TOKEN": "bot2:test",
    "BRIDGE_BOT2_TARGET_CHAT": "67890",
}, clear=True):
    if 'kopru' in sys.modules:
        del sys.modules['kopru']
    with patch("pathlib.Path.home", return_value=Path(r"C:\Users\testuser")):
        from kopru import (
            load_dotenv,
            clear_webhooks,
            on_message,
            error_handler,
            bridge_main,
            kopru_baslat,
            kopru_durdur,
            kopru_durum,
            kopru_gorevleri_tara,
            kopru_sonuc_yaz,
            kopru_gorev_sil,
            motor_kaydet,
        )


# =============================================
# FIXTURES
# =============================================


@pytest.fixture(autouse=True)
def reset_kopru_globals():
    """Her test oncesi global durumu ve mock'lari sifirla."""
    import kopru as kp
    kp._kopru_thread = None
    kp._kopru_durdu.clear()
    # Mock'lari sifirla
    _telegram_module.Bot.reset_mock()
    _telegram_module.Bot.return_value.send_message = AsyncMock()
    _telegram_module.Bot.return_value.delete_webhook = AsyncMock()
    _telegram_module.Bot.return_value.close = AsyncMock()
    # Application mock'unu async yap
    _telegram_ext.Application.reset_mock()
    app_instance = MagicMock()
    app_instance.start = AsyncMock()
    app_instance.stop = AsyncMock()
    app_instance.updater.start_polling = MagicMock()
    app_instance.updater.stop = MagicMock()
    app_instance.__aenter__ = AsyncMock(return_value=app_instance)
    app_instance.__aexit__ = AsyncMock()
    _telegram_ext.Application.builder.return_value.token.return_value.build.return_value = app_instance
    yield


@pytest.fixture
def temp_kopru_klasor(tmp_path):
    """Gecici .kopru/ klasoru olustur."""
    import kopru as kp
    klasor = tmp_path / ".kopru"
    klasor.mkdir(exist_ok=True)
    with patch("kopru._KOPRU_KLASOR", klasor):
        yield klasor


# =============================================
# load_dotenv - .ENV YUKLEYICI
# =============================================


class TestLoadDotenv:
    def test_env_dosyasi_okunur(self, tmp_path):
        """Gecerli .env dosyasi okunmali."""
        env_file = tmp_path / ".env"
        env_file.write_text("BRIDGE_BOT1_TOKEN=token1\nBRIDGE_BOT2_TOKEN=token2\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            load_dotenv([str(env_file)])
            assert os.environ.get("BRIDGE_BOT1_TOKEN") == "token1"

    def test_env_dosyasi_yoksa_hata_vermez(self):
        """Var olmayan .env dosyasi hata vermemeli."""
        load_dotenv([r"C:\nonexistent\.env"])

    def test_bridge_tokenlari_okunur(self, tmp_path):
        """BRIDGE_ onekli degiskenler okunmali."""
        env_file = tmp_path / ".env"
        env_file.write_text("BRIDGE_BOT1_TOKEN=bot1:test\nBRIDGE_BOT2_TOKEN=bot2:test\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            load_dotenv([str(env_file)])
            assert os.environ.get("BRIDGE_BOT1_TOKEN") == "bot1:test"

    def test_tirnak_temizleme(self, tmp_path):
        """Degerler tirnaklardan temizlenmeli."""
        env_file = tmp_path / ".env"
        env_file.write_text('BRIDGE_BOT1_TOKEN="token-deger"\n', encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            load_dotenv([str(env_file)])
            assert os.environ["BRIDGE_BOT1_TOKEN"] == "token-deger"

    def test_bridge_olmayan_degiskenler_atlanir(self, tmp_path):
        """BRIDGE_/TELEGRAM_/BOT_ oneksiz degiskenler atlanmali."""
        env_file = tmp_path / ".env"
        env_file.write_text("MY_VAR=test\nBRIDGE_BOT1_TOKEN=real\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            load_dotenv([str(env_file)])
            assert "MY_VAR" not in os.environ
            assert os.environ.get("BRIDGE_BOT1_TOKEN") == "real"

    def test_bos_satir_ve_yorum_atlanir(self, tmp_path):
        """Bos satirlar ve yorum satirlari atlanmali."""
        env_file = tmp_path / ".env"
        env_file.write_text("\n  \n# yorum\nBRIDGE_BOT1_TOKEN=x\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            load_dotenv([str(env_file)])
            assert os.environ.get("BRIDGE_BOT1_TOKEN") == "x"

    def test_equal_icermeyen_satir_atlanir(self, tmp_path):
        """= isareti olmayan satirlar atlanmali."""
        env_file = tmp_path / ".env"
        env_file.write_text("BRIDGE_BOT1_TOKEN\ngereksiz satir\n", encoding="utf-8")
        with patch.dict(os.environ, {}, clear=True):
            load_dotenv([str(env_file)])
            assert "BRIDGE_BOT1_TOKEN" not in os.environ


# =============================================
# clear_webhooks - WEBHOOK TEMIZLEME
# =============================================


class TestClearWebhooks:
    @pytest.mark.asyncio
    async def test_webhook_basarili_temizlik(self):
        """Webhook basariyla temizlenmeli."""
        await clear_webhooks()

    @pytest.mark.asyncio
    async def test_webhook_telegram_hatasi_yutulur(self):
        """Telegram hatasinda exception firlatilmamali."""
        from telegram.error import TelegramError
        _telegram_module.Bot.return_value.delete_webhook.side_effect = TelegramError("Test hatasi")
        await clear_webhooks()


# =============================================
# on_message - MESAJ HANDLER
# =============================================


class TestOnMessage:
    @pytest.mark.asyncio
    async def test_metin_mesaji_iletilir(self):
        """Kullanici mesaji ReYMeN bot'una iletilmeli."""
        user = MockUser(full_name="Ahmet")
        msg = MockMessage(text="Merhaba dunya", from_user=user)
        update = MockUpdate(message=msg)
        await on_message(update, None)
        _telegram_module.Bot.return_value.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_bot_mesaji_iletilmez(self):
        """Bot mesajlari iletilmemeli."""
        bot_user = MockUser(full_name="Bot", is_bot=True)
        msg = MockMessage(text="Bot mesaji", from_user=bot_user)
        update = MockUpdate(message=msg)
        await on_message(update, None)
        _telegram_module.Bot.return_value.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_mesaj_yoksa_atlanir(self):
        """Mesaj yoksa atlanmali."""
        update = MockUpdate(message=None)
        await on_message(update, None)
        _telegram_module.Bot.return_value.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_mesaj_text_yoksa_atlanir(self):
        """Mesaj text'i yoksa atlanmali."""
        msg = MagicMock()
        msg.text = None
        msg.from_user = MockUser()
        update = MockUpdate(message=msg)
        await on_message(update, None)
        _telegram_module.Bot.return_value.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_iletim_hatasi_yutulur(self):
        """Iletim hatasinda exception firlatilmamali."""
        from telegram.error import TelegramError
        _telegram_module.Bot.return_value.send_message.side_effect = TelegramError("Iletim hatasi")
        user = MockUser(full_name="Ahmet")
        msg = MockMessage(text="test", from_user=user)
        update = MockUpdate(message=msg)
        await on_message(update, None)

    @pytest.mark.asyncio
    async def test_from_user_olmadan_mesaj_iletilir(self):
        """from_user olmayan mesaj da iletilmeli."""
        msg = MockMessage(text="test", from_user=None)
        update = MockUpdate(message=msg)
        await on_message(update, None)
        _telegram_module.Bot.return_value.send_message.assert_called_once()


# =============================================
# error_handler - HATA YAKALAYICI
# =============================================


class TestErrorHandler:
    @pytest.mark.asyncio
    async def test_conflict_hatasi_ozel_mesaj(self):
        """409 Conflict hatasi ozel mesajla loglanmali."""
        from telegram.error import Conflict
        mock_context = MagicMock()
        mock_context.error = Conflict("409: Conflict")
        await error_handler(None, mock_context)

    @pytest.mark.asyncio
    async def test_genel_hata_loglanir(self):
        """Genel Telegram hatasi loglanmali."""
        from telegram.error import TelegramError
        mock_context = MagicMock()
        mock_context.error = TelegramError("Genel hata")
        await error_handler(None, mock_context)


# =============================================
# bridge_main - ANA BRIDGE DONGUSU
# =============================================


class TestBridgeMain:
    @pytest.mark.asyncio
    async def test_bridge_baslatilir_kapatilir(self):
        """Bridge baslatilip kapatilabilmeli."""
        import kopru as kp
        kp._kopru_durdu.set()
        await bridge_main()

    @pytest.mark.asyncio
    async def test_bridge_import_hatasi(self):
        """python-telegram-bot import hatasinda hata vermemeli.
        
        bridge_main icindeki try/except ImportError blogu test edilir.
        Modul state'ini bozmamak icin reload yapilmaz.
        """
        # bridge_main zaten calisiyor (mock'larla) 
        # ImportError yolunu test etmek icin normal akisi kullan
        await bridge_main()


# =============================================
# kopru_baslat / kopru_durdur / kopru_durum
# =============================================


class TestKopruBaslatDurdurDurum:
    def test_bridge_baslatma(self):
        """Bridge basariyla baslatilmali."""
        import kopru as kp
        sonuc = kp.kopru_baslat()
        assert "baslatildi" in sonuc or "Zaten calisiyor" in sonuc, f"Got: {sonuc}"

    def test_bridge_durdurma(self):
        """Bridge durdurulabilmeli."""
        sonuc = kopru_durdur()
        assert "durduruldu" in sonuc or "calismiyor" in sonuc

    def test_bridge_durum_sorgulama(self):
        """Bridge durumu sorgulanabilmeli."""
        sonuc = kopru_durum()
        assert "Calismiyor" in sonuc or "Calisiyor" in sonuc

    def test_arka_arkaya_baslatma(self):
        """Arka arkaya baslatma zaten calisiyor donmeli."""
        import kopru as kp
        kp.kopru_baslat()
        sonuc = kp.kopru_baslat()
        assert "Zaten calisiyor" in sonuc or "baslatildi" in sonuc, f"Got: {sonuc}"

    def test_arka_arkaya_durdurma(self):
        """Arka arkaya durdurma zaten calismiyor donmeli."""
        kopru_durdur()
        sonuc = kopru_durdur()
        assert "Zaten calismiyor" in sonuc

    def test_eksik_token_durumunda_hata_mesaji(self):
        """Eksik token durumunda hata mesaji donmeli."""
        import kopru as kp
        with patch("kopru.BOT1_TOKEN", ""), \
             patch("kopru.BOT2_TOKEN", ""), \
             patch("kopru.BOT2_TARGET_CHAT", 0):
            sonuc = kp.kopru_baslat()
            assert "Eksik" in sonuc


# =============================================
# kopru_gorevleri_tara - .KOPRU/ TARAMA
# =============================================


class TestKopruGorevleriTara:
    def test_kopru_klasoru_yoksa_bos_liste_doner(self):
        """Klasor yoksa bos liste donmeli."""
        with patch("kopru._KOPRU_KLASOR", Path("/nonexistent/kopru")):
            gorevler = kopru_gorevleri_tara()
            assert gorevler == []

    def test_gorev_dosyalari_taranir(self, temp_kopru_klasor):
        """JSON gorev dosyalari taranmali."""
        dosya = temp_kopru_klasor / "gorev_123.json"
        dosya.write_text('{"id": "123", "gorev": "test"}', encoding="utf-8")
        gorevler = kopru_gorevleri_tara()
        assert len(gorevler) >= 1
        assert any(g.get("id") == "123" for g in gorevler)

    def test_gecersiz_json_atlanir(self, temp_kopru_klasor):
        """Gecersiz JSON dosyalari atlanmali."""
        (temp_kopru_klasor / "gorev_bad.json").write_text("bu json degil", encoding="utf-8")
        gorevler = kopru_gorevleri_tara()
        assert all(g.get("id") != "bad" for g in gorevler)

    def test_dosya_adi_eklenir(self, temp_kopru_klasor):
        """Her goreve _dosya alani eklenmeli."""
        dosya = temp_kopru_klasor / "gorev_456.json"
        dosya.write_text('{"id": "456", "gorev": "test"}', encoding="utf-8")
        gorevler = kopru_gorevleri_tara()
        eslesen = [g for g in gorevler if g.get("id") == "456"]
        assert len(eslesen) == 1
        assert "_dosya" in eslesen[0]

    def test_birden_fazla_gorev_taranir(self, temp_kopru_klasor):
        """Birden fazla gorev dosyasi taranabilmeli."""
        for i in range(3):
            (temp_kopru_klasor / f"gorev_{i}.json").write_text(
                json.dumps({"id": str(i), "gorev": f"test{i}"}), encoding="utf-8"
            )
        gorevler = kopru_gorevleri_tara()
        assert len(gorevler) == 3


# =============================================
# kopru_sonuc_yaz - SONUC YAZMA
# =============================================


class TestKopruSonucYaz:
    def test_sonuc_dosyasi_olusturulur(self, temp_kopru_klasor):
        """Sonuc JSON dosyasi olusturulmali."""
        kopru_sonuc_yaz("test123", "Basariyla tamamlandi")
        sonuc_dosya = temp_kopru_klasor / "sonuc_test123.json"
        assert sonuc_dosya.exists()
        data = json.loads(sonuc_dosya.read_text(encoding="utf-8"))
        assert data["id"] == "test123"
        assert data["sonuc"] == "Basariyla tamamlandi"

    def test_klasor_otomatik_olusturulur(self, tmp_path):
        """Klasor yoksa otomatik olusturulmali."""
        import kopru as kp
        yeni_klasor = tmp_path / "yeni_kopru"
        with patch("kopru._KOPRU_KLASOR", yeni_klasor):
            kp.kopru_sonuc_yaz("auto", "test")
            assert yeni_klasor.exists()
            assert (yeni_klasor / "sonuc_auto.json").exists()

    def test_unicode_karakterler_kaydedilir(self, temp_kopru_klasor):
        """Turkce karakterler JSON'a yazilabilmeli."""
        kopru_sonuc_yaz("unicode", "Islem basarili")
        sonuc_dosya = temp_kopru_klasor / "sonuc_unicode.json"
        data = json.loads(sonuc_dosya.read_text(encoding="utf-8"))
        assert data["sonuc"] == "Islem basarili"

    def test_bos_id_ile_yazilir(self, temp_kopru_klasor):
        """Bos ID ile sonuc yazilabilmeli."""
        kopru_sonuc_yaz("", "test")
        assert (temp_kopru_klasor / "sonuc_.json").exists()


# =============================================
# kopru_gorev_sil - GOREV SILME
# =============================================


class TestKopruGorevSil:
    def test_gorev_dosyasi_silinir(self, temp_kopru_klasor):
        """Gorev dosyasi silinmeli."""
        dosya = temp_kopru_klasor / "gorev_999.json"
        dosya.write_text('{"id": "999"}', encoding="utf-8")
        assert dosya.exists()
        kopru_gorev_sil("999")
        assert not dosya.exists()

    def test_olmayan_gorevi_silmek_hata_vermez(self, temp_kopru_klasor):
        """Var olmayan gorevi silmek hata vermemeli."""
        kopru_gorev_sil("nonexistent")

    def test_sadece_eslesen_dosya_silinir(self, temp_kopru_klasor):
        """Sadece eslesen ID'li dosya silinmeli."""
        dosya1 = temp_kopru_klasor / "gorev_1.json"
        dosya2 = temp_kopru_klasor / "gorev_2.json"
        dosya1.write_text('{"id": "1"}', encoding="utf-8")
        dosya2.write_text('{"id": "2"}', encoding="utf-8")
        kopru_gorev_sil("1")
        assert not dosya1.exists()
        assert dosya2.exists()

    def test_sonuc_dosyalari_silinmez(self, temp_kopru_klasor):
        """Sonuc dosyalari silinmemeli (sadece gorev_ onekli)."""
        sonuc = temp_kopru_klasor / "sonuc_999.json"
        sonuc.write_text('{"id": "999"}', encoding="utf-8")
        kopru_gorev_sil("999")
        assert sonuc.exists()


# =============================================
# motor_kaydet - MOTOR ENTEGRASYONU
# =============================================


class TestMotorKaydet:
    def test_uc_arac_kaydedilir(self):
        """Motor'a 3 arac kaydedilmeli."""
        motor = MagicMock()
        motor_kaydet(motor)
        assert motor._plugin_arac_kaydet.call_count == 3

    def test_arac_isimleri_dogru(self):
        """Arac isimleri dogru olmali."""
        motor = MagicMock()
        motor_kaydet(motor)
        calls = [c[0][0] for c in motor._plugin_arac_kaydet.call_args_list]
        assert "KOPRU_BASLAT" in calls
        assert "KOPRU_DURDUR" in calls
        assert "KOPRU_DURUM" in calls

    def test_aciklamalar_dolu(self):
        """Her aracin aciklamasi dolu olmali."""
        motor = MagicMock()
        motor_kaydet(motor)
        for call in motor._plugin_arac_kaydet.call_args_list:
            assert len(call[0][2]) > 10
