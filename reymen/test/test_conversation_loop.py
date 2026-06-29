"""
test_conversation_loop.py — ReYMeN run_conversation() 18 aşama testi
====================================================================

Her aşama izole test edilir. Mock motor/beyin ile ConversationLoop
instantiate edilir, run_conversation() her adımı doğrulanır.

Kullanım:  pytest reymen/test/test_conversation_loop.py -v
"""

import json
import os
import sys
import time
import uuid
import logging
from typing import Any, Dict, Optional, List
from unittest.mock import MagicMock, patch, PropertyMock

# ── Proje root'u ekle ──────────────────────────────────────────────
PROJE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJE_ROOT not in sys.path:
    sys.path.insert(0, PROJE_ROOT)

logging.disable(logging.CRITICAL)  # Testlerde log gürültüsü yok

# ── Test sabitleri ──────────────────────────────────────────────────
TEST_HEDEF = "test hedef mesaji"

# ====================================================================
# OTOMATIK FIXTURE: tüm testlerde OnceHafiza'yı devre dışı bırak
# ====================================================================
import pytest

@pytest.fixture(autouse=True)
def _hafiza_mock():
    """Her testten önce OnceHafiza'yı mock'la (DB bağımlılığını kaldır)."""
    with patch("reymen.cereyan.conversation_loop._hafizada_ara",
               return_value={"guven": 0.0, "yanit": ""}):
        yield

# ====================================================================
# YARDIMCI: budget mock factory
# ====================================================================
def _mock_budget(devam=True, tur_sayisi=0):
    """Standart budget mock'u olustur"""
    _bitti = [not devam]  # mutable closure
    
    class _MockBudget:
        def __init__(self):
            self.tur = tur_sayisi
            self.max_tur = 30
            self.kalan_butce = 25
            self._kalan_butce = 25
            self.kalan_eylem = 20
            self.kaldi = 25
        
        def devam_etmeli_mi(self):
            return not _bitti[0]
        
        def gorev_tamamla(self):
            _bitti[0] = True
        
        def tur_basla(self):
            self.tur += 1
        
        def tur_bitir(self, basarili=True, **kw):
            pass
        
        def eylem_kaydet(self, _):
            pass
        
        def ozet_dict(self):
            return {"tur": self.tur, "max_tur": self.max_tur}
    
    return _MockBudget()


