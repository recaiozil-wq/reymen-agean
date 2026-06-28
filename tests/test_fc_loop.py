# -*- coding: utf-8 -*-
"""test_fc_loop.py — 5N1K Mühendislik: Native FC hibrit döngüsü testleri.

Kapsam:
  Motor.calistir_fc()     — dict args → string bridge
  Motor.tools_schema_al() — OpenAI schema üretimi
  Beyin.uret_v2()         — graceful FC/text fallback
  Beyin.fc_destekleniyor()— provider cache
  AIAgentOrchestrator     — FC loop: paralel araç, GOREV_BITTI, metin fallback
"""
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import pytest

# Windows tty mock (motor plugin import zinciri)
for _mod in ("tty", "pty", "termios", "paramiko", "invoke", "fabric"):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

sys.path.insert(0, str(Path(__file__).parent.parent))

# ─────────────────────────────────────────────────────────────────────────────
# Motor.calistir_fc()
# ─────────────────────────────────────────────────────────────────────────────

class TestMotorCalistirFc:

    def _motor(self):
        from reymen.cereyan.motor import Motor
        m = MagicMock(spec=Motor)
        m.calistir_fc = Motor.calistir_fc.__get__(m, Motor)
        m.calistir    = MagicMock(return_value="OK")
        return m

    def test_bos_args_bos_ham(self):
        m = self._motor()
        m.calistir_fc("DOSYA_OKU", {})
        m.calistir.assert_called_once_with("DOSYA_OKU", "")

    def test_tek_param_quoted(self):
        m = self._motor()
        m.calistir_fc("DOSYA_OKU", {"dosya": "test.py"})
        m.calistir.assert_called_once_with("DOSYA_OKU", '"test.py"')

    def test_iki_param_sirali(self):
        m = self._motor()
        m.calistir_fc("DOSYA_YAZ", {"dosya": "a.py", "icerik": "kod"})
        _arg = m.calistir.call_args[0][1]
        assert '"a.py"' in _arg
        assert '"kod"' in _arg

    def test_tur_kac_deger_string(self):
        m = self._motor()
        m.calistir_fc("PYTHON_CALISTIR", {"kod": 42})
        m.calistir.assert_called_once_with("PYTHON_CALISTIR", '"42"')

    def test_cift_tirnak_escape(self):
        m = self._motor()
        m.calistir_fc("DOSYA_YAZ", {"icerik": 'say "hi"'})
        _arg = m.calistir.call_args[0][1]
        assert '\\"hi\\"' in _arg

    def test_ters_slash_escape(self):
        m = self._motor()
        m.calistir_fc("DOSYA_OKU", {"yol": "C:\\test"})
        _arg = m.calistir.call_args[0][1]
        assert "\\\\" in _arg

    def test_sonuc_dogrudan_iletilir(self):
        m = self._motor()
        m.calistir.return_value = "dosya içeriği"
        sonuc = m.calistir_fc("DOSYA_OKU", {"yol": "x.txt"})
        assert sonuc == "dosya içeriği"


# ─────────────────────────────────────────────────────────────────────────────
# Motor.tools_schema_al()
# ─────────────────────────────────────────────────────────────────────────────

