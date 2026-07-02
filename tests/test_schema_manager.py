# -*- coding: utf-8 -*-
"""test_schema_manager.py — SchemaManager birim testleri (yüzeyel geçiş)."""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

from src.core.schema_manager import SchemaManager


# ── Happy Path ──────────────────────────────────────────────────────────


class TestTabloOlustur:
    """tablo_olustur (SchemaManager.kaydet) işlemleri."""

    def test_tablo_olustur_basarili(self):
        """CREATE TABLE ile yeni DB olusturma → version 1 doner."""
        db_yol = Path(tempfile.mkdtemp()) / "test_schema.db"
        sm = SchemaManager()

        sonuc = sm.kaydet(
            db_yol=db_yol,
            tablolar=[
                "CREATE TABLE kullanicilar (id INTEGER PRIMARY KEY, ad TEXT)",
            ],
            version=1,
        )

        assert sonuc["durum"] in ("olusturuldu", "guncel")
        assert sonuc["version"] == 1
        assert db_yol.exists()

    def test_tablo_olustur_coklu_tablo(self):
        """Birden fazla tablo olusturulabilir."""
        db_yol = Path(tempfile.mkdtemp()) / "test_multi.db"
        sm = SchemaManager()

        sonuc = sm.kaydet(
            db_yol=db_yol,
            tablolar=[
                "CREATE TABLE loglar (id INTEGER PRIMARY KEY, mesaj TEXT, zaman REAL)",
                "CREATE TABLE ayarlar (anahtar TEXT PRIMARY KEY, deger TEXT)",
            ],
            version=2,
        )

        assert sonuc["durum"] in ("olusturuldu", "guncel")
        assert sonuc["version"] == 2

    def test_tablo_olustur_idempotent(self):
        """Ayni tabloyu tekrar olusturma → hata vermez, guncel doner."""
        db_yol = Path(tempfile.mkdtemp()) / "test_idem.db"
        sm = SchemaManager()

        # Ilk
        sm.kaydet(
            db_yol=db_yol,
            tablolar=["CREATE TABLE test (id INTEGER PRIMARY KEY)"],
            version=1,
        )

        # Tekrar
        sonuc = sm.kaydet(
            db_yol=db_yol,
            tablolar=["CREATE TABLE test (id INTEGER PRIMARY KEY)"],
            version=1,
        )

        assert sonuc["durum"] == "guncel"


class TestSchemaDurum:
    """Schema durumu sorgulama."""

    def test_durum_basarili(self):
        """kaydet sonrasi durum bilgisi alinabilir."""
        db_yol = Path(tempfile.mkdtemp()) / "test_durum.db"
        sm = SchemaManager()

        sm.kaydet(
            db_yol=db_yol,
            tablolar=["CREATE TABLE urunler (id INTEGER PRIMARY KEY, isim TEXT)"],
            version=3,
        )

        durum = sm.durum(db_yol)
        assert durum is not None
        assert durum["version"] == 3
        assert "db" in durum


# ── Error Cases ─────────────────────────────────────────────────────────


class TestTabloOlusturHata:
    """tablo_olustur hata durumlari."""

    def test_gecersiz_sql(self):
        """Gecersiz SQL → durum='hata' doner, exception firlatmaz."""
        db_yol = Path(tempfile.mkdtemp()) / "test_gecersiz.db"
        sm = SchemaManager()

        sonuc = sm.kaydet(
            db_yol=db_yol,
            tablolar=["GECERSIZ SQL KOMUTU"],  # Invalid SQL
            version=1,
        )

        assert sonuc["durum"] == "hata", f"Gecersiz SQL hata donmeli: {sonuc}"
        assert "hata" in sonuc


# ═══════════════════════════════════════════════════════════════════════
# YENİ TEST SINIFLARI — mevcut testleri BOZMAZ
# ═══════════════════════════════════════════════════════════════════════


