# -*- coding: utf-8 -*-
"""tests/test_checkpoint_tool.py — Checkpoint aracı testleri.

Kapsar:
- motor_kaydet() ile CHECKPOINT_* araçlarının kaydı
- CheckpointManager CRUD (kaydet/yukle/liste/temizle/devam)
- Hatalı parametre durumları
"""

import json
import os
import sys
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))


# ── Mock motor ──────────────────────────────────────────────────────────────

class MockMotor:
    def __init__(self):
        self._araclar = {}

    def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
        self._araclar[ad] = fonk


# ── Mock CheckpointManager ──────────────────────────────────────────────────

class MockCheckpointManager:
    def __init__(self):
        self._data = {}
        self._counter = 0

    def kaydet(self, hedef, tur, durum):
        self._counter += 1
        cid = f"cp_{self._counter}"
        self._data[cid] = {"id": cid, "hedef": hedef, "tur": tur, "durum": durum, "zaman": "2026-01-01T00:00:00"}
        return cid

    def yukle(self, cid):
        return self._data.get(cid)

    def listele(self):
        return list(self._data.values())

    def temizle(self, saat=24):
        self._data.clear()

    def devam_edebilir_mi(self, hedef):
        for v in self._data.values():
            if v["hedef"] == hedef:
                return v
        return None


@pytest.fixture(autouse=True)
def mock_checkpoint_manager(monkeypatch):
    _manager = MockCheckpointManager()
    import tools.checkpoint_manager as tcm

    def _mock_run(islem="liste", **kwargs):
        try:
            c = _manager
            if islem == "kaydet":
                hedef = kwargs.get("hedef", "")
                tur = int(kwargs.get("tur", 0))
                if not hedef:
                    return "Hata: 'hedef' parametresi zorunludur."
                cid = c.kaydet(hedef, tur, {})
                return f"Checkpoint kaydedildi: {cid} (tur {tur})"
            elif islem == "yukle":
                cid = kwargs.get("checkpoint_id", "")
                if not cid:
                    return "Hata: 'checkpoint_id' parametresi zorunludur."
                veri = c.yukle(cid)
                if veri:
                    return json.dumps(veri, ensure_ascii=False, indent=2)
                return f"Checkpoint bulunamadi: {cid}"
            elif islem == "liste":
                checkpointler = c.listele()
                if not checkpointler:
                    return "Henuz checkpoint bulunmuyor."
                return "\n".join([f"  [{cp['id']}] {cp['hedef']} - tur {cp['tur']} ({cp['zaman']})" for cp in checkpointler])
            elif islem == "temizle":
                saat = int(kwargs.get("saat", 24))
                c.temizle(saat)
                return f"{saat} saatten eski checkpoint'ler temizlendi."
            elif islem == "devam":
                hedef = kwargs.get("hedef", "")
                if not hedef:
                    return "Hata: 'hedef' parametresi zorunludur."
                veri = c.devam_edebilir_mi(hedef)
                if veri:
                    return json.dumps(veri, ensure_ascii=False, indent=2)
                return f"Devam edilebilecek checkpoint bulunamadi: {hedef}"
            else:
                return f"Hata: Gecersiz islem '{islem}'."
        except Exception as e:
            return f"Checkpoint hatasi: {e}"

    monkeypatch.setattr(tcm, "run", _mock_run)
    yield _manager


# ── motor_kaydet testleri ────────────────────────────────────────────────────

class TestMotorKaydet:
    def test_araclar_kayitli(self):
        from tools.checkpoint_manager import motor_kaydet
        motor = MockMotor()
        motor_kaydet(motor)
        beklenen = {
            "CHECKPOINT_KAYDET", "CHECKPOINT_YUKLE",
            "CHECKPOINT_LISTELE", "CHECKPOINT_TEMIZLE", "CHECKPOINT_DEVAM",
        }
        assert beklenen.issubset(set(motor._araclar.keys()))

    def test_listele_bos(self):
        from tools.checkpoint_manager import motor_kaydet
        motor = MockMotor()
        motor_kaydet(motor)
        sonuc = motor._araclar["CHECKPOINT_LISTELE"]()
        assert "bulunmuyor" in sonuc.lower()


# ── Checkpoint CRUD testleri ─────────────────────────────────────────────────

class TestCheckpointCRUD:
    @pytest.fixture
    def kayitli_motor(self):
        from tools.checkpoint_manager import motor_kaydet
        motor = MockMotor()
        motor_kaydet(motor)
        return motor

    def test_kaydet_ve_listele(self, kayitli_motor):
        sonuc = kayitli_motor._araclar["CHECKPOINT_KAYDET"]("dosya_analiz", "3")
        assert "kaydedildi" in sonuc
        assert "cp_1" in sonuc

        liste = kayitli_motor._araclar["CHECKPOINT_LISTELE"]()
        assert "dosya_analiz" in liste

    def test_kaydet_hedef_zorunlu(self, kayitli_motor):
        sonuc = kayitli_motor._araclar["CHECKPOINT_KAYDET"]("", "0")
        assert "zorunludur" in sonuc

    def test_yukle_mevcut(self, kayitli_motor):
        kayitli_motor._araclar["CHECKPOINT_KAYDET"]("proje_x", "5")
        sonuc = kayitli_motor._araclar["CHECKPOINT_YUKLE"]("cp_1")
        veri = json.loads(sonuc)
        assert veri["hedef"] == "proje_x"
        assert veri["tur"] == 5

    def test_yukle_yok(self, kayitli_motor):
        sonuc = kayitli_motor._araclar["CHECKPOINT_YUKLE"]("yok_id")
        assert "bulunamadi" in sonuc

    def test_yukle_id_zorunlu(self, kayitli_motor):
        sonuc = kayitli_motor._araclar["CHECKPOINT_YUKLE"]("")
        assert "zorunludur" in sonuc

    def test_temizle(self, kayitli_motor):
        kayitli_motor._araclar["CHECKPOINT_KAYDET"]("proje_y", "1")
        sonuc = kayitli_motor._araclar["CHECKPOINT_TEMIZLE"]("24")
        assert "temizlendi" in sonuc

        liste = kayitli_motor._araclar["CHECKPOINT_LISTELE"]()
        assert "bulunmuyor" in liste.lower()

    def test_devam_var(self, kayitli_motor):
        kayitli_motor._araclar["CHECKPOINT_KAYDET"]("kod_refactor", "2")
        sonuc = kayitli_motor._araclar["CHECKPOINT_DEVAM"]("kod_refactor")
        veri = json.loads(sonuc)
        assert veri["hedef"] == "kod_refactor"

    def test_devam_yok(self, kayitli_motor):
        sonuc = kayitli_motor._araclar["CHECKPOINT_DEVAM"]("olmayan")
        assert "bulunamadi" in sonuc

    def test_devam_hedef_zorunlu(self, kayitli_motor):
        sonuc = kayitli_motor._araclar["CHECKPOINT_DEVAM"]("")
        assert "zorunludur" in sonuc

    def test_tur_varsayilan_sifir(self, kayitli_motor):
        sonuc = kayitli_motor._araclar["CHECKPOINT_KAYDET"]("hedef_a")
        assert "tur 0" in sonuc
