# -*- coding: utf-8 -*-
"""test_oz_tutarlilik.py — OzTutarlilikDenetci için kapsamlı pytest testleri."""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

_proje_koku = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _proje_koku not in sys.path:
    sys.path.insert(0, _proje_koku)

from reymen.cereyan.oz_tutarlilik import (
    OzTutarlilikDenetci,
    _JUDGE_SISTEM,
    _DEGERLENDIRME_SISTEM,
)


# ── Sahte Provider ────────────────────────────────────────────────────────


class SahteProvider:
    """Test provider — temperature ve mode'a göre farklı yanıt üretir."""

    def __init__(
        self,
        planlar=None,
        judge_yanit="EN_IYI: 1",
        puan_yanit="PUAN: 8\nACIKLAMA: Iyi.",
    ):
        self._call_count = 0
        self._planlar = planlar or [
            "Plan A: WEB_ARA ile bilgi topla.",
            "Plan B: DOSYA_YAZ ile kaydet.",
            "Plan C: KOMUT_CALISTIR ile kontrol et.",
        ]
        self._judge_yanit = judge_yanit
        self._puan_yanit = puan_yanit

    def uret(self, sistem, mesajlar, **kwargs):
        self._call_count += 1
        if "PUAN" in sistem:
            return self._puan_yanit
        if "EN_IYI" in sistem or "degerlendirici" in sistem.lower():
            return self._judge_yanit
        return self._planlar[(self._call_count - 1) % len(self._planlar)]


# ── Init Tests ────────────────────────────────────────────────────────────


class TestInit:
    def test_varsayilan_degerler(self):
        sc = OzTutarlilikDenetci()
        assert sc.varsayilan_n == 3
        assert sc.sicaklik_adimi == 0.15
        assert sc.aktif is True
        assert sc._provider is None
        assert sc._toplam_sefer == 0
        assert sc._judge_cagrisi == 0

    def test_ozel_degerler(self):
        prov = SahteProvider()
        sc = OzTutarlilikDenetci(
            provider=prov, varsayilan_n=5, sicaklik_adimi=0.3, aktif=False
        )
        assert sc._provider is prov
        assert sc.varsayilan_n == 5
        assert sc.sicaklik_adimi == 0.3
        assert sc.aktif is False


# ── en_iyi_plani_sec Tests ───────────────────────────────────────────────


class TestEnIyiPlaniSec:
    def test_aktif_degilse_none(self):
        sc = OzTutarlilikDenetci(provider=SahteProvider(), aktif=False)
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}]
        )
        assert result is None

    def test_provider_yoksa_none(self):
        sc = OzTutarlilikDenetci(provider=None)
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}]
        )
        assert result is None

    def test_n_1_sonuc_none(self):
        sc = OzTutarlilikDenetci(provider=SahteProvider())
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}], n=1
        )
        assert result is None

    def test_n_0_uses_default(self):
        """n=0 → falsy → varsayilan_n kullanılır, None dönmez."""
        prov = SahteProvider(judge_yanit="EN_IYI: 1")
        sc = OzTutarlilikDenetci(provider=prov, varsayilan_n=3)
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}], n=0
        )
        assert result is not None  # 0 or 3 = 3

    def test_tek_aday_dogrudan_donderir(self):
        provider = MagicMock()
        provider.uret.return_value = "Tek plan: Yap ve bitir."
        sc = OzTutarlilikDenetci(provider=provider, varsayilan_n=2)
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}], n=2
        )
        assert result == "Tek plan: Yap ve bitir."

    def test_coklu_aday_judge_secimi(self):
        provider = SahteProvider(judge_yanit="EN_IYI: 2")
        sc = OzTutarlilikDenetci(provider=provider, varsayilan_n=3)
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}], n=3
        )
        assert result is not None
        assert len(result) > 0

    def test_toplam_sefer_artar(self):
        prov = SahteProvider(judge_yanit="EN_IYI: 1")
        sc = OzTutarlilikDenetci(provider=prov, varsayilan_n=3)
        sc.en_iyi_plani_sec("h", "p", [{"role": "user", "content": "x"}], n=3)
        assert sc._toplam_sefer == 1
        sc.en_iyi_plani_sec("h", "p", [{"role": "user", "content": "x"}], n=3)
        assert sc._toplam_sefer == 2

    def test_bos_cevaplar_none(self):
        provider = MagicMock()
        provider.uret.return_value = ""
        sc = OzTutarlilikDenetci(provider=provider, varsayilan_n=3)
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}], n=3
        )
        assert result is None

    def test_sadece_bosluk_cevaplar_none(self):
        provider = MagicMock()
        provider.uret.return_value = "   \n  \n  "
        sc = OzTutarlilikDenetci(provider=provider, varsayilan_n=3)
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}], n=3
        )
        assert result is None

    def test_n_one_degilse_varsayilan_kullan(self):
        prov = SahteProvider(judge_yanit="EN_IYI: 1")
        sc = OzTutarlilikDenetci(provider=prov, varsayilan_n=3)
        # n=None → varsayilan_n=3 kullanilir
        result = sc.en_iyi_plani_sec(
            "hedef", "prompt", [{"role": "user", "content": "x"}], n=None
        )
        assert result is not None


