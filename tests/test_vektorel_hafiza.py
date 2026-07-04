# -*- coding: utf-8 -*-
"""test_vektorel_hafiza.py — vektorel_hafiza.py icin kapsamli pytest testleri (20+ test).

MODUL: vektorel_hafiza.py
  ChromaDB varsa onu kullanir, yoksa _BasitYedek'e duser.
  Tum testler ChromaDB'siz (_BasitYedek) ortamda calisir.
"""

import pytest
from unittest.mock import MagicMock, patch


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def chroma_devre_disi(monkeypatch):
    """Her test oncesi CHROMA_AVAILABLE=False garantile."""
    monkeypatch.setattr("reymen.hafiza.vektorel_hafiza.CHROMA_AVAILABLE", False)


@pytest.fixture
def yedek():
    """Temiz bir _BasitYedek instance'i."""
    from reymen.hafiza.vektorel_hafiza import _BasitYedek

    return _BasitYedek()


@pytest.fixture
def vh():
    """vektorel_hafiza modul referansi (import edilmisse bile taze)."""
    import importlib
    import reymen.hafiza.vektorel_hafiza as vh

    importlib.reload(vh)
    # Reload sonrasi CHROMA_AVAILABLE sifirlanir — tekrar kapat
    vh.CHROMA_AVAILABLE = False
    return vh


# ══════════════════════════════════════════════════════════════════════════
# _BasitYedek — 10 TEST
# ══════════════════════════════════════════════════════════════════════════


class TestBasitYedekAddCount:
    """_BasitYedek ekleme ve sayma."""

    def test_add_ve_count_3_kayit(self, yedek):
        """1. add ile 3 kayit, count() == 3"""
        yedek.add(
            ["id1", "id2", "id3"],
            ["dokuman bir", "dokuman iki", "dokuman uc"],
            [{"k": "v1"}, {"k": "v2"}, {"k": "v3"}],
        )
        assert yedek.count() == 3


class TestBasitYedekQuery:
    """_BasitYedek sorgulama."""

    def test_jaccard_benzerlik_calisiyor(self, yedek):
        """2. query — basit Jaccard benzerlik calisiyor"""
        yedek.add(
            ["id1", "id2"], ["kedi kopek kus balik", "araba bisiklet ucak"], [{}, {}]
        )
        sonuc = yedek.query(query_texts=["kedi kopek"], n_results=2)
        dokumanlar = sonuc["documents"][0]
        assert len(dokumanlar) >= 1
        assert "kedi" in dokumanlar[0]
        # Id1 (kedi/kopek) id2'den (araba/bisiklet) daha benzer
        assert sonuc["ids"][0][0] == "id1"

    def test_ilgisiz_sorgu_bos_sonuc(self, yedek):
        """3. query — ilgisiz sorgu -> distances icin bos dizi"""
        yedek.add(["id1"], ["python kod yazilim"], [{}])
        sonuc = yedek.query(query_texts=["xyzxyz qwerty asdfgh"], n_results=3)
        # secili'de s>0 filtresi: eslesme yok -> bos liste
        assert len(sonuc["documents"][0]) == 0
        assert len(sonuc["ids"][0]) == 0
        assert len(sonuc["metadatas"][0]) == 0


class TestBasitYedekUpsert:
    """_BasitYedek upsert."""

    def test_upsert_varolan_id_guncellenir(self, yedek):
        """4. upsert — varolan id guncelleniyor"""
        yedek.add(["id1"], ["eski icerik"], [{"k": "eski"}])
        yedek.upsert(["id1"], ["yeni icerik"], [{"k": "yeni"}])
        assert yedek.count() == 1
        sonuc = yedek.query(query_texts=["yeni"], n_results=1)
        assert "yeni icerik" in sonuc["documents"][0][0]
        assert sonuc["metadatas"][0][0]["k"] == "yeni"

    def test_upsert_yeni_id_eklenir(self, yedek):
        """5. upsert — yeni id ekleniyor"""
        yedek.upsert(["id1"], ["icerik"], [{}])
        assert yedek.count() == 1
        yedek.upsert(["id2"], ["icerik 2"], [{}])
        assert yedek.count() == 2


