"""ReYMeN ACP Server testleri — gerçek ACPServer, ReYMeNACPAgent, SessionYoneticisi."""

import json
from unittest.mock import MagicMock, patch

import pytest

from acp_adapter.server import (
    ACPServer,
    ReYMeNACPAgent,
    ReYMeN_VERSION,
    PROTOCOL_VERSION,
    SERVER_INFO,
)
from acp_adapter.session import SessionYoneticisi, SessionManager


# ============================================================
# ACPServer Tests
# ============================================================


class TestACPServerInit:
    """ACPServer başlatma testleri."""

    def test_default_host_port(self):
        server = ACPServer()
        assert server.host == "127.0.0.1"
        assert server.port == 9100
        assert server._running is False
        assert server._tools == {}

    def test_custom_host_port(self):
        server = ACPServer(host="0.0.0.0", port=9999)
        assert server.host == "0.0.0.0"
        assert server.port == 9999


class TestACPServerToolKaydet:
    """Tool kaydetme testleri."""

    def test_tool_kaydet_adds_tool(self):
        server = ACPServer()
        fn = lambda args: "ok"
        server.tool_kaydet("ping", fn)
        assert "ping" in server._tools
        assert server._tools["ping"] is fn

    def test_tool_kaydet_multiple(self):
        server = ACPServer()
        server.tool_kaydet("ping", lambda args: "pong")
        server.tool_kaydet("status", lambda args: {"durum": "hazir"})
        assert len(server._tools) == 2


class TestACPServerYanitHata:
    """JSON-RPC yanit/hata format testleri."""

    def test_yanit_format(self):
        server = ACPServer()
        result = json.loads(server._yanit(1, {"ok": True}))
        assert result == {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}

    def test_yanit_none_id(self):
        server = ACPServer()
        result = json.loads(server._yanit(None, "done"))
        assert result["id"] is None
        assert result["result"] == "done"

    def test_hata_format(self):
        server = ACPServer()
        result = json.loads(server._hata(1, -32601, "Not found"))
        assert result == {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32601, "message": "Not found"},
        }


class TestACPServerIstekIsle:
    """JSON-RPC method yonlendirme testleri."""

    def test_initialize(self):
        server = ACPServer()
        server.tool_kaydet("ping", lambda args: "pong")
        result = json.loads(server._istek_isle({"id": 1, "method": "initialize"}))
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 1
        assert result["result"]["protocolVersion"] == PROTOCOL_VERSION
        assert result["result"]["serverInfo"] == SERVER_INFO
        assert "ping" in result["result"]["capabilities"]["tools"]

    def test_tools_list(self):
        server = ACPServer()
        server.tool_kaydet("ping", lambda args: "pong")
        server.tool_kaydet("status", lambda args: "ok")
        result = json.loads(server._istek_isle({"id": 1, "method": "tools/list"}))
        tools = result["result"]["tools"]
        assert len(tools) == 2
        names = [t["name"] for t in tools]
        assert "ping" in names
        assert "status" in names

    def test_tools_call(self):
        server = ACPServer()
        server.tool_kaydet("ping", lambda args: "pong")
        result = json.loads(
            server._istek_isle(
                {
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "ping", "arguments": {}},
                }
            )
        )
        assert result["result"]["content"] == "pong"

    def test_tools_call_with_args(self):
        server = ACPServer()
        server.tool_kaydet("echo", lambda args: args.get("msg", ""))
        result = json.loads(
            server._istek_isle(
                {
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "echo", "arguments": {"msg": "merhaba"}},
                }
            )
        )
        assert result["result"]["content"] == "merhaba"

    def test_tools_call_tool_not_found(self):
        server = ACPServer()
        result = json.loads(
            server._istek_isle(
                {
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "yok", "arguments": {}},
                }
            )
        )
        assert "error" in result
        assert result["error"]["code"] == -32601
        assert "yok" in result["error"]["message"]

    def test_tools_call_exception(self):
        server = ACPServer()

        def _boom(args):
            raise ValueError("patladi")

        server.tool_kaydet("patla", _boom)
        result = json.loads(
            server._istek_isle(
                {
                    "id": 1,
                    "method": "tools/call",
                    "params": {"name": "patla", "arguments": {}},
                }
            )
        )
        assert "error" in result
        assert result["error"]["code"] == -32603

    def test_ping(self):
        server = ACPServer()
        result = json.loads(server._istek_isle({"id": 1, "method": "ping"}))
        assert result["result"] == {}

    def test_unknown_method(self):
        server = ACPServer()
        result = json.loads(server._istek_isle({"id": 1, "method": "bilinmeyen"}))
        assert "error" in result
        assert result["error"]["code"] == -32601


