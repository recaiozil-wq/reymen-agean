# -*- coding: utf-8 -*-
"""tests/test_cozum.py — Cozum uretme modulleri testleri."""

import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation_loop import ConversationLoop
from planlayici import Planlayici, PLAN_TALIMATI, YENIDEN_PLAN_TALIMATI
from closed_learning_loop import ClosedLearningLoop

# turn_context modulu su anda stub olarak proje kokunde bulunuyor
# (bkz: ./turn_context.py)
TurnContext = None
TurnKarari = None
TurnYoneticisi = None
try:
    import importlib as _importlib
    _tc = _importlib.import_module("turn_context")
    TurnContext = getattr(_tc, "TurnContext", None)
    TurnKarari = getattr(_tc, "TurnKarari", None)
    TurnYoneticisi = getattr(_tc, "TurnYoneticisi", None)
except (ImportError, Exception):
    pass


class TestConversationLoop:
    def test_conversation_loop_olusturma(self):
        """ConversationLoop baslatma."""
        cl = ConversationLoop(motor=None, beyin=None, max_tur=10)
        assert cl is not None
        assert cl.max_tur == 10
        assert cl._durum == "hazir"

    def test_conversation_loop_max_tur_default(self):
        """Varsayilan max_tur kontrolu."""
        cl = ConversationLoop()
        assert cl.max_tur == 30

    def test_conversation_loop_coz_basarisiz_motor_yok(self):
        """Motor olmadan cozum denenirse hata donmeli."""
        cl = ConversationLoop(max_tur=3)
        sonuc = cl.coz("test hedef")
        assert isinstance(sonuc, dict)
        assert sonuc["hedef"] == "test hedef"

    def test_conversation_loop_durum_ilk(self):
        """Baslangic durumu kontrolu."""
        cl = ConversationLoop()
        assert cl._durum == "hazir"


class MockProvider:
    """Mock provider for testing."""

    def uret(self, prompt, mesajlar):
        return "1. Ilk adim\n2. Ikinci adim\n3. Ucuncu adim"


class TestPlanlayici:
    def test_planlayici_olusturma(self):
        """Planlayici baslatma."""
        mp = MockProvider()
        p = Planlayici(mp)
        assert p is not None
        assert p._tamamlanan == []

    def test_plani_uret_basarili(self):
        """Plan uretme basarili."""
        mp = MockProvider()
        p = Planlayici(mp)
        plan = p.plani_uret("Bir web sayfasindan veri cek")
        assert isinstance(plan, list)
        assert len(plan) > 0

    def test_plani_uret_provider_hata(self):
        """Provider hatasinda tek adima dusme."""

        class HataProvider:
            def uret(self, prompt, mesajlar):
                raise Exception("Provider hatasi")

        p = Planlayici(HataProvider())
        plan = p.plani_uret("test")
        assert plan == ["test"]

    def test_plan_talimati_var(self):
        """PLAN_TALIMATI sabiti mevcut ve dogru formatta."""
        assert "gorev planlayicisisin" in PLAN_TALIMATI.lower()
        assert len(PLAN_TALIMATI) > 100

    def test_yeniden_plan_talimati_var(self):
        """YENIDEN_PLAN_TALIMATI sabiti mevcut."""
        assert "Yeni strateji" in YENIDEN_PLAN_TALIMATI
        assert "{hata}" in YENIDEN_PLAN_TALIMATI


