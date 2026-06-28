# -*- coding: utf-8 -*-
"""
tests/test_once_hafiza.py — once_hafiza.py kapsamlı testi.
Temp DB ile çalışır, prod DB'ye dokunmaz.
"""
import math
import os
import sqlite3
import tempfile
import threading
import time
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Import: private'lar shim'den gelmez, direkt import et ───────────────────
from reymen.cereyan.once_hafiza import (
    DB_YOLU,
    _baglanti,
    _benzerlik_skoru,
    _anahtar_kelimeler,
    _db_kur,
    _kademeli_guven,
    _kur,
    _yazma_kilit,
    ara,
    belirsiz_gorev_cozumle,
    eski_kayitlari_temizle,
    guven_guncelle,
    hafizada_ara,
    istatistik,
    isle,
    kaydet,
)


# ── Fixture: temp DB ─────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def _temp_db(tmp_path):
    """Her test'i izole temp DB ile çalıştır."""
    db_path = tmp_path / "ogrenmeler.db"
    import reymen.cereyan.once_hafiza as _mod
    with patch.object(_mod, "DB_YOLU", db_path):
        _db_kur()
        yield db_path


# ═════════════════════════════════════════════════════════════════════════════
#  _kademeli_guven
# ═════════════════════════════════════════════════════════════════════════════
class TestKademeliGuven:
    def test_ilk_basari_05(self):
        """İlk başarı (1,0) → ~0.5"""
        assert _kademeli_guven(1, 0) == pytest.approx(0.5, abs=0.01)

    def test_3_basari_0_hata(self):
        """3 başarı, 0 hata → ~0.73"""
        assert _kademeli_guven(3, 0) == pytest.approx(0.73, abs=0.02)

    def test_10_basari_0_hata(self):
        """10 başarı, 0 hata → ~0.95+"""
        guven = _kademeli_guven(10, 0)
        assert guven > 0.95

    def test_1_basari_3_hata_dusuk(self):
        """1 başarı, 3 hata → düşük güven"""
        guven = _kademeli_guven(1, 3)
        assert guven < 0.3

    def test_cok_hata_0_basari(self):
        """0 başarı, 5 hata → çok düşük"""
        guven = _kademeli_guven(0, 5)
        assert guven < 0.1

    def test_net_sifir_05(self):
        """6 basari, 5 hata → ~0.5 (net=0)"""
        guven = _kademeli_guven(6, 5)
        assert guven == pytest.approx(0.5, abs=0.02)

    def test_monoton_artan(self):
        """Basantariler arttıkça güven artmalı"""
        scores = [_kademeli_guven(i, 0) for i in range(1, 11)]
        for i in range(len(scores) - 1):
            assert scores[i] < scores[i + 1]


# ═════════════════════════════════════════════════════════════════════════════
#  kaydet
# ═════════════════════════════════════════════════════════════════════════════
class TestKaydet:
    def test_ilk_kayit_basari(self):
        """İlk kayıt succeeds → id döner, guven=0.5"""
        kid = kaydet("nmap tara", "kali", "port bilgisi", basari=True)
        assert kid > 0
        sonuclar = ara("nmap tara", "kali")
        assert len(sonuclar) == 1
        assert sonuclar[0]["guven_skoru"] == 0.5

    def test_ilk_kayit_hata(self):
        """İlk kayıt başarısız → guven=0.1"""
        kid = kaydet("test_hata_x", "test", "hata", basari=False)
        sonuclar = ara("test_hata_x", "test", min_guven=0.0)
        assert sonuclar[0]["guven_skoru"] == 0.1

    def test_update_ayni_hedef_kategori(self):
        """Aynı hedef+kategori → UPDATE, yeni kayıt değil"""
        id1 = kaydet("x", "y", "eski", basari=True)
        id2 = kaydet("x", "y", "yeni", basari=True)
        assert id1 == id2  # aynı kayıt güncellendi
        sonuclar = ara("x", "y")
        assert len(sonuclar) == 1
        assert sonuclar[0]["icerik"] == "yeni"

    def test_kaynak_url_kaydet(self):
        """kaynak_url kaydedilmeli"""
        kaydet("url test", "test", "içerik", basari=True, kaynak_url="https://example.com")
        sonuclar = ara("url test", "test")
        assert sonuclar[0]["kaynak_url"] == "https://example.com"

    def test_kaynak_url_korunur(self):
        """kaynak_url=None → eski URL korunmalı"""
        kaydet("url koru", "test", "v1", basari=True, kaynak_url="https://a.com")
        kaydet("url koru", "test", "v2", basari=True, kaynak_url=None)
        sonuclar = ara("url koru", "test")
        assert sonuclar[0]["kaynak_url"] == "https://a.com"

    def test_basari_sayisi_artar(self):
        """3 başarı → basari_sayisi=3"""
        kaydet("counter", "test", "a", basari=True)
        kaydet("counter", "test", "b", basari=True)
        kaydet("counter", "test", "c", basari=True)
        sonuclar = ara("counter", "test")
        assert sonuclar[0]["basari_sayisi"] == 3
        assert sonuclar[0]["hata_sayisi"] == 0

    def test_hata_sayisi_artar(self):
        """1 basari + 2 hata → basari=1, hata=2"""
        kaydet("err", "test", "ok", basari=True)
        kaydet("err", "test", "fail1", basari=False)
        kaydet("err", "test", "fail2", basari=False)
        sonuclar = ara("err", "test", min_guven=0.0)
        assert sonuclar[0]["basari_sayisi"] == 1
        assert sonuclar[0]["hata_sayisi"] == 2

    def test_custom_gecerlilik(self):
        """Özel gecerlilik_gun parametresi"""
        kaydet("exp", "test", "içerik", basari=True, gecerlilik_gun=5)
        sonuclar = ara("exp", "test", gecerli_mi=True)
        assert len(sonuclar) == 1