class TestBasitYedekDelete:
    """_BasitYedek silme."""

    def test_delete_ids_ile_silinir(self, yedek):
        """6. delete(ids=[...]) -> o id'ler silindi"""
        yedek.add(["id1", "id2", "id3"], ["a", "b", "c"], [{}, {}, {}])
        yedek.delete(ids=["id1", "id3"])
        assert yedek.count() == 1
        assert yedek._kayitlar[0]["id"] == "id2"


class TestBasitYedekPeek:
    """_BasitYedek peek."""

    def test_peek_limit_2(self, yedek):
        """7. peek(limit=2) -> 2 kayit"""
        yedek.add(["id1", "id2", "id3"], ["bir", "iki", "uc"], [{}, {}, {}])
        sonuc = yedek.peek(limit=2)
        assert len(sonuc["ids"]) == 2
        assert sonuc["ids"] == ["id1", "id2"]

    def test_peek_limit_100(self, yedek):
        """8. peek(limit=100) -> var olan kadar (3)"""
        yedek.add(["id1", "id2", "id3"], ["a", "b", "c"], [{}, {}, {}])
        sonuc = yedek.peek(limit=100)
        assert len(sonuc["ids"]) == 3
        assert len(sonuc["documents"]) == 3


class TestBasitYedekBos:
    """_BasitYedek bos koleksiyon."""

    def test_bos_koleksiyon_query(self, yedek):
        """9. bos koleksiyonda query -> n_results=0"""
        sonuc = yedek.query(query_texts=["test"], n_results=3)
        assert len(sonuc["documents"][0]) == 0

    def test_bos_koleksiyon_count(self, yedek):
        """10. bos koleksiyonda count() == 0"""
        assert yedek.count() == 0


# ══════════════════════════════════════════════════════════════════════════
# vektorel_hafiza_sistemini_kur — 1 TEST
# ══════════════════════════════════════════════════════════════════════════


class TestSisteminiKur:
    """vektorel_hafiza_sistemini_kur."""

    def test_temp_yol_yedek_dondurur(self, vh, tmp_path):
        """11. temp yol -> _BasitYedek veya Collection donuyor"""
        col = vh.vektorel_hafiza_sistemini_kur(str(tmp_path / "test_hf"))
        from reymen.hafiza.vektorel_hafiza import _BasitYedek

        assert isinstance(col, (_BasitYedek, type(None)))


# ══════════════════════════════════════════════════════════════════════════
# tecrube_kaydet — 6 TEST
# ══════════════════════════════════════════════════════════════════════════


class TestTecrubeKaydet:
    """tecrube_kaydet fonksiyonu."""

    def test_basit_kayit_true_doner(self, vh):
        """12. basit kayit -> True"""
        col = vh.vektorel_hafiza_sistemini_kur()
        sonuc = vh.tecrube_kaydet(col, "test1", "ornek icerik")
        assert sonuc is True
        assert col.count() == 1

    def test_bos_icerik_false_doner(self, vh):
        """13. bos icerik -> False"""
        col = vh.vektorel_hafiza_sistemini_kur()
        assert vh.tecrube_kaydet(col, "t1", "") is False
        assert vh.tecrube_kaydet(col, "t2", "   ") is False
        assert vh.tecrube_kaydet(col, "t3", "\n\t\n") is False
        assert col.count() == 0

    def test_ayni_icerik_ikinci_kere_dedup(self, vh):
        """14. ayni icerik 2 kere -> ikincisi False (dedup)"""
        col = vh.vektorel_hafiza_sistemini_kur()
        assert vh.tecrube_kaydet(col, "id1", "tekrar eden icerik") is True
        assert vh.tecrube_kaydet(col, "id2", "tekrar eden icerik") is False
        assert col.count() == 1

    def test_metadata_zaman_anahtari_var(self, vh):
        """15. metadata ile -> metadata'da 'zaman' anahtari var"""
        col = vh.vektorel_hafiza_sistemini_kur()
        vh.tecrube_kaydet(col, "id1", "test icerik", {"kullanici": "ali"})
        sonuc = col.query(query_texts=["test icerik"], n_results=1)
        meta = sonuc["metadatas"][0][0]
        assert "zaman" in meta, f"'zaman' anahtari yok: {meta}"
        assert "kullanici" in meta, f"'kullanici' anahtari yok: {meta}"

    def test_metadata_basari_evet_var(self, vh):
        """16. metadata'da basari:evet var (otomatik eklenir)"""
        col = vh.vektorel_hafiza_sistemini_kur()
        vh.tecrube_kaydet(col, "id1", "test")
        sonuc = col.query(query_texts=["test"], n_results=1)
        meta = sonuc["metadatas"][0][0]
        assert meta.get("basari") == "evet", f"'basari'='evet' degil: {meta}"

    def test_budama_2000_kayit_sonrasi_calisir(self, vh, monkeypatch):
        """17. MAKS_HAFIZA=3 iken 5 kayit -> budama sonrasi en fazla 3"""
        monkeypatch.setattr(vh, "MAKS_HAFIZA", 3)
        col = vh.vektorel_hafiza_sistemini_kur()
        for i in range(5):
            assert vh.tecrube_kaydet(col, f"id{i}", f"icerik numara {i}") is True
        assert col.count() <= 3, f"Budama basarisiz: {col.count()} kayit"