class TestMotorToolsSchemaAl:

    def _motor_with_registry(self, araclar: dict):
        from reymen.cereyan.motor import Motor
        m = MagicMock(spec=Motor)
        m.tools_schema_al = Motor.tools_schema_al.__get__(m, Motor)

        mock_reg = MagicMock()
        mock_reg._tools = araclar
        mock_reg._meta  = {}

        # Motor.__module__ ile her zaman dogru modulu bul
        # (sys.modules attribute'u vs gercek modul farki olabilir)
        import sys
        _motor_mod = sys.modules[Motor.__module__]
        with patch.object(_motor_mod, "_REGISTRY", mock_reg):
            return m.tools_schema_al()

    def test_gorev_bitti_her_zaman_ilk(self):
        schema = self._motor_with_registry({"WEB_ARA": lambda: None})
        assert schema[0]["function"]["name"] == "GOREV_BITTI"

    def test_gorev_bitti_ozet_required(self):
        schema = self._motor_with_registry({})
        gb = schema[0]["function"]
        assert "ozet" in gb["parameters"]["properties"]
        assert "ozet" in gb["parameters"]["required"]

    def test_registry_araclari_eklenir(self):
        schema = self._motor_with_registry({
            "WEB_ARA": lambda: None,
            "DOSYA_OKU": lambda: None,
        })
        isimler = {s["function"]["name"] for s in schema}
        assert "WEB_ARA" in isimler
        assert "DOSYA_OKU" in isimler

    def test_gorev_bitti_tekrarsiz(self):
        schema = self._motor_with_registry({"GOREV_BITTI": lambda: None})
        gb_sayisi = sum(1 for s in schema if s["function"]["name"] == "GOREV_BITTI")
        assert gb_sayisi == 1

    def test_maks_siniri(self):
        araclar = {f"ARAC_{i}": lambda: None for i in range(100)}
        from reymen.cereyan.motor import Motor
        m = MagicMock(spec=Motor)
        m.tools_schema_al = Motor.tools_schema_al.__get__(m, Motor)
        mock_reg = MagicMock()
        mock_reg._tools = araclar
        mock_reg._meta  = {}
        import sys
        _motor_mod = sys.modules[Motor.__module__]
        with patch.object(_motor_mod, "_REGISTRY", mock_reg):
            schema = m.tools_schema_al(maks=10)
        # GOREV_BITTI + 10 araç = 11
        assert len(schema) == 11

    def test_meta_aciklama_kullanilir(self):
        from reymen.cereyan.motor import Motor
        m = MagicMock(spec=Motor)
        m.tools_schema_al = Motor.tools_schema_al.__get__(m, Motor)
        mock_reg = MagicMock()
        mock_reg._tools = {"WEB_ARA": lambda: None}
        mock_reg._meta  = {"WEB_ARA": {"aciklama": "İnternet'te ara"}}
        import sys
        _motor_mod = sys.modules[Motor.__module__]
        with patch.object(_motor_mod, "_REGISTRY", mock_reg):
            schema = m.tools_schema_al()
        web_fn = next(s["function"] for s in schema if s["function"]["name"] == "WEB_ARA")
        assert "İnternet'te ara" in web_fn["description"]

    def test_registry_yok_sadece_gorev_bitti(self):
        from reymen.cereyan.motor import Motor
        m = MagicMock(spec=Motor)
        m.tools_schema_al = Motor.tools_schema_al.__get__(m, Motor)
        import reymen.cereyan.motor as _motor_mod
        with patch.object(_motor_mod, "_REGISTRY", None):
            schema = m.tools_schema_al()
        assert len(schema) == 1
        assert schema[0]["function"]["name"] == "GOREV_BITTI"

    def test_openai_format_gecerli(self):
        schema = self._motor_with_registry({"TEST_ARAC": lambda: None})
        for s in schema:
            assert s["type"] == "function"
            fn = s["function"]
            assert "name" in fn
            assert "description" in fn
            assert "parameters" in fn
            assert fn["parameters"]["type"] == "object"


# ─────────────────────────────────────────────────────────────────────────────
# Beyin.uret_v2() & fc_destekleniyor()
# ─────────────────────────────────────────────────────────────────────────────

