# -*- coding: utf-8 -*-
"""motor.py â€” Action resolver. Uses tools from the tools/ folder.
Catches 'Action: TOOL(...)' from LLM output, routes via ToolRegistry.
Uses file_safety + path_security for file operations.

This file is inspired by ReYMeN Agent.
Apache 2.0 License â€” github.com/NousResearch/hermes-agent
"""

from typing import Any, Optional, Dict, List, Tuple, Union
import os
import re
import sys
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).parent

# CUA Motor AracÄ±
try:
    from reymen.arac.cua_motor_araci import CUA_EKRAN_KULLAN, CUA_ARACLARI_TARA

    _CUA_MEVCUT = True
except ImportError:
    _CUA_MEVCUT = False

# Guvenlik
try:
    from reymen.guvenlik.file_safety import guvenli_mi as _dosya_guvenli
except ImportError:
    _dosya_guvenli = lambda p: (True, "")
try:
    from reymen.guvenlik.path_security import yol_dogrula as _yol_dogrula
except ImportError:
    _yol_dogrula = lambda p: (True, p)

# Context compression (dead code canlandirma)
try:
    from reymen.hafiza.context_compressor import ContextCompressor

    _COMPRESSOR = ContextCompressor(max_token=4096)
except ImportError:
    _COMPRESSOR = None

# Prompt caching (dead code canlandirma)
try:
    from reymen.arac.prompt_caching import PromptCache

    _CACHE = PromptCache(max_boyut=100, ttl_saniye=3600)
except ImportError:
    _CACHE = None

# PII redaction â€” once kapsamli agent/, sonra PII icin root/
try:
    from agent.redact import redact_sensitive_text as _agent_temizle
except ImportError:
    _agent_temizle = None
try:
    from reymen.guvenlik.redact import tam_temizle as _pii_temizle
except ImportError:
    _pii_temizle = lambda m: m

# Credential Pool
try:
    from reymen.core.credential_pool import get_credential_pool

    _CREDENTIAL_POOL = get_credential_pool()
except ImportError:
    _CREDENTIAL_POOL = None

# Voice Mode
try:
    from reymen.cereyan.voice_mode import VoiceMode

    _VOICE_MODE_KLASS = VoiceMode
except ImportError:
    _VOICE_MODE_KLASS = None

# API Server
try:
    from reymen.api_server import APIServer

    _API_SERVER_KLASS = APIServer
except ImportError:
    _API_SERVER_KLASS = None

# Otonom gÃ¶rev Ã§Ã¶zÃ¼cÃ¼ (orchestrator)
try:
    from reymen.core.orchestrator import coz_hata as _coz_hata

    _ORCHESTRATOR_MEVCUT = True
except ImportError:
    _ORCHESTRATOR_MEVCUT = False
    _coz_hata = lambda hata, kod="", ad="": f"[COZ] Orchestrator yok: {hata[:100]}"

# Ã–ÄŸrenme dÃ¶ngÃ¼sÃ¼
try:
    from reymen.core.ogrenme import OgrenmeDongusu, CozumHafizasi

    _OGRENME_MEVCUT = True
except ImportError:
    _OGRENME_MEVCUT = False

# MessageBroker (queue.Queue tabanlÄ±)
try:
    from reymen.cereyan.broker import MessageBroker, MesajTipi, Mesaj, get_broker
    from reymen.cereyan.workflow_pipeline import (
        hata_handler,
        cozum_ara_handler,
        cozum_kaydet_handler,
        gorev_coz_pipeline,
    )

    _BROKER_MEVCUT = True
except ImportError:
    _BROKER_MEVCUT = False

# Tool Registry (birincil arac kaynagi)
try:
    from reymen.arac.tool_registry import ToolRegistry as _ToolRegistry

    _REGISTRY = _ToolRegistry()
except ImportError:
    _REGISTRY = None

# Plugin Manager (ikincil arac kaynagi)
try:
    from reymen.sistem.plugin_manager import PluginManager as _PluginManager

    _PLUGIN_MGR = _PluginManager(str(ROOT.parent / "sistem" / "plugins"))
except ImportError:
    _PLUGIN_MGR = None

# Profil Yoneticisi (multi-profile sistemi)
try:
    from reymen.sistem.profile_manager import ProfileManager as _ProfileManager

    _PROFILE_MGR = _ProfileManager(str(ROOT.parent.parent / "config.yaml"))
except ImportError:
    _PROFILE_MGR = None

# Plugin Yukleyici (ReYMeN seviyesi â€” plugin.yaml destegi)
try:
    from reymen.sistem.plugin_loader import PluginYukleyici as _PluginYukleyici

    _PLUGIN_YUKLEYICI = _PluginYukleyici(dizin=ROOT.parent / "sistem" / "plugins")
except ImportError:
    _PLUGIN_YUKLEYICI = None

# Fallback (if/else icin)
try:
    from reymen.sistem.terminal_backends import TerminalBackendDispatcher
except ImportError:
    TerminalBackendDispatcher = None
try:
    from reymen.cereyan.izole_laboratuvar import izole_python_calistir
except ImportError:
    izole_python_calistir = None


# â”€â”€ Vektor bellek yardimci araci (VEKTOR_BELLEK icin) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _vektor_bellek_arac(
    vb,
    islem: str,
    metin: str = "",
    sorgu: str = "",
    kayit_id: str = "",
    k: int = 5,
) -> str:
    """VEKTOR_BELLEK aracinin arkaplan fonksiyonu.

    Args:
        vb: VektorBellek instance
        islem: ekle | ara | sil | listele | bilgi
        metin: eklenecek metin
        sorgu: arama sorgusu
        kayit_id: silinecek kayit ID
        k: kac sonuc

    Returns:
        Metin sonuc
    """
    from reymen.hafiza.vektor_bellek import VektorBellek

    if not isinstance(vb, VektorBellek):
        return "[Hata]: VektorBellek instance gerekli"

    if islem == "ekle":
        if not metin:
            return "[Hata]: Metin bos olamaz"
        kid = vb.ekle(metin)
        return f"[OK] Kayit eklendi: {kid}" if kid else "[Hata]: Kayit eklenemedi"

    elif islem == "ara":
        if not sorgu:
            return "[Hata]: Sorgu bos olamaz"
        sonuclar = vb.ara(sorgu, k=k)
        if not sonuclar:
            return "[Bilgi]: Sonuc bulunamadi"
        satirlar = [
            f"[{i+1}] skor={skor:.4f} | {metin[:120]}"
            for i, (_, metin, skor, _) in enumerate(sonuclar)
        ]
        return "\n".join(satirlar)

    elif islem == "sil":
        if not kayit_id:
            return "[Hata]: Kayit ID gerekli"
        return "[OK] Silindi" if vb.sil(kayit_id) else "[Hata]: Silme basarisiz"

    elif islem == "listele":
        kayitlar = vb.listele(limit=k or 20)
        if not kayitlar:
            return "[Bilgi]: Kayit yok"
        satirlar = [f"  {r['id'][:12]}... | {r['metin'][:80]}" for r in kayitlar]
        return f"Toplam {len(vb)} kayit:\n" + "\n".join(satirlar[:20])

    elif islem == "bilgi":
        import json

        return json.dumps(vb.bilgi(), ensure_ascii=False, indent=2)

    else:
        return (
            f"[Hata]: Bilinmeyen islem: '{islem}'. "
            f"Secenekler: ekle, ara, sil, listele, bilgi"
        )


# â”€â”€ Gateway State JSON yazma (bot.py bagimli degil) â”€â”€
import json as _json
import datetime as _dt
import logging

logger = logging.getLogger(__name__)

_GATEWAY_STATE_PATH = ROOT / "gateway_state.json"


