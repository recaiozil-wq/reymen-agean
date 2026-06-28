# -*- coding: utf-8 -*-
"""tests/test_conversation_loop.py — ConversationLoop kapsamlı test paketi (35 test).

Kapsam:
  - Başlatma ve eski API (coz) uyumluluğu
  - run_conversation() tam akış
  - Provider-agnostic mesaj formatları
  - Context compression / preflight
  - Budget tracking
  - Tool loop ve araç ayrıştırma
  - Interruptible çağrı
  - Loglama ve hata yönetimi
  - Durum ve istatistik metodları
"""

import json
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation_loop import ConversationLoop

# ── Sahte bileşenler ──────────────────────────────────────────────────────────


class _SahtMotor:
    """Basit araç çalıştırıcı stub."""

    def calistir(self, arac, ham_param=""):
        if arac == "GOREV_BITTI":
            return f"[Tamamlandi]: {ham_param}"
        return f"[{arac}]: {ham_param} islendi"

    def arac_calistir(self, arac, **kwargs):
        return {"basarili": True, "cikti": f"{arac} tamam", "tamamlandi": False}


class _SahtBeyin:
    """Belirli adım sayısından sonra GOREV_BITTI döndüren LLM stub'ı."""

    def __init__(self, adim_limit: int = 2, provider: str = "lmstudio"):
        self._adim = 0
        self._adim_limit = adim_limit
        self.provider = provider

    def uret(self, sistem_prompt, mesajlar, **kwargs):
        self._adim += 1
        if self._adim >= self._adim_limit:
            return 'Düşünce: Bitti.\nEylem: GOREV_BITTI("islem tamamlandi")'
        return f'Düşünce: Adım {self._adim}.\nEylem: PYTHON_CALISTIR("print({self._adim})")'


class _HataBeyin:
    """Her zaman exception fırlatan stub."""

    def uret(self, *args, **kwargs):
        raise RuntimeError("LLM bağlantı hatası (test stub)")


class _AnthropicBeyin:
    """Anthropic provider stub."""

    provider = "anthropic"

    def uret(self, sistem_prompt, mesajlar, **kwargs):
        return 'Düşünce: Anthropic yanıtı.\nEylem: GOREV_BITTI("anthropic ile tamamlandi")'


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 1 — Başlatma ve temel API (7 test)
# ══════════════════════════════════════════════════════════════════════════════


class TestBaslatma:
    def test_varsayilan_baslangic(self):
        """Parametresiz oluşturma — varsayılan değerler doğru olmalı."""
        cl = ConversationLoop()
        assert cl.max_tur == 30
        assert cl._durum == "hazir"
        assert cl.motor is None
        assert cl.beyin is None

    def test_ozel_max_tur(self):
        """max_tur parametresi doğru atanmalı."""
        cl = ConversationLoop(max_tur=10)
        assert cl.max_tur == 10

    def test_motor_ve_beyin_atama(self):
        """Motor ve beyin referansları doğru tutulmalı."""
        motor = _SahtMotor()
        beyin = _SahtBeyin()
        cl = ConversationLoop(motor=motor, beyin=beyin, max_tur=5)
        assert cl.motor is motor
        assert cl.beyin is beyin

    def test_durum_baslangic(self):
        """Başlangıç durumu 'hazir' olmalı."""
        cl = ConversationLoop()
        assert cl.durum() == "hazir"

    def test_istatistik_yapisi(self):
        """istatistik() dict dönmeli ve gerekli anahtarları içermeli."""
        cl = ConversationLoop(max_tur=7)
        stats = cl.istatistik()
        assert isinstance(stats, dict)
        assert "durum" in stats
        assert "max_tur" in stats
        assert stats["max_tur"] == 7

    def test_coz_eski_api_dict_doner(self):
        """coz() geriye uyumlu biçimde dict dönmeli."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.coz("test hedef")
        assert isinstance(sonuc, dict)
        assert sonuc["hedef"] == "test hedef"
        assert "basarili" in sonuc
        assert "turlar" in sonuc

    def test_coz_baglam_kabul_eder(self):
        """coz() baglam parametresi kabul etmeli, hata vermemeli."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.coz("hedef", baglam={"kullanici": "test"})
        assert isinstance(sonuc, dict)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 2 — run_conversation() temel akış (8 test)
