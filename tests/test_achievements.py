# -*- coding: utf-8 -*-
"""tools/achievements.py icin kapsamli pytest testleri.

Her testte _hermetic_environment autouse fixture'i calisir.
REYMEN_DIR = Path(__file__).parent.parent / '.reymen' yolu monkeypatch ile
tmp_path altina yonlendirilir.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest


@pytest.fixture
def reymen_ortam(monkeypatch, tmp_path):
    """Test icin gerekli .reymen dizin yapisini hazirlar.

    REYMEN_DIR / ACHIEVEMENTS_DIR / STATS_DIR degiskenlerini tmp_path altina
    monkeypatch ile yonlendirir.
    """
    fake_reymen = tmp_path / ".reymen"
    fake_reymen.mkdir()

    import tools.achievements as ach

    monkeypatch.setattr(ach, "REYMEN_DIR", fake_reymen)
    monkeypatch.setattr(ach, "ACHIEVEMENTS_DIR", fake_reymen / "achievements")
    monkeypatch.setattr(ach, "STATS_DIR", fake_reymen / "stats")

    return ach, fake_reymen


class TestCheckAchievements:
    """check_achievements() fonksiyonu testleri."""

    def test_acemi_kasif_kazanilir(self, reymen_ortam):
        """gorev_tamamlandi=True ile Acemi Kasif rozeti kazanilir."""
        ach, _ = reymen_ortam
        yeni = ach.check_achievements(gorev_tamamlandi=True)
        assert len(yeni) == 1
        assert yeni[0]["id"] == "novice_explorer"
        assert yeni[0]["name"] == "Acemi Kaşif"

    def test_idempotent_tekrar_cagir(self, reymen_ortam):
        """Ayni rozet tekrar kazanilamaz (idempotent)."""
        ach, _ = reymen_ortam
        ilk = ach.check_achievements(gorev_tamamlandi=True)
        assert len(ilk) == 1  # ilk seferde kazanilir

        ikinci = ach.check_achievements(gorev_tamamlandi=True)
        assert len(ikinci) == 0  # tekrar kazanilmaz (idempotent)

    def test_acemi_kasif_olmadan_bos_doner(self, reymen_ortam):
        """gorev_tamamlandi=False iken rozet kazanilmaz."""
        ach, _ = reymen_ortam
        yeni = ach.check_achievements(gorev_tamamlandi=False)
        assert yeni == []

    def test_araç_kullanimi_ustasi(self, reymen_ortam):
        """3 farkli arac kullanilinca Alet Ustasi rozeti kazanilir."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        tools_file = stats_dir / "tools_used.json"
        tools_file.write_text(json.dumps(["terminal", "file", "web"]), encoding="utf-8")

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "tool_master" in ids

    def test_araç_kullanimi_yetersiz(self, reymen_ortam):
        """2 arac yeterli degil -> Alet Ustasi kazanilmaz."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        tools_file = stats_dir / "tools_used.json"
        tools_file.write_text(json.dumps(["terminal", "file"]), encoding="utf-8")

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "tool_master" not in ids

    def test_hata_avcisi(self, reymen_ortam):
        """5 hata duzeltilince Hata Avcisi rozeti kazanilir."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        errors_file = stats_dir / "errors_fixed.json"
        errors_file.write_text(json.dumps({"count": 5}), encoding="utf-8")

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "bug_hunter" in ids

    def test_hata_avcisi_yetersiz(self, reymen_ortam):
        """4 hata yeterli degil -> Hata Avcisi kazanilmaz."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        errors_file = stats_dir / "errors_fixed.json"
        errors_file.write_text(json.dumps({"count": 4}), encoding="utf-8")

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "bug_hunter" not in ids

    def test_kristalci(self, reymen_ortam):
        """skill_olusturuldu=True ile Kristalci rozeti kazanilir."""
        ach, _ = reymen_ortam
        yeni = ach.check_achievements(skill_olusturuldu=True)
        ids = [r["id"] for r in yeni]
        assert "crystallizer" in ids

    def test_hafiza_bekcisi(self, reymen_ortam):
        """20+ memory JSON dosyasi olunca Hafiza Bekcisi rozeti kazanilir."""
        ach, fake_reymen = reymen_ortam
        memory_dir = fake_reymen / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        for i in range(20):
            (memory_dir / f"mem_{i}.json").write_text("{}", encoding="utf-8")

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "memory_keeper" in ids

    def test_hafiza_bekcisi_yetersiz(self, reymen_ortam):
        """19 memory dosyasi yeterli degil."""
        ach, fake_reymen = reymen_ortam
        memory_dir = fake_reymen / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        for i in range(19):
            (memory_dir / f"mem_{i}.json").write_text("{}", encoding="utf-8")

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "memory_keeper" not in ids

    def test_kopru_kurucu(self, reymen_ortam):
        """2+ kanal kullanilinca Kopru Kurucu rozeti kazanilir."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        channels_file = stats_dir / "channels_used.json"
        channels_file.write_text(json.dumps(["kanal_a", "kanal_b"]), encoding="utf-8")

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "bridge_builder" in ids

    def test_kopru_kurucu_yetersiz(self, reymen_ortam):
        """1 kanal yeterli degil."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        channels_file = stats_dir / "channels_used.json"
        channels_file.write_text(json.dumps(["kanal_a"]), encoding="utf-8")

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "bridge_builder" not in ids

    def test_otonom(self, reymen_ortam):
        """kesintisiz_adim >= 5 olunca Otonom rozeti kazanilir."""
        ach, _ = reymen_ortam
        yeni = ach.check_achievements(kesintisiz_adim=5)
        ids = [r["id"] for r in yeni]
        assert "autonomous" in ids

    def test_otonom_yetersiz(self, reymen_ortam):
        """kesintisiz_adim=4 yeterli degil."""
        ach, _ = reymen_ortam
        yeni = ach.check_achievements(kesintisiz_adim=4)
        ids = [r["id"] for r in yeni]
        assert "autonomous" not in ids

    def test_reymen_master_otomatik(self, reymen_ortam):
        """Ilk 7 rozetin tamami kazanilinca ReYMeN Ustasi otomatik verilir."""
        ach, fake_reymen = reymen_ortam

        # Ilk 7 rozeti elle olustur
        ach_dir = fake_reymen / "achievements"
        ach_dir.mkdir(parents=True, exist_ok=True)
        for rid in ach.ILK_7_ROZET:
            roket_json = {
                "id": rid,
                "name": f"Test {rid}",
                "emoji": "⭐",
                "earned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            (ach_dir / f"{rid}.json").write_text(
                json.dumps(roket_json, ensure_ascii=False), encoding="utf-8"
            )

        # check_achievements cagir -> reymen_master otomatik kazanilir
        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "reymen_master" in ids

    def test_reymen_master_ihtiyac_duyulan(self, reymen_ortam):
        """7 rozetten biri eksikse ReYMeN Ustasi kazanilmaz."""
        ach, fake_reymen = reymen_ortam

        ach_dir = fake_reymen / "achievements"
        ach_dir.mkdir(parents=True, exist_ok=True)
        # Sadece 6 rozet olustur (novice_explorer eksik)
        for rid in ach.ILK_7_ROZET[1:]:  # novice_explorer haric 6 rozet
            roket_json = {
                "id": rid,
                "name": f"Test {rid}",
                "emoji": "⭐",
                "earned_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            (ach_dir / f"{rid}.json").write_text(
                json.dumps(roket_json, ensure_ascii=False), encoding="utf-8"
            )

        yeni = ach.check_achievements()
        ids = [r["id"] for r in yeni]
        assert "reymen_master" not in ids

    def test_tum_rozet_akisi(self, reymen_ortam):
        """Tüm rozetlerin tek bir cagrida kazanilabilmesi."""
        ach, fake_reymen = reymen_ortam

        # Gerekli dosyalari hazirla
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        (stats_dir / "tools_used.json").write_text(
            json.dumps(["terminal", "file", "web"]), encoding="utf-8"
        )
        (stats_dir / "errors_fixed.json").write_text(
            json.dumps({"count": 5}), encoding="utf-8"
        )
        (stats_dir / "channels_used.json").write_text(
            json.dumps(["kanal_a", "kanal_b"]), encoding="utf-8"
        )

        memory_dir = fake_reymen / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        for i in range(20):
            (memory_dir / f"mem_{i}.json").write_text("{}", encoding="utf-8")

        # Hepsi birden
        yeni = ach.check_achievements(
            gorev_tamamlandi=True,
            skill_olusturuldu=True,
            kesintisiz_adim=5,
        )
        ids = [r["id"] for r in yeni]
        # Acemi Kasif
        assert "novice_explorer" in ids
        # 2-6 data-based
        assert "tool_master" in ids
        assert "bug_hunter" in ids
        assert "crystallizer" in ids
        assert "memory_keeper" in ids
        assert "bridge_builder" in ids
        assert "autonomous" in ids
        # reymen_master da otomatik
        assert "reymen_master" in ids
        assert len(yeni) == 8


class TestVerRozet:
    """_ver_rozet() fonksiyonu testleri."""

    def test_rozet_verme_basari(self, reymen_ortam):
        """Gecerli bir rozet ID'si ile rozet verilir."""
        ach, fake_reymen = reymen_ortam
        sonuc = ach._ver_rozet("novice_explorer")
        assert sonuc is not None
        assert sonuc["id"] == "novice_explorer"
        assert sonuc["name"] == "Acemi Kaşif"
        assert "earned_at" in sonuc

    def test_rozet_tekrari_none(self, reymen_ortam):
        """Ayni rozet iki kez verilmeye calisilirsa None doner."""
        ach, _ = reymen_ortam
        ilk = ach._ver_rozet("novice_explorer")
        assert ilk is not None
        ikinci = ach._ver_rozet("novice_explorer")
        assert ikinci is None

    def test_gecersiz_rozet_id(self, reymen_ortam):
        """Tanimsiz bir rozet ID'si icin None doner."""
        ach, _ = reymen_ortam
        sonuc = ach._ver_rozet("olmayan_rozet")
        assert sonuc is None

    def test_rozet_dosyaya_yazilir(self, reymen_ortam):
        """Rozet verilince .json dosyasi olusur."""
        ach, fake_reymen = reymen_ortam
        ach._ver_rozet("novice_explorer")
        dosya = fake_reymen / "achievements" / "novice_explorer.json"
        assert dosya.exists()
        icerik = json.loads(dosya.read_text(encoding="utf-8"))
        assert icerik["id"] == "novice_explorer"
        assert icerik["name"] == "Acemi Kaşif"