class TestACPServerStdio:
    """stdio transport testleri."""

    def test_stdio_json_decode_error(self):
        server = ACPServer()
        mock_stdout = MagicMock()
        with patch("sys.stdin", ["gecersiz json\n"]), patch("sys.stdout", mock_stdout):
            server._stdio_dinle()
        write_calls = mock_stdout.write.call_args_list
        written = "".join(call[0][0] for call in write_calls)
        result = json.loads(written.strip())
        assert result["error"]["code"] == -32700

    def test_stdio_valid_request(self):
        server = ACPServer()
        mock_stdout = MagicMock()
        req = json.dumps({"id": 1, "method": "ping"})
        with patch("sys.stdin", [req + "\n"]), patch("sys.stdout", mock_stdout):
            server._stdio_dinle()
        write_calls = mock_stdout.write.call_args_list
        written = "".join(call[0][0] for call in write_calls)
        result = json.loads(written.strip())
        assert result["id"] == 1
        assert "result" in result


class TestACPServerLifecycle:
    """ACPServer baslat/durdur testleri."""

    def test_baslat_tcp(self):
        server = ACPServer(port=0)  # port 0 = rastgele
        server.baslat("tcp")
        assert server._running is True
        assert server._thread is not None
        server.durdur()
        assert server._running is False

    def test_durdur_idempotent(self):
        server = ACPServer()
        server.durdur()  # hic baslatilmamis — patlamamali
        server.durdur()  # tekrar — patlamamali
        assert server._running is False

    def test_baslat_invalid_mode(self):
        server = ACPServer()
        server.baslat("xyz")  # gecersiz mod — patlamamali, _running kalir
        assert server._running is True


# ============================================================
# ReYMeNACPAgent Tests
# ============================================================


class TestReYMeNACPAgent:
    """ReYMeNACPAgent testleri."""

    @pytest.mark.asyncio
    async def test_initialize(self):
        agent = ReYMeNACPAgent()
        assert agent._initialized is False
        await agent.initialize()
        assert agent._initialized is True

    @pytest.mark.asyncio
    async def test_close(self):
        agent = ReYMeNACPAgent()
        await agent.initialize()
        await agent.close()
        assert agent._initialized is False

    @pytest.mark.asyncio
    async def test_prompt(self):
        agent = ReYMeNACPAgent()
        result = await agent.prompt("merhaba dünya")
        assert "content" in result
        assert "merhaba" in result["content"]

    @pytest.mark.asyncio
    async def test_prompt_with_session(self):
        agent = ReYMeNACPAgent()
        result = await agent.prompt("test", session_id="abc-123")
        assert result["content"] is not None

    @pytest.mark.asyncio
    async def test_version_constant(self):
        assert ReYMeN_VERSION == "1.0.0"
        assert PROTOCOL_VERSION == "2024-11-05"
        assert SERVER_INFO["name"] == "ReYMeN"


# ============================================================
# SessionYoneticisi Tests
# ============================================================