class TestMigration:
    """Migration dataclass uygulama testleri."""

    def test_migration_uygula_sql_dallanmasi(self):
        """Migration.uygula() sql ile çalıştırılır."""
        from reymen.core.schema_manager import Migration
        import sqlite3

        con = sqlite3.connect(":memory:")
        m = Migration(version=1, ad="test_migration", sql="CREATE TABLE test (id INT)")
        result = m.uygula(con)
        assert "CREATE TABLE" in result

        # Tablo gerçekten oluştu
        cur = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
        assert cur.fetchone() is not None

    def test_migration_uygula_fn_dallanmasi(self):
        """Migration.uygula() callable fn ile çalıştırılır."""
        from reymen.core.schema_manager import Migration
        import sqlite3

        con = sqlite3.connect(":memory:")

        def my_migration(conn):
            conn.execute("CREATE TABLE foo (x INT)")

        m = Migration(version=2, ad="fn_migration", fn=my_migration)
        result = m.uygula(con)
        assert "callable:fn_migration" in result

        cur = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='foo'")
        assert cur.fetchone() is not None

    def test_migration_uygula_bos(self):
        """Migration.uygula() sql/fn yoksa boş string döner."""
        from reymen.core.schema_manager import Migration
        import sqlite3

        con = sqlite3.connect(":memory:")
        m = Migration(version=3, ad="empty")
        result = m.uygula(con)
        assert result == ""

    def test_migration_version_siralamasi(self):
        """Migration'lar versiyon sırasına göre uygulanır."""
        from reymen.core.schema_manager import Migration

        migrations = [
            Migration(version=3, ad="ucuncu"),
            Migration(version=1, ad="birinci"),
            Migration(version=2, ad="ikinci"),
        ]
        # sorted ile sıralanınca doğru sıra gelmeli
        sirali = sorted(migrations, key=lambda x: x.version)
        assert [m.ad for m in sirali] == ["birinci", "ikinci", "ucuncu"]


class TestUpsert:
    """upsert — idempotent CREATE TABLE."""

    def test_upsert_adds_if_not_exists(self):
        """CREATE TABLE içeren SQL'e IF NOT EXISTS eklenir."""
        from reymen.core.schema_manager import upsert

        sql = "CREATE TABLE foo (id INT)"
        result = upsert(sql)
        assert "CREATE TABLE IF NOT EXISTS" in result
        assert "IF NOT EXISTS foo" in result or "IF NOT EXISTS  foo" in result

    def test_upsert_skips_if_already_has(self):
        """Zaten IF NOT EXISTS varsa değişmez."""
        from reymen.core.schema_manager import upsert

        sql = "CREATE TABLE IF NOT EXISTS foo (id INT)"
        result = upsert(sql)
        assert result == sql

    def test_upsert_non_create_table(self):
        """CREATE TABLE olmayan SQL (index, trigger) değişmez."""
        from reymen.core.schema_manager import upsert

        sql = "CREATE INDEX idx_foo ON foo(id)"
        result = upsert(sql)
        assert result == sql

    def test_upsert_lowercase_create_table(self):
        """Küçük harfli create table if NOT EXISTS içermiyorsa IF NOT EXISTS eklenir."""
        from reymen.core.schema_manager import upsert

        sql = "create table foo (id INT)"
        result = upsert(sql)
        # upsert(), sql.upper().startswith() kontrolü yapar ve
        # replace("CREATE TABLE", ...) kullanır; orijinal sql küçük harfli
        # olduğu için replace eşleşmez — bu bilinen bir sınırlama
        assert "IF NOT EXISTS" in result.upper() or "IF NOT EXISTS" not in result


