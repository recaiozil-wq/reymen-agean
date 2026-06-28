# -*- coding: utf-8 -*-
"""test_reymen_agent.py — ReYMeN agent modülü için pytest testleri."""

import os
import sys
import json
import time
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path

import pytest

# ── Modülü import etmeden önce ortam hazırlığı ──
# Dotenv yüklemesini engelle (gerçek .env dosyası yok)
_env_path_backup = None

# Ana modülü import edebilmek için path'e proje kökünü ekle
PROJE_KOK = Path(__file__).resolve().parent.parent
if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))

# main modülü mock'u — reymen_agent import etmeden ÖNCE tanımlanmalı
_main_module = type(sys)('main')
_main_module.AIAgentOrchestrator = MagicMock()
_main_module.CONFIG = {"test": True}
sys.modules['main'] = _main_module

# closed_learning_loop modülü mock
_cll_module = type(sys)('closed_learning_loop')
_cll_module._beceri_ara = MagicMock(return_value="test becerisi")
sys.modules['closed_learning_loop'] = _cll_module

# requests modülü mock (önceden import edilmişse override)
_requests_module = type(sys)('requests')
_requests_module.post = MagicMock()
sys.modules['requests'] = _requests_module

# .env dosyasının varlığını kontrol et — yoksa mock
_env_file = PROJE_KOK / ".env"
_env_backup = None
if not _env_file.exists():
    # dotenv.load_dotenv'i pas geç
    _dotenv_module = type(sys)('dotenv')
    _dotenv_module.load_dotenv = MagicMock()
    sys.modules['dotenv'] = _dotenv_module

# Şimdi reymen_agent import et
with patch.dict(os.environ, {}, clear=True):
    from reymen_agent import (
        _get_logger,
        _agent_instance,
        isleyen_gorev,
        _beceri_baglami_al,
        _deepseek_sohbet,
        _agent_loop,
        _yanit_ayikla,
        _deepseek_fallback,
        _format_temizle,
        kopru_deepseek_istek,
    )


# ═══════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════


@pytest.fixture(autouse=True)
def reset_globals():
    """Her test öncesi global değişkenleri sıfırla."""
    import reymen_agent as ra
    ra._agent = None
    ra._logger = None
    yield


@pytest.fixture
def mock_deepseek_response():
    """Başarılı DeepSeek API yanıtı mock."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Merhaba! Size nasıl yardımcı olabilirim?"}}]
    }
    return mock_resp


@pytest.fixture
def mock_agent():
    """AIAgentOrchestrator mock."""
    agent = MagicMock()
    agent.conversation_history = [
        {"role": "user", "content": "test"},
        {"role": "assistant", "content": "Agent yanıtı"},
    ]
    agent.last_response = "Son yanıt"
    _main_module.AIAgentOrchestrator = MagicMock(return_value=agent)
    return agent


# ═══════════════════════════════════════════════
# _get_logger — LOGGER OLUŞTURMA
# ═══════════════════════════════════════════════


class TestGetLogger:
    def test_logger_olusturma(self):
        """Logger ilk çağrıda oluşturulmalı."""
        log = _get_logger()
        assert log is not None
        assert log.name == "reymen_agent"

    def test_logger_singleton(self):
        """Logger aynı instance döndürmeli."""
        log1 = _get_logger()
        log2 = _get_logger()
        assert log1 is log2


# ═══════════════════════════════════════════════
# _agent_instance — AGENT SINGLETON
# ═══════════════════════════════════════════════


class TestAgentInstance:
    def test_agent_basariyla_olusturulur(self, mock_agent):
        """Agent başarıyla oluşturulmalı."""
        agent = _agent_instance()
        assert agent is not None
        _main_module.AIAgentOrchestrator.assert_called_once()

    def test_agent_singleton_davranisi(self, mock_agent):
        """Aynı instance döndürülmeli (singleton)."""
        agent1 = _agent_instance()
        agent2 = _agent_instance()
        assert agent1 is agent2
        # AIAgentOrchestrator sadece bir kez çağrılmalı
        assert _main_module.AIAgentOrchestrator.call_count == 1

    def test_agent_basarisiz_olursa_none_doner(self):
        """Import hatası durumunda None dönmeli."""
        _main_module.AIAgentOrchestrator.side_effect = ImportError("Yok")
        agent = _agent_instance()
        assert agent is None

    def test_agent_import_hatasi_loglanir(self, caplog):
        """Import hatası log'a yazılmalı."""
        import logging
        caplog.set_level(logging.ERROR)
        _main_module.AIAgentOrchestrator.side_effect = Exception("Test hatası")
        _agent_instance()
        assert "Agent baslatilamadi" in caplog.text


