# -*- coding: utf-8 -*-
"""
test_vektor_bellek.py — VektorBellek testleri.

Strateji:
  • PersistentClient → EphemeralClient (RAM'de çalışır, disk izi bırakmaz)
  • Embedding: ChromaDB'nin built-in ONNX modeli kullanılır
    (sentence-transformers/torch yüklenmez)
  • Her test kendi koleksiyon adını alır — state sızıntısı YOK
"""

import pytest
from unittest.mock import patch
import chromadb
import uuid

from reymen.hafiza.vektor_bellek import VektorBellek, ESIK_BENZERLIK


# ═══════════════════════════════════════════════════════════════════════════════
#  Fixture'lar
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def in_memory_chroma():
    """HER test öncesi PersistentClient -> EphemeralClient yaması.

    VektorBellek._chroma_kur() içindeki chromadb.PersistentClient(path=...)
    çağrısı yakalanır, argümanlar atılır ve RAM'de çalışan EphemeralClient
    döndürülür. Test bitince fixture temizlenir — diskte hiçbir chroma_db/
    klasörü oluşmaz.
    """
    with patch("chromadb.PersistentClient") as mock:
        mock.side_effect = lambda *args, **kwargs: chromadb.EphemeralClient()
        yield


@pytest.fixture
def vektor_bellek(in_memory_chroma):
    """Her test IÇIN benzersiz koleksiyon adıyla temiz bir VektorBellek."""
    uid = uuid.uuid4().hex[:8]
    vb = VektorBellek(koleksiyon_adi=f"test_reymen_{uid}")
    yield vb


@pytest.fixture
def ephemeral_collection():
    """Doğrudan EphemeralClient koleksiyonu — her test için benzersiz."""
    client = chromadb.EphemeralClient()
    uid = uuid.uuid4().hex[:8]
    collection = client.get_or_create_collection(name=f"reymen_test_ephemeral_{uid}")
    yield collection


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: VektorBellek — Singleton
# ═══════════════════════════════════════════════════════════════════════════════


def test_vektor_bellek_singleton(in_memory_chroma):
    """vektor_bellek_al() aynı instance'ı döndürmeli."""
    from reymen.hafiza.vektor_bellek import vektor_bellek_al

    vb1 = vektor_bellek_al()
    vb2 = vektor_bellek_al()
    assert vb1 is vb2


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: VektorBellek — Ekleme ve Arama
# ═══════════════════════════════════════════════════════════════════════════════


def test_ekle_ve_say(vektor_bellek):
    """Boş bellek → 0, eklendikçe artmalı."""
    assert len(vektor_bellek) == 0

    id1 = vektor_bellek.ekle("Kayseri'nin mantısı meşhurdur.")
    assert id1, "ID boş olmamalı"
    assert len(vektor_bellek) == 1

    vektor_bellek.ekle("Python ile ChromaDB entegrasyonu")
    vektor_bellek.ekle("ReYMeN otonom bir ajandır")
    assert len(vektor_bellek) == 3


def test_ekle_bos_metin(vektor_bellek):
    """Boş metin eklenememeli, sayı artmamalı."""
    sonuc = vektor_bellek.ekle("")
    assert sonuc == ""

    sonuc = vektor_bellek.ekle("   ")
    assert sonuc == ""

    assert len(vektor_bellek) == 0


def test_ekle_metadata(vektor_bellek):
    """Metadata doğru şekilde saklanmalı."""
    vid = vektor_bellek.ekle(
        "Kayseri mantısı yoğurt ve tereyağı ile servis edilir.",
        {"kategori": "yemek", "oncelik": "yuksek"},
    )
    assert vid

    sonuclar = vektor_bellek.ara("Kayseri mantısı", k=5)
    eslesen = [s for s in sonuclar if s[0] == vid]
    assert len(eslesen) >= 1
    assert eslesen[0][3].get("kategori") == "yemek"


def test_ekle_duplicate_dedup(vektor_bellek):
    """Aynı metin deduplike edilmeli (ESIK_DEDUP=0.85 → aynı metin)."""
    vid1 = vektor_bellek.ekle("Kayseri mantısı çok meşhurdur.")
    vid2 = vektor_bellek.ekle("Kayseri mantısı çok meşhurdur.")
    # Aynı SHA256 hash + dedup → aynı ID, sayı artmaz
    assert vid1 == vid2
    assert len(vektor_bellek) == 1


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: VektorBellek — Anlamsal Arama
# ═══════════════════════════════════════════════════════════════════════════════


def test_ara_kadar_sonuc(vektor_bellek):
    """k parametresi kadar sonuç dönmeli (veya daha az varsa hepsi)."""
    vektor_bellek.ekle("Kayseri'nin mantısı")
    vektor_bellek.ekle("Python ile yapay zeka")
    vektor_bellek.ekle("ReYMeN projesi")

    sonuc = vektor_bellek.ara("yapay zeka derin ogrenme", k=5)
    assert len(sonuc) <= 3  # Toplam 3 kayıt var, en fazla 3 döner


def test_ara_benzerlik_sirasi(vektor_bellek):
    """Sonuçlar cosine similarity'e göre azalan sırada olmalı."""
    vektor_bellek.ekle("Kayseri mantısı ve yoğurt")
    vektor_bellek.ekle("Python programlama dili")
    vektor_bellek.ekle("Kayseri denince akla mantı gelir")

    sonuc = vektor_bellek.ara("Kayseri mantı", k=3)
    if len(sonuc) >= 2:
        assert sonuc[0][2] >= sonuc[1][2], "Skor azalan sırada olmalı"


