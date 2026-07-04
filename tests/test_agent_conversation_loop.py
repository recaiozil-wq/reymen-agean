# -*- coding: utf-8 -*-
"""
test_agent_conversation_loop.py — agent/conversation_loop.py testleri (~35 test)
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock, ANY


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_agent():
    """Basit bir agent mock'u."""
    agent = MagicMock()
    agent.session_id = "test-session-123"
    agent.model = "gpt-4"
    agent.provider = "openai"
    agent.base_url = "https://api.openai.com"
    agent.api_key = "sk-test"
    agent.api_mode = "chat_completions"
    agent.platform = "cli"
    agent.tools = []
    agent.valid_tool_names = set()
    agent.max_iterations = 25
    agent.quiet_mode = False
    agent._cached_system_prompt = None
    agent._memory_manager = None
    agent._memory_store = None
    agent._session_db = None
    agent._todo_store = MagicMock()
    agent._todo_store.has_items = MagicMock(return_value=False)
    agent._user_turn_count = 0
    agent._turns_since_memory = 0
    agent._iters_since_skill = 0
    agent._memory_nudge_interval = 0
    agent._skill_nudge_interval = 0
    agent._ollama_num_ctx = None
    agent.compression_enabled = False
    agent.context_compressor = MagicMock()
    agent._compression_warning = None
    agent._stream_callback = None
    agent._persist_user_message_idx = None
    agent._persist_user_message_override = None
    agent._current_task_id = None
    agent._invalid_tool_retries = 0
    agent._invalid_json_retries = 0
    agent._empty_content_retries = 0
    agent._incomplete_scratchpad_retries = 0
    agent._codex_incomplete_retries = 0
    agent._thinking_prefill_retries = 0
    agent._post_tool_empty_retried = False
    agent._last_content_with_tools = None
    agent._last_content_tools_all_housekeeping = False
    agent._mute_post_response = False
    agent._unicode_sanitization_passes = 0
    agent._vision_supported = True
    agent._interrupt_requested = False
    agent._interrupt_message = None
    agent._interrupt_thread_signal_pending = False
    agent._execution_thread_id = None
    agent._budget_grace_call = False
    agent._api_call_count = 0
    agent._checkpoint_mgr = MagicMock()
    agent._turn_failed_file_mutations = {}
    agent._pending_steer = None
    agent._pending_steer_lock = None
    agent._tool_guardrails = MagicMock()
    agent._tool_guardrail_halt_decision = None
    agent.iteration_budget = MagicMock()
    agent.iteration_budget.remaining = 25
    agent.iteration_budget.consume = MagicMock(return_value=True)
    agent.iteration_budget.used = 1
    agent.iteration_budget.max_total = 25
    agent._stream_context_scrubber = None
    agent._stream_think_scrubber = None
    agent._sanitize_tool_call_arguments = MagicMock(return_value=0)
    agent._repair_message_sequence = MagicMock(return_value=0)
    agent._copy_reasoning_content_for_api = MagicMock()
    agent._should_sanitize_tool_calls = MagicMock(return_value=False)
    agent._sanitize_tool_calls_for_strict_api = MagicMock()
    agent._restore_primary_runtime = MagicMock()
    agent._ensure_db_session = MagicMock()
    agent._build_system_prompt = MagicMock(return_value="Sistem promptu")
    agent._compress_context = MagicMock(return_value=([], ""))
    agent._hydrate_todo_store = MagicMock()
    agent._cleanup_dead_connections = MagicMock(return_value=False)
    agent._emit_status = MagicMock()
    agent._replay_compression_warning = MagicMock()
    agent._safe_print = MagicMock()
    agent._vprint = MagicMock()
    agent._set_interrupt = MagicMock()
    agent._touch_activity = MagicMock()
    agent._drain_pending_steer = MagicMock(return_value=None)
    agent._run_codex_app_server_turn = MagicMock()
    agent.step_callback = None
    agent.log_prefix = "[Test]"
    agent._memory_write_origin = "assistant_tool"
    return agent