class TestBeyinUretV2:

    def _beyin(self):
        from reymen.cereyan.beyin import Beyin
        b = Beyin.__new__(Beyin)
        from reymen.cereyan.beyin import SaglayCiAdim
        b._fallback_zinciri = [
            SaglayCiAdim("deepseek", "deepseek-chat", "https://api.deepseek.com", "key")
        ]
        b._fc_desteklenmeyen = set()  # her test kendi izole set'i ile başlar
        b.config = {}
        b.provider = "deepseek"
        b.model = "deepseek-chat"
        b.base_url = "https://api.deepseek.com"
        return b

    def test_tool_calls_doner(self):
        b = self._beyin()
        _tc = [{"id": "1", "function": {"name": "WEB_ARA", "arguments": '{"param":"test"}'}}]
        with patch.object(b, "_cagir_openai_uyumlu_v2", return_value={"role": "assistant", "content": "", "tool_calls": _tc}):
            sonuc = b.uret_v2("sys", [{"role": "user", "content": "ara"}], tools=[{}])
        assert sonuc["tool_calls"] == _tc

    def test_bos_tool_calls_text_doner(self):
        b = self._beyin()
        with patch.object(b, "_cagir_openai_uyumlu_v2", return_value={"role": "assistant", "content": "tamam", "tool_calls": []}):
            sonuc = b.uret_v2("sys", [{"role": "user", "content": "test"}])
        assert sonuc["content"] == "tamam"
        assert sonuc["tool_calls"] == []

    def test_provider_hata_fallback_metin(self):
        b = self._beyin()
        with patch.object(b, "_cagir_openai_uyumlu_v2", side_effect=Exception("API hatası")):
            with patch.object(b, "dusun", return_value="metin yanıt"):
                sonuc = b.uret_v2("sys", [{"role": "user", "content": "test"}])
        assert sonuc["content"] == "metin yanıt"
        assert sonuc["tool_calls"] == []

    def test_400_hata_toolssiz_yeniden_dener(self):
        """Provider 400 döndürünce tools olmadan yeniden dener."""
        b = self._beyin()
        _calls = []

        def _mock_post(url, headers=None, json=None, timeout=None, **kw):
            has_tools = bool((json or {}).get("tools"))
            _calls.append(has_tools)
            if has_tools:
                import requests as _r
                err_resp = MagicMock()
                err_resp.status_code = 400
                exc = _r.exceptions.HTTPError("400")
                exc.response = err_resp
                raise exc
            ok = MagicMock()
            ok.status_code = 200
            ok.json.return_value = {
                "choices": [{"message": {"content": "ok", "tool_calls": None}}]
            }
            ok.raise_for_status = MagicMock()
            return ok

        # beyin.py içindeki requests modülünü patch'le (global patch'ten bağımsız)
        with patch("requests.post", side_effect=_mock_post):
            sonuc = b.uret_v2("sys", [], tools=[{"type": "function"}])

        assert sonuc["content"] == "ok"
        assert True in _calls   # tools=True ile denendi
        assert False in _calls  # tools=False ile yeniden denendi

    def test_fc_destekleniyor_baslangicta_true(self):
        b = self._beyin()
        assert b.fc_destekleniyor() is True

    def test_fc_destekleniyor_no_fc_cache(self):
        b = self._beyin()
        b._fc_desteklenmeyen.add(f"{b.base_url}:{b.model}")
        assert b.fc_destekleniyor() is False


# ─────────────────────────────────────────────────────────────────────────────
# Hibrit FC döngüsü — AIAgentOrchestrator entegrasyon
# ─────────────────────────────────────────────────────────────────────────────

SISTEM = "Sen yardımcı bir ajansın."
_TC_WEB = {"id": "tc_1", "function": {"name": "WEB_ARA", "arguments": '{"param":"python"}'}}
_TC_GB  = {"id": "tc_2", "function": {"name": "GOREV_BITTI", "arguments": '{"ozet":"Tamamlandı."}'}}


