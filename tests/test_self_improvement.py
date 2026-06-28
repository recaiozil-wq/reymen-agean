# -*- coding: utf-8 -*-
"""Tests for self_improvement.py — OzGelistirmeMotoru."""
import json
import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from self_improvement import (
    ANALIZ_RAPOR,
    SOUL_YOLU,
    OzGelistirmeMotoru,
)
import reymen.cereyan.self_improvement as real_mod


# ════════════════════════════════════════════════════════════════
# Init
# ════════════════════════════════════════════════════════════════

class TestInit:
    def test_varsayilan(self):
        m = OzGelistirmeMotoru()
        assert m.provider is None

    def test_provider(self):
        prov = MagicMock()
        m = OzGelistirmeMotoru(provider=prov)
        assert m.provider is prov


# ════════════════════════════════════════════════════════════════
# hata_analizi_yap
# ════════════════════════════════════════════════════════════════

class TestHataAnalizi:
    def test_db_yok(self, tmp_path):
        """DB yoksa bos doner."""
        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ROOT", tmp_path):
            r = m.hata_analizi_yap()
        assert r["hata_sayisi"] == 0
        assert r["en_sik_hatalar"] == []
        assert r["basarisiz_araclar"] == []

    def test_db_var_bos(self, tmp_path):
        """DB var ama tablo bos."""
        db_dir = tmp_path / ".ReYMeN"
        db_dir.mkdir()
        db = db_dir / "session.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE ajan_gunlugu (eylem TEXT, sonuc TEXT)")
        con.commit()
        con.close()

        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ROOT", tmp_path):
            r = m.hata_analizi_yap()
        assert r["hata_sayisi"] == 0

    def test_hata_var(self, tmp_path):
        """Hatali kayitlar tespit edilmeli."""
        db_dir = tmp_path / ".ReYMeN"
        db_dir.mkdir()
        db = db_dir / "session.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE ajan_gunlugu (eylem TEXT, sonuc TEXT)")
        # LIKE pattern: '%[Hata]%' or '%Hatasi]%'
        con.execute("INSERT INTO ajan_gunlugu VALUES ('KOMUT_CALISTIR(x)', 'Hatasi]: timeout')")
        con.execute("INSERT INTO ajan_gunlugu VALUES ('KOMUT_CALISTIR(y)', 'Hatasi]: error2')")
        con.execute("INSERT INTO ajan_gunlugu VALUES ('TARAYICI_AC()', '[Hata] acilmadi')")
        con.execute("INSERT INTO ajan_gunlugu VALUES ('BASARILI()', 'OK tamam')")
        con.commit()
        con.close()

        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ROOT", tmp_path):
            r = m.hata_analizi_yap()
        assert r["hata_sayisi"] == 3
        assert len(r["en_sik_hatalar"]) == 3
        # KOMUT_CALISTIR en sik olmali
        arac_map = dict(r["basarisiz_araclar"])
        assert arac_map.get("KOMUT_CALISTIR") == 2

    def test_tablo_yok(self, tmp_path):
        """ajan_gunlugu tablosu yoksa hata donmeli."""
        db_dir = tmp_path / ".ReYMeN"
        db_dir.mkdir()
        db = db_dir / "session.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE farkli_tablo (a TEXT)")
        con.commit()
        con.close()

        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ROOT", tmp_path):
            r = m.hata_analizi_yap()
        # Tablo yoksa rows=[] olur, hata donmez
        assert r["hata_sayisi"] == 0


# ════════════════════════════════════════════════════════════════
# beceri_bosluk_analizi
# ════════════════════════════════════════════════════════════════

class TestBeceriBosluk:
    def test_db_yok(self, tmp_path):
        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ROOT", tmp_path):
            r = m.beceri_bosluk_analizi()
        assert r == []

    def test_gorevler_var(self, tmp_path):
        db_dir = tmp_path / ".ReYMeN"
        db_dir.mkdir()
        db = db_dir / "session.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE ajan_gunlugu (eylem TEXT, hedef TEXT, sonuc TEXT)")
        for i in range(5):
            con.execute(
                "INSERT INTO ajan_gunlugu VALUES (?, ?, ?)",
                (f"GOREV_BITTI_{i}", f"dosya_{i}.py tamamla", "OK"),
            )
        con.commit()
        con.close()

        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ROOT", tmp_path):
            r = m.beceri_bosluk_analizi()
        assert len(r) == 5
        # ORDER BY rowid DESC → en son eklenen ilk sirada
        assert r[0] == "dosya_4.py tamamla"

    def test_limit_10(self, tmp_path):
        """Maks 10 donmeli."""
        db_dir = tmp_path / ".ReYMeN"
        db_dir.mkdir()
        db = db_dir / "session.db"
        con = sqlite3.connect(str(db))
        con.execute("CREATE TABLE ajan_gunlugu (eylem TEXT, hedef TEXT, sonuc TEXT)")
        for i in range(20):
            con.execute(
                "INSERT INTO ajan_gunlugu VALUES (?, ?, ?)",
                ("GOREV_BITTI", f"gorev_{i}", "OK"),
            )
        con.commit()
        con.close()

        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ROOT", tmp_path):
            r = m.beceri_bosluk_analizi()
        assert len(r) == 10