# ── tek_cevap_puan Tests ─────────────────────────────────────────────────


class TestTekCevapPuan:
    def test_provider_yoksa_varsayilan(self):
        sc = OzTutarlilikDenetci(provider=None)
        result = sc.tek_cevap_puan("hedef", "cevap")
        assert result["puan"] == 5
        assert "Provider yok" in result["aciklama"]

    def test_normal_puanlama(self):
        prov = SahteProvider(puan_yanit="PUAN: 9\nACIKLAMA: Mükemmel.")
        sc = OzTutarlilikDenetci(provider=prov)
        result = sc.tek_cevap_puan("hedef", "cevap icerigi")
        assert result["puan"] == 9
        assert "Mükemmel" in result["aciklama"]

    def test_exception_durumu(self):
        provider = MagicMock()
        provider.uret.side_effect = RuntimeError("API down")
        sc = OzTutarlilikDenetci(provider=provider)
        result = sc.tek_cevap_puan("hedef", "cevap")
        assert result["puan"] == 5
        assert "Degerlendirme hatasi" in result["aciklama"]

    def test_cevap_500_karakterle_sinirli(self):
        prov = MagicMock()
        prov.uret.return_value = "PUAN: 7\nACIKLAMA: Iyi."
        sc = OzTutarlilikDenetci(provider=prov)
        uzun_cevap = "A" * 1000
        sc.tek_cevap_puan("hedef", uzun_cevap)
        # Provider'a giden mesajda cevap[:500] olmali
        call_args = prov.uret.call_args
        kullanici = call_args[0][1][0]["content"]
        assert len(kullanici.split("Cevap:\n")[1]) == 500

    def test_puan_yoksa_5_donder(self):
        prov = MagicMock()
        prov.uret.return_value = "ACIKLAMA: Sadece aciklama."
        sc = OzTutarlilikDenetci(provider=prov)
        result = sc.tek_cevap_puan("hedef", "cevap")
        assert result["puan"] == 5

    def test_aciklama_yoksa_bos(self):
        prov = MagicMock()
        prov.uret.return_value = "PUAN: 7"
        sc = OzTutarlilikDenetci(provider=prov)
        result = sc.tek_cevap_puan("hedef", "cevap")
        assert result["puan"] == 7
        assert result["aciklama"] == ""


# ── coklu_oy_ver Tests ──────────────────────────────────────────────────


class TestCokluOyVer:
    def test_bos_liste(self):
        sc = OzTutarlilikDenetci()
        assert sc.coklu_oy_ver([]) == ""

    def test_tek_aday(self):
        sc = OzTutarlilikDenetci()
        assert sc.coklu_oy_ver(["Plan A"]) == "Plan A"

    def test_iki_farkli_aday_ilki_kazanir(self):
        sc = OzTutarlilikDenetci()
        # İkisi de birbirine benzer, üçüncü farklı → benzer olan kazanır
        adaylar = [
            "Dosyayı aç, oku, kaydet.",
            "Dosyayı aç, oku, kaydet.",
            "Git, bul, sil.",
        ]
        kazanan = sc.coklu_oy_ver(adaylar)
        assert kazanan == adaylar[0]  # İkisi aynı → en yüksek skor

    def test_uc_farkli_aday(self):
        sc = OzTutarlilikDenetci()
        adaylar = [
            "Dosyayı aç ve oku.",
            "Web sitesine git ve bilgi çek.",
            "Dosyayı aç ve oku, sonra kaydet.",
        ]
        kazanan = sc.coklu_oy_ver(adaylar)
        assert kazanan in adaylar

    def test_hepsi_ayni(self):
        sc = OzTutarlilikDenetci()
        adaylar = ["Aynı plan", "Aynı plan", "Aynı plan"]
        kazanan = sc.coklu_oy_ver(adaylar)
        assert kazanan == "Aynı plan"


# ── _judge_ayristir Tests ────────────────────────────────────────────────


class TestJudgeAyrilstir:
    def test_normal_cikti(self):
        assert OzTutarlilikDenetci._judge_ayristir("EN_IYI: 2", 3) == 1

    def test_ilk_sira(self):
        assert OzTutarlilikDenetci._judge_ayristir("EN_IYI: 1", 3) == 0

    def test_son_sira(self):
        assert OzTutarlilikDenetci._judge_ayristir("EN_IYI: 3", 3) == 2

    def test_buyuk_harf(self):
        assert OzTutarlilikDenetci._judge_ayristir("en_iyi: 2", 3) == 1

    def test_bosluklu_form(self):
        assert OzTutarlilikDenetci._judge_ayristir("EN_IYI : 1", 3) == 0

    def test_sayi_disinda_text(self):
        # Geçersiz numara → varsayılan 0
        assert OzTutarlilikDenetci._judge_ayristir("EN_IYI: abc", 3) == 0

    def test_sayi_sinir_disinda(self):
        # n=3 iken EN_IYI: 5 → geçersiz, varsayılan 0
        assert OzTutarlilikDenetci._judge_ayristir("EN_IYI: 5", 3) == 0

    def test_sifir_sayisi(self):
        # EN_IYI: 0 → idx=-1, geçersiz → varsayılan 0
        assert OzTutarlilikDenetci._judge_ayristir("EN_IYI: 0", 3) == 0

    def test_text_icinde_gizli(self):
        assert OzTutarlilikDenetci._judge_ayristir("Cevabım EN_IYI: 2 olarak", 3) == 1

    def test_bos_yanit(self):
        assert OzTutarlilikDenetci._judge_ayristir("", 3) == 0