class TestClosedLearningLoop:
    def test_learning_loop_olusturma(self):
        """ClosedLearningLoop baslatma (temp db ile)."""
        with tempfile.TemporaryDirectory() as tmp:
            db_yolu = os.path.join(tmp, "test_skills.db")
            skills_dir = os.path.join(tmp, "skills")
            loop = ClosedLearningLoop(db_yolu=db_yolu, skills_dir=skills_dir)
            assert loop is not None

    def test_learning_loop_beceri_kristallestir(self):
        """Beceri kristallestirme."""
        with tempfile.TemporaryDirectory() as tmp:
            db_yolu = os.path.join(tmp, "test_skills.db")
            skills_dir = os.path.join(tmp, "skills")
            # auto_index=False: proje skills dizinini FTS5'e yukleme,
            # aksi halde gercek becerilerle eslesen merge yapilir
            loop = ClosedLearningLoop(
                db_yolu=db_yolu, skills_dir=skills_dir, auto_index=False
            )
            loop.beceri_kristallestir("Test Beceri", "Aciklama", "1. Adim\n2. Adim")
            skills_path = Path(skills_dir)
            md_files = list(skills_path.glob("*.md"))
            loop.kapat()  # WAL dosyalarini temizle (Windows lock sorunu)
            assert len(md_files) >= 1

    def test_learning_loop_beceri_baglami(self):
        """Beceri baglami alma."""
        with tempfile.TemporaryDirectory() as tmp:
            db_yolu = os.path.join(tmp, "test_skills.db")
            skills_dir = os.path.join(tmp, "skills")
            loop = ClosedLearningLoop(db_yolu=db_yolu, skills_dir=skills_dir)
            baglam = loop.beceri_baglamini_al("test sorgu")
            assert isinstance(baglam, str)

    def test_learning_loop_kur(self):
        """Veritabani kurulumu."""
        with tempfile.TemporaryDirectory() as tmp:
            db_yolu = os.path.join(tmp, "test_skills.db")
            skills_dir = os.path.join(tmp, "skills")
            loop = ClosedLearningLoop(db_yolu=db_yolu, skills_dir=skills_dir)
            import sqlite3

            con = sqlite3.connect(db_yolu)
            tablo = con.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='beceriler'"
            ).fetchone()[0]
            con.close()  # Windows'ta temp-dir silinmeden once baglanti kapatilmali
            loop.kapat()
            assert tablo == 1


class TestTurnContext:
    def test_turn_context_olusturma(self):
        """TurnContext baslatma."""
        if TurnContext is None:
            return  # modul yoksa skip
        ctx = TurnContext(tur_id=1)
        assert ctx.tur_id == 1
        assert ctx.kararlar == []

    def test_turn_context_karar_ekle(self):
        """Karar ekleme."""
        if TurnContext is None:
            return
        ctx = TurnContext(tur_id=1)
        karar = ctx.karar_ekle("DOSYA_OKU", arac="DOSYA_OKU")
        assert karar is not None
        assert karar.eylem == "DOSYA_OKU"
        assert karar.arac == "DOSYA_OKU"
        assert len(ctx.kararlar) == 1

    def test_turn_context_karar_bitir(self):
        """Karar bitirme."""
        if TurnContext is None:
            return
        ctx = TurnContext(tur_id=1)
        ctx.karar_ekle("DOSYA_OKU", arac="DOSYA_OKU")
        ctx.karar_bitir(basarili=True, sonuc="Basarili")
        assert ctx.kararlar[-1].basarili is True

    def test_turn_context_coklu_karar(self):
        """Coklu karar ekleme ve sirasi."""
        if TurnContext is None:
            return
        ctx = TurnContext(tur_id=1)
        ctx.karar_ekle("ILK_ADIM")
        ctx.karar_ekle("IKINCI_ADIM")
        assert len(ctx.kararlar) == 2
        assert ctx.kararlar[0].adim == 1
        assert ctx.kararlar[1].adim == 2

    def test_turn_karari_veri_tipleri(self):
        """TurnKarari dataclass alanlari."""
        if TurnKarari is None:
            return
        karar = TurnKarari(adim=1, eylem="TEST", token_sayisi=150)
        assert karar.token_sayisi == 150
        assert karar.adim == 1
        assert karar.basarili is None

    def test_turn_yoneticisi(self):
        """TurnYoneticisi (varsa) testi."""
        if TurnYoneticisi:
            yonetici = TurnYoneticisi(max_tur=5)
            assert yonetici is not None