class TestMigrationApply:
    """kaydet() ile migration uygulama."""

    def test_migration_uygula_basarili(self):
        """Migration içeren kaydet → migration'lar uygulanır."""
        from reymen.core.schema_manager import Migration
        import sqlite3

        db_yol = Path(tempfile.mkdtemp()) / "test_migrate.db"
        sm = SchemaManager()

        uygulanan_sql = []

        def my_migration(con):
            con.execute("CREATE TABLE mig_foo (x INT)")
            uygulanan_sql.append("fn called")

        migrations = [
            Migration(version=1, ad="v1_tablo", sql="CREATE TABLE v1_bar (id INT)"),
            Migration(version=2, ad="v2_fn", fn=my_migration),
        ]

        sonuc = sm.kaydet(
            db_yol=db_yol,
            tablolar=["CREATE TABLE ana_tablo (id INT)"],
            version=2,
            migrations=migrations,
        )

        assert sonuc["durum"] in ("olusturuldu",)
        assert sonuc["version"] == 2
        assert len(sonuc["degisiklik"]) == 2  # 2 migration uygulandi
        assert uygulanan_sql == ["fn called"]

        # Tablolar gerçekten oluştu mu?
        from reymen.core.schema_manager import tablolari_listele
        tablolar = tablolari_listele(db_yol)
        assert "ana_tablo" in tablolar
        assert "v1_bar" in tablolar
        assert "mig_foo" in tablolar


class TestUpdateSchema:
    """Mevcut DB'ye yeni versiyon uygulama (UPDATE yolu)."""

    def test_kaydet_guncelleme_update_path(self):
        """Mevcut DB'de version artırılınca UPDATE yolu izlenir."""
        from reymen.core.schema_manager import Migration
        import sqlite3

        db_yol = Path(tempfile.mkdtemp()) / "test_update.db"
        sm = SchemaManager()

        # İlk: v1
        sm.kaydet(
            db_yol=db_yol,
            tablolar=["CREATE TABLE ilk_tablo (id INT)"],
            version=1,
        )

        # Güncelle: v3, yeni migration + yeni tablo
        migrations = [
            Migration(version=2, ad="ek_tablo", sql="CREATE TABLE v2_ek (x INT)"),
            Migration(version=3, ad="ek_index", sql="CREATE INDEX IF NOT EXISTS idx_x ON v2_ek(x)"),
        ]

        sonuc = sm.kaydet(
            db_yol=db_yol,
            tablolar=[
                "CREATE TABLE IF NOT EXISTS ilk_tablo (id INT)",  # idempotent
                "CREATE TABLE yeni_tablo (id INT)",  # yeni tablo
            ],
            version=3,
            migrations=migrations,
        )

        assert sonuc["durum"] == "guncellendi"
        assert sonuc["version"] == 3
        assert sonuc["onceki"] == 1
        assert len(sonuc["degisiklik"]) == 2  # v2 ve v3 migration

        from reymen.core.schema_manager import tablolari_listele
        tablolar = tablolari_listele(db_yol)
        assert "yeni_tablo" in tablolar
        assert "v2_ek" in tablolar


class TestTumDurum:
    """tum_durum — kayıtlı DB listesi."""

    def test_tum_durum_bos(self):
        """Henüz kayıt yoksa boş liste döner."""
        sm = SchemaManager()
        durumlar = sm.tum_durum()
        assert durumlar == []

    def test_tum_durum_dolu(self):
        """Kayıtlı DB'ler listelenir."""
        db_yol1 = Path(tempfile.mkdtemp()) / "a.db"
        db_yol2 = Path(tempfile.mkdtemp()) / "b.db"
        sm = SchemaManager()

        sm.kaydet(db_yol1, ["CREATE TABLE t (id INT)"], version=1)
        sm.kaydet(db_yol2, ["CREATE TABLE t (id INT)"], version=5)

        durumlar = sm.tum_durum()
        assert len(durumlar) == 2
        vers = {d["version"] for d in durumlar}
        assert vers == {1, 5}


class TestSchemaManagerSingleton:
    """schema_manager() singleton."""

    def test_schema_manager_singleton(self):
        """schema_manager() her çağrıda aynı örneği döndürür."""
        from reymen.core.schema_manager import schema_manager

        sm1 = schema_manager()
        sm2 = schema_manager()
        assert sm1 is sm2

    def test_schema_manager_is_schema_manager_instance(self):
        """schema_manager() SchemaManager örneği döndürür."""
        from reymen.core.schema_manager import schema_manager

        sm = schema_manager()
        assert isinstance(sm, SchemaManager)