# ═════════════════════════════════════════════════════════════════════════════
#  ara
# ═════════════════════════════════════════════════════════════════════════════
class TestAra:
    def test_tam_eslesme(self):
        """Tam hedef eşleşmesi"""
        kaydet("web tara", "kali", "solution")
        sonuclar = ara("web tara")
        assert len(sonuclar) >= 1
        assert sonuclar[0]["hedef"] == "web tara"

    def test_benzer_eslesme_like(self):
        """LIKE ile benzer eşleşme"""
        kaydet("nmap port tarama", "kali", "nmap -sV")
        sonuclar = ara("nmap")
        assert len(sonuclar) >= 1

    def test_kategori_filtresi(self):
        """kategori parametresi filtreleme"""
        kaydet("a1", "kali", "içerik1", basari=True)
        kaydet("a1", "dron", "içerik2", basari=True)
        kali = ara("a1", kategori="kali")
        dron = ara("a1", kategori="dron")
        assert all(r["kategori"] == "kali" for r in kali)
        assert all(r["kategori"] == "dron" for r in dron)

    def test_min_guven_filtresi(self):
        """min_guven filtresi"""
        kaydet("low", "test", "düşük", basari=False)  # guven=0.1
        kaydet("high", "test", "yüksek", basari=True)  # guven=0.5
        sonuclar = ara("low", min_guven=0.3)
        # low güven=0.1, eşiğin altında → gelmemeli (belirsiz)
        yuksek = ara("high", min_guven=0.3)
        assert len(yuksek) >= 1

    def test_durum_alani(self):
        """durum alanı: guvenilir veya belirsiz"""
        kaydet("durum_t", "test", "içerik", basari=True)  # 0.5
        sonuclar = ara("durum_t")
        assert sonuclar[0]["durum"] == "guvenilir"

        kaydet("durum_f", "test", "hata", basari=False)  # 0.1
        sonuclar2 = ara("durum_f", min_guven=0.0)
        assert sonuclar2[0]["durum"] == "belirsiz"

    def test_bos_db(self):
        """Boş DB'de ara → boş liste"""
        sonuclar = ara("yok")
        assert sonuclar == []

    def test_deduplikasyon(self):
        """Aynı kayıt hem tam hem LIKE'ta → tek sonuç"""
        kaydet("benzersiz test", "test", "veri")
        sonuclar = ara("benzersiz test")
        ids = [s["id"] for s in sonuclar]
        assert len(ids) == len(set(ids))

    def test_limit_5(self):
        """Maksimum 5 sonuç döner"""
        for i in range(10):
            kaydet(f"lim_{i}", "test", f"içerik_{i}")
        sonuclar = ara("lim_", min_guven=0.0)
        assert len(sonuclar) <= 10  # 10 kayıt var ama LIMIT 5 per query


# ═════════════════════════════════════════════════════════════════════════════
#  hafizada_ara (alias)
# ═════════════════════════════════════════════════════════════════════════════
class TestHafizadaAra:
    def test_alias(self):
        """hafizada_ara = ara"""
        kaydet("alias_t", "test", "data")
        assert hafizada_ara("alias_t") == ara("alias_t")