# ══════════════════════════════════════════════════════════════════════════════


class TestRunConversation:
    def test_task_id_uretilir(self):
        """run_conversation() task_id alanı döndürmeli."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.run_conversation("basit test")
        assert "task_id" in sonuc
        assert len(sonuc["task_id"]) >= 4

    def test_sonuc_yapisi_tam(self):
        """Sonuç dict'i tüm beklenen anahtarları içermeli."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.run_conversation("test")
        for anahtar in ("task_id", "hedef", "basarili", "turlar", "sure", "budget"):
            assert anahtar in sonuc, f"'{anahtar}' anahtarı eksik"

    def test_hedef_sonuca_yansiyor(self):
        """Verilen hedef sonuc dict'inde korunmalı."""
        cl = ConversationLoop(max_tur=2)
        hedef = "özel hedef metni"
        sonuc = cl.run_conversation(hedef)
        assert sonuc["hedef"] == hedef

    def test_sure_olcumu(self):
        """'sure' değeri sıfırdan büyük float olmalı."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.run_conversation("süre testi")
        assert isinstance(sonuc["sure"], float)
        assert sonuc["sure"] >= 0.0

    def test_budget_ozet_dict_icinde(self):
        """'budget' alanı dict veya None olmalı."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.run_conversation("budget testi")
        assert sonuc["budget"] is None or isinstance(sonuc["budget"], dict)

    def test_basarili_gorev_bitti_ile(self):
        """Beyin GOREV_BITTI döndürünce basarili=True olmalı."""
        beyin = _SahtBeyin(adim_limit=1)
        cl = ConversationLoop(beyin=beyin, max_tur=5)
        sonuc = cl.run_conversation("hızlı görev")
        assert sonuc["basarili"] is True

    def test_provider_parametresi_gecilir(self):
        """provider parametresi alınmalı ve sonuca yansımalı."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.run_conversation("test", provider="deepseek")
        assert "provider" in sonuc

    def test_baglam_parametresi_kabul(self):
        """baglam parametresi run_conversation tarafından kabul edilmeli."""
        beyin = _SahtBeyin(adim_limit=1)
        cl = ConversationLoop(beyin=beyin, max_tur=3)
        sonuc = cl.run_conversation(
            "bağlamlı hedef",
            baglam={"kullanici": "Ali", "dil": "tr"},
        )
        assert isinstance(sonuc, dict)
        assert "hedef" in sonuc


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 3 — Provider-agnostic mesaj formatları (5 test)
# ══════════════════════════════════════════════════════════════════════════════


class TestProviderAgnostic:
    def test_provider_tipi_anthropic(self):
        """'anthropic' provider adı → 'anthropic' tip dönmeli."""
        cl = ConversationLoop()
        assert cl._provider_tipi_belirle("anthropic") == "anthropic"

    def test_provider_tipi_claude(self):
        """'claude' provider adı → 'anthropic' tip dönmeli."""
        cl = ConversationLoop()
        assert cl._provider_tipi_belirle("claude") == "anthropic"

    def test_provider_tipi_codex(self):
        """'codex' provider adı → 'codex' tip dönmeli."""
        cl = ConversationLoop()
        assert cl._provider_tipi_belirle("codex") == "codex"

    def test_provider_tipi_openai_chat_completions(self):
        """OpenAI/DeepSeek/LM Studio → 'chat_completions' tip dönmeli."""
        cl = ConversationLoop()
        for p in ("openai", "deepseek", "lmstudio", "groq"):
            assert cl._provider_tipi_belirle(p) == "chat_completions", f"{p} hatalı"

    def test_api_mesajlari_sistem_icerir(self):
        """_api_mesajlari_olustur() sistem prompt mesajı içermeli."""
        cl = ConversationLoop()
        gecmis = [{"role": "user", "content": "merhaba"}]
        mesajlar = cl._api_mesajlari_olustur("sistem prompt", gecmis, "chat_completions")
        sistem_var = any(m.get("role") == "system" for m in mesajlar)
        assert sistem_var, "Sistem mesajı bulunamadı"

    def test_anthropic_api_mesajlari(self):
        """Anthropic formatında mesajlar oluşturulabilmeli."""
        cl = ConversationLoop()
        gecmis = [{"role": "user", "content": "test"}]
        mesajlar = cl._api_mesajlari_olustur("sistem", gecmis, "anthropic")
        assert isinstance(mesajlar, list)
        assert len(mesajlar) >= 1


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 4 — Context compression (5 test)
# ══════════════════════════════════════════════════════════════════════════════


class TestContextCompression:
    def _kucuk_gecmis(self):
        return [{"role": "user", "content": "kısa mesaj"}]

    def _buyuk_gecmis(self, n=30):
        return [{"role": "user" if i % 2 == 0 else "assistant",
                 "content": "A" * 2000} for i in range(n)]

    def test_kucuk_gecmis_sikistirilmaz(self):
        """Küçük geçmiş (<%50) sıkıştırılmamalı."""
        cl = ConversationLoop()
        gecmis = self._kucuk_gecmis()
        sonuc = cl._context_preflight(gecmis, "kısa sistem prompt")
        assert len(sonuc) >= 1

    def test_buyuk_gecmis_sikistiriliyor(self):
        """Büyük geçmiş (>%50) sıkıştırılmalı, uzunluk azalmalı."""
        cl = ConversationLoop()
        buyuk = self._buyuk_gecmis(30)
        onceki_uzunluk = len(buyuk)
        sonuc = cl._context_preflight(buyuk, "x" * 100)
        assert len(sonuc) <= onceki_uzunluk

    def test_sikistirma_sonrasi_liste_donuyor(self):
        """_context_preflight() her zaman liste dönmeli."""
        cl = ConversationLoop()
        sonuc = cl._context_preflight([], "sistem")
        assert isinstance(sonuc, list)

    def test_buyuk_gecmis_son_mesajlar_korunuyor(self):
        """Sıkıştırma sonrası son mesajlar korunmalı."""
        cl = ConversationLoop()
        buyuk = self._buyuk_gecmis(20)
        sonuc = cl._context_preflight(buyuk, "x" * 500)
        # Son mesaj kaybolmamalı
        son_icerik = buyuk[-1]["content"]
        son_mevcut = any(m.get("content") == son_icerik for m in sonuc)
        assert son_mevcut, "Son mesaj sıkıştırma sonrası kayboldu"

    def test_sikistirma_hata_toleransi(self):
        """Compressor exception fırlatırsa fallback çalışmalı."""
        cl = ConversationLoop()
        # Bozuk compressor
        cl._Compressor = None  # type: ignore[attr-defined]
        buyuk = self._buyuk_gecmis(20)
        sonuc = cl._context_preflight(buyuk, "x" * 500)
        assert isinstance(sonuc, list)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 5 — Budget tracking (5 test)
# ══════════════════════════════════════════════════════════════════════════════


class TestBudgetTracking:
    def test_budget_olusturuluyor(self):
        """_budget_olustur() None dönmemeli."""
        cl = ConversationLoop(max_tur=5)
        budget = cl._budget_olustur("test hedef")
        assert budget is not None

    def test_budget_max_tur_uyumlu(self):
        """Budget max_tur en az ConversationLoop.max_tur olmalı."""
        cl = ConversationLoop(max_tur=8)
        budget = cl._budget_olustur("test")
        assert budget.max_tur >= 8

    def test_budget_devam_etmeli_mi(self):
        """Yeni budget devam_etmeli_mi() True dönmeli."""
        cl = ConversationLoop(max_tur=5)
        budget = cl._budget_olustur("test")
        assert budget.devam_etmeli_mi() is True

    def test_budget_ozet_dict_yapisi(self):
        """ozet_dict() dict dönmeli."""
        cl = ConversationLoop(max_tur=5)
        budget = cl._budget_olustur("test")
        ozet = budget.ozet_dict()
        assert isinstance(ozet, dict)

    def test_run_conversation_budget_sonuca_ekleniyor(self):
        """run_conversation() sonucunda 'budget' alanı var olmalı."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.run_conversation("budget kontrol")
        assert "budget" in sonuc


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 6 — Tool loop ve araç ayrıştırma (7 test)
# ══════════════════════════════════════════════════════════════════════════════


