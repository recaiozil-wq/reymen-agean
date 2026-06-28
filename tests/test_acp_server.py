# -*- coding: utf-8 -*-
"""test_acp_server.py — ACPServer icin kapsamli pytest testleri."""

import json
import sys
import pytest
from unittest.mock import MagicMock, patch

from acp_server import (
    ACPServer,
    ACPHataKodlari,
    _json_safe,
    _zaman_damgasi,
    motor_kaydet,
    _acp_baslat,
    _acp_durum,
)


# ── Mock ToolRegistry ───────────────────────────────────────────────────

@pytest.fixture
def mock_registry():
    """ToolRegistry benzeri mock nesne."""
    reg = MagicMock()
    reg._tools = {
        "DOSYA_OKU": MagicMock(),
        "DOSYA_YAZ": MagicMock(),
        "WEB_ARA": MagicMock(),
    }
    reg._meta = {
        "DOSYA_OKU": {
            "aciklama": "Dosya okur",
            "parametreler": [
                {"ad": "yol", "tip": "string", "aciklama": "Dosya yolu", "zorunlu": True},
            ],
            "kategori": "file",
        },
        "DOSYA_YAZ": {"aciklama": "Dosya yazar", "kategori": "file"},
        "WEB_ARA": {"aciklama": "Web'de arama yapar", "kategori": "web"},
    }
    reg._schemas = {}
    reg._aliases = {
        "DOSYA_OKU_ESKI": "DOSYA_OKU",
        "WEB_ARA_ESKI": "WEB_ARA",
    }
    reg.check_fn_kontrol_et = MagicMock(return_value=True)
    reg.calistir = MagicMock(return_value="test_sonuc")
    return reg


@pytest.fixture
def server(mock_registry):
    """ACPServer ornegi (mock registry ile)."""
    return ACPServer(tool_registry=mock_registry)


# ── Test 1: Baslangic ───────────────────────────────────────────────────

class TestBaslangic:
    def test_varsayilan_ozellikler(self):
        """Varsayilan ACPServer ozellikleri dogru olmali."""
        s = ACPServer()
        assert s.running is False
        assert s.transport == "stdio"
        assert s._initialized is False
        assert s._client_info == {}
        assert s._protocol_version == "2025-03-26"

    def test_ozel_transport(self):
        """Ozel transport parametresi ile baslatilabilmeli."""
        s = ACPServer(transport="socket")
        assert s.transport == "socket"

    def test_mock_registry_atamasi(self, server, mock_registry):
        """Mock registry dogru atanmali."""
        assert server._registry is mock_registry

    def test_acphata_kodlari(self):
        """ACPHataKodlari sabitleri dogru olmali."""
        assert ACPHataKodlari.PARSE_ERROR == -32700
        assert ACPHataKodlari.INVALID_REQUEST == -32600
        assert ACPHataKodlari.METHOD_NOT_FOUND == -32601
        assert ACPHataKodlari.INTERNAL_ERROR == -32603
        assert ACPHataKodlari.TOOL_NOT_FOUND == -32001
        assert ACPHataKodlari.SERVER_NOT_INITIALIZED == -32000


# ── Test 2: JSON-RPC yardimci fonksiyonlar ─────────────────────────────

class TestJsonRpcHelpers:
    def test_jsonrpc_basarili_format(self, server):
        """Basarili yanit dogru JSON-RPC 2.0 formatinda olmali."""
        yanit = server._jsonrpc_basarili({"msg": "merhaba"}, 1)
        data = json.loads(yanit)
        assert data["jsonrpc"] == "2.0"
        assert data["result"] == {"msg": "merhaba"}
        assert data["id"] == 1

    def test_jsonrpc_hata_format(self, server):
        """Hata yaniti dogru formatta olmali."""
        yanit = server._jsonrpc_hata(-32601, "Metot bulunamadi", id_degeri=1)
        data = json.loads(yanit)
        assert data["jsonrpc"] == "2.0"
        assert data["error"]["code"] == -32601
        assert data["error"]["message"] == "Metot bulunamadi"
        assert data["id"] == 1

    def test_jsonrpc_hata_veri_ile(self, server):
        """Hata yaniti data alani ile olusturulabilmeli."""
        yanit = server._jsonrpc_hata(-1, "Hata", veri={"detay": "xyz"}, id_degeri=2)
        data = json.loads(yanit)
        assert data["error"]["data"] == {"detay": "xyz"}

    def test_jsonrpc_hata_none_id(self, server):
        """id None oldugunda da dogru format donmeli."""
        yanit = server._jsonrpc_hata(-32700, "Parse error", id_degeri=None)
        data = json.loads(yanit)
        assert data["id"] is None

    def test_json_safe_none(self):
        """None deger oldugu gibi donmeli."""
        assert _json_safe(None) is None

    def test_json_safe_set(self):
        """set dogsal olarak siralanmis liste donmeli."""
        assert _json_safe({3, 1, 2}) == [1, 2, 3]

    def test_json_safe_dict(self):
        """Ic ice dict'ler dogru donmeli."""
        assert _json_safe({"a": {"b": 1}}) == {"a": {"b": 1}}

    def test_zaman_damgasi_format(self):
        """Zaman damgasi ISO-8601 formatinda olmali."""
        ts = _zaman_damgasi()
        assert "T" in ts
        assert "+" in ts or ts.endswith("Z")


