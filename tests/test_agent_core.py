# -*- coding: utf-8 -*-
"""tests/test_agent_core.py — Agent runtime, motor, beyin testleri."""

import sys
import os
import json
import tempfile
import time
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_runtime import (
    AgentRuntime,
    RuntimeHelpers,
    HataSiniflandirici,
    BackgroundReview,
)
from motor import Motor
from beyin import Beyin


class TestAgentRuntime:
    def test_runtime_baslatma(self):
        """AgentRuntime baslatma ve durum kontrolu."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": "not-needed",
                }
            },
            "max_tur": 5,
            "onay_iste": False,
            "backend_mode": "local",
        }
        rt = AgentRuntime(cfg)
        assert rt is not None
        assert rt._durum == "bosta"
        assert rt.VERSION == "1.0.0"

    def test_runtime_durum(self):
        """durum() metodunun dogru dict dondurmesi."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": "not-needed",
                }
            },
        }
        rt = AgentRuntime(cfg)
        durum = rt.durum()
        assert "durum" in durum
        assert "versiyon" in durum
        assert durum["durum"] == "bosta"
        assert durum["versiyon"] == "1.0.0"

    def test_runtime_calisirken_durum_kontrolu(self):
        """Ay ni calisirken tekrar calistirma engellenmeli."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": "not-needed",
                }
            },
        }
        rt = AgentRuntime(cfg)
        # _durum'u manuel calisiyor yap
        rt._durum = "calisiyor"
        rt._calisma_id = "test123"
        sonuc = rt.calistir("test hedef")
        assert "hata" in sonuc
        assert "zaten calisiyor" in sonuc["hata"]

    def test_runtime_sifirla(self):
        """sifirla() metodunun dogru calismasi."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": "not-needed",
                }
            },
        }
        rt = AgentRuntime(cfg)
        rt._calisma_id = "abc123"
        rt._baslangic = time.time()
        rt.sifirla()
        assert rt._calisma_id is None
        assert rt._baslangic is None


class TestRuntimeHelpers:
    def test_hedef_analiz_basit(self):
        """Basit hedef analizi."""
        analiz = RuntimeHelpers.hedef_analiz_et("merhaba")
        assert isinstance(analiz, dict)
        assert analiz["hedef_tur"] == "selam"
        assert 1 <= analiz["karmasiklik"] <= 5

    def test_hedef_analiz_dosya(self):
        """Dosya islemi hedef analizi."""
        analiz = RuntimeHelpers.hedef_analiz_et("bir dosya olustur ve icine yaz")
        assert "dosya_islemi" in analiz["ipuclari"]
        assert analiz["hedef_tur"] == "dosya_islemi"

    def test_hedef_analiz_web(self):
        """Web islemi hedef analizi."""
        analiz = RuntimeHelpers.hedef_analiz_et("web sitesini ziyaret et ve ara")
        assert "web_islemi" in analiz["ipuclari"]

    def test_hedef_analiz_kod(self):
        """Kod islemi hedef analizi."""
        analiz = RuntimeHelpers.hedef_analiz_et("python scripti calistir ve analiz et")
        assert "kod_islemi" in analiz["ipuclari"]

    def test_tur_ilerleme_goster(self):
        """Ilerleme cubugu gosterme (stdout'a yazdirir, hata vermemeli)."""
        RuntimeHelpers.tur_ilerleme_goster(5, 10)
        RuntimeHelpers.tur_ilerleme_goster(5, 10, "TEST")
        # Hata vermeden calismali

    def test_gecmis_ozet_bos(self):
        """Bos gecmis ozeti."""
        ozet = RuntimeHelpers.gecmis_ozet([])
        assert "henuz" in ozet

    def test_gecmis_ozet_dolu(self):
        """Dolu gecmis ozeti."""
        adimlar = ["Adim 1", "Adim 2", "Adim 3"]
        ozet = RuntimeHelpers.gecmis_ozet(adimlar)
        assert "Adim 1" in ozet
        assert "Adim 2" in ozet

    def test_gecmis_ozet_limit(self):
        """Gecmis ozetinin limit parametresi."""
        adimlar = [f"Adim {i}" for i in range(10)]
        ozet = RuntimeHelpers.gecmis_ozet(adimlar, limit=3)
        assert ozet.count("Adim") <= 3


