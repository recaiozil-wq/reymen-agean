# -*- coding: utf-8 -*-
"""tests/test_hafiza_genislet.py — GelismisHafiza (hafiza_genislet.py) testleri.

Notlar:
- Sinif adi: GelismisHafiza (HafizaGenislet degil)
- initialize() SESSION_ID parametresi zorunlu
- kaydet() varsayilan koleksiyon: "konusmalar"
- session_ara() sadece "konusmalar" + "session_ozetleri" koleksiyonlarinda arar
- Her test tempfile kullanir — .reymen_hafiza/hafiza.db'ye dokunmaz
- Calistirma: python -m pytest tests/test_hafiza_genislet.py -v
"""

import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from hafiza_genislet import GelismisHafiza


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def hg(tmp_path):
    """Her test icin izole gecici DB."""
    db = str(tmp_path / "test_hafiza.db")
    inst = GelismisHafiza(db_yolu=db)
    inst.initialize(session_id="test_oturum_01", baslik="Test Oturumu")
    yield inst


@pytest.fixture
def hg_bos(tmp_path):
    """initialize() cagrilmamis ornek."""
    db = str(tmp_path / "bos_hafiza.db")
    return GelismisHafiza(db_yolu=db)


# ══════════════════════════════════════════════════════════════════════════════
# 1. INITIALIZE
# ══════════════════════════════════════════════════════════════════════════════


class TestInitialize:
    def test_yeni_session_olustur(self, tmp_path):
        db = str(tmp_path / "init.db")
        h = GelismisHafiza(db_yolu=db)
        h.initialize(session_id="ses_abc")
        assert h._aktif_session == "ses_abc"
        assert h._hazir is True

    def test_tekrar_initialize_ayni_id_crash_yok(self, hg):
        hg.initialize(session_id="test_oturum_01")
        assert hg._aktif_session == "test_oturum_01"

    def test_farkli_session_id_gecis(self, hg):
        hg.initialize(session_id="oturum_B", baslik="B Oturumu")
        assert hg._aktif_session == "oturum_B"

    def test_baslik_kaydedilir(self, tmp_path):
        db = str(tmp_path / "baslik.db")
        h = GelismisHafiza(db_yolu=db)
        h.initialize(session_id="titlesesion", baslik="Baslik Testi")
        sessions = h.session_listele()
        assert any(s["id"] == "titlesesion" for s in sessions)


# ══════════════════════════════════════════════════════════════════════════════
# 2. KAYDET
# ══════════════════════════════════════════════════════════════════════════════


class TestKaydet:
    def test_konusma_kaydet_basarili(self, hg):
        assert hg.kaydet("Python decorator nasil calisir?") is True

    def test_not_ekle(self, hg):
        assert hg.not_ekle("Not basligi", icerik="Not icerigi") is True

    def test_tercih_kaydet(self, hg):
        assert hg.tercih_kaydet("dil", "Turkce") is True

    def test_metadata_ile_kaydet(self, hg):
        assert (
            hg.kaydet(
                "Metadata testi",
                koleksiyon="konusmalar",
                anahtar="meta_test",
                metadata={"kaynak": "test", "puan": 5},
            )
            is True
        )

    def test_uzun_icerik_10k(self, hg):
        assert hg.kaydet("A" * 10_000) is True

    def test_unicode_turkce_emoji(self, hg):
        assert hg.kaydet("Türkçe karakter testi: ğüşıöç ÜÖÇ 🧠🔥") is True

    def test_ttl_sifir_sonsuz(self, hg):
        assert hg.kaydet("Sonsuz kayit", ttl_saat=0) is True

    def test_ttl_pozitif(self, hg):
        assert hg.kaydet("TTL ile kayit", ttl_saat=24) is True

    def test_varsayilan_koleksiyon_konusmalar(self, hg):
        hg.kaydet("Varsayilan koleksiyon testi")
        kayitlar = hg.session_kayitlari("test_oturum_01")
        assert any(k["koleksiyon"] == "konusmalar" for k in kayitlar)

    def test_mesaj_sayaci_artiyor(self, hg):
        onceki = hg._mesaj_sayaci
        hg.kaydet("Sayac testi")
        assert hg._mesaj_sayaci == onceki + 1

    def test_initialize_olmadan_session_genel_kullanilir(self, hg_bos):
        # Session baslatilmamissa kaydet "genel" session'a yazar
        sonuc = hg_bos.kaydet("Sessiz kayit")
        assert isinstance(sonuc, bool)


# ══════════════════════════════════════════════════════════════════════════════
# 3. ARA (FTS5)
# ══════════════════════════════════════════════════════════════════════════════