class TestRozetVarMi:
    """_rozet_var_mi() fonksiyonu testleri."""

    def test_rozet_var(self, reymen_ortam):
        """Var olan rozet icin True doner."""
        ach, _ = reymen_ortam
        ach._ver_rozet("novice_explorer")
        assert ach._rozet_var_mi("novice_explorer") is True

    def test_rozet_yok(self, reymen_ortam):
        """Var olmayan rozet icin False doner."""
        ach, _ = reymen_ortam
        assert ach._rozet_var_mi("novice_explorer") is False


class TestTumRozetleriListele:
    """_tum_rozetleri_listele() fonksiyonu testleri."""

    def test_bos_liste(self, reymen_ortam):
        """Henuz rozet kazanilmamissa [] doner."""
        ach, _ = reymen_ortam
        assert ach._tum_rozetleri_listele() == []

    def test_tek_rozet(self, reymen_ortam):
        """Bir rozet kazanilinca listede gorunur."""
        ach, _ = reymen_ortam
        ach._ver_rozet("novice_explorer")
        liste = ach._tum_rozetleri_listele()
        assert len(liste) == 1
        assert liste[0]["id"] == "novice_explorer"

    def test_coklu_rozet(self, reymen_ortam):
        """Birden fazla rozet kazanilinca hepsi listelenir."""
        ach, _ = reymen_ortam
        ach._ver_rozet("novice_explorer")
        ach._ver_rozet("tool_master")
        ach._ver_rozet("bug_hunter")
        liste = ach._tum_rozetleri_listele()
        assert len(liste) == 3
        ids = [r["id"] for r in liste]
        assert "novice_explorer" in ids
        assert "tool_master" in ids
        assert "bug_hunter" in ids

    def test_sirali_liste(self, reymen_ortam):
        """Rozetler alfabetik/sirali doner (glob ile)."""
        ach, _ = reymen_ortam
        ach._ver_rozet("tool_master")
        ach._ver_rozet("novice_explorer")
        liste = ach._tum_rozetleri_listele()
        # Alfabetik sirada: novice_explorer, tool_master
        assert liste[0]["id"] == "novice_explorer"
        assert liste[1]["id"] == "tool_master"

    def test_bozuk_dosya_ignor(self, reymen_ortam):
        """Bozuk JSON dosyasi sessizce gecilir."""
        ach, fake_reymen = reymen_ortam
        ach_dir = fake_reymen / "achievements"
        ach_dir.mkdir(parents=True, exist_ok=True)
        # Gecerli rozet
        ach._ver_rozet("novice_explorer")
        # Bozuk dosya
        (ach_dir / "bozuk.json").write_text("{{gecersiz json", encoding="utf-8")
        # Sadece gecerli rozet donmeli
        liste = ach._tum_rozetleri_listele()
        assert len(liste) == 1
        assert liste[0]["id"] == "novice_explorer"


