# -*- coding: utf-8 -*-
"""test_reymen_skill_cli.py — SkillCLI icin kapsamli pytest testleri."""

import os
import json
import tempfile
from pathlib import Path
import pytest
from reymen_skill_cli import SkillCLI


# ── Fixture ─────────────────────────────────────────────────────────────


@pytest.fixture
def temp_skill_yolu(tmp_path):
    """Gecici skills dizini olustur."""
    yol = tmp_path / "skills"
    yol.mkdir()
    return yol


@pytest.fixture
def cli(temp_skill_yolu):
    """SkillCLI ornegi (gecici dizin ile)."""
    return SkillCLI(skill_yolu=str(temp_skill_yolu))


def _skill_olustur(
    cli: SkillCLI, kategori: str, ad: str, description: str = "", tags: str = ""
):
    """Yardimci: test icin SKILL.md olustur."""
    kat_dizini = cli._kok / kategori
    kat_dizini.mkdir(parents=True, exist_ok=True)
    skill_dizini = kat_dizini / ad
    skill_dizini.mkdir(parents=True, exist_ok=True)
    md = skill_dizini / "SKILL.md"
    icerik = "---\n"
    if description:
        icerik += f"description: {description}\n"
    if tags:
        icerik += f"tags: {tags}\n"
    icerik += "---\n\n# Skill Icerigi\n"
    md.write_text(icerik, encoding="utf-8")


# ── Test 1: Baslangic ───────────────────────────────────────────────────


class TestBaslangic:
    def test_varsayilan_yol_olusturur(self, tmp_path):
        """Varsayilan yolda skills dizini olusturulmali."""
        yol = tmp_path / "skills"
        cli = SkillCLI(skill_yolu=str(yol))
        assert yol.exists()

    def test_kok_dizini_dogru(self, temp_skill_yolu):
        """_kok degiskeni dogru yolu gostermeli."""
        cli = SkillCLI(skill_yolu=str(temp_skill_yolu))
        assert cli._kok == temp_skill_yolu

    def test_bos_baslangic_liste(self, cli):
        """Baslangicta liste bos olmali."""
        assert cli.liste() == []

    def test_bos_kategoriler(self, cli):
        """Baslangicta kategori_liste bos olmali."""
        assert cli.kategori_liste() == []


# ── Test 2: liste ───────────────────────────────────────────────────────


class TestListe:
    def test_tek_skill_listele(self, cli, temp_skill_yolu):
        """Tek skill listelenebilmeli."""
        _skill_olustur(cli, "genel", "test_skill", description="Test aciklamasi")
        liste = cli.liste()
        assert len(liste) == 1
        assert liste[0]["ad"] == "test_skill"

    def test_coklu_skill_listele(self, cli):
        """Birden cok skill listelenebilmeli."""
        _skill_olustur(cli, "genel", "skill_a")
        _skill_olustur(cli, "genel", "skill_b")
        assert len(cli.liste()) == 2

    def test_kategori_filtrele(self, cli):
        """Kategori filtresi ile sadece o kategoridekiler gelmeli."""
        _skill_olustur(cli, "web", "skill1")
        _skill_olustur(cli, "db", "skill2")
        web_liste = cli.liste(kategori="web")
        assert len(web_liste) == 1
        assert web_liste[0]["kategori"] == "web"

    def test_liste_meta_bilgileri(self, cli):
        """Liste donusunde meta bilgileri dogru olmali."""
        _skill_olustur(
            cli, "genel", "my_skill", description="Deneme", tags="python, test"
        )
        liste = cli.liste()
        assert len(liste) == 1
        assert liste[0]["aciklama"] == "Deneme"
        assert "tags" in liste[0]

    def test_liste_siralama(self, cli):
        """Liste alfabetik sirali olmali."""
        _skill_olustur(cli, "genel", "b_skill")
        _skill_olustur(cli, "genel", "a_skill")
        liste = cli.liste()
        assert liste[0]["ad"] < liste[1]["ad"]

    def test_bos_kategoride_liste(self, cli):
        """Var olmayan kategoride liste bos donmeli."""
        _skill_olustur(cli, "genel", "skill1")
        assert cli.liste(kategori="yok") == []


# ── Test 3: goruntule ───────────────────────────────────────────────────


class TestGoruntule:
    def test_var_olan_skill(self, cli):
        """Var olan skill icerigi goruntulenebilmeli."""
        _skill_olustur(cli, "genel", "test_skill")
        icerik = cli.goruntule("test_skill")
        assert icerik is not None
        assert "# Skill Icerigi" in icerik

    def test_olmayan_skill(self, cli):
        """Olmayan skill icin None donmeli."""
        assert cli.goruntule("yok") is None

    def test_dosya_adi_ile_goruntule(self, cli):
        """Dosya adi ile skill goruntulenebilmeli."""
        _skill_olustur(cli, "genel", "my_skill")
        assert cli.goruntule("my_skill") is not None