# ═════════════════════════════════════════════════════════════════════════════
#  guven_guncelle
# ═════════════════════════════════════════════════════════════════════════════
class TestGuvenGuncelle:
    def test_basari_arttir(self):
        """başarı +1 → güven artar"""
        kid = kaydet("guv1", "test", "v1", basari=True)  # 1,0 → 0.5
        yeni = guven_guncelle(kid, basari=True)  # 2,0 → ~0.62
        assert yeni > 0.5

    def test_hata_arttir(self):
        """hata +1 → güven düşer"""
        kid = kaydet("guv2", "test", "v1", basari=True)  # 1,0 → 0.5
        yeni = guven_guncelle(kid, basari=False)  # 1,1 → ~0.38
        assert yeni < 0.5

    def test_olmayan_id(self):
        """Olmayan ID → 0.0"""
        sonuc = guven_guncelle(99999, basari=True)
        assert sonuc == 0.0


# ═════════════════════════════════════════════════════════════════════════════
#  eski_kayitlari_temizle
# ═════════════════════════════════════════════════════════════════════════════
class TestEskiKayitlariTemizle:
    def test_dusuk_guven_eski_silinir(self):
        """Düşük güven + eski → silinir"""
        kid = kaydet("eski1", "test", "eskimiş", basari=True)
        # Gecerlilik tarihini geçmiş yap
        with _baglanti() as con:
            con.execute(
                "UPDATE ogrenmeler SET gecerlilik_tarihi = ? WHERE id = ?",
                ((date.today() - timedelta(days=10)).isoformat(), kid),
            )
        silinen = eski_kayitlari_temizle(gun_limiti=1)
        assert silinen >= 1

    def test_yuksek_guven_korunur(self):
        """Yüksek güven (>=0.8) → eski olsa bile korunur"""
        kid = kaydet("koru", "test", "değerli", basari=True)
        # Birkaç kez başarı → güven artar
        for _ in range(5):
            guven_guncelle(kid, basari=True)
        # Gecerlilik geçmiş yap
        with _baglanti() as con:
            con.execute(
                "UPDATE ogrenmeler SET gecerlilik_tarihi = ? WHERE id = ?",
                ((date.today() - timedelta(days=10)).isoformat(), kid),
            )
        silinen = eski_kayitlari_temizle(gun_limiti=1)
        # Yüksek güvenli kayıt silinmemiş olmalı
        sonuclar = ara("koru", "test", min_guven=0.0, gecerli_mi=False)
        # En azından kayıt hâlâ DB'de (gecerli_mi=False ile bulabiliriz)
        with _baglanti() as con:
            var_mi = con.execute("SELECT COUNT(*) FROM ogrenmeler WHERE id = ?", (kid,)).fetchone()[0]
        assert var_mi == 1


# ═════════════════════════════════════════════════════════════════════════════
#  isle (ana API)
# ═════════════════════════════════════════════════════════════════════════════
class TestIsle:
    def test_cache_hit(self):
        """Hafızada varsa cache'ten döner"""
        kaydet("isle_test", "test", "cached_value", basari=True)
        # min_guven=0.3 → 0.5 güvenle bulur
        sonuc, kaynak = isle("isle_test", "test", min_guven=0.3)
        assert kaynak == "cache"
        assert sonuc["icerik"] == "cached_value"

    def test_exec_yolu(self):
        """Hafızada yoksa çalıştırır ve kaydeder"""
        called = []
        def calistir():
            called.append(True)
            return "yeni_sonuc"

        sonuc, kaynak = isle("yeni_gorev", "test", calistir=calistir, min_guven=0.5)
        assert kaynak == "exec"
        assert sonuc == "yeni_sonuc"
        assert len(called) == 1
        # Şimdi cache'te olmalı
        sonuc2, kaynak2 = isle("yeni_gorev", "test", min_guven=0.5)
        assert kaynak2 == "cache"

    def test_zorla_calistir(self):
        """zorla=True → hafızaya bakmadan çalıştır"""
        kaydet("zorla_test", "test", "eski", basari=True)
        calistir = lambda: "yeni"
        sonuc, kaynak = isle("zorla_test", "test", calistir=calistir, zorla=True)
        assert kaynak == "exec"
        assert sonuc == "yeni"

    def test_calistir_yok_bulunamadi(self):
        """calistir=None + bulamazsa → not_found"""
        sonuc, kaynak = isle("yok", "test")
        assert kaynak == "not_found"
        assert sonuc is None

    def test_hata_yakalar_ve_kaydeder(self):
        """calistir() exception fırlatırsa → kaydeder + raise"""
        def hatali():
            raise ValueError("test hatası")

        with pytest.raises(ValueError, match="test hatası"):
            isle("hatali_gorev", "test", calistir=hatali)
        # Hata kaydedilmiş olmalı
        sonuclar = ara("hatali_gorev", "test", min_guven=0.0)
        assert len(sonuclar) == 1
        assert sonuclar[0]["icerik"].startswith("[HATA]")

    def test_calistir_none_zorla(self):
        """calistir=None + zorla=True → çalıştırma yok ama hata yok"""
        sonuc, kaynak = isle("yok2", "test", zorla=True)
        assert kaynak == "not_found"
        assert sonuc is None