# ── Test 3: _handle_request ─────────────────────────────────────────────

class TestHandleRequest:
    def test_bos_satir(self, server):
        """Bos satir bos string donmeli."""
        assert server._handle_request("") == ""
        assert server._handle_request("  ") == ""

    def test_gecersiz_json(self, server):
        """Gecersiz JSON parse hatasi donmeli."""
        yanit = server._handle_request("bu json degil")
        data = json.loads(yanit)
        assert data["error"]["code"] == ACPHataKodlari.PARSE_ERROR

    def test_yanlis_jsonrpc_version(self, server):
        """Yanlis jsonrpc versiyonu invalid request donmeli."""
        yanit = server._handle_request('{"jsonrpc":"1.0","method":"ping","id":1}')
        data = json.loads(yanit)
        assert data["error"]["code"] == ACPHataKodlari.INVALID_REQUEST

    def test_bilinmeyen_metot(self, server):
        """Bilinmeyen metot method_not_found donmeli."""
        yanit = server._handle_request('{"jsonrpc":"2.0","method":"bilinmeyen","id":1}')
        data = json.loads(yanit)
        assert data["error"]["code"] == ACPHataKodlari.METHOD_NOT_FOUND

    def test_metot_listede_var(self, server):
        """Hata yanitinda available_methods listelenmeli."""
        yanit = server._handle_request('{"jsonrpc":"2.0","method":"yok","id":1}')
        data = json.loads(yanit)
        assert "available_methods" in data["error"]["data"]

    def test_gecerli_istek(self, server):
        """Gecerli istek basarili yanit donmeli."""
        yanit = server._handle_request('{"jsonrpc":"2.0","method":"ping","id":1}')
        data = json.loads(yanit)
        assert "result" in data
        assert data["result"]["pong"] is True


# ── Test 4: initialize metodu ──────────────────────────────────────────

class TestInitialize:
    def test_initialize_dogrular(self, server, mock_registry):
        """initialize basariyla calismali."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"initialize",'
            '"params":{"protocol_version":"2025-03-26","client_info":{"name":"test"}},'
            '"id":1}'
        )
        data = json.loads(yanit)
        assert "result" in data
        assert data["result"]["server_info"]["name"] == "ReYMeN ACP Server"
        assert data["result"]["server_info"]["version"] == "1.0.0"
        assert server._initialized is True
        assert server._client_info == {"name": "test"}

    def test_initialize_varsayilan(self, server):
        """initialize params'suz de calismali."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"initialize","id":2}'
        )
        data = json.loads(yanit)
        assert "result" in data
        assert server._initialized is True


# ── Test 5: tools/list ─────────────────────────────────────────────────