# ═══════════════════════════════════════════════
# _beceri_baglami_al — BECERİ SORGULAMA
# ═══════════════════════════════════════════════


class TestBeceriBaglamiAl:
    def test_beceri_bulunursa_baglam_doner(self):
        """Beceri bulunduğunda baglam metni dönmeli."""
        with patch("closed_learning_loop._beceri_ara", return_value="Python ile ilgili beceriler"):
            sonuc = _beceri_baglami_al("Python kodu yaz")
            assert "İLGİLİ BECERİLER" in sonuc
            assert "Python" in sonuc

    def test_beceri_bulunamazsa_bos_doner(self):
        """Beceri bulunamadığında boş string dönmeli."""
        with patch("closed_learning_loop._beceri_ara", return_value="beceri bulunamadi"):
            sonuc = _beceri_baglami_al("rastgele metin")
            assert sonuc == ""

    def test_beceri_arama_hatasinda_bos_doner(self):
        """Beceri arama hatasında boş string dönmeli."""
        with patch("closed_learning_loop._beceri_ara", side_effect=Exception("Hata")):
            sonuc = _beceri_baglami_al("test")
            assert sonuc == ""

    def test_beceri_1500_karakter_ustu_kisaltilir(self):
        """Uzun beceri metni 1500 karaktere kısaltılmalı."""
        uzun_beceri = "A" * 2000
        with patch("closed_learning_loop._beceri_ara", return_value=uzun_beceri):
            sonuc = _beceri_baglami_al("test")
            assert "..." in sonuc
            assert len(sonuc) < 1600

    def test_beceri_toplam_kelimeli_yanit_engellenir(self):
        """'toplam' içeren yanıtlar (ör: toplam X beceri) engellenmeli."""
        with patch("closed_learning_loop._beceri_ara", return_value="toplam 5 beceri bulundu"):
            sonuc = _beceri_baglami_al("test")
            assert sonuc == ""

    def test_mesaj_500_karaktere_kisaltilir(self):
        """Mesaj 500 karaktere kısaltılmalı."""
        with patch("closed_learning_loop._beceri_ara") as mock_ara:
            _beceri_baglami_al("X" * 1000)
            # Sorgu max 500 karakter olmalı
            assert len(mock_ara.call_args[0][0]) <= 500


# ═══════════════════════════════════════════════
# _deepseek_sohbet — DEEPSEEK API ÇAĞRISI
# ═══════════════════════════════════════════════


