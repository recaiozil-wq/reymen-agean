# -*- coding: utf-8 -*-
"""
test_vektor_bellek.py — VektorBellek testleri.

Strateji:
  • PersistentClient -> EphemeralClient (RAM'de calisir, disk izi birakmaz)
  • Her test kendi koleksiyon adini alir — state sizintisi YOK
"""

import pytest
from unittest.mock import patch, MagicMock
import chromadb
import uuid

from src.reymen.hafiza.vektor_bellek import VektorBellek, ESIK_BENZERLIK


# ═══════════════════════════════════════════════════════════════════════════════
#  Fixture'lar
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def in_memory_chroma():
    """HER test oncesi PersistentClient -> EphemeralClient yamasi."""
    with patch("chromadb.PersistentClient") as mock:
        mock.side_effect = lambda *args, **kwargs: chromadb.EphemeralClient()
        yield


@pytest.fixture
def vektor_bellek(in_memory_chroma):
    """Her test ICIN benzersiz koleksiyon adiyla temiz bir VektorBellek."""
    uid = uuid.uuid4().hex[:8]
    vb = VektorBellek(koleksiyon_adi=f"test_reymen_{uid}")
    yield vb


@pytest.fixture
def ephemeral_collection():
    """Dogrudan EphemeralClient koleksiyonu."""
    client = chromadb.EphemeralClient()
    uid = uuid.uuid4().hex[:8]
    collection = client.get_or_create_collection(name=f"reymen_test_ephemeral_{uid}")
    yield collection


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: VektorBellek — Singleton
# ═══════════════════════════════════════════════════════════════════════════════


def test_vektor_bellek_singleton(in_memory_chroma):
    from reymen.hafiza.vektor_bellek import vektor_bellek_al
    vb1 = vektor_bellek_al()
    vb2 = vektor_bellek_al()
    assert vb1 is vb2


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: VektorBellek — Ekleme ve Arama
# ═══════════════════════════════════════════════════════════════════════════════


def test_ekle_bos_metin(vektor_bellek):
    """Bos metin eklenememeli."""
    sonuc = vektor_bellek.ekle("")
    assert sonuc == ""
    sonuc = vektor_bellek.ekle("   ")
    assert sonuc == ""
    assert len(vektor_bellek) == 0


def test_ara_bos_sorgu(vektor_bellek):
    """Bos sorgu bos liste donmeli."""
    assert vektor_bellek.ara("") == []
    assert vektor_bellek.ara("   ") == []


# ═══════════════════════════════════════════════════════════════════════════════
#  Test: Dogrudan ChromaDB EphemeralClient
# ═══════════════════════════════════════════════════════════════════════════════


def _mock_embedding(boyut: int = 384) -> list:
    return [0.1] * boyut


def test_ephemeral_ekle_ve_sorgula(ephemeral_collection):
    """EphemeralClient + mock embedding ile sifir disk + sifir model yukü."""
    col = ephemeral_collection
    emb = _mock_embedding()

    col.add(
        documents=["Kayseri'nin mantisi meshhurdur."],
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

    col.add(
        documents=["ReYMeN otonom bir ajan"],
        ids=["doc_3"],
        embeddings=[emb],
        metadatas=[{"kategori": "proje", "dil": "tr"}],
    )
    sonuc = col.query(query_embeddings=[emb], n_results=3)
    meta3 = sonuc["metadatas"][0][2]
    assert meta3["kategori"] == "proje"


def test_ephemeral_upsert(ephemeral_collection):
    """Upsert: ayni ID'de guncelleme calismali."""
    col = ephemeral_collection
    emb = _mock_embedding()

    col.add(ids=["doc_1"], documents=["Eski metin"], embeddings=[emb])
    col.upsert(ids=["doc_1"], documents=["Yeni metin"], embeddings=[emb])

    sonuc = col.get(ids=["doc_1"])
    assert sonuc["documents"][0] == "Yeni metin"


def test_ephemeral_delete(ephemeral_collection):
    """Silme islemi dogru calismali."""
    col = ephemeral_collection
    emb = _mock_embedding()

    col.add(ids=["doc_1", "doc_2"], documents=["Bir", "Iki"], embeddings=[emb, emb])
    assert col.count() == 2

    col.delete(ids=["doc_1"])
    assert col.count() == 1
    assert col.get(ids=["doc_1"])["ids"] == []


def test_ephemeral_bos_koleksiyon(ephemeral_collection):
    """Bos koleksiyonda sorgu bos donmeli."""
    col = ephemeral_collection
    emb = _mock_embedding()

    sonuc = col.query(query_embeddings=[emb], n_results=5)
    assert len(sonuc["ids"][0]) == 0