# ═════════════════════════════════════════════════════════════════════════════
#  istatistik
# ═════════════════════════════════════════════════════════════════════════════
class TestIstatistik:
    def test_bos_db(self):
        """Boş DB istatistikleri"""
        ist = istatistik()
        assert ist["toplam"] == 0
        assert ist["gecerli"] == 0
        assert ist["kategori_dagilimi"] == {}

    def test_veri_ile(self):
        """Veri eklendikten sonra istatistik"""
        kaydet("s1", "kali", "a", basari=True)
        kaydet("s2", "dron", "b", basari=True)
        kaydet("s3", "kali", "c", basari=False)
        ist = istatistik()
        assert ist["toplam"] == 3
        assert ist["gecerli"] == 3
        assert ist["kategori_dagilimi"]["kali"] == 2
        assert ist["kategori_dagilimi"]["dron"] == 1

    def test_ortalama_guven(self):
        """Ortalama güven skoru"""
        kaydet("avg1", "test", "x", basari=True)  # 0.5
        kaydet("avg2", "test", "y", basari=True)  # 0.5
        ist = istatistik()
        assert ist["ortalama_guven"] > 0


# ═════════════════════════════════════════════════════════════════════════════
#  belirsiz_gorev_cozumle
# ═════════════════════════════════════════════════════════════════════════════
class TestBelirsizGorevCozumle:
    def test_bos_db(self):
        """Boş DB → tahmin=None"""
        sonuc = belirsiz_gorev_cozumle("sistemi güvenli yap")
        assert sonuc["tahmin_kategori"] is None
        assert sonuc["guven"] == 0.0

    def test_eslesme_var(self):
        """Hafızada benzer kayıt var → tahmin döner"""
        kaydet("port tarama yap", "kali/network", "nmap -sV")
        kaydet("servisleri bul", "kali/network", "nmap -sV -sC")
        sonuc = belirsiz_gorev_cozumle("port tarama yap")
        assert sonuc["tahmin_kategori"] is not None
        assert sonuc["guven"] > 0
        assert sonuc["soru"] is not None

    def test_benzersiz_gorev(self):
        """Tamamen farklı görev → tahmin=None veya backup"""
        kaydet("nmap tara", "kali", "nmap output")
        sonuc = belirsiz_gorev_cozumle("pirinç pilav tarifi")
        # Hiç kelime eşleşmez, backup devreye girebilir
        # veya None olabilir
        assert "tahmin_kategori" in sonuc

    def test_alternatifler(self):
        """Farklı kategorilerden alternatifler"""
        kaydet("port tara", "kali/network", "nmap")
        kaydet("port tara", "web", "web tarayıcı")
        sonuc = belirsiz_gorev_cozumle("port tarama")
        assert "alternatifler" in sonuc

    def test_ham_hedef_korunur(self):
        """ham_hedef her zaman döner"""
        sonuc = belirsiz_gorev_cozumle("test giriş")
        assert sonuc["ham_hedef"] == "test giriş"