# ══════════════════════════════════════════════════════════════════════════
# anlamsal_hafiza_ara — 3 TEST
# ══════════════════════════════════════════════════════════════════════════


class TestAnlamsalHafizaAra:
    """anlamsal_hafiza_ara fonksiyonu."""

    def test_3_kayit_sonrasi_en_benzer_3(self, vh):
        """18. 3 kayit sonrasi sorgu -> en benzer sonuclar"""
        col = vh.vektorel_hafiza_sistemini_kur()
        vh.tecrube_kaydet(col, "id1", "python ile dosya olusturma islemi")
        vh.tecrube_kaydet(col, "id2", "web arama motoru kullanimi")
        vh.tecrube_kaydet(col, "id3", "veritabani sorgulama")

        sonuc = vh.anlamsal_hafiza_ara(col, "dosya sorgulama islemi", adet=3)
        # En az 2 sonuc Jaccard eslesmesi beklenir
        assert (
            "dosya" in sonuc or "veritabani" in sonuc or "sorgulama" in sonuc
        ), f"Ilgili icerik bulunamadi: {sonuc}"
        # Birden fazla satir (en az 1-2 sonuc)
        assert sonuc.count("\n") >= 1

    def test_hic_kayit_yoksa_mesaj_doner(self, vh):
        """19. hic kayit yok -> '[Hafiza]' mesaji"""
        col = vh.vektorel_hafiza_sistemini_kur()
        sonuc = vh.anlamsal_hafiza_ara(col, "test")
        assert "Hafıza" in sonuc or "bulunamadı" in sonuc

    def test_sorgu_bos_string_mesaj_doner(self, vh):
        """20. sorgu bos string -> '[Hafiza]' mesaji"""
        col = vh.vektorel_hafiza_sistemini_kur()
        vh.tecrube_kaydet(col, "id1", "test icerik")
        sonuc = vh.anlamsal_hafiza_ara(col, "", adet=3)
        # Bos sorgu -> kelime eslesmesi yok -> bulunamadi
        assert "Hafıza" in sonuc or "bulunamadı" in sonuc


# ══════════════════════════════════════════════════════════════════════════
# EK: Yardimci Fonksiyonlar
# ══════════════════════════════════════════════════════════════════════════