# ════════════════════════════════════════════════════════════════
# oneri_uret / _kural_tabanli_oneri
# ════════════════════════════════════════════════════════════════

class TestOneriUret:
    def test_kural_tabanli_komut_calistir(self):
        m = OzGelistirmeMotoru()
        analiz = {"basarisiz_araclar": [("KOMUT_CALISTIR", 5), ("TARAYICI_AC", 3)]}
        r = m._kural_tabanli_oneri(analiz)
        assert "KOMUT_CALISTIR" in r
        assert "PYTHON_CALISTIR" in r
        assert "TARAYICI_AC" in r
        assert "WEB_ARA" in r

    def test_kural_tabanli_ekran_tikla(self):
        m = OzGelistirmeMotoru()
        analiz = {"basarisiz_araclar": [("EKRAN_TIKLA", 5)]}
        r = m._kural_tabanli_oneri(analiz)
        assert "EKRAN_NISAN" in r

    def test_kural_tabanli_bos(self):
        """Hic basarisiz arac yoksa varsayilan oneriler."""
        m = OzGelistirmeMotoru()
        r = m._kural_tabanli_oneri({"basarisiz_araclar": []})
        assert "HAFIZA_ARA" in r
        assert "IC_GOZLEM" in r

    def test_oneri_uret_providersiz(self):
        m = OzGelistirmeMotoru()
        r = m.oneri_uret({"hata_sayisi": 0, "basarisiz_araclar": []})
        assert "HAFIZA_ARA" in r

    def test_oneri_uret_provider_mock(self):
        prov = MagicMock()
        prov.uret.return_value = "Oneri metni"
        m = OzGelistirmeMotoru(provider=prov)
        r = m.oneri_uret({"hata_sayisi": 5, "basarisiz_araclar": []})
        assert r == "Oneri metni"
        prov.uret.assert_called_once()

    def test_oneri_uret_provider_hatasi(self):
        """Provider hata verirse fallback."""
        prov = MagicMock()
        prov.uret.side_effect = RuntimeError("API error")
        m = OzGelistirmeMotoru(provider=prov)
        r = m.oneri_uret({"hata_sayisi": 5, "basarisiz_araclar": []})
        assert "HAFIZA_ARA" in r  # fallback


# ════════════════════════════════════════════════════════════════
# soul_guncelle
# ════════════════════════════════════════════════════════════════

class TestSoulGuncelle:
    def test_dosya_yok(self, tmp_path):
        m = OzGelistirmeMotoru()
        fake_soul = tmp_path / "SOUL.md"
        with patch.object(real_mod, "SOUL_YOLU", fake_soul):
            r = m.soul_guncelle("oneri metni")
        assert r is False

    def test_dosya_var(self, tmp_path):
        fake_soul = tmp_path / "SOUL.md"
        fake_soul.write_text("Mevcut SOUL", encoding="utf-8")
        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "SOUL_YOLU", fake_soul):
            r = m.soul_guncelle("yeni oneri")
        assert r is True
        icerik = fake_soul.read_text(encoding="utf-8")
        assert "Mevcut SOUL" in icerik
        assert "yeni oneri" in icerik
        assert "Oz-Gelistirme" in icerik


# ════════════════════════════════════════════════════════════════
# rapor_kaydet
# ════════════════════════════════════════════════════════════════

class TestRaporKaydet:
    def test_kaydet(self, tmp_path):
        rapor_yolu = tmp_path / ".ReYMeN" / "self_improvement.json"
        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ANALIZ_RAPOR", rapor_yolu):
            m.rapor_kaydet({"test": True, "sayi": 42})
        assert rapor_yolu.exists()
        data = json.loads(rapor_yolu.read_text(encoding="utf-8"))
        assert data["test"] is True
        assert data["sayi"] == 42


# ════════════════════════════════════════════════════════════════
# calistir (entegrasyon)
# ════════════════════════════════════════════════════════════════

class TestCalistir:
    def test_calistir_basics(self, tmp_path):
        rapor_yolu = tmp_path / ".ReYMeN" / "self_improvement.json"
        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ANALIZ_RAPOR", rapor_yolu):
            r = m.calistir()
        assert "zaman" in r
        assert "hata_analizi" in r
        assert "oneriler" in r
        assert rapor_yolu.exists()

    def test_calistir_uygula_soul_yok(self, tmp_path):
        rapor_yolu = tmp_path / ".ReYMeN" / "self_improvement.json"
        fake_soul = tmp_path / "SOUL.md"
        m = OzGelistirmeMotoru()
        with patch.object(real_mod, "ANALIZ_RAPOR", rapor_yolu), \
             patch.object(real_mod, "SOUL_YOLU", fake_soul):
            r = m.calistir(uygula=True)
        # SOUL.md yok → soul_guncelle False doner ama calistir patlamaz
        assert "oneriler" in r


# ════════════════════════════════════════════════════════════════
# Sabitler
# ════════════════════════════════════════════════════════════════

class TestSabitler:
    def test_analiz_rapor_path(self):
        assert "self_improvement.json" in str(ANALIZ_RAPOR)

    def test_soul_yolu_path(self):
        assert "SOUL.md" in str(SOUL_YOLU)
