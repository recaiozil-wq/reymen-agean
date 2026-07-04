# -*- coding: utf-8 -*-
"""dispatcher.py için pytest testleri.

ToolDispatcher, üç harici bağımlılık kullanır:
  - ToolRegistry  (tool_registry modülü)
  - ToolGuardrails (tool_guardrails modülü)
  - ToolExecutor   (tool_executor modülü)

Bu testler, bu bağımlılıkları unittest.mock ile izole eder.
dispatcher modülü import edilmeden ÖNCE sys.modules'a mock enjekte edilir,
böylece gerçek bağımlılıklar hiç yüklenmez.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Proje kökünü ekle ──────────────────────────────────────────────────────
_proje_kok = Path(__file__).resolve().parent.parent
if str(_proje_kok) not in sys.path:
    sys.path.insert(0, str(_proje_kok))

# ── Bağımlılıkları dispatcher import edilmeden ÖNCE mock'la ───────────────
# dispatcher.py: "from tool_registry import ToolRegistry"
# dispatcher.py: "from tool_guardrails import ToolGuardrails"
# dispatcher.py: "from tool_executor import ToolExecutor"
# Bunlar module-level import'lar olduğu için sys.modules'a mock girmeliyiz.

mock_registry_module = MagicMock()
mock_registry_module.ToolRegistry = MagicMock()

mock_guardrails_module = MagicMock()
mock_guardrails_module.ToolGuardrails = MagicMock()

mock_executor_module = MagicMock()
mock_executor_module.ToolExecutor = MagicMock()

_original_modules = {}


def _install_mocks():
    """Mock modülleri sys.modules'a yerleştir."""
    _original_modules["src.reymen.arac.tool_registry"] = sys.modules.get("src.reymen.arac.tool_registry")
    _original_modules["src.reymen.guvenlik.tool_guardrails"] = sys.modules.get("src.reymen.guvenlik.tool_guardrails")
    _original_modules["src.reymen.arac.tool_executor"] = sys.modules.get("src.reymen.arac.tool_executor")
    _original_modules["tool_registry"] = sys.modules.get("tool_registry")
    _original_modules["tool_guardrails"] = sys.modules.get("tool_guardrails")
    _original_modules["tool_executor"] = sys.modules.get("tool_executor")

    sys.modules["src.reymen.arac.tool_registry"] = mock_registry_module
    sys.modules["src.reymen.guvenlik.tool_guardrails"] = mock_guardrails_module
    sys.modules["src.reymen.arac.tool_executor"] = mock_executor_module
    sys.modules["tool_registry"] = mock_registry_module
    sys.modules["tool_guardrails"] = mock_guardrails_module
    sys.modules["tool_executor"] = mock_executor_module


def _restore_mocks():
    """Orijinal modülleri sys.modules'a geri koy."""
    for key, val in _original_modules.items():
        if val is None:
            sys.modules.pop(key, None)
        else:
            sys.modules[key] = val
    _original_modules.clear()


# ── Yardımcı: mock dict'leri ──────────────────────────────────────────────


def _mock_kayit(module: str = "ornek_tool", callable: str = "run") -> dict:
    return {"module": module, "callable": callable}


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture(scope="module", autouse=True)
def _mock_dependencies():
    """Tüm modül seviyesindeki bağımlılıkları tek seferde mock'la."""
    _install_mocks()
    yield
    _restore_mocks()


@pytest.fixture
def dispatcher():
    """Mock bağımlılıklarla oluşturulmuş ToolDispatcher örneği."""
    # Her test için taze mock örnekleri
    reg = MagicMock()
    reg.resolve = MagicMock()
    reg.liste = MagicMock(return_value=["tool_a", "tool_b", "tool_c"])

    gr = MagicMock()
    gr.kontrolet = MagicMock(return_value={"guvenli": True, "sebep": None})

    ex = MagicMock()
    ex.calistir_tool = MagicMock(return_value={"ok": True, "sonuc": "calisti"})
    ex.calistir_guvenli = MagicMock(
        return_value={"ok": True, "sonuc": "guvenli_calisti"}
    )

    # ToolRegistry, ToolGuardrails, ToolExecutor constructor'larını mock'la
    mock_registry_module.ToolRegistry.return_value = reg
    mock_guardrails_module.ToolGuardrails.return_value = gr
    mock_executor_module.ToolExecutor.return_value = ex

    from reymen.cereyan.dispatcher import ToolDispatcher

    d = ToolDispatcher()
    d._mock_registry = reg
    d._mock_guardrails = gr
    d._mock_executor = ex
    return d


# ── __init__ ───────────────────────────────────────────────────────────────


class TestInit:
    """ToolDispatcher başlatma."""

    def test_attributes_olusturulur(self, dispatcher):
        """ToolDispatcher örneği gerekli attribute'lara sahip olmalı."""
        assert hasattr(dispatcher, "registry")
        assert hasattr(dispatcher, "guardrails")
        assert hasattr(dispatcher, "executor")

    def test_bilesenler_mock_olarak_atanir(self, dispatcher):
        """Bağımlılıklar mock örnekleri olarak atanmalı."""
        assert isinstance(dispatcher.registry, MagicMock)