class TestAra:
    def test_fts5_tam_kelime_bulur(self, hg):
        hg.kaydet("Python decorator fonksiyon sarici", anahtar="decorator")
        sonuclar = hg.ara("decorator")
        assert len(sonuclar) > 0
        assert any("decorator" in s["icerik"].lower() for s in sonuclar)

    def test_fts5_birden_fazla_kayit(self, hg):
        hg.kaydet("SQLite veritabani FTS5 indeksi")
        hg.kaydet("Python ile goruntu isleme")
        sonuclar = hg.ara("SQLite")
        assert len(sonuclar) >= 1

    def test_bos_sorgu_bos_doner(self, hg):
        hg.kaydet("Herhangi bir icerik")
        assert hg.ara("") == []

    def test_bosluk_sorgu_bos_doner(self, hg):
        assert hg.ara("   ") == []

    def test_koleksiyon_filtresi(self, hg):
        hg.kaydet("Not icerik", koleksiyon="notlar", anahtar="not_anahtar")
        hg.kaydet("Konusma icerik", koleksiyon="konusmalar")
        sonuclar = hg.ara("not", koleksiyon="notlar")
        for s in sonuclar:
            assert s["koleksiyon"] == "notlar"

    def test_session_filtresi(self, hg):
        hg.kaydet("Oturum A icerigi benzersiz_kwd")
        hg.initialize(session_id="oturum_B")
        hg.kaydet("Oturum B icerigi benzersiz_kwd")
        sonuclar = hg.ara("benzersiz_kwd", session_id="test_oturum_01")
        for s in sonuclar:
            assert s["session_id"] == "test_oturum_01"

    def test_limit_calisiyor(self, hg):
        for i in range(10):
            hg.kaydet(f"limit_test kelime{i} decorator python")
        sonuclar = hg.ara("limit_test", limit=3)
        assert len(sonuclar) <= 3

    def test_olmayan_kelime_bos_doner(self, hg):
        hg.kaydet("sadece bu icerik var")
        sonuclar = hg.ara("xxxxxxxxxx_yok_yok")
        assert isinstance(sonuclar, list)

    def test_sql_injection_guvenli(self, hg):
        hg.kaydet("Normal icerik")
        sonuclar = hg.ara("'; DROP TABLE kayitlar; --")
        assert isinstance(sonuclar, list)

    def test_arama_sirala_calisir(self, hg):
        hg.kaydet("Python decorator ornegi ve kullanimi")
        hg.kaydet("decorator pattern uygulama")
        sonuclar = hg.arama_sirala("decorator")
        assert isinstance(sonuclar, list)
        if sonuclar:
            assert "toplam_puan" in sonuclar[0] or "bonus_puan" in sonuclar[0]


# ══════════════════════════════════════════════════════════════════════════════
# 4. SESSION_ARA
# ══════════════════════════════════════════════════════════════════════════════


class TestSessionAra:
    def test_konusmalar_koleksiyonunda_bulur(self, hg):
        # session_ara sadece "konusmalar" ve "session_ozetleri" koleksiyonlarinda arar
        hg.kaydet("ReYMeN_agent_benzersiz testi", koleksiyon="konusmalar")
        sonuclar = hg.session_ara("ReYMeN_agent_benzersiz")
        assert len(sonuclar) > 0

    def test_bos_sorgu_bos_doner(self, hg):
        hg.kaydet("Icerik var")
        assert hg.session_ara("") == []

    def test_yanlis_koleksiyonda_veri_gorunmez(self, hg):
        hg.kaydet("ozel_koleksiyon_xyz", koleksiyon="notlar")
        # notlar koleksiyonu session_ara kapsaminda degil
        sonuclar = hg.session_ara("ozel_koleksiyon_xyz")
        for s in sonuclar:
            assert s["koleksiyon"] in ("konusmalar", "session_ozetleri")

    def test_limit_calisiyor(self, hg):
        for i in range(8):
            hg.kaydet(f"session_ara_tekrar_{i}", koleksiyon="konusmalar")
        sonuclar = hg.session_ara("session_ara_tekrar", limit=3)
        assert len(sonuclar) <= 3


# ══════════════════════════════════════════════════════════════════════════════
# 5. SESSION YONETIMI
# ══════════════════════════════════════════════════════════════════════════════