class TestSayacArtir:
    """_sayac_artir() fonksiyonu testleri."""

    def test_sayac_baslangic(self, reymen_ortam):
        """Sayac ilk cagrildiginda 1 doner."""
        ach, _ = reymen_ortam
        deger = ach._sayac_artir("deneme.json")
        assert deger == 1

    def test_sayac_arttirma(self, reymen_ortam):
        """Sayac her cagrida 1 artar."""
        ach, _ = reymen_ortam
        assert ach._sayac_artir("deneme.json") == 1
        assert ach._sayac_artir("deneme.json") == 2
        assert ach._sayac_artir("deneme.json") == 3

    def test_sayac_ozel_anahtar(self, reymen_ortam):
        """Ozel bir anahtar ile sayac calisir."""
        ach, _ = reymen_ortam
        deger = ach._sayac_artir("test.json", anahtar="custom_key")
        assert deger == 1
        deger2 = ach._sayac_artir("test.json", anahtar="custom_key")
        assert deger2 == 2

    def test_sayac_birden_cok_dosya(self, reymen_ortam):
        """Farkli dosyalar bagimsiz sayaçlardir."""
        ach, _ = reymen_ortam
        assert ach._sayac_artir("a.json") == 1
        assert ach._sayac_artir("b.json") == 1
        assert ach._sayac_artir("a.json") == 2
        assert ach._sayac_artir("b.json") == 2


