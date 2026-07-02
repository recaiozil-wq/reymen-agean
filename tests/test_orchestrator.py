# -*- coding: utf-8 -*-
"""test_orchestrator.py — orchestrator birim testleri (yüzeyel geçiş)."""

import subprocess
from unittest.mock import patch, MagicMock, call

import pytest

from src.core.orchestrator import run_script, solve_step


# ── run_script Testleri ─────────────────────────────────────────────────


class TestRunScript:
    """run_script işlemleri."""

    @patch("reymen.core.orchestrator.subprocess.run")
    def test_run_script_basarili(self, mock_run: MagicMock):
        """Başarılı script çalıştırma → (True, stdout)."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Her sey yolunda\n",
            stderr="",
        )

        success, output = run_script("/fake/path/script.py")
        assert success is True
        assert "Her sey yolunda" in output
        mock_run.assert_called_once()

    @patch("reymen.core.orchestrator.subprocess.run")
    def test_run_script_hata(self, mock_run: MagicMock):
        """Hata alan script → (False, stderr)."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="SyntaxError: invalid syntax",
        )

        success, output = run_script("/fake/path/hata.py")
        assert success is False
        assert "SyntaxError" in output

    @patch("reymen.core.orchestrator.subprocess.run")
    def test_run_script_timeout(self, mock_run: MagicMock):
        """Timeout durumu → (False, TIMEOUT mesajı)."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="python", timeout=120, output=""
        )

        success, output = run_script("/fake/path/yavas.py")
        assert success is False
        assert "TIMEOUT" in output and "120" in output

    def test_run_script_var_olmayan_dosya(self):
        """Var olmayan dosya → (False, hata mesajı)."""
        success, output = run_script("/kesinlikle/yok/boyle_bir_dosya.py")
        assert success is False
        assert output  # hata mesajı boş değil (FileNotFoundError vs.)


# ── solve_step Testleri ────────────────────────────────────────────────


class TestSolveStep:
    """solve_step işlemleri (üst seviye)."""

    @patch("reymen.core.orchestrator.run_script", return_value=(True, "Basarili\n"))
    def test_solve_step_basarili(self, mock_run: MagicMock, tmp_path):
        """Var olan script için solve_step → True döner."""
        script = tmp_path / "test_script.py"
        script.write_text("print('merhaba')")

        sonuc = solve_step("test_adimi", str(script))
        assert sonuc is True

    def test_solve_step_var_olmayan_script(self, tmp_path):
        """Var olmayan script → solve_step False döner."""
        sonuc = solve_step("kayip_adim", str(tmp_path / "yok_olan.py"))
        assert sonuc is False


# ═══════════════════════════════════════════════════════════════════════
# YENİ TEST SINIFLARI — mevcut testleri BOZMAZ
# ═══════════════════════════════════════════════════════════════════════


class TestGetAdapter:
    """_get_adapter lazy initialization."""

    @patch("reymen.core.orchestrator.get_active_adapter")
    def test_get_adapter_lazy_init(self, mock_get_adapter: MagicMock):
        """Adapter None iken ilk çağrıda init edilir."""
        from reymen.core.orchestrator import _get_adapter

        # adapter global'ini sıfırla
        import reymen.core.orchestrator as orch
        orch.adapter = None

        mock_adapter = MagicMock()
        mock_get_adapter.return_value = mock_adapter

        result = _get_adapter()
        assert result is mock_adapter
        mock_get_adapter.assert_called_once_with()

    @patch("reymen.core.orchestrator.get_active_adapter")
    def test_get_adapter_returns_cached(self, mock_get_adapter: MagicMock):
        """Adapter zaten varsa tekrar init edilmez."""
        from reymen.core.orchestrator import _get_adapter

        import reymen.core.orchestrator as orch
        cached = MagicMock()
        orch.adapter = cached

        result = _get_adapter()
        assert result is cached
        mock_get_adapter.assert_not_called()

        # Temizlik
        orch.adapter = None


class TestAskModelToFix:
    """ask_model_to_fix — LLM çağrısı."""

    @patch("reymen.core.orchestrator._get_adapter")
    def test_ask_model_to_fix_calls_adapter(self, mock_get_adapter: MagicMock):
        """Adapter.complete çağrılır ve prompt içinde hata+kod bulunur."""
        from reymen.core.orchestrator import ask_model_to_fix

        mock_adapter = MagicMock()
        mock_adapter.complete.return_value = "düzeltilmiş_kod"
        mock_get_adapter.return_value = mock_adapter

        result = ask_model_to_fix("print(1/0)", "ZeroDivisionError")

        assert result == "düzeltilmiş_kod"
        mock_adapter.complete.assert_called_once()
        prompt_arg = mock_adapter.complete.call_args[0][0]
        assert "ZeroDivisionError" in prompt_arg
        assert "print(1/0)" in prompt_arg

    @patch("reymen.core.orchestrator._get_adapter")
    def test_ask_model_to_fix_adapter_none(self, mock_get_adapter: MagicMock):
        """Adapter None ise hata fırlatılır."""
        from reymen.core.orchestrator import ask_model_to_fix

        import reymen.core.orchestrator as orch
        orch.adapter = None

        mock_get_adapter.side_effect = RuntimeError("Adapter bulunamadi")
        with pytest.raises(RuntimeError):
            ask_model_to_fix("x", "y")

        orch.adapter = None


class TestSolveStepRetry:
    """solve_step retry ve hata akışları."""

    @patch("reymen.core.orchestrator.ask_model_to_fix", return_value="fixed_code")
    @patch("reymen.core.orchestrator.run_script")
    def test_solve_step_fail_once_then_succeed(
        self, mock_run: MagicMock, mock_ask: MagicMock, tmp_path
    ):
        """İlk denemede hata, ikinci denemede başarı."""
        # İlk çağrı hata, ikinci çağrı başarılı
        mock_run.side_effect = [
            (False, "SyntaxError"),
            (True, "Basarili"),
        ]

        script = tmp_path / "test.py"
        script.write_text("original code")

        sonuc = solve_step("test", str(script))
        assert sonuc is True
        assert mock_run.call_count == 2
        mock_ask.assert_called_once()

    @patch("reymen.core.orchestrator.ask_model_to_fix", return_value="fixed_code")
    @patch("reymen.core.orchestrator.run_script")
    def test_solve_step_all_retries_exhausted(
        self, mock_run: MagicMock, mock_ask: MagicMock, tmp_path
    ):
        """Tüm MAX_RETRIES denemesi başarısız → False döner."""
        mock_run.return_value = (False, "Persistent Error")

        script = tmp_path / "test.py"
        script.write_text("original code")

        sonuc = solve_step("test", str(script))
        assert sonuc is False
        # MAX_RETRIES = 3 kez denendi
        assert mock_run.call_count == 3
        assert mock_ask.call_count == 3

    @patch("reymen.core.orchestrator.ask_model_to_fix", return_value="fixed_code")
    @patch("reymen.core.orchestrator.run_script")
    def test_solve_step_fix_files_created(
        self, mock_run: MagicMock, mock_ask: MagicMock, tmp_path
    ):
        """Hata durumunda fix/ dizini ve fix dosyaları oluşturulur."""
        mock_run.return_value = (False, "Hata mesaji")

        script = tmp_path / "test.py"
        script.write_text("original code")

        sonuc = solve_step("test", str(script))
        assert sonuc is False

        fix_dir = tmp_path / "fix"
        assert fix_dir.exists()
        # solve_step path'i her retry'de fix dosyasına günceller,
        # bu yüzden fix dosyaları iç içe dizinlerde oluşur:
        # fix/test_fix_v1.py, fix/fix/test_fix_v1_fix_v2.py, ...
        fix_files = list(fix_dir.rglob("*.py"))
        assert len(fix_files) == 3
        for f in fix_files:
            assert f.read_text("utf-8") == "fixed_code"


class TestSolveAll:
    """solve_all — tüm adımları sırayla çöz."""

    @patch("reymen.core.orchestrator.solve_step")
    def test_solve_all_all_success(self, mock_solve_step: MagicMock):
        """Tüm adımlar başarılı → hepsi True."""
        mock_solve_step.return_value = True
        from reymen.core.orchestrator import solve_all

        steps = [("adim1", "/p1.py"), ("adim2", "/p2.py"), ("adim3", "/p3.py")]
        results = solve_all(steps)

        assert results == {"adim1": True, "adim2": True, "adim3": True}
        assert mock_solve_step.call_count == 3

    @patch("reymen.core.orchestrator.solve_step")
    def test_solve_all_mixed_results(self, mock_solve_step: MagicMock):
        """Bazı adımlar başarısız → karışık sonuçlar."""
        mock_solve_step.side_effect = [True, False, True]
        from reymen.core.orchestrator import solve_all

        steps = [("ok1", "/p1.py"), ("fail1", "/p2.py"), ("ok2", "/p3.py")]
        results = solve_all(steps)

        assert results == {"ok1": True, "fail1": False, "ok2": True}
        assert mock_solve_step.call_count == 3


class TestCozHata:
    """coz_hata — doğrudan hata çözümü."""

    @patch("reymen.core.orchestrator._log")
    @patch("reymen.core.orchestrator.ask_model_to_fix", return_value="fixed_kod")
    def test_coz_hata_with_code(
        self, mock_ask: MagicMock, mock_log: MagicMock
    ):
        """kod verilmişse → ask_model_to_fix çağrılır, düzeltilmiş kod döner."""
        from reymen.core.orchestrator import coz_hata

        result = coz_hata(hata="ZeroDivisionError", kod="print(1/0)", ad="test_fix")
        assert result == "fixed_kod"
        mock_ask.assert_called_once_with("print(1/0)", "ZeroDivisionError")
        mock_log.assert_called_once()

    @patch("reymen.core.orchestrator._log")
    @patch("reymen.core.orchestrator.ask_model_to_fix")
    def test_coz_hata_without_code(
        self, mock_ask: MagicMock, mock_log: MagicMock
    ):
        """kod verilmemişse → sadece log mesajı döner, model çağrılmaz."""
        from reymen.core.orchestrator import coz_hata

        result = coz_hata(hata="Some error", kod="", ad="acil_fix")
        assert "[COZ]" in result
        assert "Some error" in result
        mock_ask.assert_not_called()
        mock_log.assert_not_called()