# ---------------------------------------------------------------------------
# _ollama_context_limit_error
# ---------------------------------------------------------------------------


class TestOllamaContextLimitError:
    @patch("agent.conversation_loop.MINIMUM_CONTEXT_LENGTH", 8192)
    def test_no_tools_none(self, mock_agent):
        from agent.conversation_loop import _ollama_context_limit_error

        agent = MagicMock()
        agent.tools = None
        agent._ollama_num_ctx = 4096
        assert _ollama_context_limit_error(agent, 100) is None

    @patch("agent.conversation_loop.MINIMUM_CONTEXT_LENGTH", 8192)
    def test_no_ollama_num_ctx_none(self, mock_agent):
        from agent.conversation_loop import _ollama_context_limit_error

        agent = MagicMock()
        agent.tools = ["tool1"]
        agent._ollama_num_ctx = None
        assert _ollama_context_limit_error(agent, 100) is None

    @patch("agent.conversation_loop.MINIMUM_CONTEXT_LENGTH", 8192)
    def test_runtime_ctx_yeterli_none(self, mock_agent):
        from agent.conversation_loop import _ollama_context_limit_error

        agent = MagicMock()
        agent.tools = ["tool1"]
        agent._ollama_num_ctx = 16384
        assert _ollama_context_limit_error(agent, 100) is None

    @patch("agent.conversation_loop.MINIMUM_CONTEXT_LENGTH", 8192)
    def test_runtime_ctx_yetersiz_mesaj_doner(self, mock_agent):
        from agent.conversation_loop import _ollama_context_limit_error

        agent = MagicMock()
        agent.tools = ["tool1"]
        agent._ollama_num_ctx = 4096
        agent.model = "llama3"
        agent.base_url = "http://localhost:11434"
        agent.provider = "ollama"
        agent.session_id = "s-1"
        msg = _ollama_context_limit_error(agent, 500)
        assert msg is not None
        assert "4,096" in msg
        assert "8,192" in msg
        assert "llama3" in msg


# ---------------------------------------------------------------------------
# _is_nous_inference_route
# ---------------------------------------------------------------------------


class TestIsNousInferenceRoute:
    def test_nous_provider(self):
        from agent.conversation_loop import _is_nous_inference_route

        assert _is_nous_inference_route("nous", "") is True

    def test_nous_case_insensitive(self):
        from agent.conversation_loop import _is_nous_inference_route

        assert _is_nous_inference_route("Nous", "") is True
        assert _is_nous_inference_route("NOUS", "") is True

    def test_nous_inference_api_url(self):
        from agent.conversation_loop import _is_nous_inference_route

        assert (
            _is_nous_inference_route("", "https://inference-api.nousresearch.com/v1")
            is True
        )

    def test_nous_inference_url(self):
        from agent.conversation_loop import _is_nous_inference_route

        assert (
            _is_nous_inference_route("", "https://inference.nousresearch.com") is True
        )

    def test_other_provider(self):
        from agent.conversation_loop import _is_nous_inference_route

        assert _is_nous_inference_route("openai", "https://api.openai.com") is False

    def test_bos_both(self):
        from agent.conversation_loop import _is_nous_inference_route

        assert _is_nous_inference_route("", "") is False

    def test_none_values(self):
        from agent.conversation_loop import _is_nous_inference_route

        assert _is_nous_inference_route(None, None) is False


# ---------------------------------------------------------------------------
# _billing_or_entitlement_message
# ---------------------------------------------------------------------------