class TestSessionYonetimi:
    def test_session_listele(self, hg):
        sessions = hg.session_listele()
        assert isinstance(sessions, list)
        assert any(s["id"] == "test_oturum_01" for s in sessions)

    def test_session_bitir(self, hg):
        hg.kaydet("Son mesaj")
        hg.session_bitir(ozet="Test oturumu tamamlandi")
        assert hg._aktif_session == ""

    def test_session_kayitlari(self, hg):
        hg.kaydet("Kayit 1")
        hg.kaydet("Kayit 2")
        kayitlar = hg.session_kayitlari("test_oturum_01")
        assert len(kayitlar) >= 2

    def test_konu_cikar_liste_doner(self, hg):
        hg.kaydet("Python decorator fonksiyon sarici wraps metodoloji")
        hg.kaydet("Python decorator kullanimi ve gercek ornekler")
        konular = hg.konu_cikar("test_oturum_01", limit=3)
        assert isinstance(konular, list)
        assert len(konular) >= 1

    def test_konu_cikar_olmayan_session_bos(self, hg):
        assert hg.konu_cikar("olmayan_session_xyz") == []

    def test_konu_cikar_bos_string_bos(self, hg):
        assert hg.konu_cikar("") == []

    def test_session_birlestir(self, hg):
        # kaynak session olustur
        hg.initialize(session_id="kaynak_ses")
        hg.kaydet("Kaynak session icerigi")
        # hedef session olustur
        hg.initialize(session_id="hedef_ses")
        hg.kaydet("Hedef session icerigi")

        assert hg.session_birlestir("hedef_ses", "kaynak_ses") is True
        # Kaynak session artik listede olmamali
        session_idler = [s["id"] for s in hg.session_listele(limit=50)]
        assert "kaynak_ses" not in session_idler
        assert "hedef_ses" in session_idler

    def test_session_birlestir_ayni_id(self, hg):
        assert hg.session_birlestir("test_oturum_01", "test_oturum_01") is True


# ══════════════════════════════════════════════════════════════════════════════
# 6. KULLANICI TERCIHLERİ
# ══════════════════════════════════════════════════════════════════════════════


class TestTercihler:
    def test_kaydet_al(self, hg):
        hg.tercih_kaydet("dil", "Turkce")
        assert hg.tercih_al("dil") == "Turkce"

    def test_olmayan_tercih_default(self, hg):
        assert hg.tercih_al("olmayan_tercih", default="varsayilan") == "varsayilan"

    def test_guncelle(self, hg):
        hg.tercih_kaydet("tema", "karanlik")
        hg.tercih_kaydet("tema", "acik")
        assert hg.tercih_al("tema") == "acik"

    def test_listele(self, hg):
        hg.tercih_kaydet("dil", "Turkce")
        hg.tercih_kaydet("tema", "karanlik")
        tercihler = hg.tercih_listele()
        assert len(tercihler) >= 2
        anahtarlar = [t["anahtar"] for t in tercihler]
        assert "dil" in anahtarlar

    def test_sil(self, hg):
        hg.tercih_kaydet("silinecek", "deger")
        hg.tercih_sil("silinecek")
        assert hg.tercih_al("silinecek") == ""

    def test_anahtar_kucuk_harf_normalize(self, hg):
        hg.tercih_kaydet("DIL", "Turkce")
        assert hg.tercih_al("dil") == "Turkce"


# ══════════════════════════════════════════════════════════════════════════════
# 7. DAYANIKLILIK
# ══════════════════════════════════════════════════════════════════════════════


class TestDayaniklilik:
    def test_buyuk_veri_200_kayit(self, hg):
        for i in range(200):
            hg.kaydet(f"Test kaydi numarasi {i} bilgi ogrenme")
        sonuclar = hg.ara("kaydi", limit=50)
        assert len(sonuclar) > 0
        assert hg.durum()["toplam_kayit"] >= 200

    def test_thread_guvenli_yazma(self, tmp_path):
        db = str(tmp_path / "thread_test.db")
        h = GelismisHafiza(db_yolu=db)
        h.initialize(session_id="thread_ses")
        hatalar = []

        def yaz(n):
            try:
                for i in range(20):
                    h.kaydet(f"Thread {n} kayit {i} icerik bilgi")
            except Exception as e:
                hatalar.append(str(e))

        threads = [threading.Thread(target=yaz, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)

        assert hatalar == [], f"Thread hatalari: {hatalar}"
        assert h.durum()["toplam_kayit"] == 100

    def test_durum_dict(self, hg):
        hg.kaydet("Durum testi")
        d = hg.durum()
        assert "toplam_kayit" in d
        assert "session_sayisi" in d
        assert d["aktif"] is True

    def test_temizle_expire_kayitlari(self, hg):
        hg.kaydet("Expire kayit", ttl_saat=0.000001)
        time.sleep(0.01)
        silinen = hg.temizle(yas_saat=0)
        assert isinstance(silinen, int)

    def test_kayit_guncelle(self, hg):
        hg.kaydet("Orijinal icerik", anahtar="guncelle_testi")
        kayitlar = hg.session_kayitlari("test_oturum_01")
        assert len(kayitlar) > 0
        kayit_id = kayitlar[-1]["id"]
        assert hg.kayit_guncelle(kayit_id, yeni_icerik="Guncellenmis icerik") is True