# ── dispatch ───────────────────────────────────────────────────────────────


class TestDispatch:
    """dispatch metodunun davranış testleri."""

    def test_basarili_dispatch(self, dispatcher):
        """Bilinen bir tool başarıyla çalıştırılmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        sonuc = dispatcher.dispatch("ornek_tool", {"param": "deger"})
        assert sonuc["ok"] is True

    def test_bilinmeyen_tool_hata_dondurur(self, dispatcher):
        """Kayıtlı olmayan tool için hata döndürülmeli."""
        dispatcher._mock_registry.resolve.return_value = None
        sonuc = dispatcher.dispatch("var_olmayan_tool")
        assert sonuc["ok"] is False
        assert "Bilinmeyen" in sonuc["error"]

    def test_bilinmeyen_tool_tool_adi_donuste(self, dispatcher):
        """Hata durumunda tool adı dönüşte yer almalı."""
        dispatcher._mock_registry.resolve.return_value = None
        sonuc = dispatcher.dispatch("bilinmeyen_x")
        assert sonuc["tool"] == "bilinmeyen_x"

    def test_guardrails_reddederse_hata_dondurur(self, dispatcher):
        """Guardrails reddettiğinde hatalı dönüş yapılmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        dispatcher._mock_guardrails.kontrolet.return_value = {
            "guvenli": False,
            "sebep": "Riskli modül",
        }
        sonuc = dispatcher.dispatch("ornek_tool")
        assert sonuc["ok"] is False
        assert "Riskli" in sonuc["error"]

    def test_guardrails_red_guard_bilgisi_eklenir(self, dispatcher):
        """Guardrails reddinde guard bilgisi dönüşte olmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        guard_dict = {"guvenli": False, "sebep": "Engellendi"}
        dispatcher._mock_guardrails.kontrolet.return_value = guard_dict
        sonuc = dispatcher.dispatch("ornek_tool")
        assert sonuc["guard"] == guard_dict

    def test_varsayilan_args_context_bos_olanak_verir(self, dispatcher):
        """args ve context olmadan çağrı da çalışmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        sonuc = dispatcher.dispatch("ornek_tool")
        assert sonuc["ok"] is True
        dispatcher._mock_executor.calistir_tool.assert_called_once()

    def test_args_context_dogru_aktarilir(self, dispatcher):
        """args ve context executor'a doğru aktarılmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        dispatcher.dispatch("ornek_tool", {"key": "val"}, {"ctx": "info"}, timeout=30)
        dispatcher._mock_executor.calistir_tool.assert_called_once_with(
            "ornek_tool", timeout=30, key="val"
        )

    def test_alias_run_degilse_execute_function_cagrilir(self, dispatcher):
        """callable != 'run' ise _execute_function kullanılmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit(
            callable="ozel_fonksiyon"
        )
        with patch.object(dispatcher, "_execute_function", return_value={"ok": True}):
            sonuc = dispatcher.dispatch("ornek_tool")
            assert sonuc["ok"] is True

    def test_alias_run_ise_executor_calistir_tool_cagrilir(self, dispatcher):
        """callable == 'run' ise executor.calistir_tool kullanılmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit(callable="run")
        dispatcher.dispatch("ornek_tool")
        dispatcher._mock_executor.calistir_tool.assert_called_once()

    def test_timeout_executor_iletilir(self, dispatcher):
        """timeout parametresi executor'a aktarılmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        dispatcher.dispatch("ornek_tool", timeout=60)
        dispatcher._mock_executor.calistir_tool.assert_called_once_with(
            "ornek_tool", timeout=60
        )

    def test_guardrails_module_name_ile_cagrilir(self, dispatcher):
        """Guardrails modül adı ile çağrılmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit(
            module="filtrelenen_modul"
        )
        dispatcher.dispatch("ornek_tool")
        dispatcher._mock_guardrails.kontrolet.assert_called_once_with(
            "filtrelenen_modul"
        )


# ── _execute_function ──────────────────────────────────────────────────────


class TestExecuteFunction:
    """_execute_function metodunun davranış testleri."""

    def test_basarili_fonksiyon_cagrisi(self, dispatcher):
        """Alias fonksiyon başarıyla çağrılmalı."""
        with patch("reymen.cereyan.dispatcher.importlib.import_module") as mock_import:
            mock_mod = MagicMock()
            mock_fn = MagicMock(return_value={"ok": True, "sonuc": "aliastan"})
            setattr(mock_mod, "ozel_islem", mock_fn)
            mock_import.return_value = mock_mod

            sonuc = dispatcher._execute_function(
                "ornek_modul", "ozel_islem", {"x": 1}, None
            )
            assert sonuc["ok"] is True

    def test_fonksiyon_bulunamazsa_hata(self, dispatcher):
        """Olmayan bir fonksiyon için hata döndürülmeli."""
        with patch("reymen.cereyan.dispatcher.importlib.import_module") as mock_import:
            mock_mod = MagicMock(spec=[])  # hiçbir attribute yok
            mock_import.return_value = mock_mod

            sonuc = dispatcher._execute_function(
                "ornek_modul", "var_olmayan_fn", {}, None
            )
            assert sonuc["ok"] is False
            assert "bulunamadi" in sonuc["error"]

    def test_exception_halinde_hata_yakalanir(self, dispatcher):
        """Fonksiyon içinde exception fırlatılırsa yakalanmalı."""
        with patch(
            "reymen.cereyan.dispatcher.importlib.import_module",
            side_effect=ImportError("modul bulunamadi"),
        ):
            sonuc = dispatcher._execute_function("olmayan_modul", "run", {}, None)
            assert sonuc["ok"] is False
            assert "modul bulunamadi" in sonuc["error"]


# ── list_tools ─────────────────────────────────────────────────────────────


class TestListTools:
    """list_tools metodunun davranış testleri."""

    def test_liste_dondurur(self, dispatcher):
        """list_tools registry.liste() sonucunu döndürmeli."""
        tools = dispatcher.list_tools()
        assert tools == ["tool_a", "tool_b", "tool_c"]

    def test_registry_liste_cagrilir(self, dispatcher):
        """list_tools registry.liste() metodunu çağırmalı."""
        dispatcher.list_tools()
        dispatcher._mock_registry.liste.assert_called_once_with()

    def test_bos_liste_donebilir(self, dispatcher):
        """Registry boş liste döndürdüğünde de çalışmalı."""
        dispatcher._mock_registry.liste.return_value = []
        assert dispatcher.list_tools() == []


# ── tool_schema ─────────────────────────────────────────────────────────────


class TestToolSchema:
    """tool_schema metodunun davranış testleri."""

    def test_var_olan_tool_schema_dondurur(self, dispatcher):
        """Var olan bir tool için schema döndürülmeli."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit(
            module="ornek_modul"
        )
        with patch("reymen.cereyan.dispatcher.importlib.import_module") as mock_import:
            mock_mod = MagicMock()
            mock_mod.SCHEMA = {"type": "object", "properties": {}}
            mock_import.return_value = mock_mod

            sonuc = dispatcher.tool_schema("ornek_tool")
            assert "schema" in sonuc
            assert sonuc["schema"]["type"] == "object"

    def test_schema_yoksa_yok_bilgisi_dondurur(self, dispatcher):
        """SCHEMA attribute'u yoksa 'yok' döndürülmeli."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit(
            module="schemasi_olmayan"
        )
        with patch("reymen.cereyan.dispatcher.importlib.import_module") as mock_import:
            mock_mod = MagicMock(spec=["__name__"])  # SCHEMA yok
            mock_import.return_value = mock_mod

            sonuc = dispatcher.tool_schema("ornek_tool")
            assert sonuc["schema"] == "yok"

    def test_bilinmeyen_tool_hata_dondurur(self, dispatcher):
        """Bilinmeyen bir tool için hata döndürülmeli."""
        dispatcher._mock_registry.resolve.return_value = None
        sonuc = dispatcher.tool_schema("var_olmayan")
        assert "error" in sonuc

    def test_import_exception_yakalanir(self, dispatcher):
        """Modül import edilemezse hata yakalanmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit(
            module="bozuk_modul"
        )
        with patch(
            "reymen.cereyan.dispatcher.importlib.import_module", side_effect=ImportError("bozuk")
        ):
            sonuc = dispatcher.tool_schema("ornek_tool")
            assert "error" in sonuc


