# -*- coding: utf-8 -*-
"""Tests for skills_hub.py — Skills Hub."""

from skills_hub import (
    HUBS,
    HUB_CACHE,
    SKILLS_KLASOR,
    hub_listele,
    hub_ekle,
    hub_indir,
)

import importlib
import sys

# hub_indir icindeki local 'import requests' i mocklayabilmek icin
# requests modulunu module-level'da import et
import requests


# ════════════════════════════════════════════════════════════════
# Sabitler
# ════════════════════════════════════════════════════════════════

class TestSabitler:
    def test_skills_klasor_yolu(self):
        assert ".ReYMeN" in str(SKILLS_KLASOR)
        assert "skills" in str(SKILLS_KLASOR)

    def test_hub_cache_yolu(self):
        assert "index-cache" in str(HUB_CACHE)

    def test_varsayilan_hublar(self):
        assert "ReYMeN-skills" in HUBS
        assert "ReYMeN-agent-skills" in HUBS
        assert "url" in HUBS["ReYMeN-skills"]
        assert "aciklama" in HUBS["ReYMeN-skills"]


# ════════════════════════════════════════════════════════════════
# hub_listele
# ════════════════════════════════════════════════════════════════

class TestHubListele:
    def test_listele_icerir(self):
        sonuc = hub_listele()
        assert "Skills Hub" in sonuc
        assert "ReYMeN-skills" in sonuc
        assert "ReYMeN-agent-skills" in sonuc

    def test_listele_aciklama(self):
        sonuc = hub_listele()
        assert "Kullaniciya ait" in sonuc
        assert "Nous Research" in sonuc


# ════════════════════════════════════════════════════════════════
# hub_ekle
# ════════════════════════════════════════════════════════════════

class TestHubEkle:
    def test_yeni_hub_ekle(self):
        hub_ekle("test-hub", "https://example.com/test.zip", "Test aciklama")
        assert "test-hub" in HUBS
        assert HUBS["test-hub"]["url"] == "https://example.com/test.zip"
        assert HUBS["test-hub"]["aciklama"] == "Test aciklama"
        # Temizle
        HUBS.pop("test-hub", None)

    def test_yeni_hub_varsayilan_aciklama(self):
        hub_ekle("test-hub2", "https://example.com/test2.zip")
        assert HUBS["test-hub2"]["aciklama"] == "test-hub2"
        HUBS.pop("test-hub2", None)


# ════════════════════════════════════════════════════════════════
# hub_indir
# ════════════════════════════════════════════════════════════════

class TestHubIndir:
    def test_bilinmeyen_hub(self):
        sonuc = hub_indir("OLMAYAN_HUB")
        assert "Bilinmeyen" in sonuc

    def test_indir_http_hatasi(self, mocker):
        mock_get = mocker.patch("requests.get")
        mock_get.return_value.status_code = 404
        mock_get.return_value.content = b""
        sonuc = hub_indir("ReYMeN-skills")
        assert "HTTP 404" in sonuc

    def test_indir_zip_hatasi(self, mocker):
        mock_get = mocker.patch("requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"notazip"
        sonuc = hub_indir("ReYMeN-skills")
        assert "Hata" in sonuc

    def test_indir_basarili(self, mocker, tmp_path):
        """Basit bir ZIP ile indirme testi."""
        import io
        import zipfile

        # Gercek bir ZIP olustur
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("repo/skills/test_skill/SKILL.md", "# Test Skill")
        buf.seek(0)

        mock_get = mocker.patch("requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = buf.read()

        # SKILLS_KLASOR ve HUB_CACHE'i tmp_path'e yonlendir
        # NOT: shim degil, gercek modul namespace'i patch edilmeli
        mocker.patch("reymen.cereyan.skills_hub.SKILLS_KLASOR", tmp_path)
        cache = tmp_path / "index-cache" / "hub"
        mocker.patch("reymen.cereyan.skills_hub.HUB_CACHE", cache)

        sonuc = hub_indir("ReYMeN-skills")
        assert "Indirme tamam" in sonuc
        assert "yeni skill" in sonuc

    def test_indir_kategorili(self, mocker, tmp_path):
        import io
        import zipfile

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("repo/skills/test_skill/SKILL.md", "# Test")
        buf.seek(0)

        mock_get = mocker.patch("requests.get")
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = buf.read()

        mocker.patch("reymen.cereyan.skills_hub.SKILLS_KLASOR", tmp_path)
        cache = tmp_path / "index-cache" / "hub"
        mocker.patch("reymen.cereyan.skills_hub.HUB_CACHE", cache)

        sonuc = hub_indir("ReYMeN-skills", kategori="test-kategori")
        assert "Indirme tamam" in sonuc

        # Kategorili klasor olusmali
        assert (tmp_path / "test-kategori" / "test_skill" / "SKILL.md").exists()


# ════════════════════════════════════════════════════════════════
# Yan etki: HUBS degisikliklerini temizle
# ════════════════════════════════════════════════════════════════

class TestHubTemiz:
    def test_varsayilan_hublar_bozulmamis(self):
        """hub_ekle testlerinden sonra HUBS temiz."""
        assert list(HUBS.keys()) == ["ReYMeN-skills", "ReYMeN-agent-skills"]