class TestBillingOrEntitlementMessage:
    def test_nous_entitlement_calls_nous_func(self):
        with patch(
            "agent.conversation_loop._is_nous_inference_route", return_value=True
        ):
            with patch(
                "agent.conversation_loop._nous_entitlement_message",
                return_value="Abonelik mesaji",
            ):
                from agent.conversation_loop import _billing_or_entitlement_message

                msg = _billing_or_entitlement_message(
                    capability="tools",
                    provider="nous",
                    base_url="",
                    model="nous-1",
                )
                assert "Abonelik mesaji" in msg

    def test_genel_faturalama_mesaji(self):
        from agent.conversation_loop import _billing_or_entitlement_message

        msg = _billing_or_entitlement_message(
            capability="tools",
            provider="openai",
            base_url="https://api.openai.com",
            model="gpt-4",
        )
        assert (
            "billing" in msg.lower()
            or "credits" in msg.lower()
            or "entitlement" in msg.lower()
        )

    def test_openrouter_url_ek_ipucu_verir(self):
        from agent.conversation_loop import _billing_or_entitlement_message

        msg = _billing_or_entitlement_message(
            capability="tools",
            provider="openrouter",
            base_url="https://openrouter.ai",
            model="gpt-4",
        )
        assert "openrouter.ai" in msg

    def test_model_degistirme_onerisi_var(self):
        from agent.conversation_loop import _billing_or_entitlement_message

        msg = _billing_or_entitlement_message(
            capability="tools",
            provider="openai",
            base_url="https://api.openai.com",
            model="gpt-4",
        )
        assert "/model" in msg


# ---------------------------------------------------------------------------
# _get_continuation_prompt
# ---------------------------------------------------------------------------


class TestGetContinuationPrompt:
    def test_partial_stub_with_dropped_tools(self):
        from agent.conversation_loop import _get_continuation_prompt

        msg = _get_continuation_prompt(
            is_partial_stub=True, dropped_tools=["tool1", "tool2"]
        )
        assert "too large" in msg.lower()
        assert "tool1" in msg
        assert "Do NOT retry" in msg

    def test_partial_stub_without_tools(self):
        from agent.conversation_loop import _get_continuation_prompt

        msg = _get_continuation_prompt(is_partial_stub=True)
        assert "cut off" in msg.lower()
        assert "Continue exactly" in msg

    def test_truncated_continuation(self):
        from agent.conversation_loop import _get_continuation_prompt

        msg = _get_continuation_prompt(is_partial_stub=False)
        assert "truncated" in msg.lower()
        assert "Continue exactly" in msg

    def test_dropped_tools_limited_to_3(self):
        from agent.conversation_loop import _get_continuation_prompt

        tools = [f"tool{i}" for i in range(10)]
        msg = _get_continuation_prompt(is_partial_stub=True, dropped_tools=tools)
        # Only first 3 should appear
        assert "tool0" in msg
        assert "tool1" in msg
        assert "tool2" in msg
        assert "tool3" not in msg


# ---------------------------------------------------------------------------
# _restore_or_build_system_prompt
# ---------------------------------------------------------------------------