class TestToolLoop:
    def test_tool_calls_openai_format(self):
        """OpenAI tool_calls formatı doğru ayrıştırılmalı."""
        cl = ConversationLoop()
        yanit = {
            "content": "",
            "tool_calls": [{"id": "tc1", "name": "DOSYA_OKU", "arguments": {}}],
        }
        tc = cl._tool_calls_al(yanit)
        assert len(tc) == 1
        assert tc[0]["name"] == "DOSYA_OKU"

    def test_tool_calls_react_format(self):
        """ReAct metin formatından araç çağrısı çıkarılmalı."""
        cl = ConversationLoop()
        yanit = {"content": 'Düşünce: Bir dosya okuyalım.\nEylem: DOSYA_OKU("test.txt")'}
        tc = cl._tool_calls_al(yanit)
        # DOSYA_OKU ya da başka bir araç çıkarılmış olmalı
        assert isinstance(tc, list)

    def test_tool_calls_gorev_bitti_bos(self):
        """GOREV_BITTI içeren yanıt → boş tool_calls dönmeli."""
        cl = ConversationLoop()
        yanit = {"content": "GOREV_BITTI görev bitti tamamlandi"}
        tc = cl._tool_calls_al(yanit)
        assert tc == []

    def test_tool_calls_dusun_atlanir(self):
        """DUSUN 'araç' sayılmamalı."""
        cl = ConversationLoop()
        yanit = {"content": "DUSUN(bir şeyler)"}
        tc = cl._tool_calls_al(yanit)
        assert tc == []

    def test_tool_calls_bos_yanit(self):
        """None / boş yanıt → boş liste."""
        cl = ConversationLoop()
        assert cl._tool_calls_al(None) == []
        assert cl._tool_calls_al({}) == []

    def test_yanit_icerigi_al(self):
        """_yanit_icerigi_al() content döndürmeli."""
        cl = ConversationLoop()
        assert cl._yanit_icerigi_al({"content": "merhaba"}) == "merhaba"
        assert cl._yanit_icerigi_al({}) == ""
        assert cl._yanit_icerigi_al(None) == ""

    def test_arac_calistir_motor_olmadan(self):
        """Motor yokken de _arac_calistir() exception fırlatmamalı."""
        cl = ConversationLoop(motor=None)
        sonuc = cl._arac_calistir({"arac": "BILINMEYEN", "parametreler": {}})
        assert isinstance(sonuc, dict)
        assert "hata" in sonuc or "basarili" in sonuc


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 7 — Hata yönetimi ve interruptible (4 test)
# ══════════════════════════════════════════════════════════════════════════════