class TestListeyeEkle:
    """_listeye_ekle() fonksiyonu testleri."""

    def test_ekleme_basit(self, reymen_ortam):
        """Listeye yeni bir deger eklenir."""
        ach, fake_reymen = reymen_ortam
        ach._listeye_ekle("test_liste.json", "deger1")
        dosya = fake_reymen / "stats" / "test_liste.json"
        assert dosya.exists()
        icerik = json.loads(dosya.read_text(encoding="utf-8"))
        assert icerik == ["deger1"]

    def test_benzersiz_ekleme(self, reymen_ortam):
        """Ayni deger iki kez eklenmez (benzersiz)."""
        ach, fake_reymen = reymen_ortam
        ach._listeye_ekle("test_liste.json", "deger1")
        ach._listeye_ekle("test_liste.json", "deger1")  # tekrar
        dosya = fake_reymen / "stats" / "test_liste.json"
        icerik = json.loads(dosya.read_text(encoding="utf-8"))
        assert icerik == ["deger1"]

    def test_coklu_ekleme(self, reymen_ortam):
        """Birden fazla farkli deger eklenebilir."""
        ach, fake_reymen = reymen_ortam
        ach._listeye_ekle("test_liste.json", "a")
        ach._listeye_ekle("test_liste.json", "b")
        ach._listeye_ekle("test_liste.json", "c")
        dosya = fake_reymen / "stats" / "test_liste.json"
        icerik = json.loads(dosya.read_text(encoding="utf-8"))
        assert icerik == ["a", "b", "c"]