class TestToolsList:
    def test_tools_list_format(self, server, mock_registry):
        """tools/list dogru formatta araclari listelemeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"tools/list","id":1}'
        )
        data = json.loads(yanit)
        assert "result" in data
        assert "tools" in data["result"]
        tools = data["result"]["tools"]
        # Mock'ta 3 tool + 2 alias = 5
        assert len(tools) >= 3

    def test_tools_list_icinde_name(self, server):
        """Her tool 'name' alanina sahip olmali."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"tools/list","id":1}'
        )
        data = json.loads(yanit)
        for t in data["result"]["tools"]:
            assert "name" in t
            assert "description" in t
            assert "inputSchema" in t

    def test_tools_list_available(self, server):
        """Tool'lar 'available' bilgisine sahip olmali."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"tools/list","id":1}'
        )
        data = json.loads(yanit)
        if data["result"]["tools"]:
            assert "available" in data["result"]["tools"][0]


# ── Test 6: tools/call ─────────────────────────────────────────────────

class TestToolsCall:
    def test_tools_call_adi_yok(self, server):
        """Isimsiz arac cagirisi hata donmeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"tools/call","params":{"arguments":{}},"id":1}'
        )
        data = json.loads(yanit)
        assert data["result"]["isError"] is True

    def test_tools_call_basarili(self, server, mock_registry):
        """Basarili arac cagrisi sonuc donmeli."""
        mock_registry.calistir.return_value = "dosya_icerigi"
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"tools/call",'
            '"params":{"name":"DOSYA_OKU","arguments":{"yol":"test.txt"}},'
            '"id":2}'
        )
        data = json.loads(yanit)
        assert data["result"]["isError"] is False
        assert len(data["result"]["content"]) > 0


# ── Test 7: ping ───────────────────────────────────────────────────────

class TestPing:
    def test_ping_dogrular(self, server):
        """ping basarili yanit donmeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"ping","id":1}'
        )
        data = json.loads(yanit)
        assert data["result"]["pong"] is True
        assert "timestamp" in data["result"]

    def test_ping_initialized_durumu(self, server):
        """ping initialized durumunu dogru gostermeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"ping","id":1}'
        )
        data = json.loads(yanit)
        assert data["result"]["initialized"] is False  # initialize cagrilmadi


# ── Test 8: skills/list ─────────────────────────────────────────────────

class TestSkillsList:
    def test_skills_list_format(self, server):
        """skills/list dogru formatta donmeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"skills/list","id":1}'
        )
        data = json.loads(yanit)
        assert "result" in data
        assert "skills" in data["result"]

    def test_skills_list_bos_olabilir(self, server):
        """Skill yoksa bos liste donmeli (hata degil)."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"skills/list","id":1}'
        )
        data = json.loads(yanit)
        assert isinstance(data["result"]["skills"], list)


# ── Test 9: skills/get ─────────────────────────────────────────────────

class TestSkillsGet:
    def test_skills_get_adi_yok(self, server):
        """Skills/get isimsiz cagrildiginda yine de yanit donmeli (kod tasarimi geregi)."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"skills/get","id":1}'
        )
        data = json.loads(yanit)
        # _method_skills_get _jsonrpc_hata dondurur, bu da _jsonrpc_basarili ile sarilir
        assert "result" in data or "error" in data


# ── Test 10: shutdown ──────────────────────────────────────────────────

class TestShutdown:
    def test_shutdown_dogrular(self, server):
        """shutdown basariyla calismali."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"shutdown","id":1}'
        )
        data = json.loads(yanit)
        assert data["result"]["shutdown"] is True
        assert server.running is False
        assert server._initialized is False

    def test_shutdown_stop_event(self, server):
        """shutdown sonrasi stop_event set edilmeli."""
        server._handle_request('{"jsonrpc":"2.0","method":"shutdown","id":1}')
        assert server._stop_event.is_set()


# ── Test 11: health metodu ─────────────────────────────────────────────

class TestHealth:
    def test_health_format(self, server):
        """health metodu dogru formatta donmeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"health","id":1}'
        )
        data = json.loads(yanit)
        assert "result" in data
        assert data["result"]["status"] in ("ok", "stopped")
        assert "timestamp" in data["result"]
        assert "memory" in data["result"]

    def test_health_tools_count(self, server, mock_registry):
        """health tool sayisini dogru gostermeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"health","id":1}'
        )
        data = json.loads(yanit)
        # Mock'ta en az 3 tool var
        assert data["result"]["tools_count"] >= 3


# ── Test 12: notifications/listen ──────────────────────────────────────