class TestYardimciFonksiyonlar:
    """basarili_tecrube_kaydet, basarisiz_tecrube_kaydet, hafiza_ozeti_al."""

    def test_basarili_tecrube_kaydedilir(self, vh):
        """basarili_tecrube_kaydet -> [BASARILI] etiketi icerir."""
        col = vh.vektorel_hafiza_sistemini_kur()
        vh.basarili_tecrube_kaydet(col, "dosya olustur", "test.txt yazildi")
        assert col.count() == 1
        sonuc = col.query(query_texts=["dosya"], n_results=1)
        assert "[BASARILI]" in sonuc["documents"][0][0]

    def test_basarisiz_tecrube_kaydedilir(self, vh):
        """basarisiz_tecrube_kaydet -> [HATA] etiketi icerir."""
        col = vh.vektorel_hafiza_sistemini_kur()
        vh.basarisiz_tecrube_kaydet(col, "docker calistir", "Docker yok")
        assert col.count() == 1
        # Jaccard eslemesi icin sorgu kelimesi dokumandaki kelimeyle ayni olmali
        # Dokuman: "[HATA] docker calistir: Docker yok"
        sonuc = col.query(query_texts=["docker"], n_results=1)
        assert "[HATA]" in sonuc["documents"][0][0]

    def test_hafiza_ozeti_bos_koleksiyon_bos_doner(self, vh):
        """hafiza_ozeti_al -> bos koleksiyonda '' doner."""
        col = vh.vektorel_hafiza_sistemini_kur()
        ozet = vh.hafiza_ozeti_al(col)
        assert ozet == ""

    def test_hafiza_ozeti_dolu_koleksiyon(self, vh):
        """hafiza_ozeti_al -> dolu koleksiyonda 'Son tecrübeler' icerir."""
        col = vh.vektorel_hafiza_sistemini_kur()
        vh.tecrube_kaydet(col, "id1", "test icerik bir")
        vh.tecrube_kaydet(col, "id2", "test icerik iki")
        ozet = vh.hafiza_ozeti_al(col)
        assert "Son tecrübeler" in ozet
        assert "test icerik" in ozet


# ══════════════════════════════════════════════════════════════════════════
# EK: _budama_yap Dogrudan Test
# ══════════════════════════════════════════════════════════════════════════


class TestBudamaYap:
    """_budama_yap dogrudan cagri."""

    def test_budama_normalde_bisey_yapmaz(self, vh):
        """MAKS_HAFIZA'dan az kayit varken budama dokunmaz."""
        col = vh.vektorel_hafiza_sistemini_kur()
        col.add(["id1", "id2"], ["a", "b"], [{}, {}])
        vh._budama_yap(col)
        assert col.count() == 2

    def test_budama_fazla_kayitlari_siler(self, vh, monkeypatch):
        """MAKS_HAFIZA=2 iken 4 kayit varsa budama 2'ye indirir."""
        monkeypatch.setattr(vh, "MAKS_HAFIZA", 2)
        col = vh.vektorel_hafiza_sistemini_kur()
        col.add(["id1", "id2", "id3", "id4"], ["a", "b", "c", "d"], [{}, {}, {}, {}])
        vh._budama_yap(col)
        assert col.count() == 2
        # En eski 2 kayit silindi, en yeni 2 kaldi
        kalan_idler = [k["id"] for k in col._kayitlar]
        assert "id3" in kalan_idler
        assert "id4" in kalan_idler


# ══════════════════════════════════════════════════════════════════════════
# EK: ChromaDB Import Mock
# ══════════════════════════════════════════════════════════════════════════


class TestChromaDBMock:
    """ChromaDB import mock — CHROMA_AVAILABLE=True senaryosu."""

    def test_vektorel_hafiza_chromadb_varsa_kullanir(self, monkeypatch):
        """CHROMA_AVAILABLE=True ise _BasitYedek degil, chromadb nesnesi doner."""
        import sys

        # chromadb'yi sys.modules'a ekle ki import basarili olsun
        fake_collection = MagicMock()
        fake_collection.name = "ReYMeN_tecrube"
        fake_client = MagicMock()
        fake_client.get_or_create_collection.return_value = fake_collection

        fake_chromadb = MagicMock()
        fake_chromadb.PersistentClient.return_value = fake_client

        monkeypatch.setitem(sys.modules, "chromadb", fake_chromadb)

        # import reymen.hafiza.vektorel_hafiza — bu kez chromadb import'u basarili olacak
        import importlib
        import reymen.hafiza.vektorel_hafiza

        importlib.reload(reymen.hafiza.vektorel_hafiza)

        assert reymen.hafiza.vektorel_hafiza.CHROMA_AVAILABLE is True

        col = reymen.hafiza.vektorel_hafiza.vektorel_hafiza_sistemini_kur("./test_hf")
        # Chromadb nesnesi donmeli, _BasitYedek degil
        assert col.name == "ReYMeN_tecrube"
        fake_chromadb.PersistentClient.assert_called_once_with(path="./test_hf")