# ── Test 4: kategori_liste ──────────────────────────────────────────────


class TestKategoriListe:
    def test_tek_kategori(self, cli):
        """Tek kategori dogru listelenmeli."""
        _skill_olustur(cli, "web", "s1")
        assert cli.kategori_liste() == ["web"]

    def test_coklu_kategori(self, cli):
        """Birden cok kategori listelenmeli."""
        _skill_olustur(cli, "web", "s1")
        _skill_olustur(cli, "db", "s2")
        _skill_olustur(cli, "ai", "s3")
        kategoriler = cli.kategori_liste()
        assert len(kategoriler) == 3
        assert kategoriler == sorted(kategoriler)

    def test_tekrar_eden_kategori_tek(self, cli):
        """Ayni kategoride birden cok skill olsa da kategori tek donmeli."""
        _skill_olustur(cli, "web", "s1")
        _skill_olustur(cli, "web", "s2")
        assert cli.kategori_liste() == ["web"]


# ── Test 5: _meta_oku ───────────────────────────────────────────────────


class TestMetaOku:
    def test_frontmatter_parse(self, cli, temp_skill_yolu):
        """Frontmatter dogru parse edilmeli."""
        kat = temp_skill_yolu / "genel"
        kat.mkdir()
        skill_dizini = kat / "test_skill"
        skill_dizini.mkdir()
        md = skill_dizini / "SKILL.md"
        md.write_text(
            "---\n"
            "description: Test aciklamasi\n"
            "tags: python, test, cli\n"
            "---\n\n# Icerik\n",
            encoding="utf-8",
        )
        meta = cli._meta_oku(md)
        assert meta["aciklama"] == "Test aciklamasi"
        assert "python" in meta["tags"]
        assert "test" in meta["tags"]

    def test_frontmatter_yok(self, cli, temp_skill_yolu):
        """Frontmatter yoksa varsayilan degerler donmeli."""
        kat = temp_skill_yolu / "genel"
        kat.mkdir()
        skill_dizini = kat / "test"
        skill_dizini.mkdir()
        md = skill_dizini / "SKILL.md"
        md.write_text("# Sadece baslik\n", encoding="utf-8")
        meta = cli._meta_oku(md)
        assert meta["aciklama"] == ""
        assert meta["tags"] == []

    def test_frontmatter_bazi_alanlar_eksik(self, cli, temp_skill_yolu):
        """Frontmatter'da bazi alanlar eksikse hata firlatmamali."""
        kat = temp_skill_yolu / "genel"
        kat.mkdir()
        skill_dizini = kat / "test"
        skill_dizini.mkdir()
        md = skill_dizini / "SKILL.md"
        md.write_text(
            "---\n" "description: sadece aciklama\n" "---\n\n# Icerik\n",
            encoding="utf-8",
        )
        meta = cli._meta_oku(md)
        assert meta["aciklama"] == "sadece aciklama"
        assert meta["tags"] == []

    def test_frontmatter_bos(self, cli, temp_skill_yolu):
        """Bos dosyada hata firlatmamali."""
        kat = temp_skill_yolu / "genel"
        kat.mkdir()
        skill_dizini = kat / "test"
        skill_dizini.mkdir()
        md = skill_dizini / "SKILL.md"
        md.write_text("---\n---\n# Icerik\n", encoding="utf-8")
        meta = cli._meta_oku(md)
        assert isinstance(meta, dict)


# ── Test 6: _tum_dosyalar ve istatistik ──────────────────────────────────


class TestDosyalarVeIstatistik:
    def test_tum_dosyalar_bos(self, cli):
        """Bos dizinde tum_dosyalar bos liste donmeli."""
        assert cli._tum_dosyalar() == []

    def test_tum_dosyalar_bulur(self, cli):
        """_tum_dosyalar tum SKILL.md dosyalarini bulmali."""
        _skill_olustur(cli, "web", "s1")
        _skill_olustur(cli, "db", "s2")
        assert len(cli._tum_dosyalar()) == 2

    def test_istatistik_toplam(self, cli):
        """istatistik toplam skill sayisini dogru vermeli."""
        _skill_olustur(cli, "web", "s1")
        _skill_olustur(cli, "web", "s2")
        _skill_olustur(cli, "db", "s3")
        stats = cli.istatistik()
        assert stats["toplam_skill"] == 3

    def test_istatistik_kategori_sayisi(self, cli):
        """istatistik kategori sayisini dogru vermeli."""
        _skill_olustur(cli, "web", "s1")
        _skill_olustur(cli, "db", "s2")
        stats = cli.istatistik()
        assert stats["kategori_sayisi"] == 2

    def test_istatistik_kategoriler(self, cli):
        """istatistik kategori listesini dogru vermeli."""
        _skill_olustur(cli, "b", "s1")
        _skill_olustur(cli, "a", "s2")
        stats = cli.istatistik()
        assert stats["kategoriler"] == ["a", "b"]