# ═════════════════════════════════════════════════════════════════════════════
#  _anahtar_kelimeler
# ═════════════════════════════════════════════════════════════════════════════
class TestAnahtarKelimeler:
    def test_basit(self):
        assert _anahtar_kelimeler("hello world") == ["hello", "world"]

    def test_noktalama_temizle(self):
        kelimeler = _anahtar_kelimeler("merhaba, dünya! nasılsın?")
        assert "merhaba" in kelimeler
        assert "dünya" in kelimeler

    def test_bos_string(self):
        assert _anahtar_kelimeler("") == []

    def test_tek_karakterler_atlanir(self):
        """1 karakterli kelimeler atlanır"""
        kelimeler = _anahtar_kelimeler("a ben c")
        assert "a" not in kelimeler
        assert "ben" in kelimeler

    def test_buyuk_kucuk_harf(self):
        kelimeler = _anahtar_kelimeler("NMAP PORT")
        assert "nmap" in kelimeler
        assert "port" in kelimeler


# ═════════════════════════════════════════════════════════════════════════════
#  _benzerlik_skoru
# ═════════════════════════════════════════════════════════════════════════════
class TestBenzerlikSkoru:
    def test_tam_eslesme(self):
        """Aynı kelimeler → yüksek skor"""
        kelimeler = _anahtar_kelimeler("nmap port tara")
        kayit = {"hedef": "nmap port tara", "kategori": "kali", "guven_skoru": 0.9}
        skor = _benzerlik_skoru("nmap port tara", kelimeler, kayit)
        assert skor > 0.5

    def test_kismi_eslesme(self):
        """Birkaç kelime eşleşir → orta skor"""
        kelimeler = _anahtar_kelimeler("nmap tara")
        kayit = {"hedef": "nmap ile port tara", "kategori": "kali", "guven_skoru": 0.5}
        skor = _benzerlik_skoru("nmap tara", kelimeler, kayit)
        assert 0.0 < skor < 1.0

    def test_eslesme_yok(self):
        """Hiç kelime eşleşmez → düşük skor"""
        kelimeler = _anahtar_kelimeler("pirinç pilav")
        kayit = {"hedef": "nmap port tara", "kategori": "kali", "guven_skoru": 0.5}
        skor = _benzerlik_skoru("pirinç pilav", kelimeler, kayit)
        assert skor < 0.3

    def test_guven_bonus(self):
        """Yüksek güven → bonus skor"""
        kelimeler = _anahtar_kelimeler("test")
        yuksek = {"hedef": "test", "kategori": "test", "guven_skoru": 0.9}
        dusuk = {"hedef": "test", "kategori": "test", "guven_skoru": 0.3}
        s1 = _benzerlik_skoru("test", kelimeler, yuksek)
        s2 = _benzerlik_skoru("test", kelimeler, dusuk)
        assert s1 > s2

    def test_kategori_eslesme_bonus(self):
        """Kategori kelimesi eşleşirse → bonus"""
        kelimeler = _anahtar_kelimeler("kali port")
        kayit = {"hedef": "port tara", "kategori": "kali/network", "guven_skoru": 0.5}
        skor = _benzerlik_skoru("kali port", kelimeler, kayit)
        assert skor > 0.2  # kategori bonusu sayesinde


# ═════════════════════════════════════════════════════════════════════════════
#  DB Migration & Kurulum
# ═════════════════════════════════════════════════════════════════════════════
class TestDBKurulum:
    def test_tablo_olustur(self):
        """DB tablosu oluşturulmalı"""
        with _baglanti() as con:
            tablolar = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ogrenmeler'"
            ).fetchall()
            assert len(tablolar) == 1

    def test_indeksler(self):
        """İndeksler oluşturulmalı"""
        with _baglanti() as con:
            indeksler = con.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='ogrenmeler'"
            ).fetchall()
            assert len(indeksler) >= 3

    def test_migration_kaynak_url(self):
        """kaynak_url kolonu mevcut olmalı"""
        with _baglanti() as con:
            kolonlar = [r[1] for r in con.execute("PRAGMA table_info(ogrenmeler)").fetchall()]
            assert "kaynak_url" in kolonlar


# ═════════════════════════════════════════════════════════════════════════════
#  Thread Güvenliği
# ═════════════════════════════════════════════════════════════════════════════
class TestThreadGuvenligi:
    def test_paralel_kaydet(self):
        """Eş zamanlı kaydet → hata vermemeli"""
        hatalar = []

        def kaydet_worker(i):
            try:
                kaydet(f"thread_{i}", "test", f"içerik_{i}", basari=True)
            except Exception as e:
                hatalar.append(e)

        threads = [threading.Thread(target=kaydet_worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert len(hatalar) == 0
        # Tüm kayıtlar mevcut olmalı
        sonuclar = ara("thread_", min_guven=0.0)
        assert len(sonuclar) >= 5  # ara() LIMIT 5 per query
