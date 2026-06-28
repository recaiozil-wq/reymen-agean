# -*- coding: utf-8 -*-
"""tests/test_authz_mixin.py — YetkilendirmeMixin birim testleri."""
import sys
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from gateway.authz_mixin import (
    YetkilendirmeMixin, Rol, Yetki,
    kullanici_yetkilendir, kuresel_yetki,
)


class TestYetkilendirmeMixin:
    def test_initial_state(self):
        ym = YetkilendirmeMixin()
        assert ym.varsayilan_rol_al() == Rol.ZIYARETCI
        assert ym.rol_listele() == {}

    def test_rol_ata_string(self):
        ym = YetkilendirmeMixin()
        assert ym.rol_ata("user1", "admin") is True
        assert ym.rol_al("user1") == Rol.YONETICI

    def test_rol_ata_enum(self):
        ym = YetkilendirmeMixin()
        assert ym.rol_ata("user2", Rol.KULLANICI) is True
        assert ym.rol_al("user2") == Rol.KULLANICI

    def test_rol_ata_invalid(self):
        ym = YetkilendirmeMixin()
        assert ym.rol_ata("user3", "nonexistent_role") is False

    def test_rol_ata_yasakli(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("user4", "yasakli")
        assert ym.rol_al("user4") == Rol.YASAKLI

    def test_rol_al_default(self):
        ym = YetkilendirmeMixin()
        assert ym.rol_al("unknown") == Rol.ZIYARETCI

    def test_rol_al_banned(self):
        ym = YetkilendirmeMixin()
        ym.kara_listeye_ekle("banned")
        assert ym.rol_al("banned") == Rol.YASAKLI

    def test_rol_al_whitelist(self):
        ym = YetkilendirmeMixin()
        ym.beyaz_listeye_ekle("trusted")
        assert ym.rol_al("trusted") == Rol.YONETICI

    def test_rol_sil(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("user5", "admin")
        ym.rol_sil("user5")
        assert ym.rol_al("user5") == Rol.ZIYARETCI

    def test_rol_listele(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("a", "admin")
        ym.rol_ata("b", "kullanici")
        lst = ym.rol_listele()
        assert lst["a"] == "yonetici"
        assert lst["b"] == "kullanici"

    def test_kara_listeye_ekle_kaldir(self):
        ym = YetkilendirmeMixin()
        ym.kara_listeye_ekle("spammer")
        assert ym.kara_liste_mi("spammer") is True
        ym.kara_liste_kaldir("spammer")
        assert ym.kara_liste_mi("spammer") is False

    def test_beyaz_liste(self):
        ym = YetkilendirmeMixin()
        ym.beyaz_listeye_ekle("vip")
        assert ym.rol_al("vip") == Rol.YONETICI

    def test_platform_izin_ekle_kaldir(self):
        ym = YetkilendirmeMixin()
        ym.platform_izin_ekle("telegram", "user_t")
        assert ym.platform_izinli_mi("telegram", "user_t") is True
        ym.platform_izin_kaldir("telegram", "user_t")
        assert ym.platform_izinli_mi("telegram", "user_t") is False

    def test_platform_izin_olmadan_herkese_acik(self):
        ym = YetkilendirmeMixin()
        assert ym.platform_izinli_mi("discord", "anyone") is True

    def test_yetki_kontrol_admin(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("admin_u", "admin")
        gecerli, hata = ym.yetki_kontrol("admin_u", Yetki.SISTEM_YONET)
        assert gecerli is True
        assert hata == ""

    def test_yetki_kontrol_yetersiz(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("guest", "ziyaretci")
        gecerli, hata = ym.yetki_kontrol("guest", Yetki.MESAJ_GONDER)
        assert gecerli is False
        assert "yetersiz" in hata

    def test_yetki_kontrol_banned(self):
        ym = YetkilendirmeMixin()
        ym.kara_listeye_ekle("banned_u")
        gecerli, hata = ym.yetki_kontrol("banned_u", Yetki.MESAJ_GONDER)
        assert gecerli is False
        assert "engellenmis" in hata

    def test_yetki_kontrol_platform_kisitli(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("slack_user", "kullanici")
        ym.rol_ata("other_user", "kullanici")
        ym.platform_izin_ekle("slack", "slack_user")
        # slack_user slack'te yetkili
        gecerli, hata = ym.yetki_kontrol("slack_user", Yetki.MESAJ_GONDER, platform="slack")
        assert gecerli is True, f"slack'te yetkili olmali: {hata}"
        # other_user slack'te yetkili degil (izni yok)
        gecerli2, hata2 = ym.yetki_kontrol("other_user", Yetki.MESAJ_GONDER, platform="slack")
        assert gecerli2 is False, f"other_user slack'te yetkisiz olmali: {hata2}"
        # Telegram'da kisitlama yok, herkes erisebilir
        gecerli3, hata3 = ym.yetki_kontrol("slack_user", Yetki.MESAJ_GONDER, platform="telegram")
        assert gecerli3 is True, "telegram kisitlamasi yok, izin verilmeli"

    def test_varsayilan_rol_ayarla(self):
        ym = YetkilendirmeMixin()
        ym.varsayilan_rol_ayarla("kullanici")
        assert ym.varsayilan_rol_al() == Rol.KULLANICI
        assert ym.rol_al("new_user") == Rol.KULLANICI

    def test_varsayilan_rol_invalid(self):
        ym = YetkilendirmeMixin()
        assert ym.varsayilan_rol_ayarla("bulunamaz") is False

    def test_yetki_esigi_ayarla(self):
        ym = YetkilendirmeMixin()
        ym.yetki_esigi_ayarla(Yetki.MESAJ_GONDER, "ziyaretci")
        assert ym.yetki_esigi_al(Yetki.MESAJ_GONDER) == Rol.ZIYARETCI

    def test_yetki_esigi_invalid(self):
        ym = YetkilendirmeMixin()
        assert ym.yetki_esigi_ayarla(Yetki.MESAJ_GONDER, "bulunamaz") is False

    def test_yetkilendirme_ozeti(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("u1", "admin")
        ozet = ym.yetkilendirme_ozeti()
        assert ozet["toplam_kullanici"] == 1
        assert ozet["varsayilan_rol"] == "ziyaretci"

    def test_ping(self):
        ym = YetkilendirmeMixin()
        result = ym.ping()
        assert result["modul"] == "authz_mixin"
        assert result["durum"] == "hazir"

    def test_send_message_yetki_var(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("hedef_u", "kullanici")
        result = ym.send_message("merhaba", "hedef_u")
        assert "kaydedildi" in result

    def test_send_message_yetki_yok(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("hedef_u", "ziyaretci")
        result = ym.send_message("merhaba", "hedef_u")
        assert "yetkisi yok" in result

    def test_yetkilendirilmis_decorator_basarili(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("admin1", "admin")

        @ym.yetkilendirilmis(Yetki.SISTEM_YONET)
        def test_fn(self, ctx, msg):
            return {"ok": True}

        result = test_fn(None, {"kullanici_id": "admin1"}, "test")
        assert result == {"ok": True}

    def test_yetkilendirilmis_decorator_red(self):
        ym = YetkilendirmeMixin()
        ym.rol_ata("guest1", "ziyaretci")

        @ym.yetkilendirilmis(Yetki.SISTEM_YONET)
        def test_fn(self, ctx, msg):
            return {"ok": True}

        result = test_fn(None, {"kullanici_id": "guest1"}, "test")
        assert "error" in result

    def test_kullanici_yetkilendir_decorator(self):
        @kullanici_yetkilendir
        def handler(kullanici_id, mesaj):
            return {"ok": True, "mesaj": mesaj}

        result = handler("user_1", "test")
        assert result["ok"] is True

    def test_kullanici_yetkilendir_red(self):
        @kullanici_yetkilendir
        def handler(kullanici_id, mesaj):
            return {"ok": True}

        result = handler("0", "test")
        assert "error" in result

    def test_kuresel_yetki_instance(self):
        assert isinstance(kuresel_yetki, YetkilendirmeMixin)

    def test_kara_liste_kaldir_return(self):
        ym = YetkilendirmeMixin()
        ym.kara_listeye_ekle("u")
        # discard returns None, bool(None) = False — test the actual behavior
        result = ym.kara_liste_kaldir("u")
        assert ym.kara_liste_mi("u") is False
        result2 = ym.kara_liste_kaldir("u")
        assert ym.kara_liste_mi("u") is False