def test_ara_bos_sorgu(vektor_bellek):
    """Boş sorgu boş liste dönmeli."""
    assert vektor_bellek.ara("") == []
    assert vektor_bellek.ara("   ") == []


def test_ara_esik_alti_filtre(vektor_bellek):
    """ESIK_BENZERLIK (0.15) altındaki sonuçlar filtrelenmeli."""
    vektor_bellek.ekle("Tamamen alakasiz bir cumle burada yaziyor")
    vektor_bellek.ekle("Bambaska bir konu hakkinda")

    sonuc = vektor_bellek.ara("qwertyuiopasdfghjklzxcvbnm", k=5)
    for s in sonuc:
        assert s[2] >= ESIK_BENZERLIK, (
            f"Skor {s[2]:.4f} esiğin altında: {s[1][:40]}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: VektorBellek — Silme
# ═══════════════════════════════════════════════════════════════════════════════


def test_sil_basarili(vektor_bellek):
    """Silinen kayıt sayıyı düşürmeli ve aramada çıkmamalı."""
    vid = vektor_bellek.ekle("Silinecek kayit")
    assert len(vektor_bellek) == 1

    assert vektor_bellek.sil(vid) is True
    assert len(vektor_bellek) == 0

    sonuc = vektor_bellek.ara("Silinecek", k=5)
    assert not any(s[0] == vid for s in sonuc)


def test_sil_gecersiz_id(vektor_bellek):
    """Geçersiz/yok ID → False dönmeli (ChromaDB delete yok ID'de error fırlatmaz)."""
    assert vektor_bellek.sil("") is False


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: VektorBellek — Listeleme
# ═══════════════════════════════════════════════════════════════════════════════


def test_listele_hepsi(vektor_bellek):
    """Listele tüm kayıtları döndürmeli."""
    vektor_bellek.ekle("Birinci kayit")
    vektor_bellek.ekle("Ikinci kayit")

    liste = vektor_bellek.listele()
    assert len(liste) == 2

    metinler = [k["metin"] for k in liste]
    assert "Birinci kayit" in metinler
    assert "Ikinci kayit" in metinler


def test_listele_limit(vektor_bellek):
    """listele(limit=N) en fazla N kayıt döndürmeli."""
    for i in range(10):
        vektor_bellek.ekle(f"Kayit numara {i}")
    assert len(vektor_bellek.listele(limit=3)) <= 3


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: VektorBellek — Bilgi
# ═══════════════════════════════════════════════════════════════════════════════


def test_bilgi(vektor_bellek):
    """bilgi() dict döndürmeli, backend chromadb olmalı."""
    bilgi = vektor_bellek.bilgi()
    assert bilgi["backend"] == "chromadb"
    assert bilgi["kayit_sayisi"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: Doğrudan ChromaDB EphemeralClient (torch/embedding modeli OLMADAN)
# ═══════════════════════════════════════════════════════════════════════════════

def _mock_embedding(boyut: int = 384) -> list:
    """384 boyutlu sabit vektör — gerçek embedding modeli çağrılmaz."""
    return [0.1] * boyut


def test_ephemeral_ekle_ve_sorgula(ephemeral_collection):
    """
    EphemeralClient + mock embedding ile sıfır disk + sıfır model yükü.

    torch/sentence-transformers KESİNLİKLE yüklenmez.
    """
    col = ephemeral_collection
    emb = _mock_embedding()

    col.add(
        documents=["Kayseri'nin mantısı meşhurdur."],
        ids=["doc_1"],
        embeddings=[emb],
    )
    col.add(
        documents=["Python ile ChromaDB entegrasyonu"],
        ids=["doc_2"],
        embeddings=[emb],
    )
    assert col.count() == 2

    sonuc = col.query(query_embeddings=[emb], n_results=2)
    assert len(sonuc["ids"][0]) == 2

    # Metadata'li ekle
    col.add(
        documents=["ReYMeN otonom bir ajandır"],
        ids=["doc_3"],
        embeddings=[emb],
        metadatas=[{"kategori": "proje", "dil": "tr"}],
    )
    sonuc = col.query(query_embeddings=[emb], n_results=3)
    meta3 = sonuc["metadatas"][0][2]
    assert meta3["kategori"] == "proje"


def test_ephemeral_upsert(ephemeral_collection):
    """Upsert: aynı ID'de güncelleme çalışmalı."""
    col = ephemeral_collection
    emb = _mock_embedding()

    col.add(ids=["doc_1"], documents=["Eski metin"], embeddings=[emb])
    col.upsert(ids=["doc_1"], documents=["Yeni metin"], embeddings=[emb])

    sonuc = col.get(ids=["doc_1"])
    assert sonuc["documents"][0] == "Yeni metin"


def test_ephemeral_delete(ephemeral_collection):
    """Silme işlemi doğru çalışmalı."""
    col = ephemeral_collection
    emb = _mock_embedding()

    col.add(ids=["doc_1", "doc_2"], documents=["Bir", "Iki"], embeddings=[emb, emb])
    assert col.count() == 2

    col.delete(ids=["doc_1"])
    assert col.count() == 1
    assert col.get(ids=["doc_1"])["ids"] == []


def test_ephemeral_bos_koleksiyon(ephemeral_collection):
    """Boş koleksiyonda sorgu boş dönmeli."""
    col = ephemeral_collection
    emb = _mock_embedding()

    sonuc = col.query(query_embeddings=[emb], n_results=5)
    assert len(sonuc["ids"][0]) == 0
