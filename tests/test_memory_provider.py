# -*- coding: utf-8 -*-
"""tests/test_memory_provider.py — memory_provider kapsamlı test paketi (35 test).

Kapsam:
  - MemoryProvider ABC
  - MemoryProviderRegistry (kayıt, listeleme)
  - JsonBackend (CRUD, istatistik, geriye uyumluluk)
  - SQLiteBackend (CRUD, istatistik, geriye uyumluluk)
  - ChromaBackend (graceful degrade)
  - AbstraktHafizaSaglayici ve HafizaPluginKayit
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from memory_provider import (
    MemoryProvider,
    MemoryProviderRegistry,
    JsonBackend,
    SQLiteBackend,
    SqliteBackend,
    ChromaBackend,
    AbstraktHafizaSaglayici,
    HafizaPluginKayit,
    get_default_provider,
    global_hafiza_kayit_al,
)


# ── Yardımcı somut sınıflar ───────────────────────────────────────────────────

class _MinimalProvider(MemoryProvider):
    _provider_name = "_minimal_test"

    @property
    def name(self): return "_minimal_test"

    def is_available(self): return True

    def initialize(self, session_id, **kwargs): pass

    def save(self, collection, document, **kwargs): return "id1"

    def search(self, collection, query, limit=5): return []

    def get(self, collection, doc_id): return None

    def delete(self, collection, doc_id): return True

    def list_collections(self): return []

    def clear(self, collection): return True

    def stats(self): return {}


class _MinimalSaglayici(AbstraktHafizaSaglayici):
    @property
    def ad(self): return "minimal_test"
    def musait_mi(self): return True
    def baslat(self, oturum_id, **kwargs): pass
    def arac_sema_al(self): return []
    def arac_cagri_isle(self, arac, args, **kwargs): return "ok"


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 1 — MemoryProvider ABC (3 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestMemoryProviderABC:
    def test_somutlastirma_mumkun(self):
        p = _MinimalProvider()
        assert p.name == "_minimal_test"

    def test_is_available_true(self):
        p = _MinimalProvider()
        assert p.is_available() is True

    def test_soyut_sinif_dogrudan_orneklenemez(self):
        with pytest.raises(TypeError):
            MemoryProvider()  # type: ignore[abstract]


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 2 — MemoryProviderRegistry (5 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestRegistry:
    def test_json_kayitli(self):
        assert MemoryProviderRegistry.get("json") is JsonBackend

    def test_sqlite_kayitli(self):
        assert MemoryProviderRegistry.get("sqlite") is SQLiteBackend

    def test_chroma_kayitli(self):
        assert MemoryProviderRegistry.get("chroma") is ChromaBackend

    def test_olmayan_provider_none(self):
        assert MemoryProviderRegistry.get("olmayan_backend_xyz") is None

    def test_list_all_en_az_iki(self):
        kayitli = MemoryProviderRegistry.list_all()
        assert "json" in kayitli
        assert "sqlite" in kayitli

    def test_list_available_json_var(self):
        mevcut = MemoryProviderRegistry.list_available()
        assert "json" in mevcut


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 3 — JsonBackend CRUD (8 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestJsonBackend:
    @pytest.fixture()
    def jb(self, tmp_path):
        b = JsonBackend(dosya_yolu=str(tmp_path / "mem.json"))
        b.initialize(session_id="s1")
        return b

    def test_save_id_doner(self, jb):
        did = jb.save("kol", {"icerik": "test"})
        assert isinstance(did, str)
        assert len(did) > 0

    def test_search_sonuc_doner(self, jb):
        jb.save("kol", {"id": "d1", "icerik": "merhaba dunya"})
        sonuc = jb.search("kol", "merhaba")
        assert len(sonuc) >= 1

    def test_get_id_ile(self, jb):
        jb.save("kol", {"id": "abc123", "icerik": "test"})
        doc = jb.get("kol", "abc123")
        assert doc is not None
        assert doc["id"] == "abc123"

    def test_get_olmayan_none(self, jb):
        assert jb.get("kol", "olmayan") is None

    def test_delete_siliyor(self, jb):
        jb.save("kol", {"id": "sil_beni", "icerik": "x"})
        ok = jb.delete("kol", "sil_beni")
        assert ok is True
        assert jb.get("kol", "sil_beni") is None

    def test_list_collections(self, jb):
        jb.save("col_a", {"icerik": "a"})
        jb.save("col_b", {"icerik": "b"})
        cols = jb.list_collections()
        assert "col_a" in cols
        assert "col_b" in cols

    def test_clear_koleksiyon(self, jb):
        jb.save("temizle", {"icerik": "x"})
        ok = jb.clear("temizle")
        assert ok is True
        assert jb.search("temizle", "") == []

    def test_stats_dict(self, jb):
        s = jb.stats()
        assert isinstance(s, dict)
        assert "backend" in s


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 4 — JsonBackend geriye uyumluluk Türkçe API (3 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestJsonBackendGeriyeUyum:
    @pytest.fixture()
    def jb(self, tmp_path):
        b = JsonBackend(dosya_yolu=str(tmp_path / "mem.json"))
        b.initialize(session_id="s1")
        return b

    def test_kaydet_calisir(self, jb):
        did = jb.kaydet("kol", {"icerik": "eski api"})
        assert isinstance(did, str)

    def test_sorgula_calisir(self, jb):
        jb.kaydet("kol", {"icerik": "deneme"})
        result = jb.sorgula("kol", "deneme")
        assert isinstance(result, list)

    def test_istatistik_calisir(self, jb):
        s = jb.istatistik()
        assert isinstance(s, dict)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 5 — SQLiteBackend CRUD (6 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestSQLiteBackend:
    @pytest.fixture()
    def sb(self, tmp_path):
        b = SQLiteBackend(db_yolu=str(tmp_path / "mem.db"))
        b.initialize(session_id="s2")
        return b

    def test_save_id_doner(self, sb):
        did = sb.save("kol", {"icerik": "sqlite test"})
        assert isinstance(did, str)

    def test_search_sonuc_doner(self, sb):
        sb.save("kol", {"id": "sq1", "icerik": "sqlite arama"})
        sonuc = sb.search("kol", "sqlite")
        assert len(sonuc) >= 1

    def test_get_id_ile(self, sb):
        sb.save("kol", {"id": "sq_abc", "icerik": "test"})
        doc = sb.get("kol", "sq_abc")
        assert doc is not None

    def test_delete_siliyor(self, sb):
        sb.save("kol", {"id": "sq_sil", "icerik": "silinecek"})
        ok = sb.delete("kol", "sq_sil")
        assert ok is True

    def test_stats_dict(self, sb):
        s = sb.stats()
        assert isinstance(s, dict)
        assert "backend" in s

    def test_alias_sqlite_backend(self):
        assert SqliteBackend is SQLiteBackend


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 6 — ChromaBackend graceful degrade (3 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestChromaBackend:
    def test_chromabackend_orneklenebilir(self):
        cb = ChromaBackend()
        assert cb is not None

    def test_stats_dict_doner(self):
        cb = ChromaBackend()
        s = cb.stats()
        assert isinstance(s, dict)

    def test_search_bos_doner_chromasiz(self):
        cb = ChromaBackend()
        # chromadb yoksa boş liste dönmeli, crash olmamalı
        result = cb.search("kol", "sorgu")
        assert isinstance(result, list)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 7 — get_default_provider (2 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestGetDefaultProvider:
    def test_json_provider_doner(self, tmp_path):
        p = get_default_provider("json", dosya_yolu=str(tmp_path / "m.json"))
        assert isinstance(p, JsonBackend)

    def test_bilinmeyen_backend_json_doner(self, tmp_path):
        p = get_default_provider("bilinmeyen_xyz", dosya_yolu=str(tmp_path / "m.json"))
        assert isinstance(p, JsonBackend)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 8 — AbstraktHafizaSaglayici (3 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestAbstraktHafizaSaglayici:
    def test_somutlastirma(self):
        s = _MinimalSaglayici()
        assert s.ad == "minimal_test"

    def test_musait_mi(self):
        s = _MinimalSaglayici()
        assert s.musait_mi() is True

    def test_arac_cagri_isle(self):
        s = _MinimalSaglayici()
        result = s.arac_cagri_isle("ARAC", {})
        assert isinstance(result, str)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 9 — HafizaPluginKayit (4 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestHafizaPluginKayit:
    def test_saglayici_kayit_ve_listele(self):
        kayit = HafizaPluginKayit()
        kayit.hafiza_saglayici_kaydet(_MinimalSaglayici())
        assert "minimal_test" in kayit.saglayici_listele()

    def test_aktif_saglayici_sec(self):
        kayit = HafizaPluginKayit()
        kayit.hafiza_saglayici_kaydet(_MinimalSaglayici())
        ok = kayit.aktif_saglayici_sec("minimal_test", "oturum-001")
        assert ok is True

    def test_olmayan_saglayici_sec_false(self):
        kayit = HafizaPluginKayit()
        ok = kayit.aktif_saglayici_sec("olmayan", "oturum-001")
        assert ok is False

    def test_global_kayit_singleton(self):
        k1 = global_hafiza_kayit_al()
        k2 = global_hafiza_kayit_al()
        assert k1 is k2