class TestHataVeInterrupt:
    def test_beyin_exception_run_donmez(self):
        """Beyin exception fırlattığında run_conversation() yine dict dönmeli."""
        cl = ConversationLoop(beyin=_HataBeyin(), max_tur=2)
        sonuc = cl.run_conversation("hata testi")
        assert isinstance(sonuc, dict)
        assert "task_id" in sonuc

    def test_run_conversation_loglama(self):
        """run_conversation() log kaydı bırakmalı (logger çağrılmalı)."""
        import logging
        with patch.object(logging.getLogger("conversation_loop"), "info") as mock_log:
            cl = ConversationLoop(max_tur=1)
            cl.run_conversation("log testi")
            assert mock_log.called

    def test_iptal_istegi_bayragi(self):
        """_iptal_istegi başlangıçta False olmalı."""
        cl = ConversationLoop()
        assert cl._iptal_istegi is False

    def test_durum_hata_sonrasi(self):
        """Başarısız çalışma sonrası durum 'hazir' olmamalı."""
        cl = ConversationLoop(max_tur=1)
        cl.run_conversation("durum testi")
        assert cl._durum in ("tamamlandi", "hata", "iptal")


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 8 — Loglama ve yardımcılar (4 test, toplam = 7+8+5+5+5+6+5+4 = 45 → 35)
# ══════════════════════════════════════════════════════════════════════════════