# ── dispatch edge cases ────────────────────────────────────────────────────


class TestDispatchEdgeCases:
    """dispatch metodunun kenar durumları."""

    def test_none_args_dict_olur(self, dispatcher):
        """args=None verildiğinde boş dict'e dönüşmeli."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        dispatcher.dispatch("ornek_tool", args=None)
        called_kwargs = dispatcher._mock_executor.calistir_tool.call_args.kwargs
        # timeout dışında parametre olmamalı
        extra = {k: v for k, v in called_kwargs.items() if k != "timeout"}
        assert extra == {}

    def test_none_context_dict_olur(self, dispatcher):
        """context=None verildiğinde sorunsuz çalışmalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        sonuc = dispatcher.dispatch("ornek_tool", context=None)
        assert sonuc["ok"] is True

    def test_executor_hatasi_yayilir(self, dispatcher):
        """Executor hata döndürdüğünde bu dönüşte yansımalı."""
        dispatcher._mock_registry.resolve.return_value = _mock_kayit()
        dispatcher._mock_executor.calistir_tool.return_value = {
            "ok": False,
            "error": "Tool çalıştırılamadı",
        }
        sonuc = dispatcher.dispatch("ornek_tool")
        assert sonuc["ok"] is False
        assert "çalıştırılamadı" in sonuc["error"]