class TestRestoreOrBuildSystemPrompt:
    def test_stored_prompt_kullanilir(self, mock_agent):
        from agent.conversation_loop import _restore_or_build_system_prompt

        mock_agent._session_db = MagicMock()
        mock_agent._session_db.get_session = MagicMock(
            return_value={"system_prompt": "kaydedilmis prompt"}
        )
        _restore_or_build_system_prompt(mock_agent, None, [{"role": "user"}])
        assert mock_agent._cached_system_prompt == "kaydedilmis prompt"
        mock_agent._build_system_prompt.assert_not_called()

    def test_null_stored_prompt_yeniden_build_eder(self, mock_agent):
        from agent.conversation_loop import _restore_or_build_system_prompt

        mock_agent._session_db = MagicMock()
        mock_agent._session_db.get_session = MagicMock(
            return_value={"system_prompt": None}
        )
        _restore_or_build_system_prompt(mock_agent, None, [{"role": "user"}])
        mock_agent._build_system_prompt.assert_called_once()

    def test_bos_gecmis_yine_de_build_eder(self, mock_agent):
        from agent.conversation_loop import _restore_or_build_system_prompt

        _restore_or_build_system_prompt(mock_agent, None, [])
        mock_agent._build_system_prompt.assert_called_once()

    def test_empty_stored_prompt_yeniden_build_eder(self, mock_agent):
        from agent.conversation_loop import _restore_or_build_system_prompt

        mock_agent._session_db = MagicMock()
        mock_agent._session_db.get_session = MagicMock(
            return_value={"system_prompt": ""}
        )
        _restore_or_build_system_prompt(mock_agent, None, [{"role": "user"}])
        mock_agent._build_system_prompt.assert_called_once()

    def test_session_db_hatasi_warning_log(self, mock_agent, caplog):
        import logging

        caplog.set_level(logging.WARNING)
        from agent.conversation_loop import _restore_or_build_system_prompt

        mock_agent._session_db = MagicMock()
        mock_agent._session_db.get_session = MagicMock(
            side_effect=ValueError("DB error")
        )
        _restore_or_build_system_prompt(mock_agent, None, [{"role": "user"}])
        assert any("Session DB get_session failed" in r.message for r in caplog.records)
        mock_agent._build_system_prompt.assert_called_once()

    def test_persist_sonrasi_update_cagrilir(self, mock_agent):
        from agent.conversation_loop import _restore_or_build_system_prompt

        mock_agent._session_db = MagicMock()
        mock_agent._session_db.get_session = MagicMock(return_value=None)
        _restore_or_build_system_prompt(mock_agent, None, [])
        mock_agent._session_db.update_system_prompt.assert_called_once_with(
            mock_agent.session_id, mock_agent._cached_system_prompt
        )

    def test_system_message_iletildiginde_build_eder(self, mock_agent):
        from agent.conversation_loop import _restore_or_build_system_prompt

        _restore_or_build_system_prompt(mock_agent, "custom sys msg", [])
        mock_agent._build_system_prompt.assert_called_once_with("custom sys msg")

    def test_on_session_start_hook_cagrilir(self, mock_agent):
        from agent.conversation_loop import _restore_or_build_system_prompt
        import ReYMeN_cli.plugins

        mock_agent._session_db = MagicMock()
        mock_agent._session_db.get_session = MagicMock(return_value=None)
        mock_hook = MagicMock()
        # inject invoke_hook into plugins module so the import inside the function works
        with patch.object(ReYMeN_cli.plugins, "invoke_hook", mock_hook, create=True):
            _restore_or_build_system_prompt(mock_agent, None, [])
            mock_hook.assert_called_once()


# ---------------------------------------------------------------------------
# _print_nous_entitlement_guidance
# ---------------------------------------------------------------------------


class TestPrintNousEntitlementGuidance:
    def test_mesaj_varsa_yazdirir(self, mock_agent):
        with patch(
            "agent.conversation_loop._nous_entitlement_message",
            return_value="Bilgilendirme mesaji",
        ):
            from agent.conversation_loop import _print_nous_entitlement_guidance

            result = _print_nous_entitlement_guidance(mock_agent, "tools")
            assert result is True
            mock_agent._vprint.assert_called()

    def test_mesaj_yoksa_yazdirmaz(self, mock_agent):
        with patch(
            "agent.conversation_loop._nous_entitlement_message", return_value=""
        ):
            from agent.conversation_loop import _print_nous_entitlement_guidance

            result = _print_nous_entitlement_guidance(mock_agent, "tools")
            assert result is False
            mock_agent._vprint.assert_not_called()


# ---------------------------------------------------------------------------
# _print_billing_or_entitlement_guidance
# ---------------------------------------------------------------------------


class TestPrintBillingOrEntitlementGuidance:
    def test_mesaj_varsa_yazdirir(self, mock_agent):
        with patch(
            "agent.conversation_loop._billing_or_entitlement_message",
            return_value="Fatura uyarisi",
        ):
            from agent.conversation_loop import _print_billing_or_entitlement_guidance

            result = _print_billing_or_entitlement_guidance(
                mock_agent,
                capability="tools",
                provider="openai",
                base_url="",
                model="gpt-4",
            )
            assert result is True
            mock_agent._vprint.assert_called()

    def test_mesaj_yoksa_yazdirmaz(self, mock_agent):
        with patch(
            "agent.conversation_loop._billing_or_entitlement_message", return_value=""
        ):
            from agent.conversation_loop import _print_billing_or_entitlement_guidance

            result = _print_billing_or_entitlement_guidance(
                mock_agent,
                capability="tools",
                provider="openai",
                base_url="",
                model="gpt-4",
            )
            assert result is False