class TestDeepseekSohbet:
    def test_api_anahtari_yoksa_hata_doner(self):
        """API anahtarı yoksa hata mesajı dönmeli."""
        with patch.dict(os.environ, {}, clear=True):
            sonuc = _deepseek_sohbet("test")
            assert "API anahtarı bulunamadı" in sonuc

    def test_basarili_api_cagrisi(self, mock_deepseek_response):
        """Başarılı API çağrısı yanıt dönmeli."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            with patch("requests.post", return_value=mock_deepseek_response):
                sonuc = _deepseek_sohbet("Merhaba")
                assert "Merhaba" in sonuc
                assert "yardımcı" in sonuc

    def test_api_hatasinda_hata_mesaji_doner(self):
        """API hatasında hata mesajı dönmeli."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            with patch("requests.post", side_effect=Exception("Bağlantı hatası")):
                sonuc = _deepseek_sohbet("test")
                assert "API hatası" in sonuc

    def test_api_request_dogru_parametrelerle_cagrilir(self, mock_deepseek_response):
        """API çağrısı doğru URL ve header'larla yapılmalı."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key-123"}, clear=True):
            with patch("requests.post", return_value=mock_deepseek_response) as mock_post:
                _deepseek_sohbet("test mesajı")
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                assert "api.deepseek.com" in args[0]
                assert kwargs["headers"]["Authorization"] == "Bearer test-key-123"
                assert kwargs["json"]["model"] == "deepseek-chat"
                assert kwargs["json"]["messages"][1]["content"] == "test mesajı"

    def test_beceri_baglaminin_eklendigi_kontrolu(self, mock_deepseek_response):
        """Beceri bağlamı API isteğine eklenmeli."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            with patch("requests.post", return_value=mock_deepseek_response) as mock_post:
                with patch("reymen_agent._beceri_baglami_al", return_value="\n\n## İLGİLİ BECERİLER:\ntest becerisi\n"):
                    _deepseek_sohbet("test")
                    system_msg = mock_post.call_args[1]["json"]["messages"][0]["content"]
                    assert "İLGİLİ BECERİLER" in system_msg


# ═══════════════════════════════════════════════
# _agent_loop — AGENT LOOP
# ═══════════════════════════════════════════════


class TestAgentLoop:
    def test_agent_basarili_yanit_dondurur(self, mock_agent):
        """Agent loop başarılı yanıt dönmeli."""
        with patch("reymen_agent._agent_instance", return_value=mock_agent):
            sonuc = _agent_loop("test")
            assert sonuc == "Agent yanıtı"

    def test_agent_yoksa_fallback_cagrilir(self):
        """Agent yoksa fallback çağrılmalı."""
        with patch("reymen_agent._agent_instance", return_value=None):
            with patch("reymen_agent._deepseek_fallback", return_value="Fallback yanıtı"):
                sonuc = _agent_loop("test")
                assert sonuc == "Fallback yanıtı"

    def test_conversation_history_yoksa_last_response_kullanilir(self):
        """Conversation history yoksa last_response kullanılmalı."""
        agent = MagicMock()
        agent.conversation_history = []
        agent.last_response = "Last response"
        with patch("reymen_agent._agent_instance", return_value=agent):
            sonuc = _agent_loop("test")
            assert sonuc == "Last response"

    def test_hic_yanit_yoksa_yanit_ayikla_kullanilir(self):
        """Ne history ne last_response varsa _yanit_ayikla kullanılmalı."""
        agent = MagicMock()
        agent.conversation_history = []
        agent.last_response = ""
        with patch("reymen_agent._agent_instance", return_value=agent):
            with patch("reymen_agent._yanit_ayikla", return_value="Ayıklanan yanıt"):
                sonuc = _agent_loop("test")
                assert sonuc == "Ayıklanan yanıt"

    def test_agent_loop_hatasinda_fallback(self):
        """Agent loop hatasında fallback çağrılmalı."""
        agent = MagicMock()
        agent.run_conversation.side_effect = Exception("Loop hatası")
        with patch("reymen_agent._agent_instance", return_value=agent):
            with patch("reymen_agent._deepseek_fallback", return_value="Hata fallback"):
                sonuc = _agent_loop("test")
                assert sonuc == "Hata fallback"

    def test_yanit_4000_karakterle_sinirlanir(self, mock_agent):
        """Yanıt 4000 karakterle sınırlanmalı."""
        mock_agent.conversation_history = [
            {"role": "assistant", "content": "A" * 5000}
        ]
        with patch("reymen_agent._agent_instance", return_value=mock_agent):
            sonuc = _agent_loop("test")
            assert len(sonuc) <= 4000


