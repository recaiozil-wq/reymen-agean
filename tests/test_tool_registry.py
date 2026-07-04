# -*- coding: utf-8 -*-
"""tool_registry.py icin pytest testleri."""

import sys

sys.path.insert(0, ".")

from tool_registry import ToolRegistry, AracMeta


class TestAracMeta:
    """AracMeta veri yapisi testleri."""

    def test_musait_check_fn_yoksa(self):
        """check_fn yoksa her zaman musait."""
        meta = AracMeta("TEST", lambda: "ok")
        assert meta.musait_mi() is True

    def test_musait_check_fn_true(self):
        """check_fn True donerse musait."""
        meta = AracMeta("TEST", lambda: "ok", check_fn=lambda: True)
        assert meta.musait_mi() is True

    def test_musait_check_fn_false(self):
        """check_fn False donerse musait degil."""
        meta = AracMeta("TEST", lambda: "ok", check_fn=lambda: False)
        assert meta.musait_mi() is False

    def test_ozet_dict(self):
        """ozet() dogru dict dondurmeli."""
        meta = AracMeta(
            "TEST", lambda x: x, aciklama="test arac", risk_seviyesi=2, kategori="test"
        )
        o = meta.ozet()
        assert o["ad"] == "TEST"
        assert o["aciklama"] == "test arac"
        assert o["risk"] == 2
        assert o["kategori"] == "test"


class TestToolRegistry:
    """ToolRegistry birim testleri."""

    def setup_method(self):
        self.reg = ToolRegistry()

    def test_kaydet_ve_calistir(self):
        """Arac kaydedilip calistirilabilmeli."""
        self.reg.kaydet("TEST", lambda x: f"sonuc:{x}")
        sonuc = self.reg.calistir("TEST", "hello")
        assert "sonuc:hello" in sonuc

    def test_check_fn_ekle(self):
        """check_fn_ekle calismali."""
        self.reg.kaydet("TEST2", lambda: "ok")
        self.reg.check_fn_ekle("TEST2", lambda: True)
        assert self.reg.musait_mi("TEST2")
        self.reg.check_fn_ekle("TEST2", lambda: False)
        assert not self.reg.musait_mi("TEST2")

    def test_check_fn_kaldir(self):
        """check_fn_kaldir ile check_fn sifirlanmali."""
        self.reg.kaydet("TEST3", lambda: "ok")
        self.reg.check_fn_ekle("TEST3", lambda: False)
        assert not self.reg.musait_mi("TEST3")
        self.reg.check_fn_kaldir("TEST3")
        assert self.reg.musait_mi("TEST3")

    def test_musait_araclar(self):
        """musait_araclar sadece musait araclari dondurmeli."""
        self.reg.kaydet("MUSAIT", lambda: "ok")
        self.reg.kaydet("DEGIL", lambda: "ok", check_fn=lambda: False)
        musait = self.reg.musait_araclar()
        assert "MUSAIT" in musait
        assert "DEGIL" not in musait

    def test_kategori_filtreleme(self):
        """Kategori filtresi calismali."""
        self.reg.kaydet("A_WEB", lambda: "ok", kategori="web")
        self.reg.kaydet("B_DOSYA", lambda: "ok", kategori="dosya")
        web = self.reg.musait_araclar(kategori="web")
        assert "A_WEB" in web
        assert "B_DOSYA" not in web

    def test_liste(self):
        """liste() tum araclari dondurmeli."""
        self.reg.kaydet("LISTE_TEST", lambda: "ok")
        lst = self.reg.liste()
        assert "LISTE_TEST" in lst

    def test_liste_sadece_musait(self):
        """liste(sadece_musait=True) sadece musait araclari dondurmeli."""
        self.reg.kaydet("L_MUSAIT", lambda: "ok")
        self.reg.kaydet("L_DEGIL", lambda: "ok", check_fn=lambda: False)
        lst = self.reg.liste(sadece_musait=True)
        assert "L_MUSAIT" in lst
        assert "L_DEGIL" not in lst

    def test_arac_meta(self):
        """arac_meta metadata dondurmeli."""
        self.reg.kaydet("META_TEST", lambda: "ok", aciklama="aciklama")
        meta = self.reg.arac_meta("META_TEST")
        assert meta is not None
        assert meta["ad"] == "META_TEST"
        assert "musait" in meta

    def test_listele_kategori(self):
        """Kategorilere gore gruplama calismali."""
        self.reg.kaydet("KAT1", lambda: "ok", kategori="grup_a")
        self.reg.kaydet("KAT2", lambda: "ok", kategori="grup_b")
        gruplar = self.reg.listele_kategori()
        assert "grup_a" in gruplar
        assert "grup_b" in gruplar

    def test_detayli_liste(self):
        """detayli_liste metadata ile liste dondurmeli."""
        self.reg.kaydet("DETAY", lambda: "ok", aciklama="detay", risk_seviyesi=3)
        lst = self.reg.detayli_liste()
        detay = [x for x in lst if x["ad"] == "DETAY"]
        assert len(detay) == 1
        assert detay[0]["risk"] == 3

    def test_resolve(self):
        """resolve dogru modul bilgisi dondurmeli."""
        self.reg.kaydet("RESOLVE_TEST", lambda: "ok")
        resolved = self.reg.resolve("RESOLVE_TEST")
        assert resolved is not None
        assert "module" in resolved
        assert "fonk" in resolved

    def test_resolve_none(self):
        """Olmayan arac icin resolve None dondurmeli."""
        assert self.reg.resolve("OLMAYAN_ARAC_12345") is None

    def test_durum(self):
        """durum() string dondurmeli."""
        self.reg.kaydet("DURUM_TEST", lambda: "ok")
        durum = self.reg.durum()
        assert "Registry" in durum
        assert "musait" in durum

    def test_bilinmeyen_arac(self):
        """Bilinmeyen arac mesaji."""
        sonuc = self.reg.calistir("BILINMEYEN_X")
        assert "Bilinmeyen" in sonuc

    def test_check_fn_basarisiz_arac(self):
        """check_fn False olan arac calistirilamaz."""
        self.reg.kaydet("BLOKE", lambda: "ok", check_fn=lambda: False)
        sonuc = self.reg.calistir("BLOKE")
        assert "KULLANILAMIYOR" in sonuc

    def test_alias_listede_var(self):
        """Alias'lar listede gorunmeli."""
        self.reg.kaydet("KOMUT_CALISTIR", lambda: "ok")
        self.reg.kaydet("WEB_ARA", lambda: "ok")
        lst = self.reg.liste()
        assert "KOMUT_CALISTIR" in lst
        assert "WEB_ARA" in lst