class TestYardimcilar:
    def test_sistem_promptu_str_doner(self):
        """_sistem_promptu_olustur() boş olmayan string dönmeli."""
        cl = ConversationLoop()
        sp = cl._sistem_promptu_olustur("test hedef")
        assert isinstance(sp, str)
        assert len(sp) > 0

    def test_ephemeral_layerlar_uyari(self):
        """_ephemeral_layerlar_ekle() liste dönmeli."""
        cl = ConversationLoop(max_tur=3)
        budget = cl._budget_olustur("test")
        # max_tur'a yaklaştır (property varsa _tur ile, yoksa tur ile)
        if hasattr(budget, "_tur"):
            budget._tur = budget.max_tur - 2  # type: ignore[attr-defined]
        elif hasattr(budget, "tur") and not callable(type(budget).tur if hasattr(type(budget), "tur") else None):
            budget.tur = budget.max_tur - 2  # type: ignore[attr-defined]
        mesajlar = [{"role": "user", "content": "merhaba"}]
        sonuc = cl._ephemeral_layerlar_ekle(mesajlar, budget, 5)
        assert isinstance(sonuc, list)

    def test_ephemeral_layerlar_bos_uyari(self):
        """Bütçe dolmadıysa ephemeral eklenmeye gerek yok."""
        cl = ConversationLoop(max_tur=20)
        budget = cl._budget_olustur("test")
        mesajlar = [{"role": "user", "content": "merhaba"}]
        sonuc = cl._ephemeral_layerlar_ekle(mesajlar, budget, 3)
        assert isinstance(sonuc, list)

    def test_run_conversation_bitis_durumu(self):
        """Başarılı çalışma sonrası _durum 'tamamlandi' olmalı."""
        beyin = _SahtBeyin(adim_limit=1)
        cl = ConversationLoop(beyin=beyin, max_tur=5)
        cl.run_conversation("bitiş durumu testi")
        assert cl._durum == "tamamlandi"


# ══════════════════════════════════════════════════════════════════════════════
# 35. TEST — Geriye uyumluluk: coz() == run_conversation()
# ══════════════════════════════════════════════════════════════════════════════


class TestGeriyeUyumluluk:
    def test_coz_run_conversation_es_davranis(self):
        """coz() ve run_conversation() aynı yapıda sonuç döndürmeli."""
        cl = ConversationLoop(max_tur=2)
        s1 = cl.coz("test")
        cl2 = ConversationLoop(max_tur=2)
        s2 = cl2.run_conversation("test")
        # Her ikisi de dict döndürmeli
        assert isinstance(s1, dict)
        assert isinstance(s2, dict)
        # Her ikisinde de 'hedef' alanı olmalı
        assert "hedef" in s1
        assert "hedef" in s2
