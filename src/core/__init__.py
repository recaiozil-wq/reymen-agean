# ReYMeN Core — Otonom görev çözücü çekirdeği
from .model_adapter import get_active_adapter, ModelAdapter
from .orchestrator import solve_step, solve_all, coz_hata, run_script
from .ogrenme import (
    imza_uret, cozum_bul, cozum_kaydet, tablo_olustur,
    istatistik, eski_basarisizlari_temizle
)
from .self_heal import SelfHeal, coz, script_coz, istatistik_al as self_heal_istatistik
from .mcp_server import tool_kaydet, tool_sil, get_tools
from .session_search import session_ara

# Provider Sistemi (P0)
from .model_provider import (
    ModelProvider,
    OpenAICompatibleProvider,
    MiniMaxProvider,
    ProviderChain,
    ProviderKayit,
    CalistirSonuc,
    varsayilan_zincir,
    zinciri_sifirla,
    _provider_fabrikasi,
)

# YAML Config Manager (P0)
from .config_manager import (
    Config,
    ProfilBilgisi,
    varsayilan_config,
    config_yeniden_yukle,
)

# Session DB — SessionDB sinifi
from .session_db import SessionDB

# Kimlik Havuzu (P0)
from .credential_pool import CredentialPool, get_credential_pool

# Cron/Scheduler (P1)
from .cron_manager import (
    CronManager,
    CronJob,
    get_cron_manager,
)

# Gateway Sistemi (P1)
from .gateway_manager import (
    GatewayAdapter,
    TelegramAdapter,
    DiscordAdapter,
    CLIAdapter,
    GatewayYoneticisi,
    get_gateway_yoneticisi,
)

# Observability / Tracing (P1)
from .observability import (
    setup_observability,
    trace_llm_call,
    trace_tool_call,
    trace_skill_load,
    trace_session_start,
    span_olustur,
    get_tracer,
    observability_aktif_mi,
    observability_durum,
)

# Tip Güvenliği / Pydantic AI (P1)
from .type_safety import (
    validated_tool,
    ValidatedTool,
    ToolResult,
    StructuredOutput,
    json_schema_al,
    model_al,
    build_pydantic_ai_tool,
)

# Skills Hub — Topluluk skill kesfi ve yonetimi (P1)
from .skills_hub import (
    SkillsHub,
    SkillMetadata,
    IndirmeSonucu,
    cron_haftalik_guncelleme,
    hub_durumu,
)