# ====================================================================
# ADIM 1: task_id üret (UUID → 8 karakter)
# ====================================================================
def test_adim1_task_id_olusturma():
    """ADIM 1: task_id = uuid4()[:8] kontrol"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=False))

    sonuc = loop.run_conversation(hedef=TEST_HEDEF)
    assert "task_id" in sonuc, "task_id eksik"
    assert len(sonuc["task_id"]) == 8, f"task_id 8 karakter olmali: {sonuc['task_id']}"
    print(f"  ✅ task_id: {sonuc['task_id']}")


# ====================================================================
# ADIM 2: Session başlat (session_db'ye kayıt + hook)
# ====================================================================
def test_adim2_session_baslatma():
    """ADIM 2: SessionStorage.session_baslat() cagrilmali"""
    with patch("reymen.cereyan.conversation_loop._SESSION_AKTIF", True):
        with patch("reymen.cereyan.conversation_loop._HOOK_AKTIF", False):
            with patch("reymen.cereyan.conversation_loop._SessionStorage") as mock_storage:
                mock_instance = MagicMock()
                session_id = "test-session-42"
                mock_instance.session_baslat.return_value = session_id
                mock_storage.return_value = mock_instance

                from reymen.cereyan.conversation_loop import ConversationLoop
                loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock(provider="deepseek"))
                loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=False))

                sonuc = loop.run_conversation(hedef=TEST_HEDEF)
                assert mock_instance.session_baslat.called, "session_baslat() cagrilmadi"
                assert sonuc.get("session_id") == session_id, f"session_id eslesmiyor"
                print(f"  ✅ Session baslatildi: {session_id}")


# ====================================================================
# ADIM 3: Hafıza kontrolü — guven > 0.8 → LLM atla
# ====================================================================
def test_adim3_hafiza_atlama():
    """ADIM 3: guven_skoru > 0.8 ise LLM atlanir, direkt yanit doner"""
    with patch("reymen.cereyan.conversation_loop._hafizada_ara") as mock_hafiza:
        mock_hafiza.return_value = {
            "guven": 0.95,
            "yanit": "Test hafiza yaniti",
            "kaynak": "test",
        }

        from reymen.cereyan.conversation_loop import ConversationLoop
        loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
        loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=False))

        sonuc = loop.run_conversation(hedef=TEST_HEDEF)
        assert sonuc.get("basarili"), "basarili=True olmali"
        assert sonuc.get("kaynak") == "once_hafiza", "once_hafiza kaynagi olmali"
        assert "Test hafiza" in sonuc.get("yanit", ""), "hafiza yaniti icerilmeli"
        assert sonuc.get("tur") == 0, "LLM cagrilmamali (tur=0)"
        print(f"  ✅ Hafiza atlamasi: guven=0.95, tur=0, maliyet=0")


# ====================================================================
# ADIM 4: Belirsiz görev önerisi (oneri_uret)
# ====================================================================
def test_adim4_belirsiz_gorev_oneri():
    """ADIM 4: Hafizada bulunamadiysa oneri uret"""
    with patch("reymen.cereyan.conversation_loop.ConversationLoop._oneri_uret") as mock_oneri:
        mock_oneri.return_value = "Sanirim test_kategori ile ilgili bir sey istiyorsun, dogru mu?"

        from reymen.cereyan.conversation_loop import ConversationLoop
        loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
        loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=False))

        sonuc = loop.run_conversation(hedef="belirsiz")
        assert sonuc.get("kaynak") == "oneri_uret", "oneri_uret kaynagi olmali"
        assert "Sanirim" in sonuc.get("oneri", ""), "oneri mesaji icermeli"
        assert sonuc.get("tur") == 0, "tur=0 olmali"
        print(f"  ✅ Oneri uretildi: {sonuc['oneri'][:50]}")


# ====================================================================
# ADIM 5: Konuşma geçmişi (önceki session'dan son 10 mesaj)
# ====================================================================
def test_adim5_konusma_gecmisi():
    """ADIM 5: _gecmis_mesajlar yeni konusmaya eklenmeli"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    # Önceki mesajları simüle et
    loop._gecmis_mesajlar = [
        {"role": "user", "content": "onceki soru"},
        {"role": "assistant", "content": "onceki cevap"},
    ]
    loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=False))

    sonuc = loop.run_conversation(hedef=TEST_HEDEF)
    # En az 1 mesaj (hedef) eklenmis olmali
    assert len(loop._konusma_gecmisi) > 0, "konusma gecmisi bos"
    # Son mesaj hedef olmali
    assert loop._konusma_gecmisi[-1]["content"] == TEST_HEDEF, "son mesaj hedef degil"
    print(f"  ✅ Konusma gecmisi: {len(loop._konusma_gecmisi)} mesaj")


# ====================================================================
# ADIM 6: Cache kontrolü (ONCELIK_CACHE)
# ====================================================================
def test_adim6_cache_kontrol():
    """ADIM 6: ONCELIK_CACHE eslesmesi → LLM atlanir"""
    with patch("reymen.cereyan.conversation_loop._hafizada_ara") as mock_hafiza:
        # Hafiza bos - cache kontrolune gececek
        mock_hafiza.return_value = {"guven": 0.0, "yanit": ""}

        from reymen.cereyan.conversation_loop import ConversationLoop, ONCELIK_CACHE

        for anahtar, beklendik_yanit in list(ONCELIK_CACHE.items())[:3]:
            loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
            loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=False))

            sonuc = loop.run_conversation(hedef=anahtar)
            assert sonuc.get("kaynak") == "oncelik_cache", f"'{anahtar}' cache atlamamali (kaynak={sonuc.get('kaynak')})"
            assert sonuc.get("tur") == 0, f"'{anahtar}' tur=0 olmali"
            assert sonuc.get("yanit") == beklendik_yanit, f"'{anahtar}' cache yaniti yanlis"
            print(f"  ✅ Cache: '{anahtar}' → {beklendik_yanit[:30]}...")