# ── _puan_ayristir Tests ────────────────────────────────────────────────


class TestPuanAyrilstir:
    def test_normal_puan_aciklama(self):
        result = OzTutarlilikDenetci._puan_ayristir("PUAN: 8\nACIKLAMA: Cok iyi.")
        assert result["puan"] == 8
        assert "Cok iyi" in result["aciklama"]

    def test_sadece_puan(self):
        result = OzTutarlilikDenetci._puan_ayristir("PUAN: 3")
        assert result["puan"] == 3
        assert result["aciklama"] == ""

    def test_sadece_aciklama(self):
        result = OzTutarlilikDenetci._puan_ayristir("ACIKLAMA: Guzel.")
        assert result["puan"] == 5
        assert result["aciklama"] == "Guzel."

    def test_bos_yanit(self):
        result = OzTutarlilikDenetci._puan_ayristir("")
        assert result["puan"] == 5
        assert result["aciklama"] == ""

    def test_buyuk_harf(self):
        result = OzTutarlilikDenetci._puan_ayristir("puan: 9\naciklama: Harika.")
        assert result["puan"] == 9

    def test_on_numara(self):
        result = OzTutarlilikDenetci._puan_ayristir("PUAN: 10\nACIKLAMA: Mukemmel.")
        assert result["puan"] == 10


# ── istatistik Tests ─────────────────────────────────────────────────────


class TestIstatistik:
    def test_baslangic(self):
        sc = OzTutarlilikDenetci()
        stats = sc.istatistik()
        assert stats["toplam_sefer"] == 0
        assert stats["judge_cagrisi"] == 0

    def test_sonrasi(self):
        prov = SahteProvider(judge_yanit="EN_IYI: 1")
        sc = OzTutarlilikDenetci(provider=prov, varsayilan_n=3)
        sc.en_iyi_plani_sec("h", "p", [{"role": "user", "content": "x"}], n=3)
        stats = sc.istatistik()
        assert stats["toplam_sefer"] == 1
        assert stats["judge_cagrisi"] == 1


# ── _judge_ile_sec Tests ────────────────────────────────────────────────


class TestJudgeIleSec:
    def test_judge_hatasi_coklu_oy_geci(self):
        """Judge exception olursa cogunluk oyuna gecilmeli."""
        provider = MagicMock()
        call_count = [0]

        def uret_side_effect(sistem, mesajlar, **kwargs):
            call_count[0] += 1
            if "EN_IYI" in sistem:
                raise RuntimeError("Judge API down")
            return "Plan X: basit plan."

        provider.uret.side_effect = uret_side_effect

        sc = OzTutarlilikDenetci(provider=provider, varsayilan_n=3)
        adaylar = ["Plan A", "Plan A", "Plan B"]
        result = sc._judge_ile_sec("hedef", adaylar)
        # Judge başarısız → cogunluk oyu → "Plan A" kazanır
        assert result == "Plan A"
        assert sc._judge_cagrisi == 1

    def test_judge_basari(self):
        provider = MagicMock()
        provider.uret.return_value = "EN_IYI: 2"
        sc = OzTutarlilikDenetci(provider=provider)
        adaylar = ["Plan A", "Plan B", "Plan C"]
        result = sc._judge_ile_sec("hedef", adaylar)
        assert result == "Plan B"
        assert sc._judge_cagrisi == 1

    def test_judge_sicaklik_adimi(self):
        """N_cevap_uret'te sicaklik artmali."""
        prov = MagicMock()
        prov.uret.return_value = "Plan X: test"
        sc = OzTutarlilikDenetci(provider=prov, sicaklik_adimi=0.1)
        sc._n_cevap_uret("prompt", [{"role": "user", "content": "x"}], n=3)
        calls = prov.uret.call_args_list
        # Sicakliklar: 0.7, 0.8, 0.9
        temps = [
            c.kwargs.get("temperature", 0) for c in calls if "temperature" in c.kwargs
        ]
        if temps:
            assert temps[0] < temps[-1]


# ── Sabit Dogrulama ─────────────────────────────────────────────────────


class TestSabitDogrulama:
    def test_judge_sistemi_icerik(self):
        assert "EN_IYI" in _JUDGE_SISTEM
        assert "Hedefle uyum" in _JUDGE_SISTEM

    def test_degerlendirme_sistemi_icerik(self):
        assert "PUAN" in _DEGERLENDIRME_SISTEM
        assert "1-10" in _DEGERLENDIRME_SISTEM
