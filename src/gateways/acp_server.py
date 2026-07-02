# -*- coding: utf-8 -*-
"""acp_server.py — Agent Communication Protocol (ACP) sunucusu.

Stdio uzerinden JSON-RPC 2.0 mesajlari alir, ReYMeN'in tool_registry
ve closed_learning_loop modullerini kullanarak yanit verir.

ACP, Claude Code / Copilot gibi harici AI araclarinin ReYMeN'in
araclarini ve becerilerini cagirmasini saglar.

Kullanim (standalone):
    python acp_server.py

Kullanim (motor.py entegrasyonu):
    from acp_server import motor_kaydet
    motor_kaydet(motor)  # ACP_BASLAT, ACP_DURUM araclari eklenir

Protokol:
    - Her satirda bir JSON mesaji (stdin/stdout)
    - Hata/debug: stderr'e yazılır
    - Metotlar: initialize, tools/list, tools/call, skills/list,
      skills/get, shutdown, ping
"""

import json
import logging
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Windows'ta stdout encoding sorunu
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception as _acp_serv_e36:
        print(f"[UYARI] acp_server.py:37 - {_acp_serv_e36}")

logger = logging.getLogger("ACP")

# ── Graceful imports ──────────────────────────────────────────────────────

_TOOL_REGISTRY = None
try:
    from reymen.arac.tool_registry import tool_registry as _TOOL_REGISTRY
except ImportError:
    logger.debug("[ACP] tool_registry yuklenemedi.")

_CLOSED_LOOP = None
_BECERI_ARA = None
_BECERI_DURUM = None
try:
    from reymen.cereyan.closed_learning_loop import (
        _get_loop as _cl_get_loop,
    )
    _CLOSED_LOOP = _cl_get_loop()
except ImportError:
    logger.debug("[ACP] closed_learning_loop yuklenemedi.")
    _CLOSED_LOOP = None


# Global sunucu ornegi (test'lerin mock icin kullandigi referans)
_ACP_SERVER_INSTANCE = None


# ── Yardimci fonksiyonlar ─────────────────────────────────────────────────

def _json_safe(deger: Any) -> Any:
    """JSON serialize edilemeyen degerleri str()'e cevir."""
    if deger is None or isinstance(deger, (str, int, float, bool)):
        return deger
    if isinstance(deger, (list, tuple)):
        return [_json_safe(d) for d in deger]
    if isinstance(deger, dict):
        return {k: _json_safe(v) for k, v in deger.items()}
    if isinstance(deger, (set, frozenset)):
        return sorted(_json_safe(d) for d in deger)
    try:
        json.dumps(deger)
        return deger
    except (TypeError, ValueError):
        return str(deger)


def _zaman_damgasi() -> str:
    """ISO-8601 UTC zaman damgasi."""
    return datetime.now(tz=timezone.utc).isoformat()


# ── JSON-RPC Hata Kodlari ─────────────────────────────────────────────────