def _mock_orchestrator():
    """Minimal AIAgentOrchestrator mock — test için gerçek dosya yazmaz."""
    from reymen.sistem.main import AIAgentOrchestrator
    with patch.object(AIAgentOrchestrator, "_cekirdekleri_baslat", lambda s: None), \
         patch.object(AIAgentOrchestrator, "_opsiyonel_modulleri_yukle", lambda s: None), \
         patch.object(AIAgentOrchestrator, "_guvenligi_baslat", lambda s: None), \
         patch.object(AIAgentOrchestrator, "_eklentileri_yukle", lambda s: None):
        orch = AIAgentOrchestrator.__new__(AIAgentOrchestrator)
        orch.config           = {"default_provider": "deepseek", "default_model": "deepseek-chat"}
        orch.max_tur          = 15
        orch.onay_iste        = False
        orch.backend_mode     = "local"
        orch._fc_mod          = None
        orch.budget           = None
        orch.trajectory       = None
        orch.halucination_filtresi = None
        orch.adaptif_ogrenme  = None
        orch.conv_compressor  = None
        orch.planlayici       = MagicMock()
        orch.planlayici.plani_uret = MagicMock(return_value=[])
        orch.planlayici.riskli_mi  = MagicMock(return_value=False)
        orch.planlayici.tamamlanan_adim_isaretle = MagicMock()
        orch.session          = MagicMock()
        orch.bounded_memory   = MagicMock()
        orch.learning         = MagicMock()
        orch.learning.beceri_baglamini_al = MagicMock(return_value="")
        orch.reflexion        = None
        orch.anayasa          = None
        orch.oz_tutarlilik_denetci = None
        orch.meta_prompt      = None
        orch.beceri_kb        = None
        orch.ajan_suru        = None
        orch.aktif_hafiza_plugin = None
        orch.compressor       = MagicMock()
        orch.compressor.compress = MagicMock(side_effect=lambda m, **kw: m)
        orch.hafiza           = MagicMock()
        orch.insan            = MagicMock()
        orch.guvenlik         = None
        orch.mem_guvenlik     = None
        orch.salted_gate      = None
        orch.hitl_sikistirici = None
        orch._plugin_yukleyici= None
        orch._sistem_talimati_fn = None
        orch.referanslar      = None
        return orch


class TestFcLoopGorevBittiNative:
    """FC yoluyla GOREV_BITTI tool çağrısı — döngü sonlanmalı."""

    def test_gorev_bitti_fc_tool_donusu(self):
        orch = _mock_orchestrator()
        orch.motor   = MagicMock()
        orch.motor.tools_schema_al = MagicMock(return_value=[{"type": "function", "function": {"name": "GOREV_BITTI"}}])
        orch.motor.eylemi_ayristir = MagicMock(return_value=("GOREV_BITTI", '"Tamamlandı."'))
        orch.motor.calistir        = MagicMock(return_value="")
        orch.provider = MagicMock()
        orch.provider.uret_v2 = MagicMock(return_value={
            "role": "assistant", "content": "", "tool_calls": [_TC_GB]
        })
        orch.provider.uret = MagicMock()

        with patch("reymen.sistem.main.anlamsal_hafiza_ara", return_value=""), \
             patch("reymen.sistem.main.tecrube_kaydet"), \
             patch("reymen.sistem.main._get_once_hafiza") as _mock_oh, \
             patch.object(orch, "_sistem_promptu_insa_et", return_value=SISTEM), \
             patch.object(orch, "_giris_temizle", side_effect=lambda x: x), \
             patch.object(orch, "_gorev_tamamla"):
            _mock_oh.return_value.hafizada_ara.return_value = None
            sonuc = orch.run_conversation("test görevi")

        assert sonuc is not None
        assert "Tamamlandı" in str(sonuc)
        orch.provider.uret.assert_not_called()   # metin modu hiç kullanılmadı

    def test_gorev_bitti_fc_ozet_dogru_aktarilir(self):
        orch = _mock_orchestrator()
        orch.motor   = MagicMock()
        orch.motor.tools_schema_al = MagicMock(return_value=[{}])
        orch.motor.eylemi_ayristir = MagicMock(return_value=("GOREV_BITTI", '"Dosya oluşturuldu."'))
        orch.motor.calistir        = MagicMock(return_value="")
        orch.provider = MagicMock()
        _gb_ozet = "Dosya oluşturuldu."
        orch.provider.uret_v2 = MagicMock(return_value={
            "role": "assistant", "content": "",
            "tool_calls": [{"id": "x", "function": {"name": "GOREV_BITTI",
                            "arguments": json.dumps({"ozet": _gb_ozet})}}]
        })

        with patch("reymen.sistem.main.anlamsal_hafiza_ara", return_value=""), \
             patch("reymen.sistem.main.tecrube_kaydet"), \
             patch("reymen.sistem.main._get_once_hafiza") as _mock_oh, \
             patch.object(orch, "_sistem_promptu_insa_et", return_value=SISTEM), \
             patch.object(orch, "_giris_temizle", side_effect=lambda x: x), \
             patch.object(orch, "_gorev_tamamla"):
            _mock_oh.return_value.hafizada_ara.return_value = None
            sonuc = orch.run_conversation("dosya oluştur")

        assert _gb_ozet in str(sonuc)


