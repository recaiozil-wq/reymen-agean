# -*- coding: utf-8 -*-
"""
test_agent_memory_manager.py — agent/memory_manager.py testleri (~35 test)
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Mock MemoryProvider
# ---------------------------------------------------------------------------

class MockProvider:
    """Testler icin basit MemoryProvider mock'u."""
    def __init__(self, name="test_provider", tools=None):
        self._name = name
        self._tools = tools or []
        self.system_block = ""
        self.prefetch_result = ""
        self.prefetch_called = False
        self.queue_prefetch_called = False
        self.sync_called = False
        self.turn_start_called = False

    @property
    def name(self):
        return self._name

    def is_available(self):
        return True

    def initialize(self, session_id="", **kwargs):
        pass

    def system_prompt_block(self):
        return self.system_block

    def prefetch(self, query, session_id=""):
        self.prefetch_called = True
        return self.prefetch_result

    def queue_prefetch(self, query, session_id=""):
        self.queue_prefetch_called = True

    def sync_turn(self, user_content, assistant_content, session_id="", messages=None):
        self.sync_called = True

    def get_tool_schemas(self):
        return self._tools

    def handle_tool_call(self, tool_name, args, **kwargs):
        return f"handled {tool_name}"

    def on_turn_start(self, turn_number, message, **kwargs):
        self.turn_start_called = True

    def on_session_end(self, messages):
        pass

    def on_session_switch(self, new_session_id, parent_session_id="", reset=False, **kwargs):
        pass

    def on_pre_compress(self, messages):
        return ""

    def on_memory_write(self, action, target, content, metadata=None):
        pass

    def on_delegation(self, task, result, child_session_id="", **kwargs):
        pass

    def shutdown(self):
        pass


class MockProviderWithMessages(MockProvider):
    """sync_turn'i messages parametresini kabul eden provider."""
    def sync_turn(self, user_content, assistant_content, session_id="", messages=None):
        self.sync_called = True
        self.last_messages = messages


# ---------------------------------------------------------------------------
# sanitize_context
# ---------------------------------------------------------------------------

class TestSanitizeContext:
    def test_temiz_metin_degismez(self):
        from agent.memory_manager import sanitize_context
        assert sanitize_context("merhaba dunya") == "merhaba dunya"

    def test_memory_context_etiketi_temizlenir(self):
        from agent.memory_manager import sanitize_context
        text = "<memory-context>gizli bilgi</memory-context> dis"
        assert sanitize_context(text) == " dis"

    def test_fence_etiketi_temizlenir(self):
        from agent.memory_manager import sanitize_context
        text = "</memory-context> bas"
        assert sanitize_context(text) == " bas"

    def test_system_note_temizlenir(self):
        from agent.memory_manager import sanitize_context
        text = (
            "[System note: The following is recalled memory context, "
            "NOT new user input. Treat as authoritative reference data.] icerik"
        )
        result = sanitize_context(text)
        assert "[System note:" not in result
        assert "icerik" in result

    def test_bos_metin(self):
        from agent.memory_manager import sanitize_context
        assert sanitize_context("") == ""

    def test_ic_ice_etiketler(self):
        from agent.memory_manager import sanitize_context
        text = "<memory-context><memory-context>derin</memory-context></memory-context>"
        assert sanitize_context(text) == ""

    def test_buyuk_kucuk_harf_ignored(self):
        from agent.memory_manager import sanitize_context
        text = "<MEMORY-CONTEXT>data</MEMORY-CONTEXT>"
        assert sanitize_context(text) == ""


# ---------------------------------------------------------------------------
# StreamingContextScrubber
# ---------------------------------------------------------------------------