class TestKullanilanAraclar:
    """_kullanilan_araclar() fonksiyonu testleri."""

    def test_bos_liste(self, reymen_ortam):
        """tools_used.json yoksa [] doner."""
        ach, _ = reymen_ortam
        assert ach._kullanilan_araclar() == []

    def test_arac_listesi(self, reymen_ortam):
        """tools_used.json varsa icerigini dondurur."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        (stats_dir / "tools_used.json").write_text(
            json.dumps(["terminal", "file"]), encoding="utf-8"
        )
        assert ach._kullanilan_araclar() == ["terminal", "file"]


class TestHataSayisi:
    """_hata_sayisi() fonksiyonu testleri."""

    def test_sifir_hata(self, reymen_ortam):
        """errors_fixed.json yoksa 0 doner."""
        ach, _ = reymen_ortam
        assert ach._hata_sayisi() == 0

    def test_hata_sayisi(self, reymen_ortam):
        """errors_fixed.json varsa count degerini doner."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        (stats_dir / "errors_fixed.json").write_text(
            json.dumps({"count": 7}), encoding="utf-8"
        )
        assert ach._hata_sayisi() == 7


class TestHafizaSayisi:
    """_hafiza_sayisi() fonksiyonu testleri."""

    def test_sifir_hafiza(self, reymen_ortam):
        """memory klasoru yoksa 0 doner."""
        ach, _ = reymen_ortam
        assert ach._hafiza_sayisi() == 0

    def test_bos_klasor(self, reymen_ortam):
        """Bos memory klasoru 0 doner."""
        ach, fake_reymen = reymen_ortam
        memory_dir = fake_reymen / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        assert ach._hafiza_sayisi() == 0

    def test_json_sayisi(self, reymen_ortam):
        """Sadece .json dosyalarini sayar."""
        ach, fake_reymen = reymen_ortam
        memory_dir = fake_reymen / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        (memory_dir / "a.json").write_text("{}", encoding="utf-8")
        (memory_dir / "b.json").write_text("{}", encoding="utf-8")
        (memory_dir / "c.txt").write_text("not json", encoding="utf-8")  # sayilmaz
        assert ach._hafiza_sayisi() == 2


class TestKanalSayisi:
    """_kanal_sayisi() fonksiyonu testleri."""

    def test_sifir_kanal(self, reymen_ortam):
        """channels_used.json yoksa 0 doner."""
        ach, _ = reymen_ortam
        assert ach._kanal_sayisi() == 0

    def test_kanal_sayisi(self, reymen_ortam):
        """channels_used.json'daki eleman sayisini doner."""
        ach, fake_reymen = reymen_ortam
        stats_dir = fake_reymen / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        (stats_dir / "channels_used.json").write_text(
            json.dumps(["a", "b", "c"]), encoding="utf-8"
        )
        assert ach._kanal_sayisi() == 3


class TestRozetListele:
    """rozet_listele() fonksiyonu testleri."""

    def test_rozet_yok_metni(self, reymen_ortam):
        """Henuz rozet yoksa ozel metin doner."""
        ach, _ = reymen_ortam
        metin = ach.rozet_listele()
        assert "Henüz rozet kazanılmamış" in metin

    def test_rozet_var_metni(self, reymen_ortam):
        """Rozetler okunabilir metin olarak listelenir."""
        ach, _ = reymen_ortam
        ach._ver_rozet("novice_explorer")
        metin = ach.rozet_listele()
        assert "[Achievements]" in metin
        assert "Acemi Kaşif" in metin
        assert "🥉" in metin

    def test_coklu_rozet_metni(self, reymen_ortam):
        """Birden fazla rozet metinde gorunur."""
        ach, _ = reymen_ortam
        ach._ver_rozet("novice_explorer")
        ach._ver_rozet("tool_master")
        metin = ach.rozet_listele()
        assert metin.count("\n") >= 2  # en az 2 rozet satiri


class TestConstants:
    """Sabitler ve yapi testleri."""

    def test_rozet_tanimlari_sayisi(self, reymen_ortam):
        """8 rozet tanimi vardir."""
        ach, _ = reymen_ortam
        assert len(ach.ROZET_TANIMLARI) == 8

    def test_ilk_7_rozet(self, reymen_ortam):
        """ILK_7_ROZET'te reymen_master haric 7 rozet vardir."""
        ach, _ = reymen_ortam
        assert len(ach.ILK_7_ROZET) == 7
        assert "reymen_master" not in ach.ILK_7_ROZET

    def test_rozet_tanimlarinda_zorunlu_alanlar(self, reymen_ortam):
        """Her rozet taniminda id, name, emoji vardir."""
        ach, _ = reymen_ortam
        for r in ach.ROZET_TANIMLARI:
            assert "id" in r
            assert "name" in r
            assert "emoji" in r