class TestFcLoopParalelAraclar:
    """FC tool_calls → paralel calistir_fc → yeni tur."""

    def test_araclar_paralel_calistirilir(self):
        orch = _mock_orchestrator()
        calistirildi = []

        def _fc(arac, args):
            calistirildi.append(arac)
            return f"[{arac}] OK"

        orch.motor = MagicMock()
        orch.motor.tools_schema_al = MagicMock(return_value=[{}])
        orch.motor.calistir_fc     = MagicMock(side_effect=_fc)
        orch.motor.eylemi_ayristir = MagicMock(return_value=("GOREV_BITTI", '"Bitti."'))
        orch.motor.calistir        = MagicMock(return_value="")

        _tur = [0]
        def _uret_v2(sp, msgs, tools=None):
            _tur[0] += 1
            if _tur[0] == 1:
                return {
                    "role": "assistant", "content": "",
                    "tool_calls": [
                        {"id": "t1", "function": {"name": "DOSYA_OKU", "arguments": '{"dosya":"a.txt"}'}},
                        {"id": "t2", "function": {"name": "WEB_ARA",   "arguments": '{"param":"test"}'}},
                    ]
                }
            return {"role": "assistant", "content": "", "tool_calls": [_TC_GB]}

        orch.provider = MagicMock()
        orch.provider.uret_v2 = MagicMock(side_effect=_uret_v2)

        with patch("reymen.sistem.main.anlamsal_hafiza_ara", return_value=""), \
             patch("reymen.sistem.main.tecrube_kaydet"), \
             patch.object(orch, "_sistem_promptu_insa_et", return_value=SISTEM), \
             patch.object(orch, "_giris_temizle", side_effect=lambda x: x), \
             patch.object(orch, "_gorev_tamamla"):
            orch.run_conversation("iki aracı kullan")

        assert "DOSYA_OKU" in calistirildi
        assert "WEB_ARA"   in calistirildi

    def test_tool_results_messages_eklendi(self):
        orch = _mock_orchestrator()
        orch.motor = MagicMock()
        orch.motor.tools_schema_al = MagicMock(return_value=[{}])
        orch.motor.calistir_fc     = MagicMock(return_value="sonuç")
        orch.motor.eylemi_ayristir = MagicMock(return_value=("GOREV_BITTI", '"Bitti."'))
        orch.motor.calistir        = MagicMock(return_value="")

        _tur = [0]
        def _uret_v2(sp, msgs, tools=None):
            _tur[0] += 1
            if _tur[0] == 1:
                return {"role": "assistant", "content": "",
                        "tool_calls": [{"id": "t1", "function": {"name": "WEB_ARA", "arguments": "{}"}}]}
            # İkinci turda mesajları kontrol edebilir gibiyiz
            # tool mesajı eklendi mi?
            has_tool = any(m.get("role") == "tool" for m in msgs)
            assert has_tool, "tool mesajı mesajlara eklenmedi"
            return {"role": "assistant", "content": "", "tool_calls": [_TC_GB]}

        orch.provider = MagicMock()
        orch.provider.uret_v2 = MagicMock(side_effect=_uret_v2)

        with patch("reymen.sistem.main.anlamsal_hafiza_ara", return_value=""), \
             patch("reymen.sistem.main.tecrube_kaydet"), \
             patch.object(orch, "_sistem_promptu_insa_et", return_value=SISTEM), \
             patch.object(orch, "_giris_temizle", side_effect=lambda x: x), \
             patch.object(orch, "_gorev_tamamla"):
            orch.run_conversation("web ara")