# ====================================================================
# ADIM 7: Sistem prompt
# ====================================================================
def test_adim7_sistem_prompt():
    """ADIM 7: sistem_prompt_al() fallback calismali"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    prompt = loop._sistem_promptu_olustur(TEST_HEDEF)
    assert prompt, "sistem prompt bos"
    assert isinstance(prompt, str), "sistem prompt string degil"
    assert len(prompt) > 10, "sistem prompt cok kisa"
    print(f"  ✅ Sistem prompt: {len(prompt)} chars")


# ====================================================================
# ADIM 8: Context preflight (>%50 → sıkıştır)
# ====================================================================
def test_adim8_context_preflight():
    """ADIM 8: context doluluk kontrolu calismali"""
    from reymen.cereyan.conversation_loop import ConversationLoop
    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())

    # Dusuk doluluk - sikistirma yapilmamali
    mesajlar_kucuk = [{"role": "user", "content": "kisa mesaj"}]
    sonuc = loop._context_preflight(mesajlar_kucuk, "sistem_prompt", "deepseek")
    assert sonuc is not None, "context preflight sonuc vermedi"
    # Yuksek doluluk - sikistirma calismali
    assert len(sonuc) > 0, "mesaj sayisi 0 olmamali"
    print(f"  ✅ Context preflight calisiyor: {len(mesajlar_kucuk)} mesaj")


# ====================================================================
# ADIM 9: Ephemeral layer (bütçe uyarısı)
# ====================================================================
def test_adim9_ephemeral_layer():
    """ADIM 9: ephemeral layer (butce uyarisi) eklenmeli"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    # Gercek budget gibi davranan mock
    budget = MagicMock()
    budget.tur = 5
    budget.max_tur = 30
    budget.kaldi = 25  # _ephemeral_layerlar_ekle getattr(budget, 'kaldi', None) ile okur
    budget.kalan_butce = 25
    budget._kalan_butce = 25
    budget.kalan_eylem = 20
    api_mesajlari = [{"role": "user", "content": "test"}]
    sonuc = loop._ephemeral_layerlar_ekle(api_mesajlari, budget, 10)
    assert sonuc is not None, "ephemeral layer sonuc vermedi"
    assert len(sonuc) > 0, "ephemeral layer mesaj eklemeli"
    print(f"  ✅ Ephemeral layer: {len(sonuc)} mesaj")


# ====================================================================
# ADIM 10: API call
# ====================================================================
def test_adim10_api_call():
    """ADIM 10: _api_call_with_retry cagrilmali (mock)"""
    with patch("reymen.cereyan.conversation_loop._hafizada_ara") as mock_hf:
        mock_hf.return_value = {"guven": 0.0, "yanit": ""}

        from reymen.cereyan.conversation_loop import ConversationLoop
        loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
        loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=True))
        loop._sistem_promptu_olustur = MagicMock(return_value="test prompt")
        loop._api_mesajlari_olustur = MagicMock(return_value=[])
        loop._ephemeral_layerlar_ekle = MagicMock(return_value=[])
        loop._context_preflight = MagicMock(return_value=[])
        loop._api_call_with_retry = MagicMock(return_value={
            "choices": [{"message": {"content": "test yanit", "role": "assistant"}}]
        })
        loop._tool_calls_al = MagicMock(return_value=[])
        loop._yanit_icerigi_al = MagicMock(return_value="test yanit")

        sonuc = loop.run_conversation(hedef=TEST_HEDEF)
        assert loop._api_call_with_retry.called, "_api_call_with_retry cagrilmadi"
        assert sonuc.get("basarili"), "basarili=False"
        print(f"  ✅ API call (mock): basarili=True, tur={sonuc.get('turlar')}")