class TestSessionYoneticisi:
    """SessionYoneticisi testleri."""

    def test_oturum_ac_returns_session(self):
        yonetici = SessionYoneticisi()
        oturum = yonetici.oturum_ac("session-1", "test hedefi")
        assert oturum["session_id"] == "session-1"
        assert oturum["hedef"] == "test hedefi"
        assert oturum["durum"] == "bekliyor"

    def test_oturum_ac_baslangic_zamani(self):
        yonetici = SessionYoneticisi()
        oturum = yonetici.oturum_ac("s1", "hedef")
        assert oturum["baslangi"] != ""
        assert oturum["bitis"] == ""

    def test_oturum_bul_found(self):
        yonetici = SessionYoneticisi()
        yonetici.oturum_ac("s1", "hedef")
        bulunan = yonetici.oturum_bul("s1")
        assert bulunan is not None
        assert bulunan["session_id"] == "s1"

    def test_oturum_bul_not_found(self):
        yonetici = SessionYoneticisi()
        assert yonetici.oturum_bul("yok") is None

    def test_durum_guncelle(self):
        yonetici = SessionYoneticisi()
        yonetici.oturum_ac("s1", "hedef")
        yonetici.durum_guncelle("s1", "calisiyor")
        assert yonetici.oturum_bul("s1")["durum"] == "calisiyor"

    def test_durum_guncelle_tamamlandi_kaydeder_bitis(self):
        yonetici = SessionYoneticisi()
        yonetici.oturum_ac("s1", "hedef")
        yonetici.durum_guncelle("s1", "tamamlandi", "basarili")
        oturum = yonetici.oturum_bul("s1")
        assert oturum["durum"] == "tamamlandi"
        assert oturum["sonuc"] == "basarili"
        assert oturum["bitis"] != ""

    def test_durum_guncelle_hata_kaydeder_bitis(self):
        yonetici = SessionYoneticisi()
        yonetici.oturum_ac("s1", "hedef")
        yonetici.durum_guncelle("s1", "hata", "crash")
        assert yonetici.oturum_bul("s1")["bitis"] != ""

    def test_durum_guncelle_olmayan_session(self):
        yonetici = SessionYoneticisi()
        yonetici.durum_guncelle("yok", "hata")  # patlamamali
        assert yonetici.oturum_bul("yok") is None

    def test_tum_oturumlar(self):
        yonetici = SessionYoneticisi()
        yonetici.oturum_ac("s1", "hedef1")
        yonetici.oturum_ac("s2", "hedef2")
        tumu = yonetici.tum_oturumlar()
        assert len(tumu) == 2

    def test_tum_oturumlar_bos(self):
        yonetici = SessionYoneticisi()
        assert yonetici.tum_oturumlar() == []

    def test_session_manager_alias(self):
        assert SessionManager is SessionYoneticisi


# ============================================================
# auth.py Export Tests
# ============================================================


class TestAuthExports:
    """acp_adapter.auth export testleri."""

    def test_TERMINAL_SETUP_AUTH_METHOD_ID(self):
        from acp_adapter.auth import TERMINAL_SETUP_AUTH_METHOD_ID

        assert TERMINAL_SETUP_AUTH_METHOD_ID == "terminal_setup"

    def test_build_auth_methods(self):
        from acp_adapter.auth import build_auth_methods, ACPAuth

        methods = build_auth_methods("test-token")
        assert len(methods) == 1
        assert isinstance(methods[0], ACPAuth)
        assert methods[0].token == "test-token"

    def test_has_provider(self):
        from acp_adapter.auth import has_provider

        assert has_provider("hmac") is True
        assert has_provider("terminal_setup") is True
        assert has_provider("unknown") is False

    def test_detect_provider_hmac(self):
        from acp_adapter.auth import detect_provider
        from types import SimpleNamespace

        req = SimpleNamespace(headers={"x-hmac-signature": "abc"})
        assert detect_provider(req) == "hmac"

    def test_detect_provider_terminal(self):
        from acp_adapter.auth import detect_provider
        from types import SimpleNamespace

        req = SimpleNamespace(headers={})
        assert detect_provider(req) == "terminal_setup"


# ============================================================
# acp.schema Export Tests
# ============================================================


class TestSchemaExports:
    """acp.schema dataclass testleri."""

    def test_UsageUpdate_defaults(self):
        from acp.schema import UsageUpdate

        u = UsageUpdate()
        assert u.input_tokens == 0
        assert u.output_tokens == 0
        assert u.total_tokens == 0

    def test_UsageUpdate_with_values(self):
        from acp.schema import UsageUpdate

        u = UsageUpdate(input_tokens=10, output_tokens=20, total_tokens=30, cost=0.5)
        assert u.total_tokens == 30
        assert u.cost == 0.5

    def test_UserMessageChunk(self):
        from acp.schema import UserMessageChunk

        m = UserMessageChunk(content="test", chunk_type="user_message")
        assert m.content == "test"
        assert m.chunk_type == "user_message"


# ============================================================
# acp.agent.router Tests
# ============================================================


class TestAgentRouter:
    """acp.agent.router testleri."""

    def test_build_agent_router(self):
        from acp.agent.router import build_agent_router, AgentRouter

        router = build_agent_router()
        assert isinstance(router, AgentRouter)

    @pytest.mark.asyncio
    async def test_router_register_dispatch(self):
        from acp.agent.router import build_agent_router

        router = build_agent_router()

        async def handler(msg):
            return "handled"

        router.register("test", handler)
        result = await router.dispatch("bu bir test mesaji")
        assert result == "handled"

    @pytest.mark.asyncio
    async def test_router_no_match(self):
        from acp.agent.router import build_agent_router

        router = build_agent_router()
        result = await router.dispatch("bilinmeyen mesaj")
        assert result is None