class ACPHataKodlari:
    """JSON-RPC standart hata kodlari + ACP ozel kodlari."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # ACP ozel
    TOOL_NOT_FOUND = -32001
    TOOL_EXECUTION_ERROR = -32002
    SKILL_NOT_FOUND = -32003
    SERVER_NOT_INITIALIZED = -32000


# ── Ana Sinif ──────────────────────────────────────────────────────────────

class ACPServer:
    """Agent Communication Protocol sunucusu.

    Stdio uzerinden JSON-RPC 2.0 isteklerini alir, isler, yanit verir.

    Attributes:
        running: Sunucu calisiyor mu?
        transport: Iletisim yontemi ("stdio" veya "socket")
        initialized: initialize() basariyla cagrildi mi?
    """

    def __init__(self, tool_registry: Optional[Any] = None, transport: str = "stdio") -> None:
        """ACP sunucusu baslat.

        Args:
            tool_registry: ToolRegistry ornegi (None = varsayilan)
            transport: Iletisim yontemi ("stdio" veya "socket")
        """
        self.running = False
        self.transport = transport
        self._registry = tool_registry or _TOOL_REGISTRY
        self._initialized = False
        self._client_info = {}
        self._protocol_version = "2025-03-26"
        self._thread = None
        self._stop_event = threading.Event()
        self._notifications: list[dict] = []

    # ── JSON-RPC Cekirdek ─────────────────────────────────────────────────

    def _jsonrpc_hata(self, kod: int, mesaj: str, veri: Any = None,
                      id_degeri: Any = None) -> str:
        """JSON-RPC hata yaniti olustur."""
        yanit = {
            "jsonrpc": "2.0",
            "error": {
                "code": kod,
                "message": mesaj,
            },
        }
        if veri is not None:
            yanit["error"]["data"] = _json_safe(veri)
        if id_degeri is not None:
            yanit["id"] = id_degeri
        else:
            yanit["id"] = None
        return json.dumps(yanit, ensure_ascii=False)

    def _jsonrpc_basarili(self, sonuc: Any, id_degeri: Any) -> str:
        """Basarili JSON-RPC yaniti olustur."""
        return json.dumps(
            {"jsonrpc": "2.0", "result": _json_safe(sonuc), "id": id_degeri},
            ensure_ascii=False,
        )

    def _handle_request(self, raw_line: str) -> str:
        """Tek bir JSON-RPC istegini isle, yanit dondur.

        Args:
            raw_line: Stdin'den gelen ham satir (JSON)

        Returns:
            JSON yanit stringi
        """
        # Bos satirlari atla
        if not raw_line or not raw_line.strip():
            return ""

        try:
            istek = json.loads(raw_line.strip())
        except json.JSONDecodeError as e:
            return self._jsonrpc_hata(
                ACPHataKodlari.PARSE_ERROR,
                f"JSON ayrisma hatasi: {e}",
                id_degeri=None,
            )

        # JSON-RPC 2.0 kontrol
        if not isinstance(istek, dict) or istek.get("jsonrpc") != "2.0":
            return self._jsonrpc_hata(
                ACPHataKodlari.INVALID_REQUEST,
                "Gecersiz istek: jsonrpc: '2.0' olmali",
                id_degeri=istek.get("id") if isinstance(istek, dict) else None,
            )

        method = istek.get("method", "")
        params = istek.get("params", {})
        req_id = istek.get("id")

        # Method dispatch
        handler = getattr(self, f"_method_{method.replace('/', '_')}", None)
        if handler is None:
            return self._jsonrpc_hata(
                ACPHataKodlari.METHOD_NOT_FOUND,
                f"Metot bulunamadi: '{method}'",
                veri={"available_methods": self._metot_listele()},
                id_degeri=req_id,
            )

        try:
            if isinstance(params, dict):
                sonuc = handler(**params)
            elif isinstance(params, list):
                sonuc = handler(*params)
            else:
                sonuc = handler(params) if params else handler()
            return self._jsonrpc_basarili(sonuc, req_id)
        except TypeError as e:
            return self._jsonrpc_hata(
                ACPHataKodlari.INVALID_PARAMS,
                f"Gecersiz parametreler: {e}",
                id_degeri=req_id,
            )
        except Exception as e:
            logger.exception("[ACP] Metot hatasi: %s", method)
            return self._jsonrpc_hata(
                ACPHataKodlari.INTERNAL_ERROR,
                f"Ic hata: {e}",
                id_degeri=req_id,
            )

    def _metot_listele(self) -> list[str]:
        """Kullanilabilir metotlari listele."""
        return sorted(
            name.replace("_method_", "").replace("_", "/", 1)
            for name in dir(self)
            if name.startswith("_method_")
        )

    # ── Metotlar ──────────────────────────────────────────────────────────

    def _method_health(self, **kwargs) -> dict:
        """Detayli saglik kontrolu.

        Returns:
            Sunucu durumu, tool/skill sayisi, calisma suresi, bellek kullanimi
        """
        import gc
        import os

        sonuc = {
            "status": "ok" if self.running else "stopped",
            "initialized": self._initialized,
            "transport": self.transport,
            "timestamp": _zaman_damgasi(),
            "uptime_seconds": (
                (datetime.now(tz=timezone.utc) - datetime.fromisoformat(str(self._start_time))).total_seconds()
                if getattr(self, "_start_time", None) else 0
            ),
            "tools_count": len(self._list_tools_raw()),
            "skills_count": len(self._list_skills_raw()),
            "memory": {
                "python_objects": len(gc.get_objects()),
            },
            "client": self._client_info if self._client_info else None,
        }

        # Bellek kullanimi (psutil varsa)
        try:
            import psutil
            proc = psutil.Process(os.getpid())
            sonuc["memory"]["rss_mb"] = round(proc.memory_info().rss / 1024 / 1024, 1)
        except ImportError:
            sonuc["memory"]["note"] = "psutil yuklu degil"

        return sonuc

    def _method_notifications_listen(self, timeout: int = 5, **kwargs) -> dict:
        """Bekleyen bildirimleri getir (polling).

        Args:
            timeout: Maksimum bekleme suresi (saniye)

        Returns:
            {"notifications": [...]}
        """
        import time
        basla = time.time()
        bekleyen = []

        while time.time() - basla < timeout:
            if self._notifications:
                bekleyen = list(self._notifications)
                self._notifications.clear()
                break
            time.sleep(0.1)

        return {"notifications": bekleyen}

    def _method_tools_call_stream(self, name: str = None, arguments: dict = None,
                                   chunk_size: int = 1000, **kwargs) -> dict:
        """Stream destekli arac cagirisi.

        Args:
            name: Arac adi
            arguments: Parametreler
            chunk_size: Kucuk yanitlarda chunk basina karakter sayisi

        Returns:
            {"chunks": [...], "total_length": int, "isError": bool}
        """
        if not name:
            return {"chunks": ["[Hata]: Arac adi gerekli"], "total_length": 0, "isError": True}

        args = arguments or {}
        sonuc = self._call_tool(name, args)
        basarili = not sonuc.get("hata", False)
        metin = sonuc.get("sonuc", sonuc.get("hata", "Bilinmeyen hata"))

        # Yaniti chunk'lara bol
        chunklar = []
        for i in range(0, len(metin), chunk_size):
            chunklar.append(metin[i:i + chunk_size])

        return {
            "chunks": chunklar,
            "total_length": len(metin),
            "chunk_count": len(chunklar),
            "isError": not basarili,
        }

    def _method_initialize(self, protocol_version: str = None,
                           client_info: dict = None, **kwargs) -> dict:
        """ACP baglantisini baslat.

        Args:
            protocol_version: Istemcinin protocol versiyonu
            client_info: Istemci bilgileri (opsiyonel)

        Returns:
            Sunucu bilgileri
        """
        self._initialized = True
        self._client_info = client_info or {}
        if protocol_version:
            self._protocol_version = protocol_version

        return {
            "protocol_version": self._protocol_version,
            "server_info": {
                "name": "ReYMeN ACP Server",
                "version": "1.0.0",
                "description": "ReYMeN agentinin ACP uyumlu arayuzu",
                "tools_count": len(self._list_tools_raw()),
                "skills_count": len(self._list_skills_raw()),
                "transport": self.transport,
                "initialized_at": _zaman_damgasi(),
            },
        }

    def _method_tools_list(self, **kwargs) -> dict:
        """Tum kullanilabilir araclari listele.

        Returns:
            {"tools": [...]}
        """
        # initialize gerekmez — tools/list her zaman calisir
        tools = self._list_tools_raw()
        return {"tools": tools}

    def _method_tools_call(self, name: str = None, arguments: dict = None,
                           **kwargs) -> dict:
        """Bir araci cagir.

        Args:
            name: Arac adi (ornek: "DOSYA_OKU", "BECERI_ARA")
            arguments: Arac parametreleri

        Returns:
            {"content": [...], "isError": bool}
        """
        if not name:
            return {
                "content": [{"type": "text", "text": "[Hata]: Arac adi gerekli"}],
                "isError": True,
            }

        args = arguments or {}
        sonuc = self._call_tool(name, args)
        basarili = not sonuc.get("hata", False)

        return {
            "content": [
                {
                    "type": "text",
                    "text": sonuc.get("sonuc", sonuc.get("hata", "Bilinmeyen hata")),
                }
            ],
            "isError": not basarili,
        }

    def _method_skills_list(self, **kwargs) -> dict:
        """Tum skill/becerileri listele.

        Returns:
            {"skills": [...]}
        """
        skills = self._list_skills_raw()
        return {"skills": skills}

    def _method_skills_get(self, name: str = None, **kwargs) -> dict:
        """Bir skill'in icerigini getir.

        Args:
            name: Skill adi

        Returns:
            {"skill": {...}}
        """
        if not name:
            return self._jsonrpc_hata(
                ACPHataKodlari.INVALID_PARAMS,
                "Skill adi gerekli",
            )

        skill = self._get_skill_raw(name)
        if skill is None:
            return {
                "skill": None,
                "error": f"Skill bulunamadi: '{name}'",
            }
        return {"skill": skill}

    def _method_shutdown(self, **kwargs) -> dict:
        """Baglantiyi kapat."""
        self.running = False
        self._initialized = False
        self._stop_event.set()
        return {"shutdown": True, "message": "ACP sunucusu kapatildi."}

    def _method_ping(self, **kwargs) -> dict:
        """Saglik kontrolu."""
        return {
            "pong": True,
            "timestamp": _zaman_damgasi(),
            "uptime": getattr(self, "_start_time", None),
            "initialized": self._initialized,
        }

    # ── Arac Listeleme ────────────────────────────────────────────────────

    def _list_tools_raw(self) -> list[dict]:
        """ToolRegistry'den araclari JSON-RPC formatinda listele.

        Returns:
            [{"name": str, "description": str, "inputSchema": {...}}, ...]
        """
        tools = []

        if self._registry is None:
            return tools

        try:
            # Tum kayitli arac adlari (tools/ icindekiler)
            for ad, fonk in self._registry._tools.items():
                meta = self._registry._meta.get(ad, {})
                aciklama = meta.get("aciklama", "") or ""
                parametreler = meta.get("parametreler", []) or []
                kategori = meta.get("kategori", "") or ""

                # Schema override varsa onu kullan
                schema_override = self._registry._schemas.get(ad)
                if schema_override:
                    params = schema_override.get("parametreler", parametreler)
                else:
                    params = parametreler

                # Musaitlik kontrolu
                musait = self._registry.check_fn_kontrol_et(ad)

                tool = {
                    "name": ad,
                    "description": aciklama or f"ReYMeN araci: {ad}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                    },
                    "available": musait,
                    "kategori": kategori,
                }

                # Parametreleri inputSchema'e ekle
                if params:
                    for p in params:
                        if isinstance(p, dict):
                            p_ad = p.get("ad", p.get("name", "param"))
                            tool["inputSchema"]["properties"][p_ad] = {
                                "type": p.get("tip", p.get("type", "string")),
                                "description": p.get("aciklama", p.get("description", "")),
                            }
                    tool["inputSchema"]["required"] = [
                        p.get("ad", p.get("name"))
                        for p in params
                        if p.get("zorunlu", p.get("required", True))
                    ]
                else:
                    # Varsayilan: "args" parametresi
                    tool["inputSchema"]["properties"]["args"] = {
                        "type": "array",
                        "description": f"{ad} icin parametreler",
                        "items": {"type": "string"},
                    }

                tools.append(tool)

            # Alias'lari da ekle (ayri birer tool olarak)
            for alias, hedef in self._registry._aliases.items():
                if alias in {t["name"] for t in tools}:
                    continue  # Ayni isim varsa tekrar ekleme
                meta = self._registry._meta.get(alias, {})
                musait = self._registry.check_fn_kontrol_et(alias)

                tools.append({
                    "name": alias,
                    "description": meta.get("aciklama", "") or f"{alias} -> {hedef}",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "args": {
                                "type": "array",
                                "description": f"{alias} icin parametreler",
                                "items": {"type": "string"},
                            },
                        },
                    },
                    "available": musait,
                    "alias_for": hedef,
                    "kategori": meta.get("kategori", ""),
                })

        except Exception as e:
            logger.exception("[ACP] Tool listeleme hatasi")

        return tools

    def _list_skills_raw(self) -> list[dict]:
        """ClosedLearningLoop'den skill/beceri listesini al.

        Returns:
            [{"ad": str, "aciklama": str, "kaynak": str}, ...]
        """
        try:
            if _CLOSED_LOOP is not None:
                return _CLOSED_LOOP.tum_beceriler()
        except Exception:
            logger.exception("[ACP] Skill listeleme hatasi")

        # Fallback: skills/ dizininden tara
        skills = []
        try:
            ROOT = Path(__file__).parent
            for dizin in [ROOT / "skills", ROOT / ".ReYMeN" / "skills"]:
                if not dizin.exists():
                    continue
                for dosya in sorted(dizin.rglob("*.md")):
                    try:
                        icerik = dosya.read_text(encoding="utf-8", errors="replace")
                        ad = dosya.stem
                        aciklama = ""
                        if icerik.startswith("---"):
                            bitis = icerik.find("\n---", 3)
                            if bitis != -1:
                                for satir in icerik[3:bitis].splitlines():
                                    satir = satir.strip()
                                    if ":" in satir:
                                        k, v = satir.split(":", 1)
                                        k = k.strip().lower()
                                        if k == "name" and v.strip():
                                            ad = v.strip().strip("\"'")
                                        elif k == "description" and v.strip():
                                            aciklama = v.strip().strip("\"'")[:200]
                        skills.append({
                            "ad": ad,
                            "aciklama": aciklama or dosya.stem,
                            "kaynak": str(dosya),
                        })
                    except Exception as _acp_serv_e581:
                        print(f"[UYARI] acp_server.py:582 - {_acp_serv_e581}")
        except Exception as _acp_serv_e583:
            print(f"[UYARI] acp_server.py:584 - {_acp_serv_e583}")

        return skills

    def _get_skill_raw(self, ad: str) -> Optional[dict]:
        """Bir skill icerigini getir.

        Args:
            ad: Skill adi

        Returns:
            {"ad": str, "aciklama": str, "icerik": str, "kaynak": str} veya None
        """
        # Once closed_learning_loop'den dene
        try:
            if _CLOSED_LOOP is not None:
                sonuclar = _CLOSED_LOOP._ilgili_becerileri_skorlu(ad, adet=1)
                if sonuclar:
                    return {
                        "ad": sonuclar[0][0],
                        "aciklama": sonuclar[0][1],
                        "icerik": sonuclar[0][2],
                        "kaynak": sonuclar[0][3] or "",
                    }
        except Exception as _acp_serv_e608:
            print(f"[UYARI] acp_server.py:609 - {_acp_serv_e608}")

        # Fallback: skills/ dizininde dosya ara
        try:
            ROOT = Path(__file__).parent
            for dizin in [ROOT / "skills", ROOT / ".ReYMeN" / "skills"]:
                if not dizin.exists():
                    continue
                for dosya in sorted(dizin.rglob("*.md")):
                    try:
                        icerik = dosya.read_text(encoding="utf-8", errors="replace")
                        dosya_adi = dosya.stem
                        if ad.lower() in (dosya_adi.lower(), icerik.split("\n")[0].lstrip("# ").strip().lower()):
                            return {
                                "ad": dosya_adi,
                                "aciklama": icerik[:200],
                                "icerik": icerik,
                                "kaynak": str(dosya),
                            }
                    except Exception as _acp_serv_e628:
                        print(f"[UYARI] acp_server.py:629 - {_acp_serv_e628}")
        except Exception as _acp_serv_e630:
            print(f"[UYARI] acp_server.py:631 - {_acp_serv_e630}")

        return None

    def _call_tool(self, name: str, arguments: dict) -> dict:
        """ToolRegistry.calistir() uzerinden araci cagir.

        Args:
            name: Arac adi
            arguments: Parametre dict'i

        Returns:
            {"sonuc": str} veya {"hata": str}
        """
        if self._registry is None:
            return {"hata": "ToolRegistry yuklu degil."}

        try:
            # arguments dict'ini ToolRegistry.calistir formatina cevir
            # Eger "args" anahtari varsa, onu kullan
            if "args" in arguments and isinstance(arguments["args"], list):
                sonuc = self._registry.calistir(name, *arguments["args"])
            else:
                # Anahtar-deger parametrelerini sirali parametre olarak gec
                params = list(arguments.values()) if arguments else []
                sonuc = self._registry.calistir(name, *params)

            return {"sonuc": str(sonuc) if sonuc is not None else "[Tamam]"}
        except Exception as e:
            logger.exception("[ACP] Tool cagirma hatasi: %s", name)
            return {"hata": f"[Hata]: {e}"}

    # ── Yasam Dongusu ─────────────────────────────────────────────────────

    def start(self) -> None:
        """ACP sunucusunu baslat (stdio modunda).

        Stdin'den JSON satirlari okur, stdout'a JSON yanitlari yazar.
        """
        self.running = True
        self._initialized = True
        self._start_time = _zaman_damgasi()

        logger.info("[ACP] Sunucu basladi (transport=%s)", self.transport)

        try:
            for satir in sys.stdin:
                if not self.running:
                    break
                satir = satir.strip()
                if not satir:
                    continue

                yanit = self._handle_request(satir)
                if yanit:
                    sys.stdout.write(yanit + "\n")
                    sys.stdout.flush()
        except EOFError as _acp_serv_e688:
            print(f"[UYARI] acp_server.py:689 - {_acp_serv_e688}")
        except KeyboardInterrupt as _acp_serv_e690:
            print(f"[UYARI] acp_server.py:691 - {_acp_serv_e690}")
        finally:
            self.running = False
            logger.info("[ACP] Sunucu durduruldu.")

    def stop(self) -> None:
        """ACP sunucusunu durdur."""
        self.running = False
        self._stop_event.set()

    def start_threaded(self) -> threading.Thread:
        """ACP sunucusunu ayri bir thread'de baslat.

        Returns:
            Baslatilan thread
        """
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.start, daemon=True)
        self._thread.start()
        return self._thread


# ── Motor Kaydi ────────────────────────────────────────────────────────────

# Global ACP sunucu instance
_ACP_SERVER_INSTANCE = None
_ACP_SERVER_LOCK = threading.Lock()


def _acp_baslat(port: str = "stdio") -> str:
    """ACP sunucusunu baslat.

    Args:
        port: "stdio" veya port numarasi (socket henuz desteklenmiyor)

    Returns:
        Durum mesaji
    """
    global _ACP_SERVER_INSTANCE
    with _ACP_SERVER_LOCK:
        if _ACP_SERVER_INSTANCE and _ACP_SERVER_INSTANCE.running:
            return "[ACP] Sunucu zaten calisiyor."

        transport = "socket" if port and port != "stdio" else "stdio"
        _ACP_SERVER_INSTANCE = ACPServer(transport=transport)
        if transport == "stdio":
            _ACP_SERVER_INSTANCE.start_threaded()
            return f"[ACP] Sunucu baslatildi (transport={transport})"

        return f"[ACP] Socket transport henuz desteklenmiyor. 'stdio' kullanin."


def _acp_durum() -> str:
    """ACP sunucusu durumu.

    Returns:
        Durum raporu
    """
    global _ACP_SERVER_INSTANCE
    if _ACP_SERVER_INSTANCE is None:
        return "[ACP] Sunucu baslatilmadi."

    return (
        f"[ACP] Durum: {'calisiyor' if _ACP_SERVER_INSTANCE.running else 'durduruldu'}\n"
        f"  Transport: {_ACP_SERVER_INSTANCE.transport}\n"
        f"  Baslatildi: {getattr(_ACP_SERVER_INSTANCE, '_start_time', '?')}\n"
        f"  Initialized: {_ACP_SERVER_INSTANCE._initialized}"
    )


def motor_kaydet(motor: object):
    """motor.py entegrasyonu: ACP araçlarını kaydet.

    Args:
        motor: Motor ornegi (_plugin_arac_kaydet metoduna sahip)
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    motor._plugin_arac_kaydet(
        "ACP_BASLAT",
        lambda port="stdio": _acp_baslat(port),
        "ACP (Agent Communication Protocol) sunucusunu baslatir. "
        "Port: 'stdio' (varsayilan) veya port numarasi. "
        "Claude Code / Copilot gibi harici AI araclarinin ReYMeN araclarini "
        "cagirmasini saglar.",
    )
    motor._plugin_arac_kaydet(
        "ACP_DURUM",
        _acp_durum,
        "ACP sunucusu durumunu gosterir: calisiyor/durduruldu, transport, "
        "baslatma zamani.",
    )