# ---------------------------------------------------------------------------
# run_conversation (partial — stateless yardimcilari test ediyoruz)
# ---------------------------------------------------------------------------


class TestRunConversationHelpers:
    def test_import_hatasiz(self, mock_agent):
        """conversation_loop modulu import edilebilir olmali."""
        try:
            import agent.conversation_loop

            assert hasattr(agent.conversation_loop, "run_conversation")
        except Exception as e:
            pytest.fail(f"Import hatasi: {e}")

    def test_run_conversation_signature(self, mock_agent):
        from agent.conversation_loop import run_conversation
        import inspect

        sig = inspect.signature(run_conversation)
        params = list(sig.parameters.keys())
        assert "user_message" in params
        assert "system_message" in params
        assert "conversation_history" in params
        assert "task_id" in params

    def test_run_conversation_temel_akisi(self, mock_agent):
        """run_conversation temel olarak cagrilabilir olmali (mock agent ile)."""
        from agent.conversation_loop import run_conversation

        # Cok genis bir fonksiyon oldugu icin sadece import ve cagri testi
        mock_ra = MagicMock()
        with patch("agent.conversation_loop._install_safe_stdio"):
            with patch("agent.conversation_loop.set_session_context"):
                with patch("agent.conversation_loop.set_current_write_origin"):
                    with patch(
                        "agent.conversation_loop._summarize_user_message_for_log",
                        return_value="test",
                    ):
                        with patch("agent.conversation_loop._ra", return_value=mock_ra):
                            with patch.object(mock_agent, "_interrupt_requested", True):
                                result = run_conversation(mock_agent, "Merhaba", "System")
        assert isinstance(result, dict)

    def test_ollama_context_warning(self, mock_agent, caplog):
        import logging

        caplog.set_level(logging.WARNING)
        with patch("agent.conversation_loop.MINIMUM_CONTEXT_LENGTH", 8192):
            from agent.conversation_loop import _ollama_context_limit_error

            agent = MagicMock()
            agent.tools = ["tool1"]
            agent._ollama_num_ctx = 4096
            agent.model = "llama3"
            agent.base_url = "http://localhost:11434"
            agent.provider = "ollama"
            msg = _ollama_context_limit_error(agent, 500)
            assert msg is not None
            assert "Ollama" in msg


# ---------------------------------------------------------------------------
# _try_refresh_nous_paid_entitlement_credentials
# ---------------------------------------------------------------------------


class TestTryRefreshNousPaidEntitlement:
    def test_nous_yoksa_false_doner(self, mock_agent):
        from agent.conversation_loop import (
            _try_refresh_nous_paid_entitlement_credentials,
        )

        with patch("ReYMeN_cli.nous_account.get_nous_portal_account_info") as mock_info:
            mock_info.return_value.paid_service_access = True
            mock_agent._try_refresh_nous_client_credentials = MagicMock(
                return_value=True
            )
            result = _try_refresh_nous_paid_entitlement_credentials(mock_agent)
            assert result is True
            mock_agent._try_refresh_nous_client_credentials.assert_called_once_with(
                force=True
            )

    def test_paid_access_yoksa_false(self, mock_agent):
        from agent.conversation_loop import (
            _try_refresh_nous_paid_entitlement_credentials,
        )

        with patch("ReYMeN_cli.nous_account.get_nous_portal_account_info") as mock_info:
            mock_info.return_value.paid_service_access = False
            result = _try_refresh_nous_paid_entitlement_credentials(mock_agent)
            assert result is False

    def test_exception_hatasinda_false(self, mock_agent):
        from agent.conversation_loop import (
            _try_refresh_nous_paid_entitlement_credentials,
        )

        with patch(
            "ReYMeN_cli.nous_account.get_nous_portal_account_info",
            side_effect=ValueError("hata"),
        ):
            result = _try_refresh_nous_paid_entitlement_credentials(mock_agent)
            assert result is False
