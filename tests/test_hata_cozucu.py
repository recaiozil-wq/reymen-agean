# -*- coding: utf-8 -*-
"""tests/test_hata_cozucu.py — HataCozucu modulu testleri."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hata_cozucu import (
    HataWatchdog,
    HataKoduUretici,
    HataKaydi,
    TerminalHataParser,
    CozumUygulayici,
    _sonraki_hata_kodu,
)


class TestHataWatchdog:
    def test_olusturma_varsayilan(self):
        wd = HataWatchdog()
        assert wd is not None
        assert wd.aralik_sn == 5.0

    def test_olusturma_ozel_aralik(self):
        wd = HataWatchdog(aralik_sn=10.0)
        assert wd.aralik_sn == 10.0

    def test_olusturma_ozel_kelimeler(self):
        kelimeler = {"test", "error"}
        wd = HataWatchdog(kelimeler=kelimeler)
        assert wd.kelimeler == kelimeler

    def test_baslat_ve_durdur(self):
        wd = HataWatchdog(aralik_sn=60.0)
        wd.baslat()
        # Thread calisiyor olmali
        assert wd._aktif is True
        wd.durdur()
        assert wd._aktif is False

    def test_cift_baslat_guvenli(self):
        wd = HataWatchdog(aralik_sn=60.0)
        wd.baslat()
        wd.baslat()  # Ikinci cagri crash etmemeli
        wd.durdur()

    def test_calisiyor_property_false_baslangic(self):
        wd = HataWatchdog()
        assert wd.calisiyor is False

    def test_callback_parametresi_kabul_edilir(self):
        sonuclar = []
        wd = HataWatchdog(callback=lambda m, k: sonuclar.append(k))
        assert wd.callback is not None

    def test_varsayilan_kelimeler_mevcut(self):
        wd = HataWatchdog()
        assert "error" in wd.kelimeler
        assert "hata" in wd.kelimeler


class TestHataKoduUretici:
    def test_olusturma(self):
        with tempfile.TemporaryDirectory() as tmp:
            from hata_cozucu import HATA_KLASORU as _orig
            uretici = HataKoduUretici()
            assert uretici is not None

    def test_kaydet_import_hatasi(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("ModuleNotFoundError: No module named 'xyz'")
        assert isinstance(kayit, HataKaydi)
        assert kayit.kod.startswith("HATA-")
        assert kayit.kategori == "import"

    def test_kaydet_syntax_hatasi(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("SyntaxError: invalid syntax at line 5")
        assert kayit.kategori == "syntax"

    def test_kaydet_dosya_hatasi(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("FileNotFoundError: no such file or directory")
        assert kayit.kategori == "dosya"

    def test_kaydet_baglanti_hatasi(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("ConnectionError: timeout occurred")
        assert kayit.kategori == "baglanti"

    def test_kaydet_diger_hata(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("Bilinmeyen bir hata olustu")
        assert kayit.kategori == "diger"

    def test_kaydet_ozet_cikar(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("Error: Something went wrong\nMore info here")
        assert len(kayit.ozet) > 0

    def test_kaydet_md_dosyasi_olusur(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("TypeError: unsupported operand")
        md_yolu = Path(uretici.__class__.__module__)
        from hata_cozucu import HATA_KLASORU
        md_yolu = HATA_KLASORU / f"{kayit.kod}.md"
        assert md_yolu.exists()

    def test_cozum_ekle_basarili(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("ValueError: bad value")
        sonuc = uretici.cozum_ekle(kayit.kod, "Degeri kontrol et.")
        assert sonuc is True

    def test_cozum_ekle_olmayan_kod(self):
        uretici = HataKoduUretici()
        sonuc = uretici.cozum_ekle("HATA-9999", "cozum")
        assert sonuc is False

    def test_kayit_bul_mevcut(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet("KeyError: 'eksik_anahtar'")
        bulunan = uretici.kayit_bul(kayit.kod)
        assert bulunan is not None
        assert bulunan.kod == kayit.kod

    def test_kayit_bul_olmayan(self):
        uretici = HataKoduUretici()
        bulunan = uretici.kayit_bul("HATA-0000")
        assert bulunan is None

    def test_kaydet_ekstra_bilgiler(self):
        uretici = HataKoduUretici()
        kayit = uretici.kaydet(
            "ImportError: cannot import name 'foo'",
            ekran_yolu="screenshot.png",
            dosya="main.py",
            satir=42,
        )
        assert kayit.dosya == "main.py"
        assert kayit.satir == 42


class TestTerminalHataParser:
    def test_olusturma(self):
        parser = TerminalHataParser()
        assert parser is not None

    def test_hata_yok(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("Her sey yolunda\nIslem tamamlandi")
        assert sonuc["hata_var"] is False
        assert sonuc["hata_sayisi"] == 0

    def test_python_traceback(self):
        parser = TerminalHataParser()
        cikti = (
            "Traceback (most recent call last):\n"
            "  File 'test.py', line 10, in <module>\n"
            "    import missing\n"
            "ModuleNotFoundError: No module named 'missing'\n"
        )
        sonuc = parser.parse(cikti)
        assert sonuc["hata_var"] is True
        assert sonuc["hata_sayisi"] > 0

    def test_error_satiri(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("Error: Something went wrong at line 5")
        assert sonuc["hata_var"] is True

    def test_exception_satiri(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("Exception: Unhandled exception occurred")
        assert sonuc["hata_var"] is True

    def test_failed_satiri(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("failed: Build process failed with code 1")
        assert sonuc["hata_var"] is True

    def test_ozet_dolu(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("Error: Test hatasi")
        assert len(sonuc["ozet"]) > 0

    def test_ozet_bos_hata_yokken(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("Normal cikti")
        assert sonuc["ozet"] == "Hata bulunamadi"

    def test_return_yapi(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("")
        assert "hata_var" in sonuc
        assert "hata_sayisi" in sonuc
        assert "hata_mesajlari" in sonuc
        assert "ps_hata_id" in sonuc
        assert "ozet" in sonuc

    def test_bos_cikti(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("")
        assert sonuc["hata_var"] is False

    def test_cok_satir_hata(self):
        parser = TerminalHataParser()
        cikti = "Error: Birinci hata\nError: Ikinci hata\nTypeError: ucuncu hata"
        sonuc = parser.parse(cikti)
        assert sonuc["hata_sayisi"] >= 2

    def test_access_denied(self):
        parser = TerminalHataParser()
        sonuc = parser.parse("Access Denied: You do not have permission")
        assert sonuc["hata_var"] is True


class TestCozumUygulayici:
    def test_olusturma(self):
        cu = CozumUygulayici()
        assert cu is not None
        assert cu.hata_uretici is not None

    def test_olusturma_ozel_uretici(self):
        uretici = HataKoduUretici()
        cu = CozumUygulayici(uretici)
        assert cu.hata_uretici is uretici

    def test_eksik_dosya_yolu(self):
        cu = CozumUygulayici()
        sonuc = cu.uygula("HATA-0001:\nYeni: yeni_kod")
        assert sonuc["basarili"] is False
        assert "eksik" in sonuc["mesaj"].lower() or "dosya" in sonuc["mesaj"].lower()

    def test_olmayan_dosya(self):
        cu = CozumUygulayici()
        cozum = (
            "HATA-0001:\n"
            "Dosya: var_olmayan_dosya.py\n"
            "Satir: 1\n"
            "Yeni: pass\n"
        )
        sonuc = cu.uygula(cozum)
        assert sonuc["basarili"] is False

    def test_gercek_dosya_patch(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("x = 1\ny = 2\nz = 3\n")
            f_adi = f.name

        try:
            cu = CozumUygulayici()
            cozum = (
                f"HATA-9990:\n"
                f"Dosya: {f_adi}\n"
                f"Eski: y = 2\n"
                f"Yeni: y = 99\n"
            )
            sonuc = cu.uygula(cozum)
            assert sonuc["basarili"] is True
            icerik = Path(f_adi).read_text(encoding="utf-8")
            assert "y = 99" in icerik
        finally:
            os.unlink(f_adi)

    def test_satir_ile_patch(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write("ilk\nikinci\nucuncu\n")
            f_adi = f.name

        try:
            cu = CozumUygulayici()
            cozum = (
                f"HATA-9991:\n"
                f"Dosya: {f_adi}\n"
                f"Satir: 2\n"
                f"Yeni: degistirildi\n"
            )
            sonuc = cu.uygula(cozum)
            assert sonuc["basarili"] is True
        finally:
            os.unlink(f_adi)

    def test_return_yapi(self):
        cu = CozumUygulayici()
        sonuc = cu.uygula("")
        assert "basarili" in sonuc
        assert "kod" in sonuc
        assert "mesaj" in sonuc
        assert "patch_sonuc" in sonuc