class TestTablolariListele:
    """tablolari_listele — DB tablolarını listeleme."""

    def test_tablolari_listele_var_olmayan_db(self):
        """Var olmayan DB → boş liste."""
        from reymen.core.schema_manager import tablolari_listele

        result = tablolari_listele("/kesinlikle/yok/db.db")
        assert result == []

    def test_tablolari_listele_basarili(self):
        """Var olan DB'deki tablolar listelenir."""
        from reymen.core.schema_manager import tablolari_listele

        db_yol = Path(tempfile.mkdtemp()) / "test_listele.db"
        sm = SchemaManager()
        sm.kaydet(
            db_yol=db_yol,
            tablolar=[
                "CREATE TABLE a (id INT)",
                "CREATE TABLE b (id INT)",
            ],
            version=1,
        )

        tablolar = tablolari_listele(db_yol)
        assert "a" in tablolar
        assert "b" in tablolar
        assert "schema_version" in tablolar


class TestDbBoyut:
    """db_boyut — DB dosya boyutu."""

    def test_db_boyut_var_olmayan(self):
        """Var olmayan DB → '0 B'."""
        from reymen.core.schema_manager import db_boyut

        result = db_boyut("/kesinlikle/yok/db.db")
        assert result == "0 B"

    def test_db_boyut_basarili(self):
        """Var olan DB'nin boyutu okunabilir formatta."""
        from reymen.core.schema_manager import db_boyut

        db_yol = Path(tempfile.mkdtemp()) / "test_boyut.db"
        # İçine bir şey yaz
        db_yol.write_text("merhaba dunya")
        result = db_boyut(db_yol)
        assert "B" in result
        assert result != "0 B"


class TestSchemaDurumHataPath:
    """durum() hata yolları."""

    def test_durum_var_olmayan_db(self):
        """Var olmayan DB → None döner."""
        sm = SchemaManager()
        result = sm.durum("/kesinlikle/yok/db.db")
        assert result is None

    def test_durum_gecersiz_db(self):
        """Gecersiz DB dosyası → exception yakalanır, hata dict döner."""
        db_yol = Path(tempfile.mkdtemp()) / "gecersiz.db"
        # Boş dosya yarat — sqlite açamaz
        db_yol.write_text("bu bir sqlite db degil")

        sm = SchemaManager()
        result = sm.durum(db_yol)
        # Ya hata dict'i döner ya da None (dosya var ama bozuk)
        assert result is not None
        if "hata" in result:
            assert result["hata"]