def _gateway_durum_yaz(state: str = "running", hata: str = "") -> None:
    """gateway_state.json'a durum yaz (ReYMeN uyumlu format)."""
    try:
        payload = {
            "pid": os.getpid(),
            "kind": "reymen-gateway",
            "gateway_state": state,
            "active_agents": 0,
            "platforms": {
                "telegram": {
                    "state": "connected" if state == "running" else "disconnected",
                    "error_code": None,
                    "error_message": hata or None,
                    "updated_at": _dt.datetime.now().isoformat(),
                }
            },
            "updated_at": _dt.datetime.now().isoformat(),
        }
        _GATEWAY_STATE_PATH.write_text(
            _json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception as _e:
        logger.warning("[Motor] except Exception (L117): %s", Exception)
        pass


# LiteLLM provider (100+ provider destegi)
try:
    from reymen.ag.litellm_provider import litellm_calisitir as _litellm_calisitir
    from reymen.ag.litellm_provider import litellm_durum as _litellm_durum

    _LITELLM_MEVCUT = True
except ImportError:
    _LITELLM_MEVCUT = False

# Observability / Tracing (opsiyonel)
try:
    from reymen.core.observability import trace_tool_call

    _TRACE_TOOL_AKTIF = True
except ImportError:

    def trace_tool_call(span_adi=None, attributes=None):
        def decorator(func):
            return func

        return decorator

    _TRACE_TOOL_AKTIF = False


class Motor:
    def __init__(
        self,
        backend_mode: str = "local",
        hafiza_collection: Any = None,
        config: Optional[dict] = None,
    ) -> None:
        self.terminal = (
            TerminalBackendDispatcher(mode=backend_mode)
            if TerminalBackendDispatcher
            else None
        )
        self.hafiza = hafiza_collection
        self.config = config or {}
        self._ekran = None
        self._provider_ref = None  # FAZ 6: ARAC_URET icin provider referansi
        # Skill allowed-tools: aktif skill'in bildirdigi araclara gecici HITL muafiyeti
        self.ekstra_izin_araclar: set = set()
        # Async hook sistemi
        try:
            from reymen.sistem.hook_dispatcher import AsynchronousHookDispatcher

            self._hooks = AsynchronousHookDispatcher()
            # Varsayilan hook callback'lerini kaydet
            try:
                from reymen.cereyan.hook_handlers import varsayilan_hooklari_kaydet

                varsayilan_hooklari_kaydet(self._hooks)
                logger.info("[Motor] Varsayilan hook callback'ler kaydedildi")
            except Exception as _he:
                logger.warning("[Motor] Hook handler kayit hatasi: %s", _he)
        except ImportError:
            self._hooks = None
        # Skill tarama cache (tekrari onle)
        self._skill_araclari_cache = None
        self._plugin_moduller_yukle()
        # FAZ 6: Onceki oturumdan kalan dinamik araclari yukle
        try:
            from reymen.cereyan.dinamik_arac_uretici import (
                mevcut_dinamik_araclari_yukle,
            )

            mevcut_dinamik_araclari_yukle(self)
        except ImportError as _e:
            logger.warning("[Motor] Modul yuklenemedi (L143): %s", ImportError)
            pass

        # MessageBroker baÅŸlat
        self._broker = None
        if _BROKER_MEVCUT:
            try:
                self._broker = get_broker(max_workers=4)
                self._broker.abone_ol_liste(
                    [
                        (MesajTipi.HATA, hata_handler),
                        (MesajTipi.COZUM_ARA, cozum_ara_handler),
                        (MesajTipi.COZUM_KAYDET, cozum_kaydet_handler),
                    ]
                )
                self._broker.baslat()
                logger.info("[Motor] MessageBroker baÅŸlatÄ±ldÄ± (4 consumer thread)")

                # Broker araÃ§larÄ±nÄ± kaydet
                self._plugin_arac_kaydet(
                    "BROKER_DURUM",
                    self.broker_durum,
                    "MessageBroker durum raporu: Ã§alÄ±ÅŸan thread'ler, kuyruk boyutlarÄ±, abone sayÄ±larÄ±",
                )
                self._plugin_arac_kaydet(
                    "GOREV_COZ_PIPELINE",
                    self.gorev_coz_pipeline,
                    "Pipeline ile gÃ¶rev Ã§Ã¶zÃ¼mÃ¼: GÃ–REV -> PLANLA -> Ã–N DOÄRULA -> KOD -> TEST -> Ä°NCELE -> KAYDET. "
                    "Parametreler: gorev_tanimi (str), script_path (str, opsiyonel). "
                    "DÃ¶ner: baÅŸarÄ±lÄ±ysa .py dosya yolu, baÅŸarÄ±sÄ±zsa hata mesajÄ±.",
                )
            except Exception as e:
                logger.warning("[Motor] Broker baÅŸlatma hatasÄ±: %s", e)
                self._broker = None

    def hook_kaydet(self, olay: str, fn: Any) -> None:
        """Olay bazlÄ± async hook kaydet (Ã¶rn. 'TOOL_CALLED', 'TOOL_ERROR')."""
        if self._hooks:
            self._hooks.kaydet(olay, fn)

    # â”€â”€ MessageBroker Entegrasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @property
    def broker(self):
        """MessageBroker instance'Ä±."""
        return getattr(self, "_broker", None)

    def broker_durum(self) -> dict:
        """Broker durum raporu."""
        if self._broker:
            return self._broker.durum()
        return {"running": False, "mesaj": "Broker aktif deÄŸil"}

    def gorev_coz_pipeline(self, gorev_tanimi: str, script_path: str = "") -> str:
        """Pipeline ile gÃ¶rev Ã§Ã¶zÃ¼mÃ¼: GÃ–REV -> PLAN -> DOÄRULA -> KOD -> TEST -> Ä°NCELE -> KAYDET

        Args:
            gorev_tanimi: GÃ¶rev aÃ§Ä±klamasÄ±
            script_path: Opsiyonel mevcut script yolu

        Returns:
            BaÅŸarÄ±lÄ±: kaydedilen .py dosya yolu
            BaÅŸarÄ±sÄ±z: hata mesajÄ±
        """
        if not _BROKER_MEVCUT or not self._broker:
            return "âŒ Broker aktif deÄŸil (broker modÃ¼lÃ¼ yÃ¼klenemedi)"
        return gorev_coz_pipeline(self._broker, gorev_tanimi, script_path)

    def _plugin_moduller_yukle(self) -> None:
        """Bilinen tÃ¼m plugin modÃ¼llerinin araÃ§larÄ±nÄ± otomatik kaydet."""
        import importlib

        moduller = [
            "persistence",
            "message_sanitization",
            "x_search_tool",
            "homeassistant_tool",
            "feishu_doc_tool",
            "yuanbao_tools",
            "model_tools",
            "mcp_tool",
            "rate_limiter",
            "araclar_web",
            "araclar_gelismis",
            "tools.discord_tool",
            "tools.browser_camofox",
            "tools.threat_patterns",
            # Batch 8 - Yeni araclar
            "tools.delegate_tool",
            "tools.kanban_tools",
            "tools.voice_mode",
            "tools.clarify_tool",
            "tools.blueprints",
            "tools.mixture_of_agents_tool",
            "tools.code_execution_tool",
            "tools.osv_check",
            "tools.todo_tool",
            "tools.skills_hub",
            "tools.skills_sync",
            "tools.feishu_doc_tool",
            "tools.feishu_drive_tool",
            "tools.homeassistant_tool",
            "tools.session_search_tool",
            "tools.approval",
            "tools.write_approval",
            # Memory plugin
            "plugins.memory",
            # Batch 9 - Yeni 25 araÃ§
            "tools.env_passthrough",
            "tools.env_probe",
            "tools.file_operations",
            "tools.file_state",
            "tools.file_tools",
            "tools.fuzzy_match",
            "tools.interrupt",
            "tools.process_registry",
            "tools.registry",
            "tools.thread_context",
            "tools.credential_files",
            "tools.schema_sanitizer",
            "tools.skill_provenance",
            "tools.skill_usage",
            "tools.tool_backend_helpers",
            "tools.browser_dialog_tool",
            "tools.browser_supervisor",
            "tools.web_tools",
            "tools.cronjob_tools",
            "tools.cronjob_tool",
            "tools.debug_helpers",
            "tools.mcp_oauth",
            "tools.microsoft_graph_auth",
            "tools.microsoft_graph_client",
            "tools.tool_output_limits",
            "tools.tool_result_storage",
            # tools.memory_tool
            "tools.memory_tool",
            # tools.skill_tool
            "tools.skill_tool",
            # tools.tts_tool
            "tools.tts_tool",
            # tools.web_search_tool
            "tools.web_search_tool",
            # tools.session_search_tool
            "tools.session_search_tool",
            # tools.execute_code_tool
            "tools.execute_code_tool",
            # tools.delegate_task_tool
            "tools.delegate_task_tool",
            # tools.context_tool
            "tools.context_tool",
            # tools.memory_providers
            "tools.memory_providers",
            # tools.clarify_tool ve tools.todo_tool
            "tools.clarify_tool",
            "tools.todo_tool",
            # Batch 10 - Son 15 eksik arac
            "tools.ansi_strip",
            "tools.binary_extensions",
            "tools.browser_camofox_state",
            "tools.browser_tool",
            "tools.clarify_gateway",
            "tools.fal_common",
            "tools.lazy_deps",
            "tools.openrouter_client",
            "tools.patch_parser",
            "tools.read_extract",
            "tools.read_terminal_tool",
            "tools.skills_tool",
            "tools.tool_search",
            "tools.website_policy",
            "tools.xai_http",
            # Entegrasyon 4 â€” kÃ¶k modÃ¼ller
            "kanban_orchestrator",
            "context_references",
            "araclar_makro",
            "araclar_ses",
            "araclar_telegram",
            "mcp_oauth",
            "batch_engine",
            "security_engine",
            "yetenek_fabrikasi",
            "sistem_sinyalleri",
            # Gorsel analiz (FAL/OpenRouter/Ollama)
            "araclar_goruntu",
            # Gorsel analiz v2 (DeepSeek V4 Flash + OpenRouter Qwen-VL) â€” araclar_goruntu'dan SONRA
            # yuklenir ki GORUNTU_ANALIZ tool'unu overwrite edip kazansin
            "reymen.cereyan.tools.vision_tools",
            # Entegrasyon 5 â€” ek modÃ¼ller
            "mcp_oauth_manager",
            "reymen_batch_runner",
            "models_dev",
            # Entegrasyon 6 â€” reyment CLI araÃ§larÄ±
            "reyment",
            # Entegrasyon 7 â€” ekran/tarayÄ±cÄ±/skill/telegram
            "araclar_ekran",
            "araclar_tarayici",
            "skill_bundles",
            "skill_commands",
            "telegram_bot",
            # Entegrasyon 8 â€” Claude Code iÅŸbirliÄŸi
            "tools.claude_code_tool",
            # Kanban Board + Worker
            "reymen.kanban",
            # Kopru (Bot1/Bot2 Bridge)
            "kopru",
            # LSP (Language Server Protocol)
            "tools.lsp_tool",
            # CUA (Computer Use Agent)
            "cua_motor_araci",
            # MCP (Model Context Protocol)
            "tools.mcp_tool",
            # MCP Paket (async MCP manager + tool registry)
            # NOTE: reymen.arac.native_mcp_client LEGACY, reymen.mcp kullaniliyor
            "reymen.mcp",
            # Merkezi Hata Toplama + Bildirim
            "reymen.sistem.hata_toplama",
            # Schema Manager (Alembic versiyonlama)
            "reymen.sistem.schema_manager",
            # Docker Sandbox + Threat Detection
            "reymen.guvenlik.docker_sandbox",
            # Container Sandbox (shell komutlari icin Docker izolasyonu)
            "reymen.guvenlik.container_sandbox",
            # Web Search Engine (coklu back-end)
            "reymen.arac.web_search_engine",
            # Gorsel Uretim Engine (FAL/OpenAI/xAI/Stub)
            "reymen.arac.image_gen_engine",
            # Browser Automation Engine (PlaywrightMCP/BrowserUse)
            "reymen.arac.browser_engine",
            # Network Restriction (Windows Firewall + iptables + Docker)
            "reymen.guvenlik.network_restriction",
            # Skill Library (SQLite kutuphane + FTS5)
            "reymen.cereyan.skill_library",
            # Skill Activator (sorgudan otomatik aktivasyon)
            "reymen.cereyan.skill_activator",
            # Skill Aktivasyonu (6868 skill hazir)
            "reymen.sistem.skill_aktive_et",
            # Surekli Ogrenme (Continuous Learning)
            "reymen.sistem.surekli_ogrenme",
            # Skill cron sync (FTS5 index cron kaydi)
            "reymen.cereyan.cron_skill_sync",
            # Merkezi Durum (durum.json okuyucu â€” herkes kullanir)
            "reymen.sistem.durum",
            # Active skill tracker (LLM context enjeksiyonu)
            "reymen.cereyan.active_skill_tracker",
            # Personality (kisilik sistemi)
            "agent.personalities",
            # Kapali Ogrenme Dongusu
            "closed_learning_loop",
            # Self-Improvement (kalite metrikleri + otomatik iyilestirme)
            "reymen.self_improve",
            # Curator (otomatik bakim: skill/hafiza/pycache kontrolu)
            "reymen.sistem.curator",
            # Cozum Hafizasi (ogrenilen cozumler + geri bildirim)
            "reymen.sistem.cozum_hafizasi",
            # SQLite FTS5 hafiza + session_search
            "hafiza_genislet",
            # MCP Server Host (Streamable HTTP + Stdio)
            "reymen.core.mcp_server",
            # Schema Manager (SQLite versiyonlama + idempotent CREATE)
            "reymen.core.schema_manager",
            # Session DB (P1) â€” FTS5 + trigram arama
            "reymen.core.session_db",
            # Cron/Scheduler (P1) â€” per-job override, watchdog
            "reymen.core.cron_manager",
            # Gateway Sistemi (P1) â€” multi-platform
            "reymen.core.gateway_manager",
            # ACP (Agent Communication Protocol)
            "acp_server",
            # A2A (Agent-to-Agent messaging)
            "reymen.a2a_integration",
            # A2A Transport (HTTP/WS ag mesajlasmasi)
            "reymen.a2a_transport",
            # A2A Distributed (config + otomatik baglanti)
            "reymen.a2a_distributed",
            # A2A/ACP (Agent Card, Skill Transfer, Task Delegation)
            "reymen.a2a_acp",
            # Gateway Sistemi (P1) â€” Ã‡oklu platform gateway
            "reymen.ag.gateway_temel",
            "reymen.ag.salted_gateway",
            "reymen.ag.platform_gateways",
            "reymen.ag.gateway_yonetici",
            # Delegasyon Sistemi (P2) â€” Subagent + gÃ¶rev ayrÄ±ÅŸtÄ±rma
            "reymen.ag.delegasyon",
            # TUI (Terminal UI - prompt_toolkit tabanli)
            "reymen.tui",
            # Web UI (FastAPI + HTMX yonetim paneli)
            "reymen.web_ui",
            # Checkpoint yÃ¶netimi (gÃ¶rev geri alma / rollback)
            "tools.checkpoint_manager",
            # Provider Sistemi (P0) â€” model routing, failover
            "reymen.core.model_provider",
            # YAML Config Manager (P0) â€” profile, env override
            "reymen.core.config_manager",
            # Analitik/Kalite sistemi (P2) â€” metrik toplama, dashboard
            "reymen.sistem.analitik",
            # Hot-Reload sistemi â€” runtime modul izleme
            "reymen.sistem.hot_reload",
            # Kanban Board sistemi â€” is takibi + worker
            "reymen.kanban",
            # Schema Manager â€” SQLite tablo + versiyon
            "reymen.core.schema_manager",
            # TTS Tool (P1) â€” edge-tts ile metin seslendirme
            "reymen.sistem.tts_tool_text",
            # STT Tool (P1) â€” faster-whisper ile ses tanima
            "reymen.sistem.stt_tool",
            # Video Generation Engine (P3) â€” moviepy + FAL + HyperFrames
            "reymen.arac.video_gen_engine",
            # Plugin Marketplacesi â€” katalog + uzaktan yukleme
            "reymen.sistem.marketplace",
            # TTS/STT araclari â€” metin->ses, ses->metin
            "reymen.ag.acp_server",
            "reymen.ag.delegation",
            "reymen.ag.mcp_oauth",
            "reymen.ag.telegram_bot",
            "reymen.arac.araclar_ekran",
            "reymen.arac.araclar_gelismis",
            "reymen.arac.araclar_goruntu",
            "reymen.arac.araclar_makro",
            "reymen.arac.araclar_ses",
            "reymen.arac.araclar_tarayici",
            "reymen.arac.araclar_video",
            "reymen.arac.araclar_web",
            "reymen.arac.batch_engine",
            "reymen.arac.cua_motor_araci",
            "reymen.arac.feishu_doc_tool",
            "reymen.arac.firecrawl_tool",
            "reymen.arac.homeassistant_tool",
            "reymen.arac.kanban_orchestrator",
            "reymen.arac.konusmadan_skill",
            "reymen.arac.mcp_client_tool",
            "reymen.arac.mcp_tool",
            "reymen.arac.native_mcp_client",
            "reymen.arac.web_search_tool",
            "reymen.arac.x_search_tool",
            "reymen.arac.yuanbao_tools",
            "reymen.cereyan.closed_learning_loop",
            "reymen.cereyan.dinamik_arac_uretici",
            "reymen.cereyan.hata_cozucu",
            "reymen.core.backup_manager",
            "reymen.core.delegation_manager",
            "reymen.core.guardrails_manager",
            "reymen.core.oauth_manager",
            "reymen.core.vector_memory",
            "reymen.guvenlik.message_sanitization",
            "reymen.hafiza.context_references",
            "reymen.hafiza.hafiza_genislet",
            "reymen.sistem.batch_runner",
            "reymen.sistem.benchmark_tools",
            "reymen.sistem.persistence",
            "reymen.sistem.rate_limiter",
            "reymen.sistem.sistem_sinyalleri",
            "reymen.sistem.plugins.browser_provider",
            "reymen.sistem.plugins.delegation_provider",
            "reymen.sistem.plugins.guardrails_provider",
            "reymen.sistem.plugins.image_gen_provider",
            "reymen.sistem.plugins.mcp_provider",
            "reymen.sistem.plugins.web_search_provider",
            "reymen.mcp",
            "reymen.mcp.mcp_discovery",
            "reymen.mcp.mcp_reconnect",
            "reymen.mcp.mcp_tool",
            # ConversationLoop (CONVERSATION_SOR tool)
            "reymen.cereyan.conversation_loop",
            "reymen.web_ui",
            "reymen.windows.tor_otomasyonu",
            # Delegate Task (ThreadPoolExecutor-based sub-agent)
            "reymen.tools.delegate_task_tool",
            # HyperFrames Video Generation (HTML/CSS/JS -> MP4)
            "reymen.tools.hyperframes_tool",
            # Obsidian Vault Entegrasyonu (.md dosya okuma/yazma/arama)
            "reymen.tools.obsidian_tool",
        ]
        _yukleme_hatalari = []
        for mod_adi in moduller:
            try:
                mod = importlib.import_module(mod_adi)
                if hasattr(mod, "motor_kaydet"):
                    mod.motor_kaydet(self)
            except ImportError as _e:
                pass  # Modul yok â€” normal, sessiz gec
            except Exception as _e:
                _yukleme_hatalari.append(f"{mod_adi}: {type(_e).__name__}: {_e}")
        if _yukleme_hatalari:
            print(f"[Motor] {len(_yukleme_hatalari)} modul yukleme hatasi:")
            for h in _yukleme_hatalari[:5]:
                print(f"  âš  {h}")
            if len(_yukleme_hatalari) > 5:
                print(f"  ... ve {len(_yukleme_hatalari) - 5} hata daha")
        # Skill araÃ§larÄ± (cache'li)
        if self._skill_araclari_cache is None:
            self._skill_araclari_kaydet()
            self._skill_v2_araclari_kaydet()
            self._skill_araclari_cache = True
        # HafÄ±za araÃ§larÄ±
        self._hafiza_araclari_kaydet()
        # Provider sistem araÃ§larÄ± (Model Router + Failover)
        try:
            from reymen.ag.model_provider_router import router_al as _router_al

            _router = _router_al()
            self._plugin_arac_kaydet(
                "PROVIDER_DURUM",
                lambda provider="": str(
                    _router.provider_durum(provider if provider else None)
                ),
                "Provider durum raporu: tÃ¼m provider'larÄ±n saÄŸlÄ±k, hata, kara liste durumu. "
                "Parametre: provider (str, opsiyonel) â€” belirli bir provider adÄ± verilirse "
                "sadece onun durumunu gÃ¶sterir. BoÅŸ bÄ±rakÄ±lÄ±rsa tÃ¼mÃ¼nÃ¼ listeler.",
            )
            self._plugin_arac_kaydet(
                "MODEL_ROUTE",
                lambda model="", provider_override="": str(
                    _router.model_route(
                        model,
                        provider_override=provider_override
                        if provider_override
                        else None,
                    )
                ),
                "Modelâ†’Provider yÃ¶nlendirme kararÄ±. Parametreler: model (str, zorunlu) â€” "
                "model adÄ± (Ã¶r: deepseek-v4-flash); provider_override (str, opsiyonel) â€” "
                "provider'Ä± zorla belirtmek iÃ§in. DÃ¶ner: model, provider, api_tipi, base_url, "
                "failover_zinciri.",
            )
            self._plugin_arac_kaydet(
                "PROVIDER_SAGLIK",
                lambda: str(_router.tum_provider_saglik()),
                "TÃ¼m provider'larÄ±n saÄŸlÄ±k kontrolÃ¼nÃ¼ yapar. Her provider'a ping atar, "
                "canlÄ±lÄ±k durumlarÄ±nÄ± dÃ¶ndÃ¼rÃ¼r.",
            )
            self._plugin_arac_kaydet(
                "MODELLERI_LISTELE",
                lambda provider="": str(
                    _router.modelleri_listele(
                        provider_filtre=provider if provider else None,
                    )
                ),
                "TÃ¼m bilinen modelleri listeler. Parametre: provider (str, opsiyonel) â€” "
                "sadece belirli bir provider'daki modelleri filtrelemek iÃ§in.",
            )
            logger.info(
                "[Motor] Provider sistem araÃ§larÄ± kaydedildi: PROVIDER_DURUM, MODEL_ROUTE, PROVIDER_SAGLIK, MODELLERI_LISTELE"
            )
        except Exception as _e:
            logger.warning("[Motor] Provider araÃ§ kaydÄ± baÅŸarÄ±sÄ±z: %s", _e)
        # OAuth araÃ§larÄ± (P2) â€” Google/GitHub/Discord giriÅŸ ve durum
        try:
            from reymen.guvenlik.oauth_servis import OAuthServis

            _oauth_servis = OAuthServis()

            def _oauth_login(provider: str = "google") -> str:
                """OAUTH_LOGIN(provider) -> auth URL"""
                try:
                    url = _oauth_servis.login(provider)
                    return (
                        f"ğŸ” {provider.upper()} giriÅŸ URL'si:\n"
                        f"{url}\n\n"
                        f"ğŸ“Œ Bu URL'yi tarayÄ±cÄ±da aÃ§Ä±n, yetkilendirme yapÄ±n, "
                        f"ardÄ±ndan callback'ten gelen 'code' parametresi ile "
                        f"OAUTH_CALLBACK aracÄ±nÄ± kullanÄ±n."
                    )
                except Exception as e:
                    return f"[OAuth:Hata] {e}"

            def _oauth_durum(provider: str = "google") -> str:
                """OAUTH_DURUM(provider) -> token durumu"""
                try:
                    durum = _oauth_servis.durum(provider)
                    if not durum.get("var_mi"):
                        return (
                            f"âŒ {provider.upper()}: GiriÅŸ yapÄ±lmamÄ±ÅŸ.\n"
                            f"Ã–nce OAUTH_LOGIN({provider}) ile giriÅŸ yapÄ±n."
                        )
                    return (
                        f"ğŸ” {provider.upper()} Token Durumu:\n"
                        f"  Durum:     {'âœ… GeÃ§erli' if durum.get('gecerli_mi') else 'âŒ SÃ¼resi dolmuÅŸ'}\n"
                        f"  KullanÄ±cÄ±: {durum.get('display_name', '?')} ({durum.get('email', '?')})\n"
                        f"  BitiÅŸ:     {durum.get('expires_at', '?')}\n"
                        f"  Scope:     {durum.get('scope', '?')}"
                    )
                except Exception as e:
                    return f"[OAuth:Hata] {e}"

            self._plugin_arac_kaydet(
                "OAUTH_LOGIN",
                _oauth_login,
                "OAuth provider'a giriÅŸ yap â€” auth URL'si al. "
                "Parametre: provider (str, varsayÄ±lan: google) â€” google/github/discord. "
                "DÃ¶ndÃ¼rÃ¼len URL'yi tarayÄ±cÄ±da aÃ§Ä±n, callback'ten gelen code ile OAUTH_CALLBACK kullanÄ±n.",
            )
            self._plugin_arac_kaydet(
                "OAUTH_DURUM",
                _oauth_durum,
                "OAuth provider token durumunu gÃ¶ster. "
                "Parametre: provider (str, varsayÄ±lan: google) â€” google/github/discord. "
                "DÃ¶ner: token geÃ§erliliÄŸi, kullanÄ±cÄ± bilgisi, bitiÅŸ zamanÄ±.",
            )
            logger.info("[Motor] OAuth araÃ§larÄ± kaydedildi: OAUTH_LOGIN, OAUTH_DURUM")
        except Exception as _e:
            logger.warning("[Motor] OAuth araÃ§ kaydÄ± baÅŸarÄ±sÄ±z: %s", _e)
        # PluginYukleyici (ReYMeN seviyesi â€” plugin.yaml destegi)
        try:
            from reymen.sistem.plugin_loader import PluginYukleyici

            _py = PluginYukleyici(dizin=ROOT.parent / "sistem" / "plugins")
            _py.hepsini_yukle()
            _py.tool_pluginlerini_yukle()  # kind: tool pluginleri de yukle
            _py.motora_kaydet(self)
            self._plugin_yukleyici = _py
        except ImportError as _e:
            self._plugin_yukleyici = None
            pass  # plugin_loader yok
        except Exception as _e:
            self._plugin_yukleyici = None
            print(f"[Motor] PluginYukleyici baslatma hatasi: {_e}")

        # MCP Reconnect â€” heartbeat + otomatik yeniden baÄŸlanma
        # reymen.mcp modÃ¼lÃ¼ yukarÄ±da yÃ¼klendiÄŸinden mcp_reconnect zaten import edilebilir
        try:
            import asyncio
            from reymen.mcp.mcp_reconnect import (
                mcp_reconnect_baslat,
                mcp_reconnect_durumu,
            )

            # Mevcut event loop varsa onu kullan, yoksa yeni bir loop'ta baÅŸlat
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    loop.create_task(mcp_reconnect_baslat())
                else:
                    loop.run_until_complete(mcp_reconnect_baslat())
            except RuntimeError:
                # HiÃ§ event loop yok â€” arkaplan thread'de yeni loop baÅŸlat
                import threading

                def _reconnect_thread():
                    _loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(_loop)
                    try:
                        _loop.run_until_complete(mcp_reconnect_baslat())
                    except Exception as _e:
                        __import__("logging").getLogger(__name__).warning(
                            "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                        )
                    _loop.run_forever()

                t = threading.Thread(
                    target=_reconnect_thread, daemon=True, name="mcp-reconnect"
                )
                t.start()
                __import__("logging").getLogger(__name__).debug(
                    "[Motor] MCP Reconnect: arkaplan thread baÅŸlatÄ±ldÄ±"
                )
        except ImportError as _e:
            logger.warning("[Motor] Modul yuklenemedi (L727): %s", ImportError)
            pass
        except Exception as e:
            __import__("logging").getLogger(__name__).debug(
                "[Motor] MCP Reconnect baÅŸlatma hatasÄ± (Ã¶nemsiz): %s", e
            )

    def _skill_araclari_kaydet(self) -> None:
        """skill_utils modÃ¼lÃ¼nden SKILL_ araÃ§larÄ±nÄ± kaydet (v1 â€” geriye uyumluluk)."""
        try:
            from reymen.arac.skill_utils import (
                skill_ara,
                kategorileri_listele,
                skill_oku,
            )

            self._plugin_arac_kaydet(
                "SKILL_ARA",
                lambda sorgu="": str(skill_ara(sorgu)),
                "Skill veritabanÄ±nda ara",
            )
            self._plugin_arac_kaydet(
                "SKILL_KATEGORILER",
                lambda: str(kategorileri_listele()),
                "TÃ¼m skill kategorilerini listele",
            )
            self._plugin_arac_kaydet(
                "SKILL_OKU",
                lambda ad="": skill_oku(ad) or f"[Hata]: '{ad}' skill bulunamadÄ±",
                "Bir skill iÃ§eriÄŸini oku",
            )
        except ImportError as _e:
            logger.warning("[Motor] Modul yuklenemedi (L300): %s", ImportError)
            pass

    def _skill_v2_araclari_kaydet(self) -> None:
        """skill_utils v2/v3 araclari: aktivasyon, kategori, script, olustur, dogrula."""
        try:
            from reymen.arac.skill_utils import (
                skill_aktivat,
                kategori_skill_listele,
                skill_script_calistir,
                skill_script_yardim,
                skill_sayisi,
                skill_olustur,
                skill_dogrula,
                skill_index_yenile,
                skill_izin_verilen_araclar,
                skill_eval_ekle,
                skill_eval_listele,
            )

            def _aktivat_ve_izin_guncelle(ad: str = "") -> str:
                from reymen.cereyan.active_skill_tracker import aktif_skill_ayarla

                sonuc = skill_aktivat(ad)
                # allowed-tools: skill'in bildirdigi araclari gecici whitelist'e ekle
                try:
                    izinler = skill_izin_verilen_araclar(ad)
                    if izinler and hasattr(self, "ekstra_izin_araclar"):
                        self.ekstra_izin_araclar.update(izinler)
                except Exception as _e:
                    logger.warning("[Motor] except Exception (L321): %s", Exception)
                    pass
                # Aktif skill tracker'a kaydet (LLM context enjeksiyonu icin)
                try:
                    aktif_skill_ayarla(ad, sonuc)
                except Exception as _e:
                    __import__("logging").getLogger(__name__).warning(
                        "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                    )
                return sonuc

            self._plugin_arac_kaydet(
                "SKILL_AKTIVAT",
                _aktivat_ve_izin_guncelle,
                "Skill'i aktive et â€” tam icerigi ReAct baglamina yukle",
            )
            self._plugin_arac_kaydet(
                "SKILL_KATEGORI",
                lambda kat="": str(kategori_skill_listele(kat)),
                "Bir kategorideki skill listesini getir",
            )
            self._plugin_arac_kaydet(
                "SKILL_SCRIPT",
                lambda skill="", script="", arglar="": skill_script_calistir(
                    skill, script, arglar
                ),
                "Skill icindeki scripts/ dizinindeki bir dosyayi calistir",
            )
            self._plugin_arac_kaydet(
                "SKILL_OLUSTUR",
                lambda ad="", aciklama="", talimatlar="", kategori="": skill_olustur(
                    ad, aciklama, talimatlar, kategori
                ),
                "Spec uyumlu yeni skill olustur .ReYMeN/skills/ altinda",
            )
            self._plugin_arac_kaydet(
                "SKILL_DOGRULA",
                lambda ad="": skill_dogrula(ad),
                "Skill'i agentskills.io spec kurallarina gore dogrula",
            )
            self._plugin_arac_kaydet(
                "SKILL_INDEX_YENILE",
                lambda: f"[Index]: {skill_index_yenile(zorla=True)} skill guncellendi.",
                "FTS5 skill arama indexini yeniden olustur",
            )
            self._plugin_arac_kaydet(
                "SKILL_SCRIPT_YARDIM",
                lambda skill="", script="": skill_script_yardim(skill, script),
                "Script'i --help ile calistir, arayuz bilgisini al",
            )
            self._plugin_arac_kaydet(
                "SKILL_EVAL_EKLE",
                lambda ad="", prompt="", expected="", assertions="": skill_eval_ekle(
                    ad,
                    prompt,
                    expected,
                    assertions=[a.strip() for a in assertions.split("|") if a.strip()]
                    if assertions
                    else [],
                ),
                "Skill icin eval test case ekle (evals/evals.json)",
            )
            self._plugin_arac_kaydet(
                "SKILL_EVAL_LISTELE",
                lambda ad="": skill_eval_listele(ad),
                "Skill'in eval test case'lerini listele",
            )
            __import__("logging").getLogger(__name__).debug(
                "[Skill v4] %d skill yuklu.", skill_sayisi()
            )
        except ImportError as _e:
            logger.warning("[Motor] Modul yuklenemedi (L374): %s", ImportError)
            pass

    # â”€â”€ Plugin API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _plugin_arac_kaydet(
        self, ad: str, fonk: Any, aciklama: str = "", only_if_missing: bool = False
    ) -> None:
        """Plugin modÃ¼llerinin araÃ§ kaydetmesi iÃ§in ortak API."""
        if _REGISTRY:
            if only_if_missing and ad in _REGISTRY._tools:
                return
            _REGISTRY.kaydet(ad, fonk)

    # â”€â”€ Pydantic Entegrasyonu (opsiyonel, graceful degrade) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    _PYDANTIK_ENTEGRE = False
    try:
        from reymen.cereyan.pydantic_entegrasyonu import (
            validate_tool_call as _pydantic_validate,
            pydantic_aktif as _pydantic_aktif,
        )

        if _pydantic_aktif:
            _PYDANTIK_ENTEGRE = True
    except ImportError:
        logger.warning("[fix_01_sessiz_except] ImportError")

    # â”€â”€ Native Function Calling desteÄŸi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @trace_tool_call()
    def calistir_fc(self, arac: str, args: dict) -> str:
        """FC API'den gelen dict args â†’ mevcut calistir() kÃ¶prÃ¼sÃ¼.

        OpenAI tool_calls'taki {key: value} dict'ini, mevcut calistir()
        altyapÄ±sÄ±nÄ±n beklediÄŸi quoted-string ham_param formatÄ±na dÃ¶nÃ¼ÅŸtÃ¼rÃ¼r.
        Pydantic aktifse Ã§aÄŸrÄ± Ã¶ncesi args doÄŸrulamasÄ± yapar.

        DÃ¶nÃ¼ÅŸÃ¼m:
            {"dosya": "test.py", "icerik": "..."} â†’ '"test.py" "..."'

        Pydantic validasyon:
            - args doÄŸrulanÄ±r, hatalÄ± tipler dÃ¼zeltilir
            - Hata varsa LLM'ye geri bildirim gÃ¶nderilir
            - Graceful degrade: hatalÄ± args olduÄŸu gibi iletilir
        """
        # Pydantic validasyon (varsa)
        if self._PYDANTIK_ENTEGRE and args:
            try:
                validated = _pydantic_validate(arac, args)
                if validated.get("hata"):
                    logger.warning(
                        "[Pydantic] %s validasyon uyarÄ±sÄ±: %s",
                        arac,
                        validated["hata"],
                    )
                # DoÄŸrulanmÄ±ÅŸ args'i kullan
                args = validated.get("args", args)
            except Exception as e:
                logger.warning(
                    "[Pydantic] %s validasyon hatasÄ± (ignore): %s",
                    arac,
                    e,
                )

        if not args:
            return self.calistir(arac, "")
        parts = []
        for v in args.values():
            v_str = str(v)
            escaped = v_str.replace("\\", "\\\\").replace('"', '\\"')
            parts.append(f'"{escaped}"')
        return self.calistir(arac, " ".join(parts))

    def tools_schema_al(self, maks: int = 64) -> list:
        """OpenAI-uyumlu tools schema listesi Ã¼retir.

        GOREV_BITTI her zaman ilk sÄ±radadÄ±r (LLM gÃ¶revi bitirmek iÃ§in kullanÄ±r).
        Geri kalanlar ToolRegistry'den alÄ±nÄ±r; _meta'daki aÃ§Ä±klamalar dahil edilir.

        Returns:
            [{"type": "function", "function": {"name": ..., ...}}, ...]
        """
        schema: list = [
            {
                "type": "function",
                "function": {
                    "name": "GOREV_BITTI",
                    "description": (
                        "GÃ¶revi baÅŸarÄ±yla tamamladÄ±ÄŸÄ±nda Ã§aÄŸÄ±r. "
                        "YapÄ±lanlarÄ±n TÃ¼rkÃ§e Ã¶zetini 'ozet' parametresine yaz."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ozet": {
                                "type": "string",
                                "description": "YapÄ±lanlarÄ±n Ã¶zeti (2â€“5 cÃ¼mle)",
                            }
                        },
                        "required": ["ozet"],
                    },
                },
            }
        ]

        if not _REGISTRY:
            return schema

        for ad, _ in list(_REGISTRY._tools.items())[:maks]:
            if ad == "GOREV_BITTI":
                continue
            meta = _REGISTRY._meta.get(ad)
            aciklama = ""
            if isinstance(meta, dict):
                aciklama = meta.get("aciklama", "") or meta.get("description", "")
            if not aciklama:
                aciklama = ad.replace("_", " ").title()

            # Bilinen tool'lar icin ozel parametre semalari
            _OZEL_SCHEMALAR = {
                "WEB_ARA": {
                    "type": "object",
                    "properties": {
                        "sorgu": {
                            "type": "string",
                            "description": "Aranacak kelime veya cÃ¼mle",
                        }
                    },
                    "required": ["sorgu"],
                },
                "DOSYA_OKU": {
                    "type": "object",
                    "properties": {
                        "dosya_yolu": {
                            "type": "string",
                            "description": "Okunacak dosyanÄ±n tam yolu",
                        }
                    },
                    "required": ["dosya_yolu"],
                },
                "DOSYA_YAZ": {
                    "type": "object",
                    "properties": {
                        "dosya_yolu": {
                            "type": "string",
                            "description": "YazÄ±lacak dosyanÄ±n tam yolu",
                        },
                        "icerik": {
                            "type": "string",
                            "description": "Dosyaya yazÄ±lacak iÃ§erik",
                        },
                    },
                    "required": ["dosya_yolu", "icerik"],
                },
                "PYTHON_CALISTIR": {
                    "type": "object",
                    "properties": {
                        "kod": {
                            "type": "string",
                            "description": "Ã‡alÄ±ÅŸtÄ±rÄ±lacak Python kodu",
                        }
                    },
                    "required": ["kod"],
                },
                "KOMUT_CALISTIR": {
                    "type": "object",
                    "properties": {
                        "komut": {
                            "type": "string",
                            "description": "Ã‡alÄ±ÅŸtÄ±rÄ±lacak shell komutu",
                        }
                    },
                    "required": ["komut"],
                },
                "PROFIL_DEGISTIR": {
                    "type": "object",
                    "properties": {
                        "profil_adi": {
                            "type": "string",
                            "description": "GeÃ§ilecek profil adÄ±: reyment, dev, test, prod",
                        }
                    },
                    "required": ["profil_adi"],
                },
                "PROFIL_LISTELE": {"type": "object", "properties": {}, "required": []},
            }

            params = _OZEL_SCHEMALAR.get(
                ad,
                {
                    "type": "object",
                    "properties": {
                        "param": {
                            "type": "string",
                            "description": f"{ad} iÃ§in parametre",
                        }
                    },
                    "required": [],
                },
            )

            schema.append(
                {
                    "type": "function",
                    "function": {
                        "name": ad,
                        "description": aciklama[:200],
                        "parameters": params,
                    },
                }
            )
        return schema

    @property
    def _plugin_araclar(self) -> dict:
        """KayÄ±tlÄ± araÃ§larÄ±n salt-okunur dict gÃ¶rÃ¼nÃ¼mÃ¼."""
        return dict(_REGISTRY._tools) if _REGISTRY else {}

    def eylemi_ayristir(self, llm_cikti: str) -> Tuple[Optional[str], Optional[str]]:
        """Eylem: ARAC(...) veya EYLEM:\\nARAC(...) satÄ±rÄ±nÄ± yakalar."""
        # 1. Standart: "Eylem: ARAC(...)" veya "EYLEM:\\nARAC(...)"
        m = re.search(
            r"Eylem:\s*([A-Z_]+)\s*\((.*)\)", llm_cikti, re.DOTALL | re.IGNORECASE
        )
        if m:
            return m.group(1).strip().upper(), m.group(2).strip()

        # 2. Fallback: bilinen ARAC_ADI(...) dogrudan herhangi bir satÄ±rda
        _BILINEN = {
            "GOREV_BITTI",
            "DOSYA_OKU",
            "DOSYA_YAZ",
            "KOMUT_CALISTIR",
            "PYTHON_CALISTIR",
            "WEB_ARA",
            "TARAYICI_AC",
            "IC_GOZLEM",
            "HAFIZA_ARA",
            "PARALLEL_CALISTIR",
            "SKILL_ARA",
            "SKILL_AKTIVAT",
            "SKILL_KATEGORILER",
            "SKILL_SCRIPT",
            "ARAC_URET",
            "GUVENLI_CALISTIR",
            "PROFIL_DEGISTIR",
            "PROFIL_LISTELE",
            "DURUM_OKU",
            "DURUM_RAPOR",
            "ANALITIK_KAYDET",
            "ANALITIK_RAPOR",
            "ANALITIK_PANEL",
            "PROVIDER_KESFET",
            "HOT_RELOAD_BASLAT",
            "HOT_RELOAD_DURDUR",
            "HOT_RELOAD_DURUM",
            "PLUGIN_MARKET_LISTE",
            "PLUGIN_MARKET_ARAMA",
            "PLUGIN_MARKET_YUKLE",
            "PLUGIN_MARKET_BILGI",
            "TTS_KONUS",
            "TTS_SES_LISTE",
            "STT_DINLE",
            "GORUNTU_ANALIZ",
            "SESSION_ARA",
        }
        for satir in llm_cikti.splitlines():
            satir_s = satir.strip()
            m2 = re.match(r"([A-Z][A-Z_0-9]+)\s*\((.*)\)\s*$", satir_s)
            if m2 and m2.group(1) in _BILINEN:
                return m2.group(1), m2.group(2).strip()
            # Cok satirli: ARAC_ADI( ile baslayan satir â€” devamÄ± alt satirlarda
            m3 = re.match(r"([A-Z][A-Z_0-9]+)\s*\(", satir_s)
            if m3 and m3.group(1) in _BILINEN:
                idx = llm_cikti.find(satir_s)
                m4 = re.search(
                    r"([A-Z][A-Z_0-9]+)\s*\((.*?)\)", llm_cikti[idx:], re.DOTALL
                )
                if m4:
                    return m4.group(1), m4.group(2).strip()

        return None, None

    def _parametreleri_coz(self, ham: str) -> List[str]:
        return re.findall(r'"((?:[^"\\]|\\.)*)"', ham)

    # â”€â”€ Toolset gruplandirma (ReYMeN Agent mimarisi) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Hafiza araclari
    def _hafiza_araclari_kaydet(self) -> None:
        try:
            from reymen.hafiza.memory_agent import hafiza_kur, hafiza_sifirla

            self._plugin_arac_kaydet(
                "HAFIZA_DURUMU",
                lambda: str(hafiza_kur().info()),
                "Konusma hafiza durumunu goster",
            )
            self._plugin_arac_kaydet(
                "HAFIZA_TEMIZLE",
                lambda: (hafiza_sifirla(), "Hafiza temizlendi.")[1],
                "Konusma hafizasini temizle",
            )
            self._plugin_arac_kaydet(
                "HAFIZA_KAYDET",
                lambda: (hafiza_kur().save_memory(), "Hafiza kaydedildi.")[1],
                "Hafizayi JSON dosyasina kaydet",
            )
        except ImportError as _e:
            logger.warning("[Motor] Modul yuklenemedi (L518): %s", ImportError)
            pass

        # â”€â”€ Vektor bellek araclari â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        try:
            from reymen.hafiza.vektor_bellek import VektorBellek, vektor_bellek_al

            # Singleton VektorBellek instance'i
            _vb_global = vektor_bellek_al()

            self._plugin_arac_kaydet(
                "VECTOR_EKLE",
                lambda metin="", kategori="": _vb_global.ekle(
                    metin, {"kategori": kategori} if kategori else None
                )
                or "[Hata]: Metin bos olamaz",
                "Vektor bellege anlamsal kayit ekle. Parametreler: metin (str, zorunlu) â€” "
                "eklenecek metin; kategori (str, opsiyonel) â€” kayit kategorisi. "
                "Doner: kayit ID'si veya hata mesaji.",
            )
            self._plugin_arac_kaydet(
                "VECTOR_ARA",
                lambda sorgu="", k=5: str(
                    _vb_global.ara(sorgu, k=int(k) if str(k).isdigit() else 5)
                ),
                "Vektor belleginde anlamsal ara. Parametreler: sorgu (str, zorunlu) â€” "
                "arama sorgusu; k (int, opsiyonel, default=5) â€” kac sonuc donsun. "
                "Doner: [(id, metin, skor, metadata)] listesi.",
            )
            self._plugin_arac_kaydet(
                "VEKTOR_BELLEK",
                lambda islem="",
                metin="",
                sorgu="",
                kayit_id="",
                k=5: _vektor_bellek_arac(
                    _vb_global,
                    islem,
                    metin,
                    sorgu,
                    kayit_id,
                    int(k) if str(k).isdigit() else 5,
                ),
                "Vektor bellek yonetim araci. Parametreler:\n"
                "  - islem (str, zorunlu): 'ekle' | 'ara' | 'sil' | 'listele' | 'bilgi'\n"
                "  - metin (str, opsiyonel): eklenecek metin (islem=ekle icin)\n"
                "  - sorgu (str, opsiyonel): arama sorgusu (islem=ara icin)\n"
                "  - kayit_id (str, opsiyonel): silinecek kayit ID'si (islem=sil icin)\n"
                "  - k (int, opsiyonel, default=5): sonuc sayisi (islem=ara icin)\n"
                "Doner: isleme gore metin sonuc.",
            )
            logger.info(
                "[Motor] Vektor bellek araclari kaydedildi: VECTOR_EKLE, VECTOR_ARA, VEKTOR_BELLEK"
            )
        except ImportError as _e:
            logger.warning("[Motor] Vektor bellek araclari yuklenemedi: %s", _e)
            pass

        # â”€â”€ SelfHeal aracÄ± (otonom hata Ã§Ã¶zÃ¼mÃ¼) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        try:
            self._plugin_arac_kaydet(
                "SELF_HEAL",
                lambda hedef_hata_kod="": self._self_heal_calistir(hedef_hata_kod),
                "Otonom hata Ã§Ã¶zÃ¼mÃ¼. Bir Python hatasÄ±nÄ± analiz eder, "
                "OnceHafiza/LLM ile Ã§Ã¶zer, hafÄ±zaya kaydeder. "
                "Parametre: 'hedef|hata|kod' formatÄ±nda, | ile ayrÄ±lmÄ±ÅŸ. "
                "Doner: cozum kodu veya hata mesaji.",
            )
            logger.info("[Motor] SelfHeal araci kaydedildi: SELF_HEAL")
        except Exception as e:
            logger.warning("[Motor] SelfHeal kaydi basarisiz: %s", e)

        # â”€â”€ Session Search FTS5 AracÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        try:
            from reymen.cereyan.session_search import session_search_al as _ss_al

            _ss = _ss_al()
            self._plugin_arac_kaydet(
                "SESSION_ARA",
                lambda sorgu="", limit=10, session_id="": str(
                    _ss.search(
                        sorgu,
                        limit=int(limit) if str(limit).isdigit() else 10,
                        session_id=session_id if session_id else None,
                    )
                ),
                "Session mesajlarinda FTS5 tam metin aramasi yap. "
                "Parametreler: sorgu (str, zorunlu) â€” aranacak kelime/ifade; "
                "limit (int, opsiyonel, default=10) â€” kac sonuc donsun; "
                "session_id (str, opsiyonel) â€” sadece belirli bir oturumda ara. "
                "Doner: [{session_id, message, role, timestamp, rank}] JSON listesi. "
                "FTS5 syntax: 'kelime1 kelime2' -> AND, 'kelime1 OR kelime2' -> OR, "
                "'kelime*' -> prefix, '\"tam ifade\"' -> exact phrase.",
            )
            logger.info("[Motor] Session Search araci kaydedildi: SESSION_ARA")
        except ImportError as _e:
            logger.warning("[Motor] Session Search aracÄ± yuklenemedi: %s", _e)
            pass
        except Exception as _e:
            logger.warning("[Motor] Session Search kayit hatasi: %s", _e)
            pass

    TOOLSET_GRUPLARI = {
        # â”€â”€ Entry Point'ler (reymen_launcher.py Ã¼zerinden baÅŸlatma) â”€â”€
        #   reymen\bin\reymen.cmd       â†’  .cmd â†’ python reymen_launcher.py
        #   venv\Scripts\reymen.cmd     â†’  .cmd â†’ python reymen_launcher.py
        #   venv\Scripts\reymen.exe     â†’  .exe direkt (PyInstaller)
        #   ~/.local/bin/reymen.exe     â†’  .exe direkt (pip console_scripts)
        #   pyproject.toml              â†’  [project.scripts] reymen = "reymen_launcher:main"
        #
        "temel": {
            "KOMUT_CALISTIR",
            "PYTHON_CALISTIR",
            "DOSYA_YAZ",
            "DOSYA_OKU",
            "HAFIZA_ARA",
            "IC_GOZLEM",
            "PARALLEL_CALISTIR",
            "GOREV_BITTI",
            "PROFIL_DEGISTIR",
            "PROFIL_LISTELE",
        },
        "web": {"WEB_ARA", "TARAYICI_AC"},
        "iletisim": {
            "TELEGRAM_GONDER",
            "TELEGRAM_RESIM_GONDER",
            "TELEGRAM_STREAM_GONDER",
            "TELEGRAM_REACTION_EKLE",
            "TELEGRAM_PING",
        },
        "ekran": {
            "EKRAN_OKU",
            "EKRAN_NISAN",
            "EKRAN_TIKLA",
            "MAKRO_OYNAT",
            "UYG_ISLEM_CAGIR",
            "EKRAN_FOTOGRAF_CEK",
        },
        "dosya": {
            "PDF_OKU",
            "EXCEL_OKU",
            "CSV_OKU",
            "GORUNTU_ANALIZ",
            "DOSYA_ANALIZ",
            "PROJE_TARA",
        },
        "skill": {
            "SKILL_ARA",
            "SKILL_AKTIVAT",
            "SKILL_KATEGORILER",
            "SKILL_KATEGORI",
            "SKILL_SCRIPT",
            "SKILL_OLUSTUR",
            "SKILL_DOGRULA",
            "SKILL_INDEX_YENILE",
            "SKILL_SCRIPT_YARDIM",
            "SKILL_EVAL_EKLE",
            "SKILL_EVAL_LISTELE",
            "ACHIEVEMENTS_LISTE",
        },
        "faz6": {"ARAC_URET", "GUVENLI_CALISTIR"},
        "container": {
            "CONTAINER_DURUM",
            "CONTAINER_CALISTIR",
            "CONTAINER_IMAGE_HAZIRLA",
            "CONTAINER_MOD",
        },
        "claude": {
            "CLAUDE_YARDIM",
            "CLAUDE_ANALIZ",
            "CLAUDE_KOD_YAZ",
            "CLAUDE_HATA_AYIKLA",
            "CLAUDE_PLAN",
            "CLAUDE_REVIZE",
            "CLAUDE_DURUM",
        },
        "gorev": {
            "TODO",
            "CLARIFY",
            "EXECUTE_CODE",
            "TUI_BASLAT",
            "KANBAN_GUNCELLE",
            "KANBAN_OZET",
        },
        "hata": {
            "HATA_WATCH_BASLAT",
            "HATA_WATCH_DURDUR",
            "HATA_KOD_AL",
            "TERMINAL_HATA_PARSE",
            "COZUM_UYGULA",
        },
        "vektor": {"VECTOR_EKLE", "VECTOR_ARA", "VEKTOR_BELLEK"},
        "session": {"SESSION_ARA"},
        "tor": {
            "TOR_AC",
            "TOR_KAPAT",
            "TOR_FORM_DOLDUR",
            "TOR_LOGIN",
            "TOR_KAYIT",
            "TOR_SIPARIS",
        },
        "kopru": {"KOPRU_BASLAT", "KOPRU_DURDUR", "KOPRU_DURUM"},
        "watchdog": {"WATCHDOG_KONTROL"},
    }

    # â”€â”€ check_fn: araÃ§ kullanÄ±labilirlik kontrol fonksiyonlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # ReYMeN Agent: her araÃ§ check_fn ile LLM listesine girip girmeyeceÄŸini belirler
    # Burada en sÄ±k kullanÄ±lan araÃ§lar iÃ§in ortam kontrolleri tanÄ±mlanÄ±r
    _ARAC_CHECK_FNS: dict = {}  # ad -> callable; False dÃ¶nerse araÃ§ LLM listesinden Ã§Ä±kar

    @classmethod
    def check_fn_kaydet(cls, arac_adi: str, fn: Any) -> None:
        """Bir araca kullanÄ±labilirlik kontrol fonksiyonu baÄŸla."""
        cls._ARAC_CHECK_FNS[arac_adi] = fn

    def musait_araclar(self, toolset: Optional[str] = None) -> set:
        """check_fn'i geÃ§en kullanÄ±labilir araÃ§larÄ±n kÃ¼mesini dÃ¶ndÃ¼r.

        Hem motor._ARAC_CHECK_FNS hem de tool_registry'deki check_fn'leri sorgular.
        (ReYMeN Agent ToolRegistry.get_definitions pattern'i)

        Args:
            toolset: Sadece bu gruptaki araÃ§larÄ± filtrele (None = hepsi).

        Returns:
            KullanÄ±labilir araÃ§ adlarÄ± kÃ¼mesi.
        """
        if toolset:
            aday = self.TOOLSET_GRUPLARI.get(toolset, set())
        else:
            aday = {a for g in self.TOOLSET_GRUPLARI.values() for a in g}

        sonuc = set()
        for ad in aday:
            # 1. Motor'un kendi check_fn'ini kontrol et
            fn = self._ARAC_CHECK_FNS.get(ad)
            if fn is not None and not fn():
                continue  # Motor blokladi

            # 2. tool_registry'deki check_fn'i kontrol et
            try:
                from reymen.arac.tool_registry import tool_registry as _reg

                if not _reg.check_fn_kontrol_et(ad):
                    continue  # Registry blokladi
            except (ImportError, AttributeError) as _e:
                pass  # Registry yoksa sadece motor'a guven

            sonuc.add(ad)
        return sonuc

    def toolset_tanimi_al(self, araÃ§lar: Optional[set] = None) -> str:
        """LLM sistem promptu icin kisa toolset tanimi uret.

        Args:
            araÃ§lar: Dahil edilecek araÃ§ seti (None = tÃ¼m musait araÃ§lar).
        """
        if araÃ§lar is None:
            araÃ§lar = self.musait_araclar()

        satirlar = []
        for grup, uyeler in self.TOOLSET_GRUPLARI.items():
            aktif = araÃ§lar & uyeler
            if aktif:
                satirlar.append(f"[{grup.upper()}] {', '.join(sorted(aktif))}")
        return "\n".join(satirlar)

    def tum_arac_tanimini_al(self) -> str:
        """Toolset + registry'deki dinamik araclari tek seferde al.

        Her turda cagrilir, boylece yeni eklenen araclar
        (plugin, skill, dinamik_arac_uretici ile uretilen)
        LLM sistem promptunda gorunur.

        Returns:
            str: Gruplandirilmis arac listesi (toolset + dinamik ek).
        """
        tanim = self.toolset_tanimi_al()
        # Registry'de olup toolset'te olmayan araclari ekle
        if _REGISTRY and hasattr(_REGISTRY, "_tools"):
            toolset_araclari = {a for g in self.TOOLSET_GRUPLARI.values() for a in g}
            ek = set(_REGISTRY._tools.keys()) - toolset_araclari
            if ek:
                if tanim:
                    tanim += "\n"
                tanim += "[DINAMIK] " + ", ".join(sorted(ek))
        return tanim

    # AraÃ§ â†’ kullanÄ±cÄ±ya gÃ¶sterilen durum mesajÄ±
    _DURUM_MESAJLARI = {
        "WEB_ARA": "Ä°nternette aranÄ±yor...",
        "TARAYICI_AC": "Sayfa aÃ§Ä±lÄ±yor...",
        "DOSYA_OKU": "Dosya okunuyor...",
        "DOSYA_YAZ": "Dosya yazÄ±lÄ±yor...",
        "KOMUT_CALISTIR": "Komut Ã§alÄ±ÅŸtÄ±rÄ±lÄ±yor...",
        "PYTHON_CALISTIR": "Python kodu Ã§alÄ±ÅŸtÄ±rÄ±lÄ±yor...",
        "HAFIZA_ARA": "HafÄ±zada aranÄ±yor...",
        "EKRAN_OKU": "Ekran okunuyor (OCR)...",
        "EKRAN_TIKLA": "Ekran Ã¶ÄŸesine tÄ±klanÄ±yor...",
        "TELEGRAM_GONDER": "Mesaj gÃ¶nderiliyor...",
        "TELEGRAM_PING": "Telegram baglantisi test ediliyor...",
        "TELEGRAM_STREAM_GONDER": "Stream mesaj gonderiliyor...",
        "TELEGRAM_REACTION_EKLE": "Reaction ekleniyor...",
        "TELEGRAM_RESIM_GONDER": "Resim gÃ¶nderiliyor...",
        "EKRAN_FOTOGRAF_CEK": "Ekran fotoÄŸrafÄ± Ã§ekiliyor...",
        "PARALLEL_CALISTIR": "AraÃ§lar paralel Ã§alÄ±ÅŸtÄ±rÄ±lÄ±yor...",
        "PDF_OKU": "PDF okunuyor...",
        "EXCEL_OKU": "Excel dosyasÄ± okunuyor...",
        "CSV_OKU": "CSV dosyasÄ± okunuyor...",
        "GORUNTU_ANALIZ": "GÃ¶rÃ¼ntÃ¼ analiz ediliyor (LLaVA)...",
        "DOSYA_ANALIZ": "Dosya analiz ediliyor...",
        "PROJE_TARA": "Proje dosyalari taranÄ±yor...",
        "SKILL_AKTIVAT": "Skill yukleniyor...",
        "SKILL_KATEGORI": "Skill kategorisi listeleniyor...",
        "SKILL_SCRIPT": "Skill scripti calistiriliyor...",
        "SKILL_OLUSTUR": "Yeni skill olusturuluyor...",
        "SKILL_DOGRULA": "Skill dogrulanÄ±yor (spec kontrol)...",
        "SKILL_INDEX_YENILE": "Skill FTS5 indexi yenileniyor...",
        "SKILL_SCRIPT_YARDIM": "Script arayuzu ogreniyor (--help)...",
        "SKILL_EVAL_EKLE": "Skill eval test case ekleniyor...",
        "SKILL_EVAL_LISTELE": "Skill eval listesi getiriliyor...",
        "ARAC_URET": "Yeni arac uretiliyor (Code-As-A-Tool)...",
        "GUVENLI_CALISTIR": "Guvenli sandbox'ta kod calistiriliyor...",
        "CONTAINER_DURUM": "Container sandbox durumu sorgulaniyor...",
        "CONTAINER_CALISTIR": "Container'da komut calistiriliyor...",
        "CONTAINER_IMAGE_HAZIRLA": "Container image hazirlaniyor...",
        "CONTAINER_MOD": "Container sandbox modu degistiriliyor...",
        "HATA_WATCH_BASLAT": "Hata watchdog baslatiliyor (ekran izleme)...",
        "HATA_WATCH_DURDUR": "Hata watchdog durduruluyor...",
        "HATA_KOD_AL": "Hata kodu aliniyor...",
        "TERMINAL_HATA_PARSE": "Terminal ciktisi hata icin taranÄ±yor...",
        "COZUM_UYGULA": "Cozum uygulaniyor (patch)...",
        "TOR_AC": "Tor Browser baslatiliyor...",
        "TOR_KAPAT": "Tor Browser kapatiliyor...",
        "TOR_FORM_DOLDUR": "Form dolduruluyor...",
        "TOR_LOGIN": "Siteye giris yapiliyor...",
        "TOR_KAYIT": "Yeni kayit olusturuluyor...",
        "TOR_SIPARIS": "Siparis veriliyor...",
        "CUA_EKRAN_KULLAN": "CUA: Ekran vizyon+koordinat+eylem...",
        "CUA_ARACLARI_TARA": "CUA bilesenleri taranÄ±yor...",
        "ACHIEVEMENTS_LISTE": "Rozetler listeleniyor...",
        "PROXY_AYARLA": "Proxy yapilandiriliyor...",
        "CLARIFY": "Talep netleÅŸtiriliyor...",
        "EXECUTE_CODE": "Python kodu Ã§alÄ±ÅŸtÄ±rÄ±lÄ±yor...",
        "TUI_BASLAT": "Terminal UI baslatiliyor...",
        "TELEGRAM_STREAM": "Telegram'a stream mesaj gonderiliyor...",
        "TELEGRAM_REACT": "Telegram reaction ekleniyor...",
        "KOPRU_BASLAT": "Telegram Bridge baslatiliyor (Bot1/Bot2)...",
        "KOPRU_DURDUR": "Telegram Bridge durduruluyor...",
        "KOPRU_DURUM": "Telegram Bridge durumu sorgulaniyor...",
        "PROFIL_DEGISTIR": "Profil degistiriliyor...",
        "PROFIL_LISTELE": "Profiller listeleniyor...",
        "SESSION_ARA": "Session mesajlarinda araniyor...",
    }

    def _durum_goster(self, arac: str, params: List[str]) -> None:
        """AraÃ§ baÅŸlamadan Ã¶nce kullanÄ±cÄ±ya durum mesajÄ± yaz."""
        mesaj = self._DURUM_MESAJLARI.get(arac)
        if mesaj:
            ozet = (params[0] if params else "")[:60]
            print(f"  [*] {mesaj}" + (f" [{ozet}]" if ozet else ""), flush=True)

    _RISKLI_ARACLAR: frozenset = frozenset(
        {
            "KOMUT_CALISTIR",
            "PYTHON_CALISTIR",
            "TARAYICI_AC",
            "EKRAN_TIKLA",
            "MAKRO_OYNAT",
            "ARAC_URET",
            "CUA_EKRAN_KULLAN",
        }
    )

    @trace_tool_call()
    def calistir(self, arac: str, ham_param: str) -> str:
        params = self._parametreleri_coz(ham_param)

        # AraÃ§ durum mesajÄ±
        self._durum_goster(arac, params)

        # SayaÃ§: kullanÄ±lan araÃ§larÄ± kaydet (achievement iÃ§in)
        try:
            from tools.achievements import _listeye_ekle

            _listeye_ekle("tools_used.json", arac)
        except Exception as _e:
            logger.warning("[Motor] except Exception (L713): %s", Exception)
            pass

        # check_fn: araÃ§ musait mi?
        _check = self._ARAC_CHECK_FNS.get(arac)
        if _check is not None and not _check():
            return f"[{arac}]: Bu araÃ§ bu ortamda kullanÄ±lamÄ±yor (gereksinim eksik)."

        # HITL: riskli araclarda onay
        _izinli = arac in getattr(self, "ekstra_izin_araclar", set())
        if (
            arac in self._RISKLI_ARACLAR
            and not _izinli
            and getattr(self, "onay_fonksiyonu", None)
        ):
            ozet = (params[0] if params else "")[:120]
            if not self.onay_fonksiyonu(arac, ozet):
                return f"[Ä°ptal]: KullanÄ±cÄ± '{arac}' eylemini reddetti."

        # HATA_COZUCU araÃ§larÄ± â€” Registry/Plugin Ã¶ncesi erken kontrol
        if arac in (
            "HATA_WATCH_BASLAT",
            "HATA_WATCH_DURDUR",
            "HATA_KOD_AL",
            "TERMINAL_HATA_PARSE",
            "COZUM_UYGULA",
        ):
            try:
                from reymen.cereyan.hata_cozucu import (
                    HataWatchdog,
                    HataKoduUretici,
                    TerminalHataParser,
                    CozumUygulayici,
                )

                if not hasattr(self, "_hata_watchdog"):
                    self._hata_watchdog = HataWatchdog()
                    self._hata_kod = HataKoduUretici()
                    self._hata_terminal = TerminalHataParser()
                    self._hata_cozum = CozumUygulayici(self._hata_kod)
                if arac == "HATA_WATCH_BASLAT":
                    self._hata_watchdog.baslat()
                    return "[HataWatchdog] Baslatildi."
                if arac == "HATA_WATCH_DURDUR":
                    self._hata_watchdog.durdur()
                    return "[HataWatchdog] Durduruldu."
                if arac == "HATA_KOD_AL":
                    kayit = self._hata_kod.kaydet(
                        params[0] if params else "Bilinmeyen hata"
                    )
                    return (
                        f"[HataKod] {kayit.kod}: [{kayit.kategori}] {kayit.ozet}\n"
                        f"Claude'a yapistir: {kayit.kod}"
                    )
                if arac == "TERMINAL_HATA_PARSE":
                    sonuc = self._hata_terminal.parse(params[0] if params else "")
                    if sonuc["hata_var"]:
                        return f"[Terminal] {sonuc['hata_sayisi']} hata.\nIlki: {sonuc['ozet']}"
                    return "[Terminal] Hata bulunamadi."
                if arac == "COZUM_UYGULA":
                    sonuc = self._hata_cozum.uygula(params[0] if params else "")
                    if sonuc["basarili"]:
                        return f"[Cozum] Basarili: {sonuc['patch_sonuc']}"
                    return f"[Cozum] Basarisiz: {sonuc['mesaj']}"
            except Exception as e:
                return f"[Hata]: hata_cozucu: {e}"

        # SELF_HEAL aracÄ± â€” otonom hata Ã§Ã¶zÃ¼mÃ¼
        if arac == "SELF_HEAL":
            try:
                from reymen.core.self_heal import SelfHeal

                parts = [p.strip() for p in ham_param.split("|", 2)]
                hedef = parts[0] if len(parts) > 0 else "bilinmeyen"
                hata = parts[1] if len(parts) > 1 else ""
                kod = parts[2] if len(parts) > 2 else ""
                if not hata:
                    return "[SelfHeal] âŒ Hata mesajÄ± gerekli. Format: hedef|hata|kod"
                heal = SelfHeal()
                sonuc = heal.coz(hedef, hata, kod)
                if sonuc["basarili"]:
                    return (
                        f"[SelfHeal] âœ… Ã‡Ã¶zÃ¼ldÃ¼ (kaynak: {sonuc['kaynak']}, "
                        f"deneme: {sonuc['deneme_sayisi']})\n"
                        f"Ã‡Ã¶zÃ¼m:\n{sonuc['cozum']}"
                    )
                else:
                    return (
                        f"[SelfHeal] âŒ Ã‡Ã¶zÃ¼lemedi "
                        f"({sonuc['deneme_sayisi']} deneme)\n"
                        f"Hata: {sonuc['hata']}"
                    )
            except Exception as e:
                logger.exception("[Motor] SelfHeal hatasÄ±")
                return f"[SelfHeal] âŒ Ä°Ã§ hata: {e}"

        # TOR_OTOMASYONU araÃ§larÄ±
        if arac in (
            "TOR_AC",
            "TOR_KAPAT",
            "TOR_FORM_DOLDUR",
            "TOR_LOGIN",
            "TOR_KAYIT",
            "TOR_SIPARIS",
        ):
            try:
                from reymen.windows.tor_otomasyonu import (
                    TorBrowserKontrol,
                    FormDoldurucu,
                    OtomasyonAkislari,
                    tor_baslat,
                    tor_kapat,
                )

                if not hasattr(self, "_tor_browser"):
                    self._tor_browser = None
                    self._tor_akislar = None

                if arac == "TOR_AC":
                    sonuc = tor_baslat(ham_param.strip() or None)
                    if "[Tor] Browser baslatildi" in sonuc:
                        from reymen.windows.tor_otomasyonu import (
                            _aktif_tor,
                            _aktif_akislar,
                        )

                        self._tor_browser = _aktif_tor
                        self._tor_akislar = _aktif_akislar
                    return sonuc
                if arac == "TOR_KAPAT":
                    sonuc = tor_kapat()
                    self._tor_browser = None
                    self._tor_akislar = None
                    return sonuc

                if not self._tor_browser:
                    return "[Tor]: Once TOR_AC ile baslatin."

                if arac == "TOR_FORM_DOLDUR":
                    import json

                    alanlar = json.loads(ham_param) if ham_param.startswith("{") else {}
                    if alanlar and self._tor_browser.driver:
                        sonuc = FormDoldurucu.doldur(self._tor_browser.driver, alanlar)
                        if sonuc["basarisiz"]:
                            # 3 asamali NisanBulucu fallback
                            try:
                                from reymen.arac.araclar_nisan import NisanBulucu

                                nisan = NisanBulucu()
                                for alan in sonuc["basarisiz"]:
                                    deger = alanlar.get(alan, "")
                                    if deger:
                                        # Asama 1: DOM ile alani bul
                                        if (
                                            self._tor_browser
                                            and self._tor_browser.driver
                                        ):
                                            nisan_bul = nisan.bul(
                                                alan,
                                                driver=self._tor_browser.driver,
                                                metin_alternatif=deger,
                                            )
                                        else:
                                            nisan_bul = nisan.bul(
                                                alan, metin_alternatif=deger
                                            )
                                        if nisan_bul.get("asama", 0) > 0:
                                            logger.info(
                                                "[Tor] Nisan asama %d ile '%s' bulundu (%d,%d)",
                                                nisan_bul["asama"],
                                                alan,
                                                nisan_bul.get("x", 0),
                                                nisan_bul.get("y", 0),
                                            )
                            except Exception as ocr_e:
                                logger.warning("[Tor] Nisan fallback hatasi: %s", ocr_e)
                            return f"[Form] Basarili: {sonuc['basarili']}, Basarisiz: {sonuc['basarisiz']}"
                        return f"[Form] Basarili: {sonuc['basarili']}, Basarisiz: {sonuc['basarisiz']}"
                    return "[Tor]: JSON formatinda alanlar gonderin."
                if arac == "TOR_LOGIN":
                    import json

                    data = json.loads(ham_param) if ham_param.startswith("{") else {}
                    if data:
                        s = self._tor_akislar.login(
                            data.get("url", ""),
                            data.get("kullanici", ""),
                            data.get("sifre", ""),
                        )
                        return (
                            "[Login] Basarili."
                            if s["basarili"]
                            else f"[Login] Basarisiz: {s['hata']}"
                        )
                    return '[Tor]: {\\"url\\":\\"...\\", \\"kullanici\\":\\"...\\", \\"sifre\\":\\"...\\"}'
                if arac == "TOR_KAYIT":
                    # HITL: insan onayi zorunlu
                    try:
                        from reymen.cereyan.insan_arayuzu import HumanInterface

                        izin = HumanInterface().onay_iste(
                            "TOR_KAYIT",
                            "Yeni uyelik olusturma talebi. Onayliyor musun?",
                        )
                        if not izin:
                            return "[Kayit] REDDEDILDI: Kullanici onay vermedi."
                    except Exception:
                        logger.warning(
                            "[Tor] insan_arayuzu HITL calismadi, onay atlandi."
                        )
                    import json

                    data = json.loads(ham_param) if ham_param.startswith("{") else {}
                    if data:
                        s = self._tor_akislar.kayit_ol(
                            data.get("url", ""), data.get("bilgiler", {})
                        )
                        return (
                            "[Kayit] Basarili."
                            if s["basarili"]
                            else f"[Kayit] Basarisiz: {s['hata']}"
                        )
                    return '[Tor]: {\\"url\\":\\"...\\", \\"bilgiler\\":{...}}'
                if arac == "TOR_SIPARIS":
                    # HITL: insan onayi zorunlu
                    try:
                        from reymen.cereyan.insan_arayuzu import HumanInterface

                        izin = HumanInterface().onay_iste(
                            "TOR_SIPARIS", "Siparis verme talebi. Onayliyor musun?"
                        )
                        if not izin:
                            return "[Siparis] REDDEDILDI: Kullanici onay vermedi."
                    except Exception:
                        logger.warning("[Tor] insan_arayuzu bulunamadi, onay atlandi.")
                    import json

                    data = json.loads(ham_param) if ham_param.startswith("{") else {}
                    if data:
                        s = self._tor_akislar.siparis_ver(
                            data.get("url", ""),
                            data.get("urun", ""),
                            data.get("adres", {}),
                        )
                        return (
                            "[Siparis] Basarili."
                            if s["basarili"]
                            else f"[Siparis] Basarisiz: {s['hata']}"
                        )
                    return '[Tor]: {\\"url\\":\\"...\\", \\"urun\\":\\"...\\", \\"adres\\":{...}}'
            except Exception as e:
                return f"[Hata]: tor_otomasyonu: {e}"

        # Paralel araÃ§ Ã§alÄ±ÅŸtÄ±rma
        if arac == "PARALLEL_CALISTIR":
            return self._paralel_calistir(params[0] if params else "")

        # 1. ToolRegistry ile dene â€” startswith ile dogru kontrol
        if _REGISTRY:
            _registry_sonuc = _REGISTRY.calistir(arac, *params)
            if not _registry_sonuc.startswith("[Bilinmeyen arac]"):
                self._hook_tetikle(arac, params, _registry_sonuc)
                return _registry_sonuc

        # 2. PluginManager ile dene
        if _PLUGIN_MGR:
            try:
                plugin_sonuc = _PLUGIN_MGR.run(arac.lower())
                self._hook_tetikle(arac, params, plugin_sonuc)
                return str(plugin_sonuc)
            except KeyError as _e:
                logger.warning("[Motor] Anahtar bulunamadi (L873): %s", KeyError)
                pass

        # 3. Fallback: if/else zinciri
        sonuc = self._fallback_calistir(arac, params)
        self._hook_tetikle(arac, params, sonuc)
        return sonuc

    def _paralel_calistir(self, tanim: str) -> str:
        """PARALLEL_CALISTIR("ARAC1(\\"p1\\") | ARAC2(\\"p2\\")") â€” araÃ§larÄ± paralel Ã§alÄ±ÅŸtÄ±rÄ±r.

        Pipe (|) ile ayrÄ±lmÄ±ÅŸ araÃ§ Ã§aÄŸrÄ±larÄ±nÄ± ThreadPoolExecutor ile eÅŸzamanlÄ± yÃ¼rÃ¼tÃ¼r.
        SonuÃ§lar sÄ±rasÄ±yla dÃ¶ner.
        """
        # Pipe ile bÃ¶lme â€” iÃ§ tÄ±rnak iÃ§indeki | karakterlerine dikkat et
        # Basit regex: ARAC_ADI(...) formunu yakala
        cagrilar = re.findall(r"([A-Z_]+)\s*\(((?:[^()]*|\((?:[^()]*)\))*)\)", tanim)
        if not cagrilar:
            # Pipe ile bÃ¶lÃ¼p her parÃ§ayÄ± eylemi_ayristir ile Ã§Ã¶zmeyi dene
            parcalar = [p.strip() for p in tanim.split("|") if p.strip()]
            cagrilar = []
            for parca in parcalar:
                m = re.match(r"([A-Z_]+)\s*\((.*)\)", parca.strip(), re.DOTALL)
                if m:
                    cagrilar.append((m.group(1).strip(), m.group(2).strip()))

        if not cagrilar:
            return "[PARALLEL_CALISTIR] Hicbir gecerli arac cagr'i bulunamadi."

        sonuclar = {}
        hata_sayisi = 0
        _ARAC_TIMEOUT = int(getattr(self, "config", {}).get("parallel_timeout", 30))

        def _cagri_yap(idx: int, arac_adi: str, ham: str) -> Tuple[int, str, str]:
            try:
                return idx, arac_adi, self.calistir(arac_adi, ham)
            except Exception as e:
                return idx, arac_adi, f"[Hata]: {e}"

        try:
            with ThreadPoolExecutor(max_workers=min(len(cagrilar), 8)) as executor:
                gelecekler = {
                    executor.submit(_cagri_yap, i, a, h): (i, a)
                    for i, (a, h) in enumerate(cagrilar)
                }
                for gelecek in as_completed(
                    gelecekler, timeout=_ARAC_TIMEOUT * len(cagrilar)
                ):
                    i_ref, arac_ref = gelecekler[gelecek]
                    try:
                        idx, arac_adi, sonuc = gelecek.result(timeout=_ARAC_TIMEOUT)
                    except TimeoutError:
                        idx, arac_adi, sonuc = (
                            i_ref,
                            arac_ref,
                            f"[Hata]: {arac_ref} zaman asimi ({_ARAC_TIMEOUT}s).",
                        )
                    except Exception as _e:
                        idx, arac_adi, sonuc = i_ref, arac_ref, f"[Hata]: {_e}"
                    sonuclar[idx] = (arac_adi, sonuc)
                    if "[Hata]" in sonuc:
                        hata_sayisi += 1
        except TimeoutError:
            eksik = set(range(len(cagrilar))) - set(sonuclar.keys())
            for i in eksik:
                a_adi = cagrilar[i][0] if i < len(cagrilar) else "?"
                sonuclar[i] = (a_adi, f"[Hata]: Zaman asimi â€” tamamlanamadi.")
                hata_sayisi += 1

        satirlar = [f"[PARALLEL_CALISTIR] {len(cagrilar)} arac, {hata_sayisi} hata:"]
        for i in range(len(cagrilar)):
            arac_adi, sonuc = sonuclar.get(i, ("?", "[Sonuc yok]"))
            satirlar.append(f"\n--- {arac_adi} ---\n{sonuc[:500]}")

        return "\n".join(satirlar)

    def _hook_tetikle(self, arac: str, params: List[str], sonuc: str) -> None:
        """AraÃ§ Ã§alÄ±ÅŸtÄ±ktan sonra async hooklarÄ± tetikle."""
        hata = "[Hata]" in sonuc or "[hata]" in sonuc.lower() if sonuc else False
        olay = "TOOL_ERROR" if hata else "TOOL_CALLED"

        if self._hooks:
            self._hooks.tetikle(
                olay, arac=arac, params=params, sonuc=sonuc[:200] if sonuc else ""
            )

        # conversation_loop hook'larÄ±nÄ± da tetikle (entegrasyon)
        try:
            from reymen.cereyan.hook_dispatcher import (
                arac_cagri_tetikle as _ac_tetikle,
                arac_sonuc_tetikle as _as_tetikle,
            )

            _ac_tetikle(arac_adi=arac, argumanlar={"params": params})
            _as_tetikle(
                arac_adi=arac, sonuc=str(sonuc)[:200] if sonuc else "", sure_sn=0.0
            )
        except Exception as _e:
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] %%s: %%s", type(_e).__name__, _e
            )

    def _fallback_calistir(self, arac: str, params: List[str]) -> str:
        """Yedek if/else zinciri (registry calismazsa)."""
        if arac == "KOMUT_CALISTIR":
            komut = params[0] if params else ""
            if not komut:
                return "[Hata]: Komut gerekli"
            # Container sandbox aktifse container'da calistir
            try:
                from reymen.guvenlik.container_sandbox import (
                    komut_calistir as _container_komut,
                )

                # Motor config'inden container ayarlarini gecir
                _container_cfg = None
                if hasattr(self, "config") and self.config:
                    from reymen.guvenlik.container_sandbox import ContainerConfig

                    _container_cfg = ContainerConfig.from_dict(self.config)
                _cikti = _container_komut(komut, config=_container_cfg)
                # Sandbox aktifse ve Docker varsa direkt container ciktisini dondur
                # Sandbox kapaliysa veya Docker yoksa _local_calistir calisir (hatasiz dondur)
                # Sadece "[ContainerSandbox]" ile baslayan hatalarda terminale dus
                if not _cikti.startswith("[ContainerSandbox]"):
                    return _cikti
                # Container hatasi â€” normal terminale dus
                logger.warning(
                    "[Motor] Container sandbox hatasi, normal terminale dusuluyor: %.100s",
                    _cikti,
                )
            except ImportError:
                pass  # container_sandbox yoksa normal terminal
            except Exception as _ce:
                logger.warning(
                    "[Motor] Container sandbox hatasi (fallback terminal): %s", _ce
                )
            # Fallback: normal terminal
            return (
                self.terminal.calistir(komut)
                if self.terminal
                else "[Hata]: Terminal yok"
            )
        if arac == "PYTHON_CALISTIR":
            # FAZ 6: once guvenli sandbox dene
            try:
                from reymen.guvenlik.guvenli_sandbox import guvenli_calistir

                return guvenli_calistir(params[0] if params else "", timeout=30)
            except ImportError as _e:
                logger.warning("[Motor] Modul yuklenemedi (L960): %s", ImportError)
                pass
            if izole_python_calistir:
                return izole_python_calistir(params[0] if params else "")
            return "[Hata]: Sandbox yok"
        if arac == "GUVENLI_CALISTIR":
            try:
                from reymen.guvenlik.guvenli_sandbox import guvenli_calistir

                mod = params[1] if len(params) >= 2 else "oto"
                return guvenli_calistir(
                    params[0] if params else "", mod=mod, timeout=30
                )
            except ImportError:
                return "[Hata]: guvenli_sandbox modulu yuklu degil."
        if arac == "ARAC_URET":
            try:
                from reymen.cereyan.dinamik_arac_uretici import arac_uret_ve_calistir

                problem = params[0] if params else ""
                test_girdisi = params[1] if len(params) >= 2 else ""
                provider = getattr(self, "_provider_ref", None)
                return arac_uret_ve_calistir(
                    problem,
                    motor=self,
                    provider=provider,
                    test_girdisi=test_girdisi,
                    max_deneme=2,
                )
            except ImportError:
                return "[Hata]: dinamik_arac_uretici modulu yuklu degil."
        if arac == "GOREV_BITTI":
            # Achievement kontrolÃ¼
            try:
                from tools.achievements import check_achievements

                yeni = check_achievements(gorev_tamamlandi=True)
                if yeni:
                    return "__GOREV_BITTI__\n" + "\n".join(
                        f"{r['emoji']} {r['name']} kazanÄ±ldÄ±! ğŸ‰" for r in yeni
                    )
            except Exception as _e:
                logger.warning("[Motor] except Exception (L991): %s", Exception)
                pass
            return "__GOREV_BITTI__"
        if arac == "DURUM_BILDIR":
            try:
                durum = params[0] if params else "idle"
                mesaj = params[1] if len(params) >= 2 else ""
                return f"[Durum] {durum}" + (f": {mesaj}" if mesaj else "")
            except Exception as e:
                return f"[Durum] Hata: {e}"
        if arac == "DURUM_RAPOR":
            try:
                import time as _t

                satirlar = [
                    "[Durum Raporu]",
                    f"  Zaman: {_t.strftime('%Y-%m-%d %H:%M:%S')}",
                    f"  Motor: calisiyor",
                    f"  Kayitli arac: {len(dir(self))}",
                ]
                # Provider referansi varsa durumunu ekle
                if getattr(self, "_provider_ref", None):
                    satirlar.append(f"  Provider: bagli")
                else:
                    satirlar.append(f"  Provider: bagli degil")
                # Plugin var mi
                if _PLUGIN_MGR:
                    satirlar.append(f"  Plugin: aktif")
                else:
                    satirlar.append(f"  Plugin: yok")
                return "\n".join(satirlar)
            except Exception as e:
                return f"[DurumRaporu] Hata: {e}"
        if arac == "WATCHDOG_KONTROL":
            """Bot process canlÄ±lÄ±k kontrolÃ¼. Ã–lÃ¼yse restart dener."""
            import subprocess
            import json as _json

            try:
                sonuc = subprocess.run(
                    [
                        "powershell.exe",
                        "-NoProfile",
                        "-Command",
                        "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'bot\\.py' } | "
                        "Select-Object ProcessId | ConvertTo-Json -Compress",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                cikti = sonuc.stdout.strip()
                if cikti and cikti != "null":
                    try:
                        data = _json.loads(cikti)
                        if isinstance(data, dict):
                            data = [data]
                        pidler = [
                            str(p.get("ProcessId")) for p in data if p.get("ProcessId")
                        ]
                        if pidler:
                            return (
                                f"__WATCHDOG__ Bot calisiyor. PID: {', '.join(pidler)}"
                            )
                    except _json.JSONDecodeError as _e:
                        logger.warning(
                            "[Motor] JSON parse hatasi (L1043): %s",
                            _json.JSONDecodeError,
                        )
                        pass
                # Bot Ã¶lÃ¼ â€” restart dene
                _py = sys.executable
                _bot = ROOT / "bot.py"
                subprocess.Popen(
                    [_py, str(_bot)],
                    cwd=str(ROOT),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                return "__WATCHDOG__ Bot calismiyordu, yeniden baslatildi."
            except Exception as e:
                return f"__WATCHDOG__ Hata: {e}"
        if arac == "GATEWAY_DURUM_YAZ":
            """gateway_state.json yaz â€” durum ve isteÄŸe baÄŸlÄ± hata mesajÄ±."""
            durum = params[0] if params else "running"
            hata = params[1] if len(params) >= 2 else ""
            _gateway_durum_yaz(durum, hata)
            return f"__GATEWAY_DURUM_YAZ: {durum}__"
        if arac == "TELEGRAM_TOKEN_TEST":
            """TELEGRAM_BOT_TOKEN'in geÃ§erliliÄŸini test et."""
            import urllib.request as _ur
            import json as _js

            token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
            if not token:
                return "[TOKEN] TELEGRAM_BOT_TOKEN .env'de bulunamadi"
            try:
                resp = _ur.urlopen(
                    f"https://api.telegram.org/bot{token}/getMe", timeout=10
                )
                data = _js.loads(resp.read().decode())
                if data.get("ok"):
                    bot = data["result"]
                    return (
                        f"[TOKEN] âœ… {bot['first_name']} (@{bot['username']}) â€” gecerli"
                    )
                return f"[TOKEN] âŒ {data.get('description', 'bilinmeyen hata')}"
            except Exception as e:
                return f"[TOKEN] âŒ Baglanti hatasi: {e}"
        if arac == "PROXY_AYARLA":
            try:
                from proxy import ProxyEngine, ProxyConfig

                _proxy_engine = ProxyEngine(ProxyConfig())
                komut = (params[0] if params else "status").lower()
                if komut == "start":
                    sonuc = _proxy_engine.start()
                elif komut == "stop":
                    sonuc = _proxy_engine.stop()
                elif komut == "status":
                    sonuc = _proxy_engine.status()
                else:
                    sonuc = {"hata": f"Bilinmeyen komut: {komut}"}
                return str(sonuc)
            except Exception as e:
                return f"[Proxy] Hata: {e}"
        if arac == "ACHIEVEMENTS_LISTE":
            from tools.achievements import rozet_listele

            return rozet_listele()
        if arac == "DOSYA_YAZ":
            if len(params) < 2:
                return "[Hata]: DOSYA_YAZ iki parametre ister."
            ad, icerik = params[0], params[1].replace("\\n", "\n")
            guvenli, mesaj = _dosya_guvenli(ad)
            if not guvenli:
                return f"[Guvenlik]: {mesaj}"
            gecerli, yol = _yol_dogrula(ad)
            if not gecerli:
                return f"[Guvenlik]: {yol}"
            # LSP: yazma Ã¶ncesi baseline (sessiz, hata vermez)
            try:
                from agent.lsp.file_operations_lsp import (
                    lsp_diagnostics_before_write,
                    lsp_diagnostics_after_write,
                    format_diagnostics,
                )

                lsp_diagnostics_before_write(ad)
            except ImportError as _e:
                logger.warning("[Motor] Modul yuklenemedi (L1115): %s", ImportError)
                pass
            # DosyayÄ± yaz
            with open(ad, "w", encoding="utf-8") as f:
                f.write(icerik)
            # LSP: yazma sonrasÄ± diagnostik
            lsp_notu = ""
            try:
                diags = lsp_diagnostics_after_write(ad)
                if diags:
                    lsp_notu = "\n" + format_diagnostics(diags)
            except Exception as _e:
                logger.warning("[Motor] except Exception (L1126): %s", Exception)
                pass
            return f"[Tamam]: {ad} yazÄ±ldÄ± ({len(icerik)} karakter).{lsp_notu}"
        if arac == "DOSYA_OKU":
            dosya = params[0] if params else ""
            if not os.path.exists(dosya):
                return f"[Hata]: {dosya} bulunamadi."
            gecerli, mesaj = _yol_dogrula(dosya)
            if not gecerli:
                return f"[Guvenlik]: {mesaj}"
            with open(dosya, "r", encoding="utf-8") as f:
                return f"[Dosya icerigi]:\n{f.read()}"
        if arac == "HAFIZA_ARA":
            if self.hafiza is None:
                return "[Hafiza]: Bagli degil."
            from reymen.hafiza.vektorel_hafiza import anlamsal_hafiza_ara

            return anlamsal_hafiza_ara(self.hafiza, params[0] if params else "")
        if arac == "WEB_ARA":
            from reymen.arac.araclar_web import web_ara

            return web_ara(params[0] if params else "")
        if arac == "TELEGRAM_GONDER":
            # ReYMeN Iletisim katmani uzerinden gonder (varsa)
            try:
                from reymen_iletisim import iletisim_hazir, iletisim_al

                if iletisim_hazir():
                    ileti = iletisim_al()
                    ileti.gonder(params[0] if params else "", kanal="telegram")
                    return f"[TELEGRAM_GONDER]: Iletisim katmani uzerinden gonderildi."
            except Exception as _e:
                logger.warning("[Motor] except Exception (L1154): %s", Exception)
                pass
            # Fallback: tools.send_message_tool
            from tools.send_message_tool import telegram_gonder

            tg = self.config.get("telegram", {})
            return telegram_gonder(
                params[0] if params else "",
                tg.get("token", ""),
                tg.get("chat_id", "6328823909"),
            )
        if arac == "TELEGRAM_STREAM_GONDER":
            try:
                from gateway.platforms.telegram import send_stream as _send_stream

                chat_id = (
                    params[1]
                    if len(params) > 1
                    else os.environ.get("TELEGRAM_CHAT_ID", "6328823909")
                )
                sonuc = _send_stream(
                    chat_id, params[0] if params else "", parse_mode="HTML"
                )
                if sonuc.get("durum") == "basarili":
                    return f"[TELEGRAM_STREAM_GONDER]: Stream mesaj gonderildi ({sonuc.get('chunk_sayisi',1)} chunk)"
                return f"[TELEGRAM_STREAM_GONDER]: Hata â€” {sonuc.get('hata', 'bilinmiyor')}"
            except Exception as e:
                return f"[TELEGRAM_STREAM_GONDER]: Hata â€” {e}"
        if arac == "TELEGRAM_REACTION_EKLE":
            try:
                from gateway.platforms.telegram import set_reaction as _set_reaction

                chat_id = (
                    params[1]
                    if len(params) > 1
                    else os.environ.get("TELEGRAM_CHAT_ID", "6328823909")
                )
                mesaj_id = int(params[0]) if params else 0
                emoji = params[2] if len(params) > 2 else "\U0001f44d"
                sonuc = _set_reaction(chat_id, mesaj_id, emoji)
                if sonuc.get("durum") == "basarili":
                    return f"[TELEGRAM_REACTION_EKLE]: Reaction eklendi: {emoji}"
                return f"[TELEGRAM_REACTION_EKLE]: Hata â€” {sonuc.get('hata', 'bilinmiyor')}"
            except Exception as e:
                return f"[TELEGRAM_REACTION_EKLE]: Hata â€” {e}"
        if arac == "TELEGRAM_PING":
            try:
                from gateway.platforms.telegram import ping as _ping

                canli = _ping()
                return f"[TELEGRAM_PING]: {'Baglanti basarili' if canli else 'Baglanti basarisiz (token yok veya API erisilemez)'}"
            except Exception as e:
                return f"[TELEGRAM_PING]: Hata â€” {e}"
        if arac == "TELEGRAM_RESIM_GONDER":
            from tools.send_message_tool import telegram_resim_gonder

            tg = self.config.get("telegram", {})
            dosya_yolu = params[0] if params else ""
            return telegram_resim_gonder(
                dosya_yolu, tg.get("token", ""), tg.get("chat_id", "6328823909")
            )
        if arac == "ILETISIM_BASLAT":
            try:
                from reymen_iletisim import iletisim_kur, iletisim_hazir

                iletisim_kur()
                if iletisim_hazir():
                    return "[ILETISIM] ReYMeN Iletisim Katmani baslatildi."
                return "[ILETISIM] Baslatma basarisiz."
            except Exception as e:
                return f"[ILETISIM] Hata: {e}"
        if arac == "ILETISIM_DURDUR":
            try:
                from reymen_iletisim import iletisim_durdur

                iletisim_durdur()
                return "[ILETISIM] ReYMeN Iletisim Katmani durduruldu."
            except Exception as e:
                return f"[ILETISIM] Hata: {e}"
        if arac == "ILETISIM_DURUM":
            try:
                from reymen_iletisim import iletisim_hazir, iletisim_al

                if not iletisim_hazir():
                    return "[ILETISIM] Calismiyor."
                ileti = iletisim_al()
                return ileti.durum_text()
            except Exception as e:
                return f"[ILETISIM] Hata: {e}"
        if arac == "KANBAN_EKLE":
            baslik = params[0] if len(params) > 0 else ""
            aciklama = params[1] if len(params) > 1 else ""
            from ReYMeN_cli.kanban import kanban_add

            return kanban_add(baslik, aciklama)
        if arac == "KANBAN_LISTE":
            from ReYMeN_cli.kanban import kanban_list

            return kanban_list()
        if arac == "KANBAN_CLAIM":
            gorev_id = params[0] if len(params) > 0 else ""
            atanan = params[1] if len(params) > 1 else "ajan"
            from ReYMeN_cli.kanban import kanban_claim

            return kanban_claim(gorev_id, atanan)
        if arac == "KANBAN_COMPLETE":
            gorev_id = params[0] if len(params) > 0 else ""
            sonuc = params[1] if len(params) > 1 else ""
            from ReYMeN_cli.kanban import kanban_complete

            return kanban_complete(gorev_id, sonuc)
        if arac == "KANBAN_HEARTBEAT":
            gorev_id = params[0] if len(params) > 0 else ""
            from ReYMeN_cli.kanban import kanban_heartbeat

            return kanban_heartbeat(gorev_id)
        if arac == "KANBAN_FAIL":
            gorev_id = params[0] if len(params) > 0 else ""
            neden = params[1] if len(params) > 1 else "belirtilmedi"
            from ReYMeN_cli.kanban import kanban_fail

            return kanban_fail(gorev_id, neden)
        if arac == "KANBAN_GUNCELLE":
            gorev_id = params[0] if len(params) > 0 else ""
            if len(params) == 1:
                return "[Kanban] KANBAN_GUNCELLE icin en az 2 parametre gerekli."
            elif len(params) >= 3:
                # 3 parametre: id, baslik, aciklama
                baslik = params[1]
                aciklama = params[2]
                from ReYMeN_cli.kanban import kanban_update

                return kanban_update(gorev_id, baslik, aciklama)
            else:
                # 2 parametre: id, yeni_durum
                yeni_durum = params[1]
                from ReYMeN_cli.kanban import kanban_move

                return kanban_move(gorev_id, yeni_durum)
        if arac == "KANBAN_OZET":
            from ReYMeN_cli.kanban import kanban_stats

            return kanban_stats()
        if arac == "TARAYICI_AC":
            from reymen.arac.araclar_tarayici import TarayiciKontrol

            return TarayiciKontrol().sayfa_ac_ve_oku(params[0] if params else "")
        if arac == "EKRAN_TIKLA":
            if not self._ekran:
                from reymen.arac.araclar_ekran import EkranOCRTikla

                self._ekran = EkranOCRTikla()
            yazi = params[0] if params else ""
            hangi = (
                int(params[1])
                if len(params) >= 2 and params[1].lstrip("-").isdigit()
                else 0
            )
            return self._ekran.yaziyi_bul_ve_tikla(yazi, hangi=hangi)
        if arac == "EKRAN_OKU":
            if not self._ekran:
                from reymen.arac.araclar_ekran import EkranOCRTikla

                self._ekran = EkranOCRTikla()
            return self._ekran.ekran_metnini_oku()
        if arac == "EKRAN_FOTOGRAF_CEK":
            import subprocess, os

            py3 = sys.executable
            script = os.path.join(os.path.dirname(__file__), "screenshot_bot.py")
            if os.path.exists(script):
                r = subprocess.run(
                    [py3, script], capture_output=True, text=True, timeout=30
                )
                if r.returncode == 0:
                    return "[EKRAN_FOTOGRAF_CEK]: " + r.stdout.strip()
                return f"[EKRAN_FOTOGRAF_CEK]: Hata: {r.stderr[:300]}"
            return "[EKRAN_FOTOGRAF_CEK]: screenshot_bot.py bulunamadi."
        if arac == "MAKRO_OYNAT":
            from tools.macro import oynat

            return oynat(params[0] if params else "")
        if arac == "UYG_ISLEM_CAGIR":
            from reymen.hafiza.uygulama_hafizasi import UygulamaHafizasi

            uh = UygulamaHafizasi()
            if len(params) < 2:
                return "[Hata]: UYG_ISLEM_CAGIR iki parametre ister."
            adimlar = uh.islem_cagir(params[0], params[1])
            if adimlar:
                return f"[UygHafiza]: {params[0]} - {params[1]}\n" + "\n".join(adimlar)
            return f"[UygHafiza]: '{params[1]}' kaydi yok."
        # FAZ 4 H7 â€” Dosya analiz araÃ§larÄ±
        if arac == "PDF_OKU":
            from reymen.arac.araclar_dosya_analiz import pdf_oku

            return pdf_oku(params[0] if params else "")
        if arac == "EXCEL_OKU":
            from reymen.arac.araclar_dosya_analiz import excel_oku

            sayfa = params[1] if len(params) >= 2 else ""
            return excel_oku(params[0] if params else "", sayfa=sayfa)
        if arac == "CSV_OKU":
            from reymen.arac.araclar_dosya_analiz import csv_oku

            ayirici = params[1] if len(params) >= 2 else ","
            return csv_oku(params[0] if params else "", ayirici=ayirici)
        if arac == "GORUNTU_ANALIZ":
            from reymen.arac.araclar_dosya_analiz import goruntu_analiz

            soru = params[1] if len(params) >= 2 else ""
            return goruntu_analiz(params[0] if params else "", soru=soru)
        if arac == "DOSYA_ANALIZ":
            from reymen.arac.araclar_dosya_analiz import dosya_analiz

            ek = params[1] if len(params) >= 2 else ""
            return dosya_analiz(params[0] if params else "", ek_parametre=ek)
        if arac == "PROJE_TARA":
            import os, json

            kok = os.path.dirname(os.path.abspath(__file__))
            py_dosyalar = []
            toplam_boyut = 0
            for kokdizini, altklasorler, dosyalar in os.walk(kok):
                # .ReYMeN, __pycache__, .git gibi gizli klasÃ¶rleri atla
                altklasorler[:] = [
                    d
                    for d in altklasorler
                    if not d.startswith(".") and d != "__pycache__"
                ]
                for f in dosyalar:
                    if f.endswith(".py"):
                        tam = os.path.join(kokdizini, f)
                        boyut = os.path.getsize(tam)
                        py_dosyalar.append((os.path.relpath(tam, kok), boyut))
                        toplam_boyut += boyut
            py_dosyalar.sort()
            ozet = {
                "toplam_py": len(py_dosyalar),
                "toplam_boyut_kb": round(toplam_boyut / 1024, 1),
                "dosyalar": py_dosyalar[:100],  # ilk 100
            }
            return f"[PROJE_TARA]: {json.dumps(ozet, ensure_ascii=False, indent=2)}"
        # â”€â”€ CUA (Computer Use Agent) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if arac == "CUA_EKRAN_KULLAN":
            if not _CUA_MEVCUT:
                return "[Hata]: cua_motor_araci modulu yuklu degil."
            hedef = params[0] if params else ""
            return CUA_EKRAN_KULLAN(hedef)
        if arac == "CUA_ARACLARI_TARA":
            if not _CUA_MEVCUT:
                return "[Hata]: cua_motor_araci modulu yuklu degil."
            kok = params[0] if params else "."
            return CUA_ARACLARI_TARA(kok)
        # â”€â”€ TUI (Terminal UI) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if arac == "TUI_BASLAT":
            try:
                import subprocess
                import sys

                reymentui_path = Path(__file__).parent / "reymentui"
                if not reymentui_path.exists():
                    return "[TUI] reymentui/ dizini bulunamadi."
                # Node.js ile TUI'yi baslat
                npm_script = params[0] if params else ""
                if npm_script == "build":
                    cmd = ["npm", "run", "build"]
                else:
                    cmd = ["npm", "start"]
                subprocess.Popen(
                    cmd,
                    cwd=str(reymentui_path),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return f"[TUI] reymentui baslatildi (npm {'start' if not npm_script else npm_script})"
            except Exception as e:
                return f"[TUI] Baslatma hatasi: {e}"
        # â”€â”€ Gateway AraÃ§larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if arac == "GATEWAY_BASLAT":
            try:
                from gateway.run import GatewayRunner

                filtre = params[0].split(",") if params and params[0] else None
                # Thread'de Ã§alÄ±ÅŸtÄ±r (ana dÃ¶ngÃ¼ bloke etmesin)
                import threading as _gt

                self._gateway_runner = GatewayRunner(polling_interval=5.0)
                _gt.Thread(
                    target=self._gateway_runner.calistir,
                    args=(filtre,),
                    daemon=True,
                    name="gateway-thread",
                ).start()
                import time as _gt_time

                _gt_time.sleep(1.5)  # baÅŸlangÄ±Ã§ iÃ§in bekle
                ozet = self._gateway_runner.durum_ozeti()
                return (
                    f"[GATEWAY_BASLAT] Gateway baslatildi. "
                    f"Platform: {ozet['aktif_platform']}/{ozet['platform_sayisi']} aktif"
                )
            except Exception as e:
                return f"[GATEWAY_BASLAT] Hata: {e}"
        if arac == "GATEWAY_DURDUR":
            try:
                if hasattr(self, "_gateway_runner") and self._gateway_runner:
                    sebep = params[0] if params else "komut"
                    self._gateway_runner.durdur(sebep=sebep)
                    self._gateway_runner = None
                    return "[GATEWAY_DURDUR] Gateway durduruldu."
                return "[GATEWAY_DURDUR] Gateway calismiyor."
            except Exception as e:
                return f"[GATEWAY_DURDUR] Hata: {e}"
        if arac == "GATEWAY_RESTART":
            try:
                from gateway.restart import platform_kaydet, restart_all

                # Mevcut platformlarÄ± restart.py'ye kaydet
                from gateway.platforms import platform_listele, platform_al

                for ad in platform_listele():
                    bilgi = platform_al(ad)
                    if bilgi:
                        platform_kaydet(
                            ad,
                            bilgi.get("baslat", lambda: None),
                            bilgi.get("durdur", lambda: None),
                        )
                bekleme = (
                    float(params[0])
                    if params and params[0].replace(".", "").isdigit()
                    else 1.0
                )
                sonuclar = restart_all(bekleme=bekleme)
                basarili = sum(1 for v in sonuclar.values() if v)
                toplam = len(sonuclar)
                return f"[GATEWAY_RESTART] {basarili}/{toplam} platform yeniden baslatildi."
            except Exception as e:
                return f"[GATEWAY_RESTART] Hata: {e}"
        if arac == "GATEWAY_DURUM":
            try:
                from gateway.status import read_runtime_status

                durum = read_runtime_status()
                if not durum:
                    return "[GATEWAY_DURUM] Gateway calismiyor (durum dosyasi yok)."
                satirlar = [
                    "[Gateway Durumu]",
                    f"  Durum: {durum.get('gateway_state', '?')}",
                    f"  PID: {durum.get('pid', '?')}",
                    f"  Baslangic: {durum.get('updated_at', '?')[:19]}",
                ]
                platformlar = durum.get("platforms", {})
                if platformlar:
                    satirlar.append(f"  Platformlar ({len(platformlar)}):")
                    for p_ad, p_bilgi in platformlar.items():
                        p_durum = p_bilgi.get("state", "?")
                        satirlar.append(f"    - {p_ad}: {p_durum}")
                # GatewayRunner'dan ek bilgi
                if hasattr(self, "_gateway_runner") and self._gateway_runner:
                    runner_ozet = self._gateway_runner.durum_ozeti()
                    satirlar.append(
                        f"  Aktif: {runner_ozet['aktif_platform']}/{runner_ozet['platform_sayisi']}"
                    )
                    satirlar.append(f"  Hata: {runner_ozet['hata_sayisi']}")
                return "\n".join(satirlar)
            except Exception as e:
                return f"[GATEWAY_DURUM] Hata: {e}"

        # ALT_AJAN araÃ§larÄ±
        if arac in ("ALT_AJAN_GOREVLENDIR", "ALT_AJAN_DURUM", "ALT_AJAN_IPTAL"):
            try:
                from reymen.cereyan.alt_ajan import AltAjanKoordinatÃ¶rÃ¼

                if not hasattr(self, "_alt_ajan"):
                    self._alt_ajan = AltAjanKoordinatÃ¶rÃ¼()
                if arac == "ALT_AJAN_GOREVLENDIR":
                    import json

                    try:
                        gorev_data = (
                            json.loads(ham_param)
                            if isinstance(ham_param, str)
                            and ham_param.strip().startswith("{")
                            else {"hedef": ham_param}
                        )
                    except json.JSONDecodeError:
                        gorev_data = {"hedef": ham_param}
                    hedef = gorev_data.get("hedef", ham_param)
                    tip = gorev_data.get("tip", "decorator")
                    sonuc = self._alt_ajan.gorevlendir(hedef, tip=tip)
                    return f"[ALT_AJAN] Gorev baslatildi: {sonuc}"
                if arac == "ALT_AJAN_DURUM":
                    durum = (
                        self._alt_ajan.durum_raporu()
                        if hasattr(self._alt_ajan, "durum_raporu")
                        else "Durum bilgisi alinamadi"
                    )
                    return f"[ALT_AJAN] {durum}"
                if arac == "ALT_AJAN_IPTAL":
                    self._alt_ajan.iptal_et()
                    return "[ALT_AJAN] Tum gorevler iptal edildi."
            except Exception as e:
                return f"[ALT_AJAN] Hata: {e}"

        # CLARIFY aracÄ±
        if arac == "CLARIFY":
            try:
                from tools.clarify_tool import run as clarify_run

                soru = params[0] if len(params) > 0 else ""
                sec_str = params[1] if len(params) > 1 and params[1] else ""
                varsayilan = params[2] if len(params) > 2 else ""
                secenekler = (
                    [s.strip() for s in sec_str.split("|") if s.strip()]
                    if sec_str
                    else None
                )
                return clarify_run(
                    soru=soru, secenekler=secenekler, varsayilan=varsayilan
                )
            except Exception as e:
                return f"[CLARIFY HATASI] {e}"

        # EXECUTE_CODE aracÄ±
        if arac == "EXECUTE_CODE":
            try:
                from tools.execute_code_tool import run as exec_run

                kod = params[0] if len(params) > 0 else ""
                timeout = (
                    int(params[1])
                    if len(params) > 1 and params[1].strip().isdigit()
                    else 30
                )
                calisma_dizini = params[2] if len(params) > 2 else ""
                return exec_run(kod=kod, timeout=timeout, calisma_dizini=calisma_dizini)
            except Exception as e:
                return f"[EXECUTE_CODE HATASI] {e}"

        # PROFIL_DEGISTIR â€” aktif profili deÄŸiÅŸtir
        if arac == "PROFIL_DEGISTIR":
            if not _PROFILE_MGR:
                return "[Profil] HATA: Profil yoneticisi yuklu degil."
            profil_adi = params[0] if params else ""
            if not profil_adi:
                return '[Profil] HATA: Profil adi gerekli. Kullanim: PROFIL_DEGISTIR("profil_adi")'
            return _PROFILE_MGR.profil_degistir(profil_adi)

        # PROFIL_LISTELE â€” tÃ¼m profilleri listele
        if arac == "PROFIL_LISTELE":
            if not _PROFILE_MGR:
                return "[Profil] HATA: Profil yoneticisi yuklu degil."
            return _PROFILE_MGR.profil_listele()

        return f"[Hata]: Bilinmeyen araÃ§ '{arac}'."

    def _cevabi_temizle(self, cevap: str) -> str:
        """Ã‡Ä±ktÄ±yÄ± PII/sÄ±rlardan temizle: Ã¶nce API key/token, sonra PII."""
        if not cevap:
            return cevap
        if _agent_temizle:
            cevap = _agent_temizle(cevap)
        if callable(_pii_temizle):
            cevap = _pii_temizle(cevap)
        return cevap

    def _context_sikistir(self, gecmis: list) -> list:
        """Uzun konuÅŸma geÃ§miÅŸini sÄ±kÄ±ÅŸtÄ±r."""
        if _COMPRESSOR and len(gecmis) > 15:
            return _COMPRESSOR.sikistir(gecmis)
        return gecmis

    def _cache_kontrol(self, prompt: str, sistem: str = "") -> Optional[str]:
        """Tekrarlanan promptlarÄ± cache'den dÃ¶ndÃ¼r."""
        if _CACHE:
            return _CACHE.al(sistem, [{"role": "user", "content": prompt}])
        return None

    def _cache_kaydet(self, prompt: str, yanit: str, sistem: str = "") -> None:
        """YanÄ±tÄ± cache'e kaydet."""
        if _CACHE:
            _CACHE.ekle(sistem, [{"role": "user", "content": prompt}], yanit)

    # â”€â”€ Otonom GÃ¶rev Ã‡Ã¶zÃ¼cÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _llm_fix_iste(self, hata_msg: str, kod: str, dosya_adi: str = "") -> str:
        """LLM'e hatayÄ± gÃ¶nder, dÃ¼zeltilmiÅŸ kodu al.

        Ä°yileÅŸtirmeler:
        - Dosya adÄ± context'e eklenir
        - Hata tipi Ã§Ä±karÄ±lÄ±r ve eklenir
        - Token limiti (4000 char kod, 2000 char hata)
        """
        from reymen.core.model_adapter import get_active_adapter

        a = get_active_adapter()

        # Hata tipini Ã§Ä±kar (ilk satÄ±rdan)
        hata_tipi = ""
        if hata_msg:
            ilk_satir = hata_msg.strip().split("\n")[0]
            if ":" in ilk_satir:
                hata_tipi = ilk_satir.split(":")[0].strip()

        # Kod ve hatayÄ± kÄ±salt (token limiti)
        kod_kisa = kod[:4000] if len(kod) > 4000 else kod
        hata_kisa = hata_msg[:2000] if len(hata_msg) > 2000 else hata_msg

        dosya_bilgisi = f"Dosya: {dosya_adi}\n" if dosya_adi else ""

        return a.complete(
            f"Bu Python kodu ÅŸu hatayÄ± verdi:\n\n"
            f"{dosya_bilgisi}"
            f"HATA TÄ°PÄ°: {hata_tipi}\n"
            f"HATA:\n{hata_kisa}\n\n"
            f"KOD:\n{kod_kisa}\n\n"
            "GÃ¶revi:\n"
            "1. HatanÄ±n kaynaÄŸÄ±nÄ± belirle\n"
            "2. DÃ¼zelt\n"
            "3. Sadece Ã§alÄ±ÅŸan Python kodunu dÃ¶ndÃ¼r â€” aÃ§Ä±klama yok, markdown yok, ``` yok"
        )

    @staticmethod
    def _fix_dogrula(fix_path: Path) -> tuple:
        """Fix'i doÄŸrula. DÃ¶ner: (baÅŸarÄ±lÄ±_mÄ±, stderr).

        Ä°yileÅŸtirmeler:
        - sys.executable kullan (doÄŸru Python)
        - stderr dÃ¶ndÃ¼r (hata ayÄ±klama iÃ§in)
        """
        import subprocess
        import sys

        r = subprocess.run(
            [sys.executable, str(fix_path)], capture_output=True, text=True, timeout=120
        )
        return r.returncode == 0, r.stderr

    def script_calistir(self, script_path: str) -> bool:
        """Python script Ã§alÄ±ÅŸtÄ±r, hata alÄ±rsa SelfHeal ile Ã§Ã¶z.

        SelfHeal v2 entegrasyonu:
        1. Script Ã§alÄ±ÅŸtÄ±r (subprocess)
        2. Hata varsa â†’ SelfHeal.script_coz() tetikle
        3. SelfHeal: imza â†’ hafÄ±za â†’ LLM â†’ subprocess doÄŸrulama â†’ kaydet
        4. Ã‡Ã¶zÃ¼m baÅŸarÄ±lÄ±ysa fix'i Ã§alÄ±ÅŸtÄ±r
        5. DeÄŸilse False dÃ¶n
        """
        path = Path(script_path)
        if not path.exists():
            return False

        import subprocess
        import sys

        for deneme in range(1, 4):
            r = subprocess.run(
                [sys.executable, str(path)], capture_output=True, text=True, timeout=120
            )
            if r.returncode == 0:
                return True

            stderr = r.stderr
            logger.info(
                "[script_calistir] âŒ Hata (deneme %d/3): %.80s", deneme, stderr[:80]
            )

            # SelfHeal ile Ã§Ã¶z
            try:
                from reymen.core.self_heal import SelfHeal

                heal = SelfHeal(max_deneme=1)  # her denemede 1 LLM Ã§aÄŸrÄ±sÄ±
                sonuc = heal.script_coz(script_path, stderr)

                if sonuc["basarili"]:
                    # Fix baÅŸarÄ±lÄ± â€” fix dosyasÄ±nÄ± kullan
                    path = Path(sonuc["fix_path"])
                    logger.info(
                        "[script_calistir] âœ… SelfHeal Ã§Ã¶zdÃ¼ (deneme %d, kaynak: %s)",
                        deneme,
                        sonuc["kaynak"],
                    )
                else:
                    logger.warning(
                        "[script_calistir] âŒ SelfHeal Ã§Ã¶zemedi (deneme %d): %.80s",
                        deneme,
                        sonuc.get("hata", "bilinmeyen")[:80],
                    )
            except Exception as e:
                logger.exception("[script_calistir] SelfHeal hatasÄ±: %s", e)

            # Backoff (2. ve 3. denemede)
            if deneme < 3:
                import time

                bekleme = 1.0 * (2.0 ** (deneme - 1))
                time.sleep(bekleme)

        return False

    def ogren(self, hata_mesaji: str, script_kodu: str, ad: str) -> str:
        """LLM'e sor, fix Ã¼ret, dÃ¶ndÃ¼r.

        SelfHeal v2 entegrasyonu:
        Ã–nce SelfHeal dene, olmazsa direkt LLM fallback.
        """
        # SelfHeal ile dene
        try:
            from reymen.core.self_heal import SelfHeal

            heal = SelfHeal(max_deneme=1)
            # script_kodu = kod, hata_mesaji = hata
            sonuc = heal.coz(hedef=ad, hata=hata_mesaji, kod=script_kodu)
            if sonuc["basarili"]:
                return sonuc["cozum"]
        except Exception as e:
            logger.warning("[ogren] SelfHeal hatasÄ±: %s, LLM fallback", e)

        # Fallback: direkt LLM'e sor
        return self._llm_fix_iste(hata_mesaji, script_kodu, dosya_adi=ad)

    def ogrenme_istatistik(self) -> dict:
        """Ã–ÄŸrenme hafÄ±zasÄ± + SelfHeal istatistikleri."""
        ogrenme = {}
        self_heal = {}
        try:
            from reymen.core.ogrenme import istatistik

            ogrenme = istatistik()
        except ImportError:
            ogrenme = {"hata": "ogrenme modulu yok"}
        except Exception as _e:
            logger.warning("[Motor] except Exception (L2349): %s", Exception)
            pass
        try:
            from reymen.core.self_heal import istatistik_al

            self_heal = istatistik_al()
        except Exception:
            self_heal = {"hata": "SelfHeal henÃ¼z Ã§alÄ±ÅŸmadÄ±"}

        return {
            "ogrenme_hafiza": ogrenme,
            "self_heal": self_heal,
            "toplam_cozum": ogrenme.get("toplam", 0),
            "toplam_self_heal": self_heal.get("toplam_hata", 0),
        }

    def gorev_coz(self, gorev_yolu: str) -> dict:
        """Verilen gÃ¶rev dosyasÄ±nÄ± oku, adÄ±mlarÄ± Ã§Ã¶z, sonuÃ§larÄ± dÃ¶ndÃ¼r.
        KullanÄ±m: motor.gorev_coz(".ReYMeN/gorev_cozucu_sistemi.md")
        """
        if not _ORCHESTRATOR_MEVCUT:
            return {"hata": "Orchestrator yuklu degil. pip install reymen-core"}
        try:
            from reymen.core.orchestrator import solve_all, solve_step

            steps = self._gorev_adimlari_oku(gorev_yolu)
            return {"sonuclar": solve_all(steps), "durum": "tamam"}
        except Exception as e:
            return {"hata": str(e), "durum": "hata"}

    def hatadan_kurtul(self, kod: str, hata: str, dosya_adi: str = "") -> str:
        """Bir Python kodundaki hatayÄ± Ã§Ã¶z, dÃ¼zeltilmiÅŸ halini al.

        Ä°yileÅŸtirmeler (v2):
        - Ã–nce Ã¶ÄŸrenme hafÄ±zasÄ±nda ara (hÄ±zlÄ± Ã§Ã¶zÃ¼m)
        - HafÄ±zada yoksa OgrenmeDongusu kullan (LLM + backoff)
        - Son Ã§are olarak orchestrator'a baÅŸvur
        - Dosya adÄ± context'e eklenir
        """
        # 1. Ã–nce Ã¶ÄŸrenme hafÄ±zasÄ±nda ara
        try:
            from reymen.core.ogrenme import imza_uret, cozum_bul, tablo_olustur

            tablo_olustur()
            hata_objesi = RuntimeError(hata)
            imza = imza_uret(hata_objesi)
            onceki = cozum_bul(imza)
            if onceki:
                logger.info(
                    "[hatadan_kurtul] HafÄ±zadan Ã§Ã¶zÃ¼m bulundu (imza: %s)", imza[:16]
                )
                return onceki
        except Exception as e:
            logger.warning("[hatadan_kurtul] HafÄ±za arama hatasÄ±: %s", e)

        # 2. OgrenmeDongusu dene (LLM + backoff + kaydetme)
        try:
            cozum = self.ogren(hata, kod, dosya_adi or "motor_kurtarma")
            if cozum and not cozum.startswith("Hata"):
                return cozum
        except Exception as e:
            logger.warning("[hatadan_kurtul] OgrenmeDongusu hatasÄ±: %s", e)

        # 3. Son Ã§are: orchestrator
        if _ORCHESTRATOR_MEVCUT:
            try:
                from reymen.core.orchestrator import coz_hata

                return coz_hata(hata, kod, dosya_adi or "motor_kurtarma")
            except Exception as e:
                return f"Hata cozulemedi: {e}"

        return f"Ã‡Ã¶zÃ¼m bulunamadÄ±. Hata: {hata[:200]}"

    def _self_heal_calistir(self, hedef_hata_kod: str) -> str:
        """SELF_HEAL aracÄ± iÃ§in lambda wrapper.

        Parametre: 'hedef|hata|kod' (| ile ayrÄ±lmÄ±ÅŸ)
        """
        try:
            from reymen.core.self_heal import SelfHeal

            parts = [p.strip() for p in hedef_hata_kod.split("|", 2)]
            hedef = parts[0] if len(parts) > 0 else "bilinmeyen"
            hata = parts[1] if len(parts) > 1 else ""
            kod = parts[2] if len(parts) > 2 else ""
            if not hata:
                return "[SelfHeal] âŒ Hata mesajÄ± gerekli. Format: hedef|hata|kod"
            heal = SelfHeal()
            sonuc = heal.coz(hedef, hata, kod)
            if sonuc["basarili"]:
                return (
                    f"[SelfHeal] âœ… Ã‡Ã¶zÃ¼ldÃ¼ (kaynak: {sonuc['kaynak']}, "
                    f"deneme: {sonuc['deneme_sayisi']})\n"
                    f"Ã‡Ã¶zÃ¼m:\n{sonuc['cozum']}"
                )
            else:
                return (
                    f"[SelfHeal] âŒ Ã‡Ã¶zÃ¼lemedi "
                    f"({sonuc['deneme_sayisi']} deneme)\n"
                    f"Hata: {sonuc['hata']}"
                )
        except Exception as e:
            return f"[SelfHeal] âŒ Ä°Ã§ hata: {e}"

    @staticmethod
    def _gorev_adimlari_oku(gorev_yolu: str) -> list[tuple[str, str]]:
        """GÃ¶rev dosyasÄ±ndan ADIMLARI oku. Format:
        ADIM_1 | reymen/scripts/step_01.py
        ADIM_2 | reymen/scripts/step_02.py
        """
        import re

        path = Path(gorev_yolu)
        if not path.exists():
            return [("HATA", gorev_yolu)]
        text = path.read_text("utf-8")
        steps = []
        for line in text.splitlines():
            m = re.match(r"^\s*(ADIM_\d+)\s*\|\s*(.+\.py)\s*$", line)
            if m:
                steps.append((m.group(1), m.group(2).strip()))
        return steps if steps else [("TEK_ADIM", gorev_yolu)]


if __name__ == "__main__":
    m = Motor(backend_mode="local")
    arac, ham = m.eylemi_ayristir('Eylem: DOSYA_OKU("test.txt")')
    print(f"{arac} -> {m.calistir(arac, ham)[:60]}")