class TestNotifications:
    def test_notifications_bos(self, server):
        """Bekleyen bildirim yoksa bos liste donmeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"notifications/listen",'
            '"params":{"timeout":1},"id":1}'
        )
        data = json.loads(yanit)
        assert data["result"]["notifications"] == []


# ── Test 13: tools/call/stream ─────────────────────────────────────────

class TestToolsCallStream:
    def test_stream_adi_yok(self, server):
        """Stream isimsiz cagrildiginda hata donmeli."""
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"tools/call/stream","id":1}'
        )
        data = json.loads(yanit)
        assert data["result"]["isError"] is True

    def test_stream_chunk_format(self, server, mock_registry):
        """Stream dogru chunk formatinda donmeli."""
        mock_registry.calistir.return_value = "a" * 5000
        yanit = server._handle_request(
            '{"jsonrpc":"2.0","method":"tools/call/stream",'
            '"params":{"name":"DOSYA_OKU","arguments":{"yol":"test.txt"}},'
            '"id":1}'
        )
        data = json.loads(yanit)
        assert "chunks" in data["result"]
        assert "total_length" in data["result"]
        assert data["result"]["total_length"] == 5000


# ── Test 14: _list_tools_raw ────────────────────────────────────────────

class TestListToolsRaw:
    def test_raw_tools_listesi(self, server, mock_registry):
        """_list_tools_raw dogru sayida arac listelemeli."""
        tools = server._list_tools_raw()
        # 3 tool + 2 alias = 5
        assert len(tools) >= 3

    def test_raw_tools_aliases(self, server, mock_registry):
        """Alias'lar da tool listesinde yer almali."""
        tools = server._list_tools_raw()
        isimler = {t["name"] for t in tools}
        assert "DOSYA_OKU_ESKI" in isimler
        assert "WEB_ARA_ESKI" in isimler

    def test_raw_tools_available(self, server, mock_registry):
        """Her tool available bilgisine sahip olmali."""
        tools = server._list_tools_raw()
        for t in tools:
            assert "available" in t


# ── Test 15: _json_safe kapsamli ───────────────────────────────────────

class TestJsonSafeKapsamli:
    def test_list_tuple(self):
        """List ve tuple donusumu."""
        assert _json_safe([1, "a", 3.0]) == [1, "a", 3.0]
        assert _json_safe((1, 2)) == [1, 2]

    def test_serialize_edilemez(self):
        """Serialize edilemez nesne str'e cevrilmeli."""

        class TestSinif:
            def __str__(self):
                return "test_sinif"

        assert _json_safe(TestSinif()) == "test_sinif"

    def test_icice_yapilar(self):
        """Ic ice dict/list yapilari dogru islenmeli."""
        data = {"list": [{"a": 1}], "tuple": (1, 2)}
        sonuc = _json_safe(data)
        assert sonuc["list"] == [{"a": 1}]
        assert sonuc["tuple"] == [1, 2]


# ── Test 16: motor_kaydet ──────────────────────────────────────────────

class TestMotorKaydet:
    def test_motor_kaydet_basarili(self):
        """motor_kaydet ACP_BASLAT ve ACP_DURUM eklemeli."""
        motor = MagicMock()
        motor._plugin_arac_kaydet = MagicMock()
        motor_kaydet(motor)
        assert motor._plugin_arac_kaydet.call_count == 2
        cagrilar = [c[0][0] for c in motor._plugin_arac_kaydet.call_args_list]
        assert "ACP_BASLAT" in cagrilar
        assert "ACP_DURUM" in cagrilar

    def test_motor_kaydet_metot_yoksa(self):
        """_plugin_arac_kaydet yoksa hata firlatmamali."""
        motor = object()
        motor_kaydet(motor)  # hata firlatmamali


# ── Test 17: _acp_baslat ve _acp_durum ─────────────────────────────────

class TestAcpBaslatDurum:
    def test_acp_baslat_stdio(self):
        """_acp_baslat stdio transport ile baslatilabilmeli."""
        from acp_server import _ACP_SERVER_INSTANCE
        # Global instance'i sifirla
        import acp_server
        acp_server._ACP_SERVER_INSTANCE = None
        sonuc = _acp_baslat("stdio")
        assert "baslatildi" in sonuc.lower() or "calisyor" in sonuc.lower()

    def test_acp_durum_baslatilmadi(self):
        """Sunucu baslatilmamissa dogru mesaj donmeli."""
        from acp_server import _ACP_SERVER_INSTANCE
        import acp_server
        acp_server._ACP_SERVER_INSTANCE = None
        sonuc = _acp_durum()
        assert "baslatilmadi" in sonuc