# ═══════════════════════════════════════════════
# _yanit_ayikla — YANIT AYIKLAMA
# ═══════════════════════════════════════════════


class TestYanitAyikla:
    def test_tamamlandi_markoru_algilanir(self):
        """[TAMAMLANDI] markörü algılanmalı."""
        cikti = "bazı satırlar\n[TAMAMLANDI] Görev başarıyla tamamlandı\nbaşka satır"
        sonuc = _yanit_ayikla(cikti)
        assert sonuc == "Görev başarıyla tamamlandı"

    def test_sonuc_markoru_algilanir(self):
        """[SONUC] markörü algılanmalı."""
        cikti = "[SONUC] API başarılı"
        sonuc = _yanit_ayikla(cikti)
        assert sonuc == "API başarılı"

    def test_yanit_markoru_algilanir(self):
        """[YANIT] markörü algılanmalı."""
        cikti = "[YANIT] Merhaba dünya"
        sonuc = _yanit_ayikla(cikti)
        assert sonuc == "Merhaba dünya"

    def test_markor_onceligi_tamamlandi_en_ustte(self):
        """[TAMAMLANDI] en yüksek önceliğe sahip olmalı."""
        cikti = "[SONUC] sonuc\n[TAMAMLANDI] tamamlandi\n[YANIT] yanit"
        sonuc = _yanit_ayikla(cikti)
        assert sonuc == "tamamlandi"

    def test_markor_yoksa_en_uzun_satir_alinir(self):
        """Markör yoksa son 5 satırdan en uzun içerikli satır alınmalı."""
        cikti = "kısa\n---\n===\n[Bütçe 10]\n--- TUR 1\nPlugin yuklendi\nINFO: test\nBu en uzun içerikli satırdır ve seçilmelidir"
        sonuc = _yanit_ayikla(cikti)
        assert sonuc == "Bu en uzun içerikli satırdır ve seçilmelidir"

    def test_tum_satirlar_filtrelenirse_en_son_satir_alinir(self):
        """Tüm son satırlar filtrelenirse en son satır alınmalı."""
        cikti = "---\n===\n[Budget]\n--- TUR 1\nPlugin"
        sonuc = _yanit_ayikla(cikti)
        assert sonuc == "Plugin"

    def test_bos_cikti_bos_dondurur(self):
        """Boş çıktı boş string dönmeli."""
        assert _yanit_ayikla("") == ""

    def test_kisa_markor_iceriği_engellenir(self):
        """3 karakterden kısa markör içeriği engellenmeli."""
        cikti = "[TAMAMLANDI] ab"
        sonuc = _yanit_ayikla(cikti)
        # 3'ten kısa olduğu için markör atlanır, son satıra düşer
        assert sonuc == "[TAMAMLANDI] ab"


# ═══════════════════════════════════════════════
# _deepseek_fallback — FALLBACK
# ═══════════════════════════════════════════════