# ── Test / Dogrudan Calistirma ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=== ACP Server Test ===\n")

    # 1. Sunucu olustur
    server = ACPServer()
    print("[Test 1] Sunucu olusturuldu.")

    # 2. tools/list test
    yanit = server._handle_request('{"jsonrpc":"2.0","method":"tools/list","id":1}')
    data = json.loads(yanit)
    assert "result" in data, f"tools/list basarisiz: {data}"
    tools = data["result"].get("tools", [])
    print(f"[Test 2] tools/list: {len(tools)} arac bulundu.")
    if tools:
        print(f"  Ilk 5: {', '.join(t['name'] for t in tools[:5])}")

    # 3. initialize test
    yanit = server._handle_request(
        '{"jsonrpc":"2.0","method":"initialize",'
        '"params":{"protocol_version":"2025-03-26","client_info":{"name":"test"}},'
        '"id":3}'
    )
    data = json.loads(yanit)
    assert "result" in data, f"initialize basarisiz: {data}"
    svr = data["result"].get("server_info", {})
    print(f"[Test 3] initialize: {svr.get('name', '?')} v{svr.get('version', '?')}")

    # 4. ping test
    yanit = server._handle_request('{"jsonrpc":"2.0","method":"ping","id":4}')
    data = json.loads(yanit)
    assert data.get("result", {}).get("pong"), f"ping basarisiz: {data}"
    print(f"[Test 4] ping: OK ({data['result'].get('timestamp', '?')})")

    # 5. skills/list test
    yanit = server._handle_request('{"jsonrpc":"2.0","method":"skills/list","id":5}')
    data = json.loads(yanit)
    assert "result" in data, f"skills/list basarisiz: {data}"
    skills = data["result"].get("skills", [])
    print(f"[Test 5] skills/list: {len(skills)} skill bulundu.")
    if skills:
        print(f"  Ilk 3: {', '.join(s.get('ad', '?') for s in skills[:3])}")

    # 6. Bilinmeyen metot test
    yanit = server._handle_request('{"jsonrpc":"2.0","method":"bilinmeyen","id":6}')
    data = json.loads(yanit)
    assert "error" in data, f"Hata donmeliydi: {data}"
    assert data["error"]["code"] == -32601
    print(f"[Test 6] Bilinmeyen metot: {data['error']['code']} - {data['error']['message']}")

    # 7. shutdown test
    yanit = server._handle_request('{"jsonrpc":"2.0","method":"shutdown","id":7}')
    data = json.loads(yanit)
    assert data.get("result", {}).get("shutdown"), f"shutdown basarisiz: {data}"
    print(f"[Test 7] shutdown: OK")

    # 8. Gecersiz JSON test
    yanit = server._handle_request("bu gecerli bir json degil")
    data = json.loads(yanit)
    assert "error" in data, f"Hata donmeliydi: {data}"
    assert data["error"]["code"] == -32700
    print(f"[Test 8] Gecersiz JSON: {data['error']['code']} - {data['error']['message']}")

    # 9. motor_kaydet test
    class MockMotor:
        def __init__(self):
            self._araclar = {}
        def _plugin_arac_kaydet(self, ad, fonk, aciklama=""):
            self._araclar[ad] = (fonk, aciklama)

    mm = MockMotor()
    motor_kaydet(mm)
    assert "ACP_BASLAT" in mm._araclar, "motor_kaydet ACP_BASLAT eklemedi"
    assert "ACP_DURUM" in mm._araclar, "motor_kaydet ACP_DURUM eklemedi"
    print(f"[Test 9] motor_kaydet: {len(mm._araclar)} arac kaydedildi")
    print(f"  Arac: ACP_BASLAT -> {mm._araclar['ACP_BASLAT'][1][:50]}...")
    print(f"  Arac: ACP_DURUM -> {mm._araclar['ACP_DURUM'][1][:50]}...")

    print(f"\n[OK] Tum testler gecti! ({len(tools)} tool, {len(skills)} skill)")