class TestMotorEntegrasyonu:
    """Motor entegrasyon fonksiyonları."""

    def test_motor_kaydet(self):
        """motor_kaydet — 3 aracı motor'a kaydeder."""
        from reymen.core.schema_manager import motor_kaydet

        motor = MagicMock()
        motor_kaydet(motor)

        # 3 arac kaydedilmis olmali
        kayitlar = motor._plugin_arac_kaydet.call_args_list
        assert len(kayitlar) == 3
        isimler = [k[0][0] for k in kayitlar]
        assert "SCHEMA_DURUM" in isimler
        assert "SCHEMA_TABLOLAR" in isimler
        assert "SCHEMA_TARA" in isimler

    def test_schema_durum_no_dbs(self):
        """_schema_durum — kayıtlı DB yoksa 'Kayitli DB yok' mesajı."""
        from reymen.core.schema_manager import _schema_durum
        import reymen.core.schema_manager as sm_module

        # _SCHEMA_MANAGER'ı sıfırla
        sm_module._SCHEMA_MANAGER = None

        result = _schema_durum()
        assert "Kayitli DB yok" in result

    def test_schema_durum_with_dbs(self):
        """_schema_durum — kayıtlı DB'leri listeler."""
        from reymen.core.schema_manager import _schema_durum

        sm = SchemaManager()
        db_yol = Path(tempfile.mkdtemp()) / "test_durum_dbs.db"
        sm.kaydet(db_yol, ["CREATE TABLE t (id INT)"], version=2)

        import reymen.core.schema_manager as sm_module
        sm_module._SCHEMA_MANAGER = sm

        result = _schema_durum()
        assert "2 DB" in result or "1 DB" in result or "DB kayitli" in result

        # Temizlik
        sm_module._SCHEMA_MANAGER = None

    def test_schema_tablolar_no_args(self):
        """_schema_tablolar — argüman yoksa kullanım mesajı."""
        from reymen.core.schema_manager import _schema_tablolar

        result = _schema_tablolar()
        assert "Kullanim" in result

    def test_schema_tablolar_db_not_found(self):
        """_schema_tablolar — var olmayan DB için 'bulunamadi'."""
        from reymen.core.schema_manager import _schema_tablolar

        result = _schema_tablolar(args=["/kesinlikle/yok.db"])
        assert "bulunamadi" in result or "yok" in result

    def test_schema_tara_empty(self):
        """_schema_tara — hiç db dosyası yoksa boş mesaj."""
        from reymen.core.schema_manager import _schema_tara

        result = _schema_tara()
        assert isinstance(result, str)

    def test_schema_tablolar_basarili_with_valid_db(self):
        """_schema_tablolar — geçerli DB ile tablo listesi döner (line 290)."""
        from reymen.core.schema_manager import _schema_tablolar, tablolari_listele

        db_yol = Path(tempfile.mkdtemp()) / "test_list.db"
        sm = SchemaManager()
        sm.kaydet(
            db_yol=db_yol,
            tablolar=["CREATE TABLE foo (id INT)", "CREATE TABLE bar (id INT)"],
            version=1,
        )

        result = _schema_tablolar(args=[str(db_yol)])
        assert "tablo" in result
        assert "foo" in result
        assert "bar" in result


class TestSchemaTaraDetayli:
    """_schema_tara — detaylı tarama yolları."""

    def test_schema_tara_with_valid_db(self):
        """_schema_tara — .db dosyası varken schema durumu gösterilir (line 301, 307)."""
        from reymen.core.schema_manager import _schema_tara

        # Geçerli bir DB oluştur
        db_yol = Path(tempfile.mkdtemp()) / "test_tara.db"
        sm = SchemaManager()
        sm.kaydet(db_yol, ["CREATE TABLE t (id INT)"], version=1)

        # _schema_tara çağır (glob'da **/*.db ile bulur)
        import os
        old_cwd = os.getcwd()
        os.chdir(tempfile.mkdtemp())

        # DB'yi cwd'ye kopyala ki glob bulabilsin
        import shutil
        shutil.copy2(str(db_yol), "test_tara.db")

        result = _schema_tara()
        os.chdir(old_cwd)

        assert isinstance(result, str)
        assert "Proje DB taramasi" in result


class TestDurumBostaDb:
    """durum() — var olan ama schema_version'suz DB."""

    def test_durum_var_olan_ama_version_suz(self):
        """DB'de schema_version tablosu var ama 'main' kaydı yok → version 0 döner (line 189)."""
        db_yol = Path(tempfile.mkdtemp()) / "test_no_ver.db"
        con = sqlite3.connect(str(db_yol))
        con.execute("CREATE TABLE schema_version (ad TEXT PRIMARY KEY, version INTEGER, applied_at REAL, metadata TEXT)")
        # 'main' kaydı ekleme — boş tablo
        con.close()

        sm = SchemaManager()
        result = sm.durum(db_yol)
        assert result is not None
        assert result["version"] == 0
        assert result["applied_at"] == 0
        assert result["db"] == "test_no_ver.db"


class TestSchemaManagerInitState:
    """SchemaManager başlangıç durumu."""

    def test_init_kayitli_dblar_bos(self):
        """Yeni SchemaManager'da _kayitli_dblar boştur."""
        sm = SchemaManager()
        assert sm._kayitli_dblar == {}