# ====================================================================
# ADIM 11: Tool loop
# ====================================================================
def test_adim11_tool_loop():
    """ADIM 11: tool_calls varsa -> _arac_calistir -> tekrar LLM"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())

    # _tool_calls_al'in tool dondurmesini sagla
    loop._tool_calls_al = MagicMock(return_value=[{
        "id": "call_123",
        "type": "function",
        "function": {
            "name": "test_tool",
            "arguments": json.dumps({"param": "test"}),
        }
    }])

    loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=True, tur_sayisi=1))
    loop._sistem_promptu_olustur = MagicMock(return_value="test prompt")
    loop._api_mesajlari_olustur = MagicMock(return_value=[])
    loop._ephemeral_layerlar_ekle = MagicMock(return_value=[])
    loop._context_preflight = MagicMock(return_value=[])
    loop._api_call_with_retry = MagicMock(return_value={})  # dummy
    loop._yanit_icerigi_al = MagicMock(return_value="Arac cagiriyorum")
    loop._arac_calistir = MagicMock(return_value={
        "basarili": True, "tamamlandi": True, "cikti": "tool sonucu"
    })

    sonuc = loop.run_conversation(hedef=TEST_HEDEF)
    assert loop._arac_calistir.called, "_arac_calistir cagrilmadi"
    assert sonuc.get("basarili"), "basarili=False"
    print(f"  ✅ Tool loop: _arac_calistir cagrildi, basarili=True")


# ====================================================================
# ADIM 12: Text yanıt
# ====================================================================
def test_adim12_text_yanit():
    """ADIM 12: tool_calls yoksa direkt text yanit alinir"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=True))
    loop._sistem_promptu_olustur = MagicMock(return_value="test prompt")
    loop._api_mesajlari_olustur = MagicMock(return_value=[])
    loop._ephemeral_layerlar_ekle = MagicMock(return_value=[])
    loop._context_preflight = MagicMock(return_value=[])
    loop._api_call_with_retry = MagicMock(return_value={
        "choices": [{"message": {"content": "Merhaba! Bunu yapabilirim.", "role": "assistant"}}]
    })
    loop._tool_calls_al = MagicMock(return_value=[])
    loop._yanit_icerigi_al = MagicMock(return_value="Merhaba! Bunu yapabilirim.")

    sonuc = loop.run_conversation(hedef=TEST_HEDEF)
    assert "Merhaba" in sonuc.get("yanit", ""), "text yanit alinamadi"
    assert sonuc.get("basarili"), "basarili=False"
    print(f"  ✅ Text yanit: {sonuc['yanit'][:50]}")


# ====================================================================
# ADIM 13: Circuit breaker (3 arka arkaya hata → kalıcı durdurma)
# ====================================================================
def test_adim13_circuit_breaker():
    """ADIM 13: 3 arka arkaya hata → circuit breaker aktif"""
    from reymen.cereyan.conversation_loop import ConversationLoop, CIRCUIT_BREAKER_MAX_HATA

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    # CB acik: 3 hata birikmis
    loop._cb_acik = True
    loop._cb_art_arda_hata = 3

    # _api_call_with_retry'i CB kontrolune takilacak - mock gerekmez
    # cunku CB kontrolu _interruptible_api_call'dan ONCE
    sonuc = loop._api_call_with_retry(
        api_mesajlari=[],
        provider_tipi="chat_completions",
        task_id="test-cb",
        budget=MagicMock(),
    )
    assert sonuc is None, "CB acikken None donmeli"
    assert loop._cb_acik, "CB hala acik olmali"
    print(f"  ✅ Circuit breaker: kalici kilit aktif ({CIRCUIT_BREAKER_MAX_HATA} hata)")