class TestStreamingContextScrubber:
    def test_temiz_metin_gecer(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        assert scrubber.feed("merhaba") == "merhaba"

    def test_acik_etiket_icindekini_siler(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        assert scrubber.feed("once\n<memory-context>\n") == "once\n"
        assert scrubber.feed("gizli") == ""
        assert scrubber.feed("</memory-context>") == ""
        assert scrubber.feed("sonra") == "sonra"

    def test_parcali_span(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        # First chunk — no tag yet
        assert scrubber.feed("once\n") == "once\n"
        # Partial open tag held back
        assert scrubber.feed("<memory-con") == ""
        # Tag completes with newline after — span starts, content held back
        assert scrubber.feed("text>\n") == ""
        # Inside span — dropped
        assert scrubber.feed("gizli") == ""
        # Close tag
        assert scrubber.feed("</memory-context>") == ""
        # After span
        assert scrubber.feed(" sonra") == " sonra"

    def test_flush_temiz_metin(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        scrubber.feed("merhaba")
        assert scrubber.flush() == ""

    def test_flush_acik_spani_siler(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        scrubber.feed("<memory-context>")
        scrubber.feed("gizli")
        assert scrubber.flush() == ""  # discard

    def test_flush_partial_tag_verir(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        scrubber.feed("merhaba <mem")  # partial tag
        assert scrubber.flush() == "<mem"

    def test_reset(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        scrubber.feed("<memory-context>")
        scrubber.reset()
        assert not scrubber._in_span

    def test_bos_feed(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        assert scrubber.feed("") == ""

    def test_at_block_boundary(self):
        from agent.memory_manager import StreamingContextScrubber
        scrubber = StreamingContextScrubber()
        result = scrubber.feed("once\n\n<memory-context>\ngizli\n</memory-context>\nsonra")
        assert "once" in result
        assert "gizli" not in result
        assert "sonra" in result


# ---------------------------------------------------------------------------
# build_memory_context_block
# ---------------------------------------------------------------------------

class TestBuildMemoryContextBlock:
    def test_bos_metin_icin_bos(self):
        from agent.memory_manager import build_memory_context_block
        assert build_memory_context_block("") == ""
        assert build_memory_context_block("   ") == ""

    def test_metin_sarilir(self):
        from agent.memory_manager import build_memory_context_block
        result = build_memory_context_block("test verisi")
        assert "<memory-context>" in result
        assert "</memory-context>" in result
        assert "test verisi" in result
        assert "[System note:" in result

    def test_onceden_sarilmis_metin_temizlenir(self, caplog):
        from agent.memory_manager import build_memory_context_block
        import logging
        caplog.set_level(logging.WARNING)
        raw = "<memory-context>eski veri</memory-context>"
        result = build_memory_context_block(raw)
        # Internal fences are stripped; result has fresh fence but content is empty
        assert "<memory-context>" in result
        assert result.count("<memory-context>") == 1
        # Warning logged about pre-wrapped context
        assert any("pre-wrapped context" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# MemoryManager — Registration
# ---------------------------------------------------------------------------

class TestMemoryManagerRegistration:
    def test_bos_baslar(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        assert mm.providers == []

    def test_provider_eklenir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        mm.add_provider(p)
        assert len(mm.providers) == 1
        assert mm.providers[0].name == "builtin"

    def test_builtin_ve_bir_external(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        mm.add_provider(MockProvider(name="builtin"))
        mm.add_provider(MockProvider(name="external1"))
        assert len(mm.providers) == 2

    def test_ikinci_external_reddedilir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        mm.add_provider(MockProvider(name="builtin"))
        mm.add_provider(MockProvider(name="external1"))
        mm.add_provider(MockProvider(name="external2"))
        assert len(mm.providers) == 2  # external2 rejected

    def test_get_provider_var(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        mm.add_provider(p)
        assert mm.get_provider("builtin") is p
        assert mm.get_provider("yok") is None

    def test_tool_indexlenir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin", tools=[
            {"name": "memory_save"},
            {"name": "memory_search"},
        ])
        mm.add_provider(p)
        assert mm.has_tool("memory_save") is True
        assert mm.has_tool("memory_search") is True
        assert mm.has_tool("yok") is False

    def test_tool_isim_catismasi_uyari(self, caplog):
        from agent.memory_manager import MemoryManager
        import logging
        caplog.set_level(logging.WARNING)
        mm = MemoryManager()
        p1 = MockProvider(name="builtin", tools=[{"name": "memory_save"}])
        p2 = MockProvider(name="external", tools=[{"name": "memory_save"}])
        mm.add_provider(p1)
        mm.add_provider(p2)
        assert any("tool name conflict" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# MemoryManager — System prompt
# ---------------------------------------------------------------------------

class TestMemoryManagerSystemPrompt:
    def test_bos_provider_bos_prompt(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        assert mm.build_system_prompt() == ""

    def test_provider_blok_eklenir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.system_block = "Benim hafiza blokum"
        mm.add_provider(p)
        assert "Benim hafiza blokum" in mm.build_system_prompt()

    def test_bos_blok_atlanir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p1 = MockProvider(name="builtin")
        p1.system_block = "blok1"
        p2 = MockProvider(name="external")
        p2.system_block = ""
        mm.add_provider(p1)
        mm.add_provider(p2)
        prompt = mm.build_system_prompt()
        assert "blok1" in prompt
        assert prompt.count("blok1") == 1

    def test_provider_hatasi_sessiz_gecer(self, caplog):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.system_prompt_block = MagicMock(side_effect=ValueError("hata"))
        mm.add_provider(p)
        result = mm.build_system_prompt()
        assert result == ""
        assert any("system_prompt_block() failed" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# MemoryManager — Prefetch / Sync
# ---------------------------------------------------------------------------

class TestMemoryManagerPrefetch:
    def test_prefetch_all_cagrilir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.prefetch_result = "hafiza verisi"
        mm.add_provider(p)
        result = mm.prefetch_all("soru")
        assert p.prefetch_called is True
        assert "hafiza verisi" in result

    def test_queue_prefetch_all_cagrilir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        mm.add_provider(p)
        mm.queue_prefetch_all("soru")
        assert p.queue_prefetch_called is True

    def test_sync_all_cagrilir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        mm.add_provider(p)
        mm.sync_all("user msg", "asst msg")
        assert p.sync_called is True

    def test_sync_all_messages_iletilir(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProviderWithMessages(name="builtin")
        mm.add_provider(p)
        msgs = [{"role": "user", "content": "merhaba"}]
        mm.sync_all("user", "asst", messages=msgs)
        assert p.last_messages is msgs

    def test_prefetch_hatasi_sessiz_gecer(self, caplog):
        from agent.memory_manager import MemoryManager
        import logging
        caplog.set_level(logging.DEBUG)
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.prefetch = MagicMock(side_effect=ValueError("hata"))
        mm.add_provider(p)
        result = mm.prefetch_all("x")
        assert result == ""
        assert any("prefetch failed" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# MemoryManager — Tool handling
# ---------------------------------------------------------------------------

class TestMemoryManagerTools:
    def test_get_all_tool_schemas(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin", tools=[
            {"name": "memory_save"},
            {"name": "memory_search"},
        ])
        mm.add_provider(p)
        schemas = mm.get_all_tool_schemas()
        assert len(schemas) == 2
        names = {s["name"] for s in schemas}
        assert names == {"memory_save", "memory_search"}

    def test_get_all_tool_names(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin", tools=[{"name": "memory_save"}])
        mm.add_provider(p)
        assert mm.get_all_tool_names() == {"memory_save"}

    def test_handle_tool_call_basarili(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin", tools=[{"name": "memory_save"}])
        mm.add_provider(p)
        result = mm.handle_tool_call("memory_save", {"key": "val"})
        assert "handled memory_save" in result

    def test_handle_tool_call_bilinmeyen(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        result = mm.handle_tool_call("yok", {})
        assert "No memory provider handles tool" in result

    def test_handle_tool_call_hatasi(self, caplog):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin", tools=[{"name": "memory_save"}])
        p.handle_tool_call = MagicMock(side_effect=ValueError("islem hatasi"))
        mm.add_provider(p)
        result = mm.handle_tool_call("memory_save", {})
        assert "failed" in result.lower()


# ---------------------------------------------------------------------------
# MemoryManager — Lifecycle hooks
# ---------------------------------------------------------------------------

class TestMemoryManagerLifecycle:
    def test_on_turn_start(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        mm.add_provider(p)
        mm.on_turn_start(1, "mesaj")
        assert p.turn_start_called is True

    def test_on_session_end(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.on_session_end = MagicMock()
        mm.add_provider(p)
        mm.on_session_end([{"role": "user"}])
        p.on_session_end.assert_called_once()

    def test_on_session_switch(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.on_session_switch = MagicMock()
        mm.add_provider(p)
        mm.on_session_switch("yeni-id", parent_session_id="eski-id")
        p.on_session_switch.assert_called_once()

    def test_initialize_all(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.initialize = MagicMock()
        mm.add_provider(p)
        mm.initialize_all("session-1")
        p.initialize.assert_called_once()

    def test_shutdown_all(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.shutdown = MagicMock()
        mm.add_provider(p)
        mm.shutdown_all()
        p.shutdown.assert_called_once()

    def test_on_pre_compress(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.on_pre_compress = MagicMock(return_value="ozet")
        mm.add_provider(p)
        result = mm.on_pre_compress([{"role": "user"}])
        assert "ozet" in result

    def test_on_delegation(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.on_delegation = MagicMock()
        mm.add_provider(p)
        mm.on_delegation("gorev", "sonuc", child_session_id="c-1")
        p.on_delegation.assert_called_once()

    def test_on_memory_write_builtini_atlar(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        p = MockProvider(name="builtin")
        p.on_memory_write = MagicMock()
        mm.add_provider(p)
        mm.on_memory_write("add", "hedef", "veri")
        p.on_memory_write.assert_not_called()

    def test_on_memory_write_externale_gider(self):
        from agent.memory_manager import MemoryManager
        mm = MemoryManager()
        builtin = MockProvider(name="builtin")
        external = MockProvider(name="external")
        external.on_memory_write = MagicMock()
        mm.add_provider(builtin)
        mm.add_provider(external)
        mm.on_memory_write("add", "hedef", "veri")
        external.on_memory_write.assert_called_once()