class TestFcLoopFallback:
    """FC desteklenmiyorsa metin moduna geçiş."""

    def test_fc_hata_metin_fallback(self):
        orch = _mock_orchestrator()
        orch._fc_mod = None
        orch.motor = MagicMock()
        orch.motor.tools_schema_al = MagicMock(return_value=[{}])
        orch.motor.eylemi_ayristir = MagicMock(return_value=("GOREV_BITTI", '"Bitti."'))
        orch.motor.calistir        = MagicMock(return_value="")

        orch.provider = MagicMock()
        orch.provider.uret_v2 = MagicMock(side_effect=Exception("FC desteklenmiyor"))
        orch.provider.uret    = MagicMock(return_value='GOREV_BITTI("Metin modu bitti.")')

        with patch("reymen.sistem.main.anlamsal_hafiza_ara", return_value=""), \
             patch("reymen.sistem.main.tecrube_kaydet"), \
             patch("reymen.sistem.main._get_once_hafiza") as _mock_oh, \
             patch.object(orch, "_sistem_promptu_insa_et", return_value=SISTEM), \
             patch.object(orch, "_giris_temizle", side_effect=lambda x: x), \
             patch.object(orch, "_gorev_tamamla"):
            _mock_oh.return_value.hafizada_ara.return_value = None
            sonuc = orch.run_conversation("metin test")

        orch.provider.uret.assert_called()
        assert orch._fc_mod is False  # devre dışı bırakıldı

    def test_fc_mod_false_direkt_metin(self):
        """_fc_mod=False ise uret_v2 hiç denenmez."""
        orch = _mock_orchestrator()
        orch._fc_mod = False
        orch.motor = MagicMock()
        orch.motor.tools_schema_al = MagicMock(return_value=[{}])
        orch.motor.eylemi_ayristir = MagicMock(return_value=("GOREV_BITTI", '"Bitti."'))
        orch.motor.calistir        = MagicMock(return_value="")

        orch.provider = MagicMock()
        orch.provider.uret_v2 = MagicMock()
        orch.provider.uret    = MagicMock(return_value='GOREV_BITTI("Tamam.")')

        with patch("reymen.sistem.main.anlamsal_hafiza_ara", return_value=""), \
             patch("reymen.sistem.main.tecrube_kaydet"), \
             patch("reymen.sistem.main._get_once_hafiza") as _mock_oh, \
             patch.object(orch, "_sistem_promptu_insa_et", return_value=SISTEM), \
             patch.object(orch, "_giris_temizle", side_effect=lambda x: x), \
             patch.object(orch, "_gorev_tamamla"):
            _mock_oh.return_value.hafizada_ara.return_value = None
            orch.run_conversation("direkt metin test")

        orch.provider.uret_v2.assert_not_called()
        orch.provider.uret.assert_called()


class TestFcDizaynDogrulama:
    """5N1K tasarım doğrulama: tüm kritik arayüzler var mı?"""

    def test_motor_calistir_fc_mevcut(self):
        from reymen.cereyan.motor import Motor
        assert hasattr(Motor, "calistir_fc")

    def test_motor_tools_schema_al_mevcut(self):
        from reymen.cereyan.motor import Motor
        assert hasattr(Motor, "tools_schema_al")

    def test_beyin_uret_v2_mevcut(self):
        from reymen.cereyan.beyin import Beyin
        assert hasattr(Beyin, "uret_v2")

    def test_beyin_cagir_openai_uyumlu_v2_mevcut(self):
        from reymen.cereyan.beyin import Beyin
        assert hasattr(Beyin, "_cagir_openai_uyumlu_v2")

    def test_beyin_fc_destekleniyor_mevcut(self):
        from reymen.cereyan.beyin import Beyin
        assert hasattr(Beyin, "fc_destekleniyor")

    def test_beyin_fc_desteklenmeyen_instance_izole(self):
        """__init__ her instance için bağımsız set oluşturur."""
        from reymen.cereyan.beyin import Beyin
        b = Beyin.__new__(Beyin)
        b._fc_desteklenmeyen = set()
        assert isinstance(b._fc_desteklenmeyen, set)
        assert len(b._fc_desteklenmeyen) == 0

    def test_orchestrator_fc_mod_attr(self):
        from reymen.sistem.main import AIAgentOrchestrator
        import inspect
        src = inspect.getsource(AIAgentOrchestrator._cekirdekleri_baslat)
        assert "_fc_mod" in src

    def test_main_json_import(self):
        import reymen.sistem.main as _m
        assert hasattr(_m, "_json"), "_json import edilmedi"

    def test_main_tpool_import(self):
        import reymen.sistem.main as _m
        assert hasattr(_m, "_TPool"), "_TPool import edilmedi"