# ====================================================================
# ADIM 14: Takılma dedektörü (aynı eylem 3x → durdur)
# ====================================================================
def test_adim14_takilma_dedektoru():
    """ADIM 14: ayni eylem 3x tekrarlanirsa → durdur"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    # Önceki eylemler: aynı tool 3x (takilma esigi)
    loop._onceki_eylemler = ["test_tool", "test_tool", "test_tool"]
    loop._cb_acik = False

    loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=True))
    loop._sistem_promptu_olustur = MagicMock(return_value="test prompt")
    loop._api_mesajlari_olustur = MagicMock(return_value=[])
    loop._ephemeral_layerlar_ekle = MagicMock(return_value=[])
    loop._context_preflight = MagicMock(return_value=[])
    loop._api_call_with_retry = MagicMock(return_value={
        "choices": [{
            "message": {
                "content": "test_tool kullaniyorum",
                "role": "assistant",
                "tool_calls": [{
                    "id": "tc_test_1",
                    "name": "test_tool",
                    "arguments": {"param": "test"},
                }],
            }
        }]
    })
    loop._tool_calls_al = MagicMock(return_value=[{
        "id": "tc_test_1",
        "name": "test_tool",
        "arguments": {"param": "test"},
    }])
    loop._yanit_icerigi_al = MagicMock(return_value="test_tool kullaniyorum")
    loop._arac_calistir = MagicMock(return_value={"basarili": False, "hata": "simule"})

    sonuc = loop.run_conversation(hedef=TEST_HEDEF)
    assert sonuc.get("basarili") is False, "basarili=False olmali"
    assert sonuc.get("hata") is not None, "hata mesaji olmali"
    assert "Takilma" in sonuc["hata"], f"takilma mesaji icermeli: {sonuc['hata']}"
    print(f"  ✅ Takilma dedektoru: 3x tekrar → durdur")


# ====================================================================
# ADIM 15: Session kapat
# ====================================================================
def test_adim15_session_kapat():
    """ADIM 15: session_bitir() cagrilmali"""
    with patch("reymen.cereyan.conversation_loop._SessionStorage") as mock_storage:
        mock_instance = MagicMock()
        mock_instance.session_baslat.return_value = "test-session"
        mock_storage.return_value = mock_instance

        from reymen.cereyan.conversation_loop import ConversationLoop
        loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock(provider="deepseek"))
        loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=False))

        sonuc = loop.run_conversation(hedef=TEST_HEDEF)
        # session_bitir en az 1 kez cagrilmis olmali
        session_bitir_calls = [c for c in mock_instance.method_calls if c[0] == 'session_bitir']
        assert session_bitir_calls, "session_bitir() cagrilmadi"
        print(f"  ✅ Session kapatildi")


# ====================================================================
# ADIM 16: Hafıza genişletme (gorev_sonrasi_hafiza)
# ====================================================================
def test_adim16_hafiza_genisletme():
    """ADIM 16: _gorev_sonrasi_hafiza() cagrilmali (basarili gorevde)"""
    with patch("reymen.cereyan.conversation_loop.ConversationLoop._gorev_sonrasi_hafiza") as mock_hafiza_genislet:
        mock_hafiza_genislet.return_value = None

        from reymen.cereyan.conversation_loop import ConversationLoop
        loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
        loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=True))
        loop._sistem_promptu_olustur = MagicMock(return_value="test prompt")
        loop._api_mesajlari_olustur = MagicMock(return_value=[])
        loop._ephemeral_layerlar_ekle = MagicMock(return_value=[])
        loop._context_preflight = MagicMock(return_value=[])
        loop._api_call_with_retry = MagicMock(return_value={
            "choices": [{"message": {"content": "Bu 20 karakterden uzun bir test yaniti", "role": "assistant"}}]
        })
        loop._tool_calls_al = MagicMock(return_value=[])
        loop._yanit_icerigi_al = MagicMock(return_value="Bu 20 karakterden uzun bir test yaniti")

        sonuc = loop.run_conversation(hedef=TEST_HEDEF)
        assert mock_hafiza_genislet.called, "_gorev_sonrasi_hafiza cagrilmadi"
        assert sonuc.get("kaydedildi"), "kaydedildi True olmali"
        print(f"  ✅ Hafiza genisletme: _gorev_sonrasi_hafiza cagrildi")


# ====================================================================
# ADIM 17: Hata analizi (basarisiz gorevde)
# ====================================================================
def test_adim17_hata_analizi():
    """ADIM 17: basarisiz gorevde hata mesaji olusmali"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=True))
    loop._sistem_promptu_olustur = MagicMock(return_value="test prompt")
    loop._api_mesajlari_olustur = MagicMock(return_value=[])
    loop._ephemeral_layerlar_ekle = MagicMock(return_value=[])
    loop._context_preflight = MagicMock(return_value=[])
    # _api_call_with_retry None donerse -> hata
    loop._api_call_with_retry = MagicMock(return_value=None)

    sonuc = loop.run_conversation(hedef=TEST_HEDEF)
    assert sonuc.get("basarili") is False, "basarili=False olmali"
    assert sonuc.get("hata") is not None, "hata mesaji olmali"
    print(f"  ✅ Hata analizi: hata mesaji olustu ({sonuc.get('hata', '')[:50]})")