class TestHataSiniflandirici:
    def test_siniflandir_ag(self):
        """Ag hatasi siniflandirmasi."""
        kategori = HataSiniflandirici.siniflandir(
            "ConnectionError: baglanti reddedildi"
        )
        assert kategori == "ag"

    def test_siniflandir_dosya(self):
        """Dosya hatasi siniflandirmasi."""
        kategori = HataSiniflandirici.siniflandir("FileNotFoundError: dosya bulunamadi")
        assert kategori == "dosya"

    def test_siniflandir_modul(self):
        """Modul hatasi siniflandirmasi."""
        kategori = HataSiniflandirici.siniflandir(
            "ModuleNotFoundError: No module named 'xyz'"
        )
        assert kategori == "modul"

    def test_siniflandir_python(self):
        """Python hatasi siniflandirmasi."""
        kategori = HataSiniflandirici.siniflandir("SyntaxError: invalid syntax")
        assert kategori == "python"

    def test_siniflandir_basarili(self):
        """Basarili durum siniflandirmasi."""
        kategori = HataSiniflandirici.siniflandir("Her sey yolunda")
        assert kategori == "basarili"

    def test_kurtarma_onerisi_ag(self):
        """Kurtarma onerisi - ag."""
        oneri = HataSiniflandirici.kurtarma_onerisi("ag")
        assert "baglantisini" in oneri

    def test_kurtarma_onerisi_bilinmeyen(self):
        """Bilinmeyen kategori icin kurtarma onerisi."""
        oneri = HataSiniflandirici.kurtarma_onerisi("bilinmeyen")
        assert oneri == "Devam et."


class TestMotor:
    def test_motor_olusturma(self):
        """Motor olusturma."""
        m = Motor(backend_mode="local")
        assert m is not None
        assert m.config == {}

    def test_motor_eylem_ayristir(self):
        """Eylem ayristirma: Eylem: DOSYA_OKU(\"test.txt\")."""
        m = Motor(backend_mode="local")
        arac, ham = m.eylemi_ayristir('Eylem: DOSYA_OKU("test.txt")')
        assert arac == "DOSYA_OKU"
        assert "test.txt" in ham

    def test_motor_eylem_ayristir_bos(self):
        """Gecersiz eylem ayristirma."""
        m = Motor(backend_mode="local")
        arac, ham = m.eylemi_ayristir("Bu bir eylem degil")
        assert arac is None
        assert ham is None

    def test_motor_parametre_coz(self):
        """Parametre cozme."""
        m = Motor(backend_mode="local")
        params = m._parametreleri_coz('"param1", "param2", "param3"')
        assert len(params) == 3
        assert params[0] == "param1"

    def test_motor_bilinmeyen_arac(self):
        """Bilinmeyen arac calistirma."""
        m = Motor(backend_mode="local")
        sonuc = m.calistir("OLMAYAN_ARAC", '"test"')
        assert isinstance(sonuc, str)
        assert len(sonuc) > 0

    def test_motor_gorev_bitti(self):
        """GOREV_BITTI aracinin dogru calismasi."""
        m = Motor(backend_mode="local")
        sonuc = m.calistir("GOREV_BITTI", "")
        assert isinstance(sonuc, str)


class TestBeyin:
    def test_beyin_olusturma(self):
        """Beyin olusturma."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test-model",
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": "not-needed",
                }
            },
        }
        b = Beyin(cfg)
        assert b is not None
        assert b.provider == "lmstudio"
        assert b.model == "test-model"

    def test_beyin_anahtar_bul_lmstudio(self):
        """LM Studio icin anahtar bulma."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": "not-needed",
                }
            },
        }
        b = Beyin(cfg)
        anahtar = b._anahtar_bul("lmstudio", {"api_key": "not-needed"})
        assert anahtar == "not-needed"

    def test_beyin_varsayilan_model(self):
        """Varsayilan model adlari."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": "not-needed",
                }
            },
        }
        b = Beyin(cfg)
        assert b._varsayilan_model("deepseek") == "deepseek-chat"
        assert b._varsayilan_model("openai") == "gpt-4o-mini"
        assert b._varsayilan_model("anthropic") == "claude-haiku-4-5-20251001"
        assert b._varsayilan_model("bilinmeyen") == "default"

    def test_beyin_fallback_zinciri(self):
        """Fallback zinciri olusumu."""
        cfg = {
            "default_provider": "lmstudio",
            "default_model": "test",
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "api_key": "not-needed",
                }
            },
        }
        b = Beyin(cfg)
        assert len(b._fallback_zinciri) >= 1
        assert b._fallback_zinciri[0].provider == "lmstudio"