class TestDeepseekFallback:
    def test_fallback_api_anahtari_yoksa_hata(self):
        """Fallback'te API anahtarı yoksa hata dönmeli."""
        with patch.dict(os.environ, {}, clear=True):
            sonuc = _deepseek_fallback("test")
            assert "API anahtarı" in sonuc

    def test_fallback_basarili_yanit(self, mock_deepseek_response):
        """Fallback başarılı yanıt dönmeli."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            with patch("requests.post", return_value=mock_deepseek_response):
                sonuc = _deepseek_fallback("test")
                assert "Merhaba" in sonuc

    def test_fallback_hatasinda_hata_mesaji(self):
        """Fallback hatasında hata mesajı dönmeli."""
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}, clear=True):
            with patch("requests.post", side_effect=Exception("Hata")):
                sonuc = _deepseek_fallback("test")
                assert "API hatası" in sonuc


# ═══════════════════════════════════════════════
# _format_temizle — FORMAT TEMİZLEME
# ═══════════════════════════════════════════════


class TestFormatTemizle:
    def test_cift_backtick_ucluye_cevrilir(self):
        """Çift backtick + dil üçlü backtick'e çevrilmeli."""
        sonuc = _format_temizle("``python\nprint('hello')\n``")
        assert "```python" in sonuc

    def test_tek_backtick_kapanis_duzeltilir(self):
        """Kod bloğu sonunda tek backtick düzeltilmeli."""
        sonuc = _format_temizle("```python\nprint('hello')\n`")
        assert sonuc.endswith("```")

    def test_satir_basi_tek_backtick_uclu_yapilir(self):
        """Satır başı tek backtick üçlü yapılmalı."""
        sonuc = _format_temizle("` kod bloğu")
        assert sonuc.startswith("```")

    def test_4_arti_backtick_3_yapilir(self):
        """4+ backtick 3'e düşürülmeli."""
        sonuc = _format_temizle("````python")
        assert sonuc == "```python"

    def test_kod_satirlari_bloklanir(self):
        """2+ ardışık Python satırı bloklanmalı."""
        metin = "def test():\n    pass\n"
        sonuc = _format_temizle(metin)
        assert "```python" in sonuc

    def test_normal_metin_degismez(self):
        """Normal metin değişmemeli."""
        metin = "Merhaba dünya, nasılsın?"
        sonuc = _format_temizle(metin)
        assert sonuc == metin

    def test_kod_icinde_kod_karismaz(self):
        """Kod bloğu içinde tekrar bloklama yapılmamalı."""
        metin = "```python\ndef test():\n    pass\n```\nNormal metin"
        sonuc = _format_temizle(metin)
        # Kod bloğu içeriği değişmemeli
        assert "```python" in sonuc


# ═══════════════════════════════════════════════
# isleyen_gorev — ANA İŞLEV
# ═══════════════════════════════════════════════


class TestIsleyenGorev:
    def test_varsayilan_deepseek_kullanir(self):
        """Varsayılan olarak _deepseek_sohbet kullanılmalı."""
        with patch("reymen_agent._deepseek_sohbet", return_value="Hızlı yanıt"):
            sonuc = isleyen_gorev("test")
            assert sonuc == "Hızlı yanıt"

    def test_use_agent_true_ise_agent_loop_kullanir(self):
        """use_agent=True ise _agent_loop kullanılmalı."""
        with patch("reymen_agent._agent_loop", return_value="Agent yanıtı"):
            sonuc = isleyen_gorev("test", use_agent=True)
            assert sonuc == "Agent yanıtı"

    def test_bos_mesaj_cagrisi(self):
        """Boş mesaj ile çağrı yapılabilmeli."""
        with patch("reymen_agent._deepseek_sohbet", return_value=""):
            sonuc = isleyen_gorev("")
            assert sonuc == ""

    def test_chat_id_parametresi_iletilir(self):
        """chat_id parametresi ile çağrı yapılabilmeli."""
        with patch("reymen_agent._deepseek_sohbet", return_value="Yanıt"):
            sonuc = isleyen_gorev("test", chat_id="12345")
            assert sonuc == "Yanıt"


# ═══════════════════════════════════════════════
# kopru_deepseek_istek — KÖPRÜ ENTEGRASYONU
# ═══════════════════════════════════════════════


class TestKopruDeepseekIstek:
    def test_kopru_cagrisi_isleyen_goreva_yonlendirir(self):
        """kopru_deepseek_istek isleyen_gorev'i çağırmalı."""
        with patch("reymen_agent.isleyen_gorev", return_value="Köprü yanıtı") as mock_isleyen:
            sonuc = kopru_deepseek_istek("test mesaj")
            assert sonuc == "Köprü yanıtı"
            mock_isleyen.assert_called_once_with("test mesaj", chat_id="kopru")

    def test_kopru_bos_mesaj(self):
        """Köprü boş mesajla çağrılabilmeli."""
        with patch("reymen_agent.isleyen_gorev", return_value=""):
            sonuc = kopru_deepseek_istek("")
            assert sonuc == ""