# ====================================================================
# ADIM 18: Konuşma geçmişi taşıma (son user/assistant max 10)
# ====================================================================
def test_adim18_gecmis_tasima():
    """ADIM 18: son user/assistant mesajlar (max 10) bir sonraki goreve tasinir"""
    from reymen.cereyan.conversation_loop import ConversationLoop

    loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
    loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=True))
    loop._sistem_promptu_olustur = MagicMock(return_value="test prompt")
    loop._api_mesajlari_olustur = MagicMock(return_value=[])
    loop._ephemeral_layerlar_ekle = MagicMock(return_value=[])
    loop._context_preflight = MagicMock(return_value=[])
    loop._api_call_with_retry = MagicMock(return_value={
        "choices": [{"message": {"content": "cevap", "role": "assistant"}}]
    })
    loop._tool_calls_al = MagicMock(return_value=[])
    loop._yanit_icerigi_al = MagicMock(return_value="cevap")

    sonuc = loop.run_conversation(hedef=TEST_HEDEF)
    # _gecmis_mesajlar guncellenmis olmali
    assert len(loop._gecmis_mesajlar) > 0, "gecmis mesajlar bos"
    # Sadece user/assistant mesajlari
    for m in loop._gecmis_mesajlar:
        assert m["role"] in ("user", "assistant"), f"gecmiste {m['role']} rolu olmamali"
    assert len(loop._gecmis_mesajlar) <= loop._max_gecmis_mesaj, \
        f"max {loop._max_gecmis_mesaj} mesaj: {len(loop._gecmis_mesajlar)}"
    print(f"  ✅ Gecmis tasindi: {len(loop._gecmis_mesajlar)} mesaj (max={loop._max_gecmis_mesaj})")


# ====================================================================
# ENTEGRASYON: Tam akış testi (tüm adımlar zincir)
# ====================================================================
def test_entegrasyon_tam_akis():
    """Tum adimlar zinciri: hafiza bos -> cache yok -> API call -> yanit -> session kapat"""
    with patch("reymen.hafiza.gorev_once_kontrol.hafizada_ara") as mock_hafiza:
        mock_hafiza.return_value = {"bulundu": False}

        from reymen.cereyan.conversation_loop import ConversationLoop

        loop = ConversationLoop(motor=MagicMock(), beyin=MagicMock())
        loop._budget_olustur = MagicMock(return_value=_mock_budget(devam=True))
        loop._sistem_promptu_olustur = MagicMock(return_value="test prompt")
        loop._api_mesajlari_olustur = MagicMock(return_value=[])
        loop._ephemeral_layerlar_ekle = MagicMock(return_value=[])
        loop._context_preflight = MagicMock(return_value=[])
        loop._api_call_with_retry = MagicMock(return_value={
            "choices": [{"message": {"content": "Tamam islem tamam.", "role": "assistant"}}]
        })
        loop._tool_calls_al = MagicMock(return_value=[])
        loop._yanit_icerigi_al = MagicMock(return_value="Tamam islem tamam.")

        sonuc = loop.run_conversation(hedef="dosya olustur")
        assert sonuc["basarili"], f"entegrasyon basarisiz: {sonuc.get('hata')}"
        assert sonuc["yanit"] == "Tamam islem tamam.", "yanit eslesmiyor"
        assert sonuc["turlar"] > 0, "en az 1 tur olmali"
        assert "sure" in sonuc, "sure bilgisi eksik"
        assert "task_id" in sonuc, "task_id eksik"
        print(f"  ✅ Entegrasyon: task_id={sonuc['task_id']}, "
              f"tur={sonuc['turlar']}, sure={sonuc['sure']}s")


if __name__ == "__main__":
    print("=" * 60)
    print("ConversationLoop run_conversation() — 18 Adim Testi")
    print("=" * 60)

    test_adim1_task_id_olusturma()
    test_adim2_session_baslatma()
    test_adim3_hafiza_atlama()
    test_adim4_belirsiz_gorev_oneri()
    test_adim5_konusma_gecmisi()
    test_adim6_cache_kontrol()
    test_adim7_sistem_prompt()
    test_adim8_context_preflight()
    test_adim9_ephemeral_layer()
    test_adim10_api_call()
    test_adim11_tool_loop()
    test_adim12_text_yanit()
    test_adim13_circuit_breaker()
    test_adim14_takilma_dedektoru()
    test_adim15_session_kapat()
    test_adim16_hafiza_genisletme()
    test_adim17_hata_analizi()
    test_adim18_gecmis_tasima()
    test_entegrasyon_tam_akis()

    print("\n" + "=" * 60)
    print("SONUC: Tum testler gecti! ✅")
    print("=" * 60)
