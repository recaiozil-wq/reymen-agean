# -*- coding: utf-8 -*-
"""conversation_loop.py â€” ReYMeN Agent seviyesi konusma dongusu.

Ajan ile kullanici arasindaki etkilesimi yonetir:
- Amaç belirleme ve takip (task_id, budget)
- Provider-agnostik API mesaj formati (OpenAI / Anthropic / Codex / LM Studio)
- Context compression (esik asilinca otomatik sikistirma)
- Prompt caching (Anthropic icin cache_control marker'lari)
- Interruptible API call (Ctrl+C destekli, thread bazli)
- Tool call dongusu (tool_calls geldikce calistir, sonuclari ekle, devam)
- Iteration budget
- Hata yonetimi: her adimda try/except
- Loglama: her adimda logging.INFO / ERROR
"""

import json
import logging
import os
import re
import sys
import threading
import time
import traceback
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

from dotenv import load_dotenv

_env_yolu = Path(__file__).resolve().parent.parent.parent.parent / ".env"
if _env_yolu.exists():
    load_dotenv(_env_yolu, override=False)

# Hermes profil .env'sini de dene (API key'ler için)
for _profil in ["reymen", "default", "kiral38"]:
    _profil_env = Path.home() / f"AppData/Local/hermes/profiles/{_profil}/.env"
    if _profil_env.exists():
        load_dotenv(_profil_env, override=False)

# Proje kokunu sys.path'e ekle (gateway bagimsiz calisma icin)
_PROJE_KOK = Path(__file__).resolve().parent.parent.parent
if str(_PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(_PROJE_KOK))

# ── Out-of-band iptal sinyali (Hermes-style) ────────────────────────
# Herhangi bir yerden (Telegram/CLI/web) conversation_loop'u durdurmak icin
# Dosya tabanli: .stop dosyasi varsa loop kirilir
_STOP_SINYAL_DOSYASI = _PROJE_KOK / ".stop"
# Alternatif: .ReYMeN/.stop (proje disindan da erisilebilir)
_STOP_SINYAL_ALTERNATIF = _PROJE_KOK / ".ReYMeN" / ".stop"

logger = logging.getLogger(__name__)

log = logging.getLogger("conversation_loop")

# Kullaniciya gereksiz log gosterme - sadece ERROR ve uzeri
logging.getLogger("reymen").setLevel(logging.ERROR)
logging.getLogger("conversation_loop").setLevel(logging.ERROR)
# Tum alt logger'lari da kapat
for _l in ["CUA", "Motor", "motor", "ReYMeN", "beyin", "plugin", "cron", "skill"]:
    logging.getLogger(_l).setLevel(logging.ERROR)

from reymen.cereyan.prompt_assembly import cache_dosya_oku


# â”€â”€ Konusmadan Skill Cikarma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.arac.konusmadan_skill import konusmadan_skill_cikar as _skill_cikar

    _SKILL_CIKAR_AKTIF = True
except ImportError:
    _SKILL_CIKAR_AKTIF = False

# â”€â”€ @file/@url Referans Isleme (ref_processor) â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.ref_processor import ref_isle as _ref_isle
    from reymen.cereyan.ref_processor import ref_context_olustur as _ref_context_olustur

    _REF_PROCESSOR_AKTIF = True
except ImportError:
    _ref_isle = None
    _ref_context_olustur = None
    _REF_PROCESSOR_AKTIF = False

# â”€â”€ Nudge / latent kullanÄ±cÄ± modeli â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.nudge_model import NudgeModel

    _NUDGE_AKTIF = True
except ImportError:
    NudgeModel = None
    _NUDGE_AKTIF = False

# â”€â”€ Skill iyileÅŸtirici â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.scripts.skill_iyilestirici import SkillIyilestirici

    _SKILL_IYI_AKTIF = True
except ImportError:
    SkillIyilestirici = None
    _SKILL_IYI_AKTIF = False

# â”€â”€ Adaptif öÄŸrenme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.adaptif_ogrenme import AdaptifOgrenme

    _ADAPTIF_AKTIF = True
except ImportError:
    AdaptifOgrenme = None
    _ADAPTIF_AKTIF = False

# â”€â”€ Proaktif kontrol (her cevap sonrasÄ± eksik analizi) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.proaktif_kontrol import (
        soru_sonrasi_kontrol as _proaktif_kontrol,
    )

    _PROAKTIF_AKTIF = True
except ImportError:
    _proaktif_kontrol = None
    _PROAKTIF_AKTIF = False

# â”€â”€ Yeni import'lar: circuit breaker, streaming, error classify â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.iteration_budget import IterationBudget
except ImportError:
    IterationBudget = None

try:
    from turn_retry_state import TurnRetryState
except ImportError:
    TurnRetryState = None

# â”€â”€ Opsiyonel modüller (graceful degrade) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

try:
    from turn_context import TurnYoneticisi, TurnContext
except ImportError:
    TurnYoneticisi = None
    TurnContext = None

try:
    from reymen.cereyan.iteration_budget import IterationBudget, standart_budget

    _BUDGET_AKTIF = True
except ImportError:
    IterationBudget = None
    standart_budget = None
    _BUDGET_AKTIF = False

try:
    from reymen.arac.prompt_builder import PromptBuilder

    _BUILDER_AKTIF = True
except ImportError:
    PromptBuilder = None
    _BUILDER_AKTIF = False

try:
    from reymen.hafiza.context_compressor import ContextCompressor as _Compressor

    _COMPRESS_AKTIF = True
except ImportError:
    _Compressor = None
    _COMPRESS_AKTIF = False

# `_CACHING_AKTIF` â€” provider'a gore dinamik olarak hesaplanir.
# ``caching_aktif_mi(provider)`` fonksiyonu ile provider prompt caching
# destekliyorsa True doner. Ayrica ``agent._use_prompt_caching`` da dikkate
# alinir (Anthropic / OpenRouter / DeepSeek / OpenAI).
try:
    from reymen.arac.prompt_caching import _prompt_caching_ekle, caching_aktif_mi

    # _CACHING_AKTIF artik dinamik: provider'a gore hesaplanir.
    # Dogrudan kullanim yerine caching_aktif_mi() fonksiyonu tercih edilir.
    _CACHING_AKTIF = None  # None = "provider'a bak" anlaminda
except ImportError:
    _prompt_caching_ekle = None
    caching_aktif_mi = None
    _CACHING_AKTIF = False

# Geriye uyumluluk: eski import hala calissin
try:
    from reymen.arac.prompt_caching import (
        apply_anthropic_cache_control as _apply_anthropic_cache_control,
    )
except ImportError:
    _apply_anthropic_cache_control = None

try:
    from reymen.hafiza.session_db import AdvancedSessionStorage as _SessionStorage

    _SESSION_AKTIF = True
except ImportError:
    _SessionStorage = None
    _SESSION_AKTIF = False

# â”€â”€ Session Search FTS5 (tam metin arama) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.session_search import (
        SessionSearch as _SessionSearch,
        session_search_al as _session_search_al,
    )

    _SESSION_SEARCH_AKTIF = True
except ImportError:
    _SessionSearch = None
    _session_search_al = None
    _SESSION_SEARCH_AKTIF = False

# â”€â”€ OnceHafiza (bellegi-oncelikli kontrol) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.sistem.once_hafiza import hafizada_ara as _hafizada_ara

    _ONCE_HAFIZA_AKTIF = True
except ImportError:
    _hafizada_ara = None
    _ONCE_HAFIZA_AKTIF = False

# â”€â”€ Rules Engine (Kural/izin yonetimi) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.sistem.kurallar import (
        RulesEngine as _RulesEngine,
        engine_al as _rules_engine_al,
    )

    _RULES_ENGINE = _rules_engine_al()
    _RULES_AKTIF = True
    log.info("[Rules] Kural motoru aktif (%d kural)", _RULES_ENGINE.kural_sayisi)
except ImportError:
    _RULES_ENGINE = None
    _RULES_AKTIF = False

# â”€â”€ Skill Activator (auto-activation) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.skill_activator import SkillActivator as _SkillActivator

    _SKILL_ACTIVATOR = _SkillActivator()
    _SKILL_ACTIVATOR_AKTIF = True
    # Startup'ta tum skill'leri aktif et
    # Continuous Learning
    try:
        from reymen.cereyan.continuous_learning import session_baslat as _cl_baslat
        from reymen.cereyan.continuous_learning import ogrenme_baglani_al as _cl_baglam

        _CL_AKTIF = True
    except ImportError:
        _CL_AKTIF = False
    # Startup'ta tum skill'leri aktif et
    try:
        aktif_sayisi = _SKILL_ACTIVATOR.tumunu_aktif_et()
        log.info("[Baslangic] %d skill basariyla aktif edildi", aktif_sayisi)
    except Exception as e:
        log.warning("[Baslangic] Skill toplu aktivasyon basarisiz: %s", e)
except ImportError:
    _SKILL_ACTIVATOR = None
    _SKILL_ACTIVATOR_AKTIF = False

# â”€â”€ Delegasyon Sistemi (P2) â€” Subagent + görev ayrÄ±ÅŸtÄ±rma â”€â”€â”€â”€â”€
try:
    from reymen.ag.delegasyon import (
        DelegasyonSistemi as _DelegasyonSistemi,
        sistem_al as _delegasyon_sistemi_al,
        konusma_dongusu_hook_bul as _delegasyon_hook_bul,
    )

    _DELEGASYON_AKTIF = True
    # Hook'u otomatik kaydet
    try:
        _delegasyon_hook = _delegasyon_hook_bul()
    except Exception:
        _delegasyon_hook = None
except ImportError:
    _DelegasyonSistemi = None
    _delegasyon_sistemi_al = None
    _delegasyon_hook_bul = None
    _DELEGASYON_AKTIF = False

# â”€â”€ Plugin Sistemi (lifecycle hooks) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.plugin.manager import (
        PluginManager as _PluginManager,
        plugin_manager_al as _plugin_manager_al,
    )

    _PLUGIN_SISTEMI = _plugin_manager_al()  # singleton, config + auto_load
    _PLUGIN_AKTIF = _PLUGIN_SISTEMI.aktif
    log.info(
        "[Plugin] Plugin sistemi aktif=%s (%d plugin yuklu)",
        _PLUGIN_AKTIF,
        _PLUGIN_SISTEMI.sayi,
    )
except ImportError as _pie:
    _PLUGIN_SISTEMI = None
    _PLUGIN_AKTIF = False
    log.debug("[Plugin] Plugin sistemi yuklenemedi: %s", _pie)

# â”€â”€ Hata sÄ±nÄ±flandÄ±rÄ±cÄ± ve mesaj tamirci â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.hata_siniflandirici import (
        api_hatasini_siniflandir,
        classify_api_error,
        FailoverReason,
        SiniflandirilmisHata,
    )

    _HATA_SINIFLANDIRICI_AKTIF = True
except ImportError:
    api_hatasini_siniflandir = None  # type: ignore[assignment]
    classify_api_error = None  # type: ignore[assignment]
    FailoverReason = None  # type: ignore[assignment]
    SiniflandirilmisHata = None  # type: ignore[assignment]
    _HATA_SINIFLANDIRICI_AKTIF = False

try:
    from reymen.cereyan.mesaj_tamirci import (
        arac_cagri_argumanlarini_temizle,
        mesaj_siralamasi_tamir_et,
        surrogate_karakterleri_temizle,
        sanitize_tool_call_arguments,
        repair_message_sequence,
    )

    _MESAJ_TAMIRCI_AKTIF = True
except ImportError:
    arac_cagri_argumanlarini_temizle = None  # type: ignore[assignment]
    mesaj_siralamasi_tamir_et = None  # type: ignore[assignment]
    surrogate_karakterleri_temizle = None  # type: ignore[assignment]
    sanitize_tool_call_arguments = None  # type: ignore[assignment]
    repair_message_sequence = None  # type: ignore[assignment]
    _MESAJ_TAMIRCI_AKTIF = False

try:
    from reymen.cereyan.hook_dispatcher import (
        hook_cagir as _hook_cagir,
        hook_kaydet as _hook_kaydet,
        oturum_baslat_tetikle as _oturum_baslat_tetikle,
        oturum_bitir_tetikle as _oturum_bitir_tetikle,
        tur_baslat_tetikle as _tur_baslat_tetikle,
        tur_bitir_tetikle as _tur_bitir_tetikle,
        arac_cagri_tetikle as _arac_cagri_tetikle,
        arac_sonuc_tetikle as _arac_sonuc_tetikle,
        hata_tetikle as _hata_tetikle,
        context_sikistirma_tetikle as _context_sikistirma_tetikle,
    )

    _HOOK_AKTIF = True
    # Self-improvement hook'unu otomatik kaydet (her tur sonu metrik)
    try:
        from reymen.self_improve import conversation_loop_hook as _si_hook

        _hook_kaydet("on_turn_end", _si_hook)
    except Exception as _e:
        __import__("logging").getLogger(__name__).warning(
            "[SessizExcept] %%s: %%s", type(_e).__name__, _e
        )
except ImportError:
    _hook_cagir = None  # type: ignore[assignment]
    _oturum_baslat_tetikle = _oturum_bitir_tetikle = None  # type: ignore[assignment]
    _tur_baslat_tetikle = _tur_bitir_tetikle = None  # type: ignore[assignment]
    _arac_cagri_tetikle = _arac_sonuc_tetikle = None  # type: ignore[assignment]
    _hata_tetikle = _context_sikistirma_tetikle = None  # type: ignore[assignment]
    _HOOK_AKTIF = False

try:
    from reymen.cereyan.stream_diagnostics import (
        StreamSaglikTakibi as _StreamSaglikTakibi,
    )

    _STREAM_DIAG_AKTIF = True
except ImportError:
    _StreamSaglikTakibi = None  # type: ignore[assignment]
    _STREAM_DIAG_AKTIF = False

# â”€â”€ Web arama (halusinasyon onleme) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ArtÄ±k doÄŸrudan DDGS yerine web_search_engine'deki SearchDispatcher kullanÄ±lÄ±r.
# _WEB_ARAMA_AKTIF, dispatcher her zaman hazÄ±r olduÄŸu için True olarak kalÄ±r.
_WEB_ARAMA_AKTIF = True

# â”€â”€ MCP (Model Context Protocol) entegrasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.arac.native_mcp_client import NativeMCPClient as _NativeMCPClient

    _MCP_NATIVE_AKTIF = True
except ImportError:
    _NativeMCPClient = None
    _MCP_NATIVE_AKTIF = False

try:
    from reymen.arac.mcp_client_tool import (
        mcp_client as _mcp_client_get,
        mcp_client_baglan as _mcp_client_baglan,
        mcp_client_listele as _mcp_client_listele,
        motor_kaydet as _mcp_client_motor_kaydet,
    )

    _MCP_CLIENT_AKTIF = True
except ImportError:
    _mcp_client_get = None
    _mcp_client_baglan = None
    _mcp_client_listele = None
    _mcp_client_motor_kaydet = None
    _MCP_CLIENT_AKTIF = False

try:
    from reymen.arac.mcp_catalog import (
        run as _mcp_catalog_run,
        listele as _mcp_catalog_listele,
    )

    _MCP_CATALOG_AKTIF = True
except ImportError:
    _mcp_catalog_run = None
    _mcp_catalog_listele = None
    _MCP_CATALOG_AKTIF = False

try:
    from reymen.arac.mcp_tool import (
        MCPIstemci as _MCPIstemci,
        mcp_istemci as _mcp_istemci_get,
    )

    _MCP_TOOL_AKTIF = True
except ImportError:
    _MCPIstemci = None
    _mcp_istemci_get = None
    _MCP_TOOL_AKTIF = False

_MCP_AKTIF = (
    _MCP_NATIVE_AKTIF or _MCP_CLIENT_AKTIF or _MCP_CATALOG_AKTIF or _MCP_TOOL_AKTIF
)

# â”€â”€ Framework Adaptörleri (LangGraph / CrewAI / AutoGen) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.arac.framework_adaptor import (
        FrameworkYonetici as _FrameworkYonetici,
        framework_adaptor as _framework_adaptor,
        framework_adaptor_durum as _framework_adaptor_durum,
    )

    _FRAMEWORK_ADAPTOR_AKTIF = True
    _framework_aktif_fw = _framework_adaptor.aktif_frameworkler
    # Log active frameworks (once only)
    _aktif_liste = [ad for ad, aktif in _framework_aktif_fw.items() if aktif]
    if _aktif_liste:
        log.info("[Framework] Adaptor aktif: %s", ", ".join(_aktif_liste))
    else:
        log.debug("[Framework] Adaptor yuklu ama hic framework kurulu degil")
except ImportError:
    _FrameworkYonetici = None
    _framework_adaptor = None
    _framework_adaptor_durum = None
    _FRAMEWORK_ADAPTOR_AKTIF = False

# â”€â”€ Reasoning-Core (akil yurutme motoru) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.sistem.ortak_komut import reasoning_loop as _reasoning_loop

    _REASONING_AKTIF = True
except ImportError:
    _reasoning_loop = None
    _REASONING_AKTIF = False

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

from reymen.cereyan.config.circuit_breaker import CONTEXT_SIKISTIRMA_ESIGI

from reymen.cereyan.config.provider_limits import PROVIDER_LIMITS, PROVIDER_LIMIT_VARSAYILAN

from reymen.cereyan.config.oncelik_cache import ONCELIK_CACHE

# YanÄ±ttaki "gorev bitti" tetikleyicileri
GOREV_BITTI_TETIK = ("GOREV_BITTI", "görev bitti", "tamamlandi", "TASK_DONE")


from reymen.cereyan.motor import motor_tools_schema_al

# Geriye uyumlu alias (alt çizgili)
_motor_tools_schema_al = motor_tools_schema_al

from reymen.cereyan.config.circuit_breaker import (
    CIRCUIT_BREAKER_MAX_HATA,
    CIRCUIT_BREAKER_SURESI,
    CIRCUIT_BREAKER_KALICI,
    MAX_RETRY,
    MAX_API_RETRY,
    TAKILMA_ESI,
    ARTI_ARDA_TOOL_HATA_LIMIT,
    MAX_TOOL_CALLS,
    CONTEXT_BUDGET_CHARS,
    STREAMING_AKTIF,
)


from reymen.cereyan.tools.vision_adapter import VisionAdapter
from reymen.cereyan.credits_tracker import budget_olustur
from reymen.cereyan.turn_context_builder import context_preflight, api_mesajlari_olustur


class ConversationLoop:
    """Ana konusma dongusu â€” geriye uyumlu + ReYMeN Agent seviyesi.

    Eski API:
        loop = ConversationLoop(motor=motor, beyin=beyin, max_tur=30)
        sonuc = loop.coz("bir dosya olustur")

    Yeni API:
        sonuc = loop.run_conversation(
            hedef="bir dosya olustur",
            provider="deepseek",
            baglam={"kullanici": "Ahmet"},
        )
    """

    def __init__(self, motor: Any = None, beyin: Any = None, max_tur: int = 30) -> None:
        self.motor = motor
        self.beyin = beyin
        self.max_tur = max_tur
        self.tur_yoneticisi = (
            TurnYoneticisi(max_tur=max_tur) if TurnYoneticisi else None
        )
        self._durum = "hazir"
        self._iptal_istegi = False
        self._konusma_gecmisi: list = []
        # Konusma gecmisi â€” son N mesaj (user/assistant) bir sonraki goreve aktarilir
        self._gecmis_mesajlar: list[dict] = []
        self._max_gecmis_mesaj = 10
        # Circuit breaker state
        self._cb_art_arda_hata = 0
        self._cb_son_hata_zamani = 0.0
        self._cb_acik = False
        # Ä°yileÅŸtirme #2: Mekanik retry sayacÄ±
        self._retry_sayaci = 0
        self._max_retry = MAX_RETRY
        self._retry_kalici_kilit = False
        # Takılma dedektörü
        self._onceki_eylemler: list[str] = []
        # Art arda tool hatası sayacı (Hermes pattern)
        self._arti_arda_tool_hatasi = 0
        self._tool_hata_zorla_cevap = False
        # Toplam tool çağrısı sayacı (max_tool_calls)
        self._tool_call_sayaci = 0
        # Duplicate detection için önceki tool çağrıları (ad + param)
        self._onceki_tool_cagrilari: list[tuple[str, str]] = []
        # Context budget: güncel mesaj boyutu
        self._context_budget_chars = CONTEXT_BUDGET_CHARS
        # Dusuk temperature (web verisi icin)
        self._force_low_temp = False
        # Streaming
        self._stream_callback = None
        # A2A mesajlaÅŸma
        self._a2a_broker = None
        self._a2a_agent = None
        try:
            from reymen.a2a import Broker as _Broker, Agent as _Agent

            self._a2a_broker = _Broker()
            self._a2a_agent = _Agent("conversation_loop", self._a2a_broker)
        except Exception as _e:
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] %%s: %%s", type(_e).__name__, _e
            )

        # â”€â”€ MCP (Model Context Protocol) otomatik baslatma â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._native_mcp = None
        if _MCP_NATIVE_AKTIF:
            try:
                self._native_mcp = _NativeMCPClient()
                mcp_sunucular = self._native_mcp.konfig_yukle()
                for cfg in mcp_sunucular:
                    baglanti = self._native_mcp._baglantilar.get(cfg.ad)
                    if baglanti is None:
                        from reymen.arac.native_mcp_client import MCPBaglanti

                        yeni = MCPBaglanti(cfg)
                        if yeni.baslat():
                            self._native_mcp._baglantilar[cfg.ad] = yeni
                            log.info(
                                "[MCP] %s otomatik baslatildi (%d tool)",
                                cfg.ad,
                                len(yeni.araclar),
                            )
                if self.motor:
                    self._mcp_motor_kaydet()
            except Exception as _mcp_e:
                log.warning("[MCP] Baslatma hatasi (sessiz): %s", _mcp_e)

        # MCP Client Tool (config'den yukle)
        if _MCP_CLIENT_AKTIF:
            try:
                # Config varsa zaten singleton otomatik yuklenir
                yonetici = _mcp_client_get()
                durum = yonetici.durum()
                if durum:
                    for ad, bilgi in durum.items():
                        log.info(
                            "[MCPClient] %s hazir (%d tool)",
                            ad,
                            bilgi.get("arac_sayisi", 0),
                        )
                    if self.motor:
                        _mcp_client_motor_kaydet(self.motor)
            except Exception as _mcp_e:
                log.warning("[MCPClient] Baslatma hatasi: %s", _mcp_e)

        # â”€â”€ VisionAdapter baglantisi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        try:
            self._vision_adapter = VisionAdapter()
            self._vision_adapter._loop_ref = self
        except Exception:
            self._vision_adapter = None

        # â”€â”€ Nudge / latent kullanÄ±cÄ± modeli â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._nudge = None
        if _NUDGE_AKTIF:
            try:
                self._nudge = NudgeModel()
                log.info("[NUDGE] Latent kullanici modeli aktif")
            except Exception as e:
                log.warning("[NUDGE] Baslatma hatasi: %s", e)

        # â”€â”€ Session Search FTS5 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._session_search = None
        if _SESSION_SEARCH_AKTIF:
            try:
                self._session_search = _session_search_al()
                log.info("[SESSION_SEARCH] FTS5 arama motoru aktif")
            except Exception as e:
                log.warning("[SESSION_SEARCH] Baslatma hatasi: %s", e)

        # â”€â”€ Adaptif öÄŸrenme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._adaptif = None
        if _ADAPTIF_AKTIF:
            try:
                self._adaptif = AdaptifOgrenme()
                log.info("[ADAPTIF] Adaptif ogrenme aktif")
            except Exception as e:
                log.warning("[ADAPTIF] Baslatma hatasi: %s", e)

        # â”€â”€ Skill iyileÅŸtirici â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._skill_iyi = None
        if _SKILL_IYI_AKTIF:
            try:
                self._skill_iyi = SkillIyilestirici()
                log.info("[SKILL_IYI] Skill iyilestirici aktif")
            except Exception as e:
                log.warning("[SKILL_IYI] Baslatma hatasi: %s", e)

        # ── Kalan ReYMeN modulleri ────────────────────────────────
        try:
            from reymen.curator import SkillCurator
            self._curator = SkillCurator()
        except Exception:
            self._curator = None
        try:
            from reymen.curator_backup import SkillBackup
            self._curator_backup = SkillBackup()
        except Exception:
            self._curator_backup = None
        try:
            from reymen.secret_scope import SecretScope
            self._secret_scope = SecretScope()
        except Exception:
            self._secret_scope = None
        try:
            from reymen.nous_rate_guard import NousRateGuard
            self._rate_guard = NousRateGuard()
        except Exception:
            self._rate_guard = None
        try:
            from reymen.memory_provider import OnceHafizaProvider
            self._memory_provider = OnceHafizaProvider()
        except Exception:
            self._memory_provider = None
        try:
            from reymen.models_dev import dev_model_mi
            self._dev_model = dev_model_mi
        except Exception:
            self._dev_model = None
        try:
            from reymen.jiter_preload import json_parse
            self._json_parse = json_parse
        except Exception:
            self._json_parse = None
        try:
            from reymen.manual_compression_feedback import CompressionFeedback
            self._compression_feedback = CompressionFeedback()
        except Exception:
            self._compression_feedback = None
        try:
            from reymen.onboarding import Onboarding
            self._onboarding = Onboarding()
        except Exception:
            self._onboarding = None

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
            # Plugin LLM
        try:
            from reymen.plugin_llm import PluginLLM
            self._plugin_llm = PluginLLM()
        except Exception:
            self._plugin_llm = None

    # MEVCUT API â€” geriye uyumluluk
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def coz(self, hedef: str, baglam: Optional[dict] = None) -> dict:
        """Eski API — run_conversation'a yonlendirir."""
        return self.run_conversation(hedef, baglam)

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # YENÄ° API â€” run_conversation (ReYMeN Agent seviyesi)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def run_conversation(
        self,
        hedef: str,
        baglam: Optional[dict] = None,
        provider: Optional[str] = None,
    ) -> dict:
        """ReYMeN Agent seviyesi konusma dongusu.

        Hermes run_agent mantiginda:
        1. OnceHafiza + Web arama (guncel bilgi varsa direkt cevap)
        2. LLM cagrisi (tool_calls ile)
        3. Tool calls varsa -> calistir -> mesaja ekle -> tekrar LLM
        4. Content varsa -> background review -> kullaniciya don
        """
        import time as _time
        basla = _time.time()
        task_id = str(uuid.uuid4())[:8]
        self._durum = "calisiyor"
        self._iptal_istegi = False
        self._retry_sayaci = 0
        self._tool_call_sayaci = 0
        self._onceki_tool_cagrilari = []
        self._arti_arda_tool_hatasi = 0
        self._tool_hata_zorla_cevap = False

        log.info("[%s] Basliyor: %.80s", task_id, hedef)

        # Trajectory kaydi
        try:
            from reymen.trajectory import Trajectory
            self._trajectory = Trajectory()
            self._trajectory.adim_ekle("baslangic", hedef, True)
        except Exception:
            self._trajectory = None

        # Title generator
        try:
            from reymen.title_generator import baslik_olustur
            _baslik = baslik_olustur([{"role": "user", "content": hedef}])
            if _baslik:
                log.info("[%s] Baslik: %s", task_id, _baslik)
        except Exception:
            pass

        # Rate limit tracker
        try:
            from reymen.rate_limit_tracker import tracker_al
            self._rate_tracker = tracker_al()
        except Exception:
            self._rate_tracker = None

        # Redact
        try:
            from reymen.redact import redakte_et
            _guvenli_hedef = redakte_et(hedef)
        except Exception:
            _guvenli_hedef = hedef

        # ── Asama 1: OnceHafiza kontrolu ────────────────────────────
        try:
            from reymen.sistem.once_hafiza import hafizada_ara as _ha
            oh = _ha(hedef)
            if oh and oh.get("cozum") and oh.get("guven", 0) >= 0.7:
                log.info("[%s] OnceHafiza'da cozum bulundu", task_id)
                self._durum = "tamam"
                return {
                    "basarili": True,
                    "yanit": str(oh["cozum"])[:2000],
                    "task_id": task_id,
                    "turlar": 0,
                    "sure": _time.time() - basla,
                    "kaynak": "once_hafiza",
                }
        except Exception:
            pass

        # ── Asama 2: Web arama (guncel bilgi varsa direkt don) ─────
        web_sonuc = None
        try:
            from reymen.cereyan.conversation_loop import _WEB_ARAMA_AKTIF
            if _WEB_ARAMA_AKTIF:
                web_sonuc = self._web_ara(hedef)
        except Exception:
            pass

        if web_sonuc and len(web_sonuc.strip()) > 30:
            log.info("[%s] Web sonucu bulundu, direkt cevap olarak kullaniliyor", task_id)
            self._durum = "tamam"
            return {
                "basarili": True,
                "yanit": web_sonuc.strip()[:4000],
                "task_id": task_id,
                "turlar": 1,
                "sure": _time.time() - basla,
                "kaynak": "web",
            }

        # ── Asama 3: LLM dongusu (tool-driven) ─────────────────────
        mesajlar: list = [{"role": "user", "content": hedef}]
        gecici_mesaj = baglam if baglam else {}
        self._konusma_gecmisi = mesajlar

        for tur in range(1, self.max_tur + 1):
            # Context compressor: mesaj sayisi coksa sikistir
            try:
                from reymen.context_compressor import context_sikistir, budget_asildi
                if len(mesajlar) > 15 and budget_asildi(mesajlar):
                    mesajlar = context_sikistir(mesajlar)
                    log.info("[%s] Context sikistirildi (%d mesaj)", task_id, len(mesajlar))
            except Exception:
                pass
            if self._iptal_istegi:
                self._durum = "iptal"
                return {"basarili": False, "yanit": "Islem iptal edildi.", "task_id": task_id, "turlar": tur, "sure": _time.time() - basla}

            # Sistem promptu
            try:
                sistem_prompt = self._sistem_promptu_olustur(hedef, gecici_mesaj)
            except Exception:
                sistem_prompt = "Sen ReYMeN, otonom bir yazilim ajanisin. Turkce yanitla."

            # Context engine
            try:
                if hasattr(self, '_ctx_engine') and self._ctx_engine:
                    _ek = self._ctx_engine.build(hedef)
                    if _ek:
                        sistem_prompt = sistem_prompt + '\n\n' + _ek
            except Exception:
                pass
            # API mesajlarini hazirla
            api_mesajlari = [{"role": "system", "content": sistem_prompt}] + mesajlar

            # LLM cagrisi
            try:
                from reymen.retry_utils import jittered_backoff
                _deneme = 0
                _max_den = 2
                cevap = None
                while _deneme < _max_den and cevap is None:
                    _deneme += 1
                    if _deneme > 1:
                        _b = jittered_backoff(_deneme, base=0.5, cap=5)
                        log.info("[%s] API retry %d (%.1fs)", task_id, _deneme, _b)
                    cevap = self._direct_api_call(api_mesajlari, tools_bos=False)
            except Exception as e:
                log.warning("[%s] API hatasi (deneme %d): %s", task_id, _deneme, e)
                cevap = Nonell(api_mesajlari, tools_bos=False)
            except Exception as e:
                log.warning("[%s] LLM cagrisi hatasi: %s", task_id, e)
                try:
                    from reymen.errors import ProviderError, ToolError
                    self._son_hata = ProviderError(str(e)[:100], kod=500)
                except Exception:
                    pass
                # Rate limit tracker
                try:
                    if self._rate_tracker:
                        self._rate_tracker.hata_kaydet("deepseek", 500)
                        if self._rate_tracker.bloke_mi("deepseek"):
                            log.warning("[%s] DeepSeek rate limit bloke, fallback", task_id)
                except Exception:
                    pass
                continue

            if not cevap:
                try:
                    if hasattr(self, "_nudge") and self._nudge:
                        _ipucu = getattr(self._nudge, "bos_cevap_ipucu", lambda: "")()
                        if _ipucu:
                            log.info("[%s] Nudge: %s", task_id, _ipucu)
                except Exception:
                    pass
                log.warning("[%s] LLM bos cevap dondu", task_id)
                continue

            icerik = ""
            tool_calls = []
            try:
                msg = cevap.get("choices", [{}])[0].get("message", {})
                icerik = msg.get("content", "") or ""
                tool_calls = msg.get("tool_calls", []) or []
            except Exception:
                pass

            # Tool calls varsa calistir
            if tool_calls:
                log.info("[%s] %d tool call calistiriliyor", task_id, len(tool_calls))
                try:
                    from reymen.kendini_anlat import tool_bilgisi_goster
                    tool_bilgisi_goster([tc.get("function",{}).get("name","") for tc in tool_calls])
                except Exception:
                    pass
                for tc in tool_calls:
                    eylem = {
                        "arac": tc.get("function", {}).get("name", ""),
                        "parametreler": tc.get("function", {}).get("arguments", "{}"),
                    }
                    try:
                        sonuc = self._arac_calistir(eylem)
                    except Exception as e:
                        sonuc = {"basarili": False, "hata": str(e)}

                    mesajlar.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{"id": tc.get("id", ""), "type": "function", "function": {"name": eylem["arac"], "arguments": str(eylem["parametreler"])}}],
                    })
                    mesajlar.append({
                        "role": "tool",
                        "content": str(sonuc.get("cikti", "") or str(sonuc)),
                        "tool_call_id": tc.get("id", ""),
                    })
                    self._konusma_gecmisi = mesajlar

                # Tool sonrasi tekrar LLM (bir sonraki tur)
                continue

            # Content varsa kullaniciya don
            if icerik and len(icerik.strip()) > 5:
                self._durum = "tamam"
                yanit = icerik.strip()
                try:
                    from reymen.turn_finalizer import finalize_turn
                    finalize_turn(task_id, {"yanit": yanit}, True, 0, None)
                except Exception:
                    pass

                # Think scrubber
                try:
                    from reymen.think_scrubber import dusunce_temizle
                    yanit = dusunce_temizle(yanit)
                except Exception:
                    pass

                # Redact
                try:
                    from reymen.redact import redakte_et
                    yanit = redakte_et(yanit)
                except Exception:
                    pass

                # Background review
                try:
                    from reymen.cereyan.background_review import spawn_background_review, background_review_sonucu_formatla
                    _actions = spawn_background_review(self._konusma_gecmisi, notification_mode="on")
                    if _actions:
                        _footer = background_review_sonucu_formatla(_actions)
                        if _footer:
                            yanit = yanit.rstrip() + "\n\n" + _footer
                except Exception:
                    pass

                return {
                    "basarili": True,
                    "yanit": yanit[:4000],
                    "task_id": task_id,
                    "turlar": tur,
                    "sure": _time.time() - basla,
                    "kaynak": "llm",
                }

        # ── Asama 4: Fallback ───────────────────────────────────────
        self._durum = "tamam"
        log.info("[%s] Tamamlandi (%d tur, %.1fs)", task_id, self.max_tur, _time.time() - basla)
        # Insights kaydi
        try:
            from reymen.insights import insights_al
            insights_al().soru_kaydet(_guvenli_hedef, "deepseek", 0)
        except Exception:
            pass

        return {
            "basarili": False,
            "yanit": "Uzgunum, bu soruya cevap bulamadim. Lutfen daha aciklayici olun.",
            "task_id": task_id,
            "turlar": self.max_tur,
            "sure": _time.time() - basla,
        }


    def _hata_coz(self, hata: Exception, hedef: str, task_id: str) -> Optional[str]:
        """Hata alinca OnceHafiza+ogrenme.py ile cozum bul, yoksa LLM'e sor."""
        # 1. Ogrenme modulunden imza + cozum ara
        try:
            from reymen.core.ogrenme import imza_uret, cozum_bul, cozum_kaydet

            imza = imza_uret(hata)
            if imza:
                onceki_cozum = cozum_bul(imza)
                if onceki_cozum:
                    log.info(
                        "[%s] _hata_coz: onceki cozum bulundu: %.60s",
                        task_id,
                        str(onceki_cozum)[:60],
                    )
                    return onceki_cozum
        except ImportError:
            imza = None
            onceki_cozum = None

        # 2. OnceHafiza'da hata cozumu ara
        try:
            from reymen.sistem.once_hafiza import hafizada_ara as _ha

            hata_sorgu = f"hata: {str(hata)[:100]}"
            oh_sonuc = _ha(hata_sorgu, kategori="hata")
            if oh_sonuc:
                cozum = (
                    oh_sonuc.get("yanit")
                    or oh_sonuc.get("sonuc")
                    or oh_sonuc.get("cozum", "")
                )
                if cozum:
                    log.info("[%s] _hata_coz: OnceHafiza'da cozum bulundu", task_id)
                    return cozum
        except Exception as _e:

            pass

        # 3. Yoksa LLM'e sor
        try:
            cozum_soru = f"Hata alindi: {hata}. Cozum nedir?"
            ds_mesaj = [
                {"role": "system", "content": "Hata cozum onerisi ver. Kisa, oz."},
                {"role": "user", "content": cozum_soru},
            ]
            ds_yanit = self._direct_api_call(ds_mesaj, tools_bos=True)
            if ds_yanit:
                cozum = ds_yanit.get("content", "") or ""
                if cozum and len(cozum.strip()) > 5:
                    try:
                        from reymen.sistem.once_hafiza import kaydet as _kaydet

                        _kaydet(
                            hedef=f"hata: {str(hata)[:100]}",
                            cozum=str(cozum)[:500],
                            kategori="hata",
                            kaynak="hata_cozucu",
                        )
                    except Exception:
                        pass
                    try:
                        if imza:
                            cozum_kaydet(imza, type(hata).__name__, str(hata)[:100], str(cozum)[:500])
                    except Exception:
                        pass
                    return cozum
        except Exception:
            pass

        return None

    def _hata_analiz_entegre(self, hata: Exception, task_id: str) -> None:
        """hata_analiz.py'yi cagir (varsa)."""
        try:
            from reymen.cereyan.hata_cozucu import HataKaydi, HataWatchdog
            watchdog = HataWatchdog()
            watchdog.baslat()
            kayit = HataKaydi(
                kaynak="conversation_loop",
                hata_tipi=type(hata).__name__,
                mesaj=str(hata)[:200],
            )
            log.info("[%s] _hata_analiz_entegre: HataWatchdog calisti", task_id)
        except Exception as _e:
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] %%s: %%s", type(_e).__name__, _e
            )

    def _oneri_uret(self, hedef: str) -> Optional[str]:
        """OnceHafiza tabanli belirsiz gorev onerisi.
        Hedef cok kisa/belirsizse en alakali OnceHafiza kategorisini bulur.
        TEK tahmin: "Sanirim X demek istiyorsun" formatinda.
        """
        if not _ONCE_HAFIZA_AKTIF or _hafizada_ara is None:
            return None
        try:
            sonuc = _hafizada_ara(hedef)
            if sonuc and sonuc.get("guven", 0) > 0.3:
                kate = sonuc.get("kategori") or sonuc.get("kaynak", "genel")
                return f"Sanirim {kate} ile ilgili bir sey istiyorsun, dogru mu?"
        except Exception as _e:
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] %%s: %%s", type(_e).__name__, _e
            )
        return None

    def _takilma_tespit(self, eylem_adi: str) -> bool:
        """Ayni eylem 3x tekrarlanirsa True doner (takilma tespiti)."""
        self._onceki_eylemler.append(eylem_adi)
        if len(self._onceki_eylemler) > TAKILMA_ESI:
            self._onceki_eylemler = self._onceki_eylemler[-TAKILMA_ESI:]
        return (
            len(self._onceki_eylemler) >= TAKILMA_ESI
            and len(set(self._onceki_eylemler[-TAKILMA_ESI:])) == 1
        )

    def _gorev_sonrasi_hafiza(self, hedef: str, yanit: str, task_id: str) -> None:
        """Gorev sonrasi OnceHafiza'yi guncelle (ogrenme)."""
        if not _ONCE_HAFIZA_AKTIF:
            return
        try:
            from reymen.sistem.once_hafiza import kaydet as _kaydet

            _kaydet(
                hedef=hedef,
                cozum=str(yanit)[:500],
                kategori="conversation",
                kaynak=f"run_conversation_{task_id}",
            )
            log.debug("[%s] _gorev_sonrasi_hafiza: kaydedildi", task_id)
        except Exception as _he:
            log.warning("[%s] _gorev_sonrasi_hafiza hatasi: %s", task_id, _he)

    def _vision_analiz(self, sorgu: str) -> Optional[str]:
        """Gorsel/resim analizi. VisionAdapter'daki vision_analiz_yap'a yonlendirir."""
        from reymen.cereyan.tools.vision_adapter import vision_analiz_yap
        return vision_analiz_yap(sorgu)

    def _skill_bul(self, sorgu: str, limit: int = 2) -> Optional[str]:
        """FTS5 skills_index.db'de sorguya en alakali skill'i bul."""
        try:
            import sqlite3, re

            db_path = os.path.join(
                os.path.dirname(__file__), ".ReYMeN", "skills_index.db"
            )
            if not os.path.exists(db_path):
                return None
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            # FTS5 ile ara
            kelimeler = re.findall(r"\w+", sorgu.lower())
            fts_query = " OR ".join(f'"{k}"' for k in kelimeler[:5] if len(k) > 2)
            if not fts_query:
                conn.close()
                return None
            cur.execute(
                "SELECT beceriler.name, beceriler_5n1k.ne FROM beceriler "
                "JOIN beceriler_5n1k ON beceriler.rowid = beceriler_5n1k.rowid "
                "WHERE beceriler MATCH ? LIMIT ?",
                (fts_query, limit),
            )
            rows = cur.fetchall()
            conn.close()
            if rows:
                metin = ""
                for name, aciklama in rows:
                    if name:
                        metin += f"- {name}: {str(aciklama or '')[:100]}\n"
                return metin.strip() if metin.strip() else None
            return None
        except Exception:
            return None

    def _ensemble_dogrula(self, ensemble: dict, sonuc: dict, task_id: str) -> dict:
        """Ensemble sonucunu dogrula: en iyi aday bos/hataliysa 2.yi dene."""
        sirali = sorted(ensemble.values(), key=lambda x: x["puan"], reverse=True)
        for aday in sirali:
            yanit = aday.get("yanit", "")
            if yanit and len(str(yanit).strip()) > 5:
                sonuc["basarili"] = True
                sonuc["yanit"] = yanit
                sonuc["kaynak"] = aday["kaynak"]
                sonuc["puan"] = aday["puan"]
                log.info(
                    "[%s] Dogrulama: %s secildi (puan=%.1f)",
                    task_id,
                    aday["kaynak"],
                    aday["puan"],
                )
                return sonuc
        # Hicbiri uygun degil
        sonuc["basarili"] = False
        sonuc["hata"] = "Tum kaynaklar basarisiz veya bos"
        sonuc["dogrulama_uyarisi"] = "hepsi_bos"
        log.warning("[%s] Dogrulama: tum adaylar bos/hatali", task_id)
        # ── Background review (memory + skill) ────────────────────────
        if sonuc.get("basarili") and sonuc.get("yanit"):
            try:
                from reymen.cereyan.background_review import spawn_background_review
                _actions = spawn_background_review(
                    getattr(self, "_konusma_gecmisi", []) or [],
                    notification_mode="on",
                )
                if _actions and sonuc.get("yanit"):
                    from reymen.cereyan.background_review import background_review_sonucu_formatla
                    _footer = background_review_sonucu_formatla(_actions)
                    if _footer:
                        sonuc["yanit"] = sonuc["yanit"].rstrip() + "\n\n" + _footer
            except Exception:
                pass


        return sonuc

    # â”€â”€ Delegasyon (P2) â€” Subagent yönetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _delegasyon_kontrol(self, hedef: str) -> Optional[Dict[str, Any]]:
        """
        Hedef metnini kontrol eder, delegasyon gerekiyorsa subagent
        oluÅŸturup çalÄ±ÅŸtÄ±rÄ±r.

        Delegasyon ipuçlarÄ±:
            - "delege et", "subagent", "alt ajan", "görev devret"
            - "paralel", "aynÄ± anda", "zincir"
            - NumaralÄ± liste + "paralel" veya "zincir" kelimeleri

        Returns:
            Delegasyon sonucu dict veya None (delegasyon gerekmiyorsa)
        """
        if not _DELEGASYON_AKTIF:
            return None

        try:
            # Lazy import â€” GorevAyristirici
            from reymen.ag.delegasyon import GorevAyristirici

            hedef_lower = hedef.lower()

            # Delegasyon tetikleyicileri
            tek_tetik = ["delege et", "subagent çalÄ±ÅŸtÄ±r", "alt ajan", "görev devret"]
            paralel_tetik = ["paralel", "aynÄ± anda", "eÅŸ zamanlÄ±", "beraber"]
            zincir_tetik = ["zincir", "sÄ±rayla", "ardÄ±ÅŸÄ±k", "adÄ±m adÄ±m"]

            # Mod belirle
            mod = None
            for t in tek_tetik:
                if t in hedef_lower:
                    mod = "TEK"
                    break
            if not mod:
                for t in zincir_tetik:
                    if t in hedef_lower:
                        mod = "ZINCIR"
                        break
            if not mod:
                for t in paralel_tetik:
                    if t in hedef_lower:
                        mod = "PARALEL"
                        break

            if not mod:
                return None  # Delegasyon gerekmiyor

            sistem = _delegasyon_sistemi_al()
            if sistem is None:
                return None

            if mod == "TEK":
                agent = sistem.delege_et(goal=hedef)
                if agent.basarili_mi():
                    return {
                        "basarili": True,
                        "mod": "TEK",
                        "yanit": agent.result,
                        "agent_id": agent.id,
                        "sure": agent.sure,
                    }
                return {
                    "basarili": False,
                    "mod": "TEK",
                    "hata": agent.error,
                    "agent_id": agent.id,
                }

            elif mod == "PARALEL":
                alt_gorevler = GorevAyristirici.ayir(hedef)
                if len(alt_gorevler) >= 2:
                    gorev_dicts = [
                        {"goal": a.goal, "context": a.context} for a in alt_gorevler[:3]
                    ]
                    agentler = sistem.paralel_delege(gorev_dicts)
                    basarili = sum(1 for a in agentler if a.basarili_mi())

                    if basarili > 0:
                        yanit_parts = [f"[Paralel {basarili}/{len(agentler)} baÅŸarÄ±lÄ±]"]
                        for a in agentler:
                            ikon = "âœ…" if a.basarili_mi() else "âŒ"
                            yanit_parts.append(
                                f"{ikon} {a.goal[:50]}: {a.result[:200]}"
                            )
                        return {
                            "basarili": True,
                            "mod": "PARALEL",
                            "yanit": "\n".join(yanit_parts),
                            "agentler": [a.id for a in agentler],
                        }
                else:
                    # Paralel için yeterli görev yok, TEK dene
                    agent = sistem.delege_et(goal=hedef)
                    if agent.basarili_mi():
                        return {
                            "basarili": True,
                            "mod": "TEK",
                            "yanit": agent.result,
                            "agent_id": agent.id,
                        }

            elif mod == "ZINCIR":
                alt_gorevler = GorevAyristirici.ayir(hedef)
                if len(alt_gorevler) >= 2:
                    adim_dicts = [
                        {"goal": a.goal, "context": a.context} for a in alt_gorevler
                    ]
                    agentler = sistem.zincir_delege(adim_dicts)
                    basarili = sum(1 for a in agentler if a.basarili_mi())

                    yanit_parts = [f"[Zincir {basarili}/{len(agentler)} adÄ±m baÅŸarÄ±lÄ±]"]
                    for i, a in enumerate(agentler, 1):
                        ikon = "âœ…" if a.basarili_mi() else "âŒ"
                        yanit_parts.append(f"AdÄ±m {i}: {ikon} {a.result[:200]}")
                    return {
                        "basarili": basarili > 0,
                        "mod": "ZINCIR",
                        "yanit": "\n".join(yanit_parts),
                        "agentler": [a.id for a in agentler],
                    }

            return None

        except Exception as e:
            logger.warning(f"[Delegasyon] Kontrol hatasÄ±: {e}")
            return None

    def _mcp_web_ara(self, sorgu: str, maks_sonuc: int = 3) -> Optional[str]:
        """MCP uzerinden web aramayi dene."""
        from reymen.cereyan.tools.web_search import mcp_web_ara
        return mcp_web_ara(
            sorgu, maks_sonuc,
            native_mcp=self._native_mcp if _MCP_NATIVE_AKTIF else None,
            mcp_client_get=_mcp_client_get if _MCP_CLIENT_AKTIF else None,
            mcp_istemci_get=_mcp_istemci_get if _MCP_TOOL_AKTIF else None,
        )


    def _web_ara(self, sorgu: str, maks_sonuc: int = 3) -> Optional[str]:
        """Web arama yap â€” MCP Firecrawl öncelikli, sonra SearchDispatcher.
        LLM atlanir, direkt web verisi kullanilir (halusinasyon onleme).
        Basarisiz olursa hata sayaci tutar, 3 hata sonra devre disi kalir.

        Kullanilabilir engine'ler: duckduckgo, google, bing, firecrawl,
        brave, searxng, exa, auto (config'e gore en iyisi).
        Ayrica MCP firecrawl/search sunucusu varsa once o denenir.
        """
        if not _WEB_ARAMA_AKTIF:
            return None
        # Circuit breaker: 3 hata sonra web aramayi kapat
        if hasattr(self, "_web_hata") and self._web_hata >= 3:
            return None
        try:
            # Ã–NCE: MCP Firecrawl / search dene (varsa)
            mcp_sonuc = self._mcp_web_ara(sorgu, maks_sonuc)
            if mcp_sonuc:
                self._web_hata = 0
                return mcp_sonuc

            # FALLBACK: SearchDispatcher (DDGS + FirecrawlEngine + ...)
            from reymen.arac.web_search_engine import _get_registry

            dispatcher = _get_registry()
            sonuc_str = dispatcher.ara(sorgu, engine="auto", max_sonuc=maks_sonuc)
        except Exception as _we:
            self._web_hata = getattr(self, "_web_hata", 0) + 1
            if self._web_hata >= 3:
                log.warning("Web arama 3 kez hata verdi - kalici olarak devre disi")
            return None

        if not sonuc_str or sonuc_str.strip() in (
            "",
            "Sonuc bulunamadi.",
            "[WEB_ARAMA] Kullanilabilir engine bulunamadi.",
        ):
            self._web_hata = getattr(self, "_web_hata", 0) + 1
            return None

        # Circuit breaker basarili aramada sifirlanir
        self._web_hata = 0

        # Sayfa icerigi ekstraksiyonu: ilk 1-2 sonucu fetch et
        try:
            import re as _re, urllib.request as _ur
            _ekstra_icerik = ""
            _url_sayisi = 0
            for _satir in sonuc_str.split("\n"):
                _url_m = _re.search(r"https?://[^\s\)\]]+", _satir)
                if _url_m:
                    _url = _url_m.group(0).rstrip(".,;)")
                    if _url_sayisi >= 2:
                        break
                    try:
                        _req = _ur.Request(
                            _url,
                            headers={
                                "User-Agent": (
                                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/120.0.0.0 Safari/537.36"
                                ),
                                "Accept": "text/html,application/xhtml+xml",
                                "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
                            },
                        )
                        _resp = _ur.urlopen(_req, timeout=8)
                        _html = _resp.read().decode("utf-8", errors="replace")
                        # HTML temizle
                        _text = _re.sub(r"<[^>]+>", " ", _html)
                        _text = _re.sub(r"\s+", " ", _text).strip()
                        # Fiyat/bilgi satirlarini filtrele
                        _fiyat_satirlari = []
                        for _cumle in _text.split(". "):
                            _cumle = _cumle.strip()
                            if len(_cumle) < 10 or len(_cumle) > 300:
                                continue
                            # Sayi + para birimi/eski/deger iceren cumleler
                            if _re.search(r"\d+[,.]\d{2}", _cumle) and _re.search(
                                r"(TL|USD|EUR|\$|£|altın|ons|fiyat|değer|deger|Alış|Satış|Fiyat)",
                                _cumle,
                                _re.IGNORECASE,
                            ):
                                _fiyat_satirlari.append(_cumle[:200])
                        if _fiyat_satirlari:
                            _ekstra_icerik += (
                                f"\n[SAYFA: {_url}]\n"
                                + "\n".join(_fiyat_satirlari[:5])
                                + "\n"
                            )
                        _url_sayisi += 1
                    except Exception:
                        pass
            if _ekstra_icerik:
                sonuc_str += "\n\n--- SAYFA ICERIKLERI ---" + _ekstra_icerik
        except Exception:
            pass

        return sonuc_str

    def _mcp_motor_kaydet(self) -> None:
        """Native MCP Client tool'larini motora kaydet."""
        if not self.motor or not hasattr(self.motor, "_plugin_arac_kaydet"):
            return
        if not self._native_mcp:
            return
        try:
            self._native_mcp._motor_ref = self.motor
            self._native_mcp._kesfedildi = False
            # native_mcp_client'Ä±n motor_kaydet() metodunu çaÄŸÄ±r
            if hasattr(self._native_mcp, "motor_kaydet"):
                self._native_mcp.motor_kaydet(self.motor)
            else:
                # Manuel kayÄ±t
                for ad, baglanti in self._native_mcp._baglantilar.items():
                    for arac in baglanti.araclar:
                        arac_adi = f"MCP_{ad.upper()}_{arac['name'].upper()}"

                        def _fn(sun=ad, ar=arac["name"], **kw):
                            return baglanti.arac_cagir(ar, kw)

                        try:
                            self.motor._plugin_arac_kaydet(
                                arac_adi,
                                _fn,
                                arac.get("description", f'MCP: {ad}/{arac["name"]}'),
                            )
                        except Exception as _e:
                            log.warning(
                                "[MCP] Tool kayit hatasi (%s): %s", arac_adi, _e
                            )
        except Exception as _mcp_e:
            log.warning("[MCP] Motor kayit hatasi: %s", _mcp_e)

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # YARDIMCI METODLAR â€” run_conversation
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _budget_olustur(self, hedef: str) -> Any:
        """IterationBudget olustur; modul yoksa basit sayac doner."""
        return budget_olustur(hedef, max_tur=self.max_tur)

    # â”€â”€ Session Search Kaydet â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _session_search_kaydet(
        self, session_id: Optional[str], message: str, role: str = "user"
    ) -> None:
        """Session Search FTS5'e mesaj kaydet (guvenli)."""
        if (
            not _SESSION_SEARCH_AKTIF
            or not self._session_search
            or not session_id
            or not message
        ):
            return
        try:
            self._session_search.save(session_id, message, role)
        except Exception as _ss_e:
            log.debug("[SESSION_SEARCH] Kayit hatasi: %s", _ss_e)
        # Session messages tablosuna da kaydet (ID=26 fix) â€” mesaj_ekle() ile
        try:
            if not hasattr(self, "_session_ekleme_storage") or self._session_ekleme_storage is None:
                _db_yol = str(Path(__file__).parent.parent.parent.parent / "merkez_db" / "session.db")
                from reymen.hafiza.session_db import AdvancedSessionStorage
                self._session_ekleme_storage = AdvancedSessionStorage(_db_yol)
            self._session_ekleme_storage.mesaj_ekle(session_id, role, message)
        except Exception as _sm_e:
            log.debug("[SESSION_MSGS] mesaj_ekle hatasi: %s", _sm_e)

    def _hata_cozumle(self, hata_metni: str, kaynak: str = "genel") -> None:
        """Hata aninda Reasoning-Core'u tetikle.

        conversation_loop icinden cagrilir: API hatasi, bos yanit, tool hatasi.
        reasoning_loop yoksa / calismazsa sessizce gec (ana akis bozulmasin).
        """
        if not _REASONING_AKTIF or _reasoning_loop is None:
            return
        try:
            # DURUM_OKU icin ortak_komut.guncelle() ciktisini kullan
            from reymen.sistem.ortak_komut import guncelle as _ortak_guncelle

            durum = _ortak_guncelle()
            durum_ozeti = str(durum)[:2000]

            # fallback_providers'i config.yaml'dan oku
            import yaml as _yaml

            cfg_yol = Path(__file__).parent.parent.parent / "config.yaml"
            if cfg_yol.exists():
                cfg = _yaml.safe_load(cfg_yol.read_text(encoding="utf-8"))
                fallback = cfg.get("fallback_providers", [])
            else:
                fallback = []

            _reasoning_loop(
                hata_metni=hata_metni,
                durum_ozeti=durum_ozeti,
                bot_adi="reymen_agent",
                fallback_providers=fallback,
            )
        except Exception as _rh:
            log.debug("[Reasoning-Core] Atlandi: %s", _rh)

    def _sistem_promptu_olustur(self, hedef: str, baglam: Optional[dict] = None) -> str:
        """PromptBuilder ile sistem promptu insa et."""
        from reymen.cereyan.prompt_assembly import sistem_promptu_olustur as _spo
        return _spo(hedef, baglam, motor=self.motor)

    def _profil_bilgisi_al(self) -> str:
        """MEMORY.md + USER.md profil bilgisi."""
        from reymen.cereyan.prompt_assembly import profil_bilgisi_al as _pba
        return _pba()

    def _provider_tipi_belirle(self, provider: Optional[str] = None) -> str:
        """Provider tipini belirle."""
        kaynak = (
            provider
            or (getattr(self.beyin, "provider", None) if self.beyin else None)
            or ""
        ).lower()
        if kaynak in ("anthropic", "claude", "bedrock"):
            return "anthropic"
        if kaynak in ("codex", "codex_responses", "o4", "o3", "o1"):
            return "codex"
        return "chat_completions"

    def _context_preflight(
        self, mesajlar: list, sistem_prompt: str, provider_tipi: Optional[str] = None
    ) -> list:
        """Context doluluk oranini kontrol et, asimi varsa sikistir."""
        return context_preflight(
            mesajlar, sistem_prompt, provider_tipi,
            provider_limits=PROVIDER_LIMITS,
            provider_limit_varsayilan=PROVIDER_LIMIT_VARSAYILAN,
            context_sikistirma_esigi=CONTEXT_SIKISTIRMA_ESIGI,
            compressor=_Compressor() if _COMPRESS_AKTIF else None,
            hook_sikistirma_tetikle=_context_sikistirma_tetikle if _HOOK_AKTIF else None,
        )

    def _api_mesajlari_olustur(
        self,
        sistem_prompt: str,
        gecmis: list,
        provider_tipi: str,
    ) -> List[dict]:
        """Provider tipine gore API mesaj listesi olustur."""
        return api_mesajlari_olustur(sistem_prompt, gecmis, provider_tipi)

    def _ephemeral_layerlar_ekle(
        self,
        mesajlar: List[dict],
        budget: Any,
        gecmis_uzunlugu: int,
    ) -> List[dict]:
        """Butce uyarisi ve context baskisi ephemeral katmanlari ekle."""
        uyarilar: list[str] = []

        kalan = getattr(budget, "kaldi", None)
        if kalan is None:
            kalan = getattr(budget, "max_tur", 0) - getattr(budget, "tur", 0)

        if kalan is not None and kalan <= 3:
            uyarilar.append(
                f"[UYARI] Kalan tur: {kalan}. "
                "Hedefe hemen odaklan veya GOREV_BITTI yaz."
            )

        if gecmis_uzunlugu > 20:
            uyarilar.append(
                f"[BAGLAM] Gecmis {gecmis_uzunlugu} mesaj. " "Ozlu yaz, tekrar etme."
            )

        if not uyarilar:
            return mesajlar

        icerik = "\n".join(uyarilar)
        return mesajlar + [{"role": "user", "content": icerik}]

    def _prompt_caching_ekle(self, mesajlar: List[dict]) -> List[dict]:
        """Provider'a gore prompt caching stratejisini uygula.

        - Anthropic: cache_control marker'lari (system + son 3 mesaj)
        - OpenRouter: x-request-prompt-caching header + marker'lar
        - OpenAI: otomatik prefix caching
        - DeepSeek: context caching marker'lari
        - Diger: ``_use_prompt_caching`` aktifse Anthropic formati dene
        """
        try:
            # Dinamik _CACHING_AKTIF kontrolu
            if _CACHING_AKTIF is None:
                # Provider'a gore hesapla â€” su an icin True kabul et
                # (cogu modern provider otomatik prefix caching yapar)
                caching_aktif = True
            else:
                caching_aktif = _CACHING_AKTIF

            if not caching_aktif:
                return mesajlar

            # Yeni coklu-provider fonksiyonunu dene
            if _prompt_caching_ekle is not None:
                try:
                    return _prompt_caching_ekle(self, mesajlar)
                except Exception as _e:
                    logger.warning(
                        "[ConversationLoop] except Exception (L1117): %s", Exception
                    )
                    pass

            # Geriye uyumluluk: eski Anthropic yontemi
            if _apply_anthropic_cache_control:
                return _apply_anthropic_cache_control(
                    mesajlar, cache_ttl="5m", native_anthropic=False
                )
            return mesajlar
        except Exception as e:
            log.warning("Prompt caching hatasi: %s", e)
            return mesajlar

    def _direct_api_call(
        self, mesajlar: List[dict], tools_bos: bool = False,
        session_id: Optional[str] = None
    ) -> Optional[dict]:
        """Dogrudan OpenAI SDK ile API cagrisi."""
        from reymen.cereyan.api_caller import direct_api_call
        return direct_api_call(
            mesajlar, tools_bos=tools_bos, session_id=session_id,
            context_budget_chars=self._context_budget_chars,
            beyin=self.beyin,
        )


    def _interruptible_api_call(
        self, mesajlar: List[dict], provider_tipi: str
    ) -> Optional[dict]:
        """Thread bazli interruptible API cagri (Ctrl+C destekli).

        Beyin modulu yoksa direkt OpenAI SDK ile DeepSeek API cagrisi yapar.
        """
        if not self.beyin:
            log.debug("Beyin yok â€” direkt OpenAI SDK kullaniliyor")
            return self._direct_api_call(mesajlar)

        sonuc_kutusu: list = [None]
        hata_kutusu: list = [None]

        def _cagir() -> None:
            try:
                # Sistem ve kullanici mesajlarini ayir
                sistem = ""
                kullanici_mesajlari = []
                for m in mesajlar:
                    if m.get("role") == "system":
                        sistem = m.get("content", "")
                    else:
                        kullanici_mesajlari.append(m)

                if not kullanici_mesajlari:
                    kullanici_mesajlari = [{"role": "user", "content": "devam"}]

                # uret_v2 önceliÄŸi: beyin'de varsa ve motor tools saÄŸlÄ±yorsa kullan
                _kullan_v2 = (
                    hasattr(self.beyin, "uret_v2")
                    and self.motor is not None
                    and hasattr(self.motor, "_plugin_araclar")
                )
                if _kullan_v2:
                    tools = motor_tools_schema_al(self.motor)
                    if tools:
                        sonuc_kutusu[0] = self.beyin.uret_v2(
                            sistem, kullanici_mesajlari, tools=tools
                        )
                        return

                if hasattr(self.beyin, "uret"):
                    yanit_metin = self.beyin.uret(sistem, kullanici_mesajlari)
                    sonuc_kutusu[0] = {
                        "role": "assistant",
                        "content": yanit_metin or "",
                    }
                else:
                    hata_kutusu[0] = RuntimeError("Beyin.uret() metodu bulunamadi")
            except Exception as exc:
                hata_kutusu[0] = exc

        t = threading.Thread(target=_cagir, daemon=True)
        t.start()

        try:
            t.join(timeout=300)  # 5 dakika max
        except KeyboardInterrupt:
            self._iptal_istegi = True
            raise

        if not t.is_alive() and hata_kutusu[0]:
            log.error("API cagri hatasi: %s", hata_kutusu[0])
            return None

        return sonuc_kutusu[0]

    def _tool_calls_al(self, yanit: dict) -> List[dict]:
        """Yanit dict'inden tool call'lari cikar."""
        from reymen.cereyan.tools.parser import tool_calls_al as _tca
        return _tca(yanit)

    def _yanit_icerigi_al(self, yanit: dict) -> str:
        """Yanit dict'inden metin icerigi cikar."""
        from reymen.cereyan.tools.parser import yanit_icerigi_al as _yia
        return _yia(yanit)

    def _yanit_temizle(self, metin: str) -> str:
        """DUSUN/EYLEM gibi ic dusunce bloklarini temizle, GOREV_BITTI icindeki metni cikar."""
        from reymen.cereyan.tools.parser import yanit_temizle as _yt
        return _yt(metin)

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # MEVCUT YARDIMCI METODLAR (coz() icin)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _beyin_eylem_sec(self, hedef: str, baglam: Optional[dict] = None) -> dict:
        """Beyin modulunu kullanarak bir sonraki eylemi sec."""
        try:
            if hasattr(self.beyin, "sihirbaz_karar"):
                return self.beyin.sihirbaz_karar(hedef, baglam)
            return {"tur": "mesaj", "icerik": "Beyin karar veremedi"}
        except Exception as e:
            return {"tur": "hata", "icerik": str(e)}

    def _arac_calistir(self, eylem: dict) -> dict:
        """Bir araci calistir ve sonucu dondur. tools/tool_executor.py'ye yonlendirir."""
        from reymen.cereyan.tools.tool_executor import execute_tool

        return execute_tool(
            eylem,
            motor=self.motor,
            web_ara_fn=self._web_ara,
            once_hafiza_fn=_hafizada_ara if _ONCE_HAFIZA_AKTIF else None,
            oncelik_cache=ONCELIK_CACHE,
            mcp_catalog_run=_mcp_catalog_run if _MCP_CATALOG_AKTIF else None,
            mcp_client_listele=_mcp_client_listele if _MCP_CLIENT_AKTIF else None,
            mcp_client_baglan=_mcp_client_baglan if _MCP_CLIENT_AKTIF else None,
            mcp_catalog_aktif=_MCP_CATALOG_AKTIF,
            mcp_client_aktif=_MCP_CLIENT_AKTIF,
            once_hafiza_aktif=_ONCE_HAFIZA_AKTIF,
            rules_engine=_RULES_ENGINE,
            rules_aktif=_RULES_AKTIF,
            hata_cozumle_fn=self._hata_cozumle,
        )

    def durum(self) -> str:
        """Dongu durumunu dondur."""
    def durum(self) -> str:
        """Dongu durumunu dondur."""
        from reymen.cereyan.stats import loop_durum
        return loop_durum(self._durum)

    def istatistik(self) -> dict:
        """Dongu istatistiklerini dondur."""
        from reymen.cereyan.stats import loop_istatistik
        return loop_istatistik(self._durum, self.max_tur, self.tur_yoneticisi)

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # YENÄ° METODLAR â€” ReYMeN Agent seviyesi
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def set_stream_callback(self, callback: Any) -> None:
        """Stream callback fonksiyonu ata.
        callback(text: str) -> None seklinde cagrilir.
        """
        self._stream_callback = callback

    def _streaming_api_call(
        self, mesajlar: List[dict], provider: str, task_id: str, budget: Any
    ) -> Optional[dict]:
        """Streaming API cagrisi. ReYMeN Agent streaming pattern'i."""
        if not self.beyin:
            return self._interruptible_api_call(mesajlar, provider)
        try:
            tam_yanit = ""
            for chunk in self.beyin.uret_stream(mesajlar):
                if chunk:
                    tam_yanit += chunk
                    if self._stream_callback:
                        try:
                            self._stream_callback(chunk)
                        except Exception as _e:
                            logger.warning(
                                "[ConversationLoop] except Exception (L1346): %s",
                                Exception,
                            )
                            pass
            return {
                "choices": [{"message": {"role": "assistant", "content": tam_yanit}}]
            }
        except NotImplementedError:
            return self._interruptible_api_call(mesajlar, provider)
        except Exception as e:
            log.warning("Streaming hatasi (fallback): %s", e)
            return self._interruptible_api_call(mesajlar, provider)

    def _error_classify(self, hata: Exception, task_id: str) -> str:
        """Hatayi siniflandir. ReYMeN Agent FailoverReason pattern'i.
        Returns: 'retry' | 'abort' | 'compress' | 'rotate'
        """
        # GeliÅŸmiÅŸ sÄ±nÄ±flandÄ±rÄ±cÄ± varsa kullan
        if _HATA_SINIFLANDIRICI_AKTIF and api_hatasini_siniflandir is not None:
            try:
                sinif = api_hatasini_siniflandir(hata)
                neden = sinif.neden
                if neden == FailoverReason.context_overflow:
                    return "compress"
                if neden in {
                    FailoverReason.auth,
                    FailoverReason.auth_permanent,
                    FailoverReason.billing,
                    FailoverReason.model_not_found,
                    FailoverReason.provider_policy_blocked,
                }:
                    return "rotate"
                if neden == FailoverReason.content_policy_blocked:
                    return "abort"
                if neden == FailoverReason.format_error:
                    return "abort" if not sinif.yeniden_denenebilir else "retry"
                return "retry"
            except Exception as _e:
                __import__("logging").getLogger(__name__).warning(
                    "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                )  # SÄ±nÄ±flandÄ±rÄ±cÄ± baÅŸarÄ±sÄ±z â†’ basit fallback

        # Basit fallback (sÄ±nÄ±flandÄ±rÄ±cÄ± yoksa)
        hata_str = str(hata).lower()
        if any(t in hata_str for t in ("timeout", "timed out", "connection")):
            return "retry"
        if any(t in hata_str for t in ("429", "rate limit", "too many requests")):
            return "retry"
        if any(t in hata_str for t in ("401", "403", "auth", "unauthorized")):
            return "rotate"
        if any(
            t in hata_str for t in ("402", "billing", "insufficient_quota", "payment")
        ):
            return "rotate"
        if any(
            t in hata_str for t in ("context_length", "too large", "maximum context")
        ):
            return "compress"
        if any(t in hata_str for t in ("500", "502", "503", "internal", "overloaded")):
            return "retry"
        return "retry"

    def circuit_breaker_durum(self) -> dict:
        """Circuit breaker durum raporu."""
        return {
            "acik": self._cb_acik,
            "ardisik_hata": self._cb_art_arda_hata,
            "max_hata": CIRCUIT_BREAKER_MAX_HATA,
            "sure": CIRCUIT_BREAKER_SURESI,
            "kalan": max(
                0, CIRCUIT_BREAKER_SURESI - (time.time() - self._cb_son_hata_zamani)
            )
            if self._cb_acik
            else 0,
        }

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # RETRY â€” exponential backoff (ReYMeN Agent pattern)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _api_call_with_retry(
        self,
        api_mesajlari: List[dict],
        provider_tipi: str,
        task_id: str,
        budget: Any,
    ) -> Optional[dict]:
        """API cagrisini exponential backoff ile retry eder.

        _error_classify 'retry' dondugunde bekler ve tekrar dener.
        _error_classify 'rotate' dondugunde provider degistirir (fallback).
        Max 3 retry, backoff: 1sn, 2sn, 4sn.
        ReYMeN Agent retry pattern ile uyumlu calisir.

        Provider rotate: beyin'in _fallback_zinciri'ndeki siradaki
        saglayiciya gecer. Zincirdeki tum saglayicilar basarisizsa None doner.

        Args:
            api_mesajlari: Provider'a ozel mesaj listesi.
            provider_tipi: Provider turu (anthropic/codex/chat_completions).
            task_id:       Mevcut gorev ID'si (log icin).
            budget:        IterationBudget nesnesi.

        Returns:
            API yaniti (dict) veya None (tum retry'ler basarisiz).
        """
        max_retry = 3
        # Provider rotate icin fallback zincirini hazirla
        fallback_providerlar: list[tuple[str, str]] = []  # (tip, ad)
        if self.beyin and hasattr(self.beyin, "_fallback_zinciri"):
            for adim in self.beyin._fallback_zinciri:
                p_tip = self._provider_tipi_belirle(adim.provider)
                fallback_providerlar.append((p_tip, adim.provider))

        # Su anki provider tipini ilk adim olarak ekle
        mevcut_tip = provider_tipi
        mevcut_index = 0

        # -- Circuit breaker kontrolü ---------------------------------
        if self._cb_acik:
            if (
                CIRCUIT_BREAKER_SURESI > 0
                and (time.time() - self._cb_son_hata_zamani) > CIRCUIT_BREAKER_SURESI
            ):
                # Automatic reset: süre dolmuÅŸsa sÄ±fÄ±rla
                self._cb_acik = False
                self._cb_art_arda_hata = 0
                log.info(
                    "[%s] Circuit breaker otomatik sifirlandi (sure dustu)", task_id
                )
            elif CIRCUIT_BREAKER_KALICI:
                log.error(
                    "[%s] Circuit breaker ACIK (kalici kilit, %d hata)",
                    task_id,
                    self._cb_art_arda_hata,
                )
                return None
            else:
                log.error(
                    "[%s] Circuit breaker ACIK (manual reset bekleniyor)", task_id
                )
                return None

        # API'ye göndermeden önce mesaj geçmiÅŸini onar
        if _MESAJ_TAMIRCI_AKTIF and mesaj_siralamasi_tamir_et is not None:
            try:
                n_tamirler = mesaj_siralamasi_tamir_et(api_mesajlari)
                if n_tamirler:
                    log.debug(
                        "[%s] Mesaj sÄ±ralamasÄ± tamiri: %d düzeltme", task_id, n_tamirler
                    )
                n_arg_tamirler = arac_cagri_argumanlarini_temizle(
                    api_mesajlari, oturum_id=task_id
                )
                if n_arg_tamirler:
                    log.debug(
                        "[%s] Araç argümanÄ± tamiri: %d düzeltme",
                        task_id,
                        n_arg_tamirler,
                    )
            except Exception as _e:
                log.debug("[%s] Mesaj tamiri baÅŸarÄ±sÄ±z (devam): %s", task_id, _e)

        for deneme in range(max_retry + 1):
            try:
                if STREAMING_AKTIF and self._stream_callback:
                    yanit = self._streaming_api_call(
                        api_mesajlari,
                        mevcut_tip,
                        task_id,
                        budget,
                    )
                else:
                    yanit = self._interruptible_api_call(api_mesajlari, mevcut_tip)

                # Beyin yoksa (offline/test modu) retry yapma
                if yanit is None and self.beyin is None:
                    return None

                # Basarili yanit
                if yanit is not None:
                    return yanit

                # yanit None ama beyin var -> hata olarak ele al
                raise RuntimeError("API yanit vermedi (None)")

            except KeyboardInterrupt:
                raise
            except Exception as e:
                # Circuit breaker: ardÄ±ÅŸÄ±k hata sayacÄ±nÄ± artÄ±r
                self._cb_art_arda_hata += 1
                self._cb_son_hata_zamani = time.time()
                if self._cb_art_arda_hata >= CIRCUIT_BREAKER_MAX_HATA:
                    self._cb_acik = True
                    log.error(
                        "[%s] Circuit breaker DEVREDE (%d/%d hata) - kalici kilit",
                        task_id,
                        self._cb_art_arda_hata,
                        CIRCUIT_BREAKER_MAX_HATA,
                    )
                sinif = self._error_classify(e, task_id)
                # Hook: hata olayÄ±
                if _HOOK_AKTIF and _hata_tetikle is not None:
                    try:
                        _hata_tetikle(
                            hata=e,
                            olay_baglami=f"api_retry deneme={deneme+1} sinif={sinif}",
                            task_id=task_id,
                        )
                    except Exception:
                        logger.warning("[fix_01_sessiz_except] Exception")
                if sinif == "abort" or deneme >= max_retry:
                    log.error(
                        "[%s] API cagri hatasi (%d/%d deneme, sinif=%s): %s",
                        task_id,
                        deneme + 1,
                        max_retry + 1,
                        sinif,
                        e,
                    )
                    # Provider rotate dene (abort bile olsa zincirde baska provider varsa)
                    if sinif == "rotate" or sinif == "abort":
                        yeni_tip, yeni_provider = self._provider_rotate(
                            mevcut_tip,
                            fallback_providerlar,
                            mevcut_index,
                            task_id,
                        )
                        if yeni_tip != mevcut_tip:
                            mevcut_tip = yeni_tip
                            mevcut_index += 1
                            # API mesajlarini yeni provider icin yeniden olustur
                            api_mesajlari = self._api_mesajlari_olustur(
                                self._sistem_promptu_olustur(
                                    getattr(budget, "_hedef", ""),
                                ),
                                self._konusma_gecmisi,
                                mevcut_tip,
                            )
                            log.info(
                                "[%s] Provider rotate: %s -> %s (devam)",
                                task_id,
                                fallback_providerlar[mevcut_index - 1][1]
                                if mevcut_index - 1 < len(fallback_providerlar)
                                else "?",
                                yeni_provider,
                            )
                            continue  # yeni provider ile tekrar dene
                    return None

                # 'retry' veya 'compress' â€” bekle ve tekrar dene
                if sinif == "compress":
                    # Context sikistirma iste: mesajlari yariya indir
                    log.warning(
                        "[%s] Context compression gerekiyor â€” mesajlar yarilaniyor",
                        task_id,
                    )
                    if len(api_mesajlari) > 4:
                        api_mesajlari = (
                            api_mesajlari[:2]
                            + api_mesajlari[-(len(api_mesajlari) // 2) :]
                        )

                bekle = 2**deneme  # 1sn, 2sn, 4sn
                log.warning(
                    "[%s] API cagri basarisiz (deneme %d/%d). "
                    "%d saniye sonra tekrar deneniyor... (sebep: %s, sinif: %s)",
                    task_id,
                    deneme + 1,
                    max_retry + 1,
                    bekle,
                    e,
                    sinif,
                )
                time.sleep(bekle)

        log.error(
            "[%s] Tum %d retry denemesi basarisiz",
            task_id,
            max_retry + 1,
        )
        return None

    def _provider_rotate(
        self,
        mevcut_tip: str,
        fallback_providerlar: List[Tuple[str, str]],
        mevcut_index: int,
        task_id: str,
    ) -> Tuple[str, str]:
        """Fallback zincirinde siradaki provider'a gecer.

        Args:
            mevcut_tip: Su anki provider tipi.
            fallback_providerlar: (tip, ad) tuple listesi.
            mevcut_index: Su anki index.
            task_id: Log icin task ID.

        Returns:
            (yeni_tip, yeni_provider_adi) â€” bulunamazsa (mevcut_tip, "?").
        """
        if mevcut_index + 1 < len(fallback_providerlar):
            yeni_tip, yeni_ad = fallback_providerlar[mevcut_index + 1]
            log.info(
                "[%s] Provider rotate: %s -> %s",
                task_id,
                fallback_providerlar[mevcut_index][1]
                if mevcut_index < len(fallback_providerlar)
                else "?",
                yeni_ad,
            )
            return yeni_tip, yeni_ad
        return mevcut_tip, "?"

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SESSION CONTEXT INJECTION â€” onceki session ozetleri
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _session_context_injection(
        self,
        session_id: str,
        storage: Any,
        max_onceki: int = 3,
    ) -> str:
        """Onceki session ozetlerini alip baglam metni olarak doner.

        Session storage'dan onceki session'larin ozet/sonuc bilgilerini
        ceker ve konusma gecmisine eklenecek bir baglam metni olusturur.

        Args:
            session_id: Mevcut session ID (kendini disarda birakir).
            storage:    SessionStorage instance (_SessionStorage).
            max_onceki: Kac onceki session alinacak (default: 3).

        Returns:
            Baglam metni. Hata durumunda veya session yoksa bos string.
        """
        if not storage or not session_id:
            return ""

        try:
            # Farkli storage API'lerini dene
            if hasattr(storage, "session_gecmisi_al"):
                oncekiler = storage.session_gecmisi_al(
                    limit=max_onceki,
                    exclude_current=session_id,
                )
            elif hasattr(storage, "session_listele"):
                tumu = storage.session_listele(limit=max_onceki + 1)
                oncekiler = [s for s in tumu if s.get("session_id") != session_id][
                    :max_onceki
                ]
            else:
                return ""
        except Exception as e:
            log.warning(
                "[session=%s] Session gecmisi alinirken hata: %s",
                session_id,
                e,
            )
            return ""

        if not oncekiler:
            return ""

        satirlar = ["[Onceki Session Ozetleri]", ""]
        for s in oncekiler[:max_onceki]:
            sid = s.get("session_id") or s.get("id", "?")
            ozet = (
                s.get("ozet")
                or s.get("summary")
                or s.get("system_prompt", "")
                or s.get("hedef", "")
            )
            sonuc = s.get("sonuc") or s.get("result") or ""
            durum = s.get("end_reason") or s.get("durum", "")

            satirlar.append(f"- Session {sid}: {str(ozet)[:200]}")
            if sonuc:
                satirlar.append(f"  Sonuc: {str(sonuc)[:100]}")
            if durum:
                satirlar.append(f"  Durum: {durum}")

        satirlar.append("")
        baglam_metni = "\n".join(satirlar)
        log.info(
            "[session=%s] Session context injection: %d onceki session eklendi",
            session_id,
            len(oncekiler[:max_onceki]),
        )
        return baglam_metni

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SOUL.md + AGENTS.md ENJEKSIYONU (ReYMeN stili)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _soul_bilgisi_al(self) -> str:
        """SOUL.md icerigini oku."""
        from reymen.cereyan.prompt_assembly import soul_bilgisi_al as _sba
        return _sba()

    def _agents_bilgisi_al(self) -> str:
        """AGENTS.md icerigini oku."""
        from reymen.cereyan.prompt_assembly import agents_bilgisi_al as _aba
        return _aba()

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # SKILL TARAMA
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _skill_tara(self, query: str, maks: int = 3) -> str:
        """Skills/ icinde SKILL.md dosyalarinda query ara, eslesenleri don.

        Dogru yol: reymen/cereyan/skills/ (reymen/skills/ DEGIL).
        Alt dizinlerde recursive ara (ceil yapisi).
        """
        try:
            kok = Path(__file__).parent.parent
            # once reymen/cereyan/skills/ dene
            sd = kok / "cereyan" / "skills"
            if not sd.exists():
                sd = kok / "skills"  # fallback
            if not sd.exists():
                return ""
            eslesen = []
            # Recursive search with rglob for .md files
            for f in sorted(sd.rglob("*.md")):
                if f.name == "README.md" or f.name == "PATHS.md":
                    continue
                icerik = f.read_text(encoding="utf-8", errors="replace")[:500]
                if query.lower() in icerik.lower():
                    baslik = f.stem.replace("_SKILL", "").replace(".md", "")
                    eslesen.append(f"- {baslik}: {icerik[:100].strip()}")
                    if len(eslesen) >= maks:
                        break
            return "\n".join(eslesen) + "\n" if eslesen else ""
        except Exception:
            return ""

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TOOL ROUTING
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _tool_routing(self, query: str) -> str:
        """Sorgu tipini siniflandir: selam/soru/web/komut/kod/genel."""
        q = query.strip().lower()
        if len(q) <= 3:
            return "selam"
        if any(
            k in q
            for k in ("kimdir", "nedir", "ne demek", "nasil", "ne zaman", "nerede")
        ):
            return "soru"
        if any(
            k in q
            for k in ("haber", "2026", "dunya", "guncel", "fiyat", "dolar", "altin")
        ):
            return "web"
        if any(
            k in q
            for k in (
                "yap",
                "olustur",
                "calistir",
                "indir",
                "kur",
                "goster",
                "yaz",
                "kod",
            )
        ):
            return "komut"
        if any(
            k in q for k in ("hata", "calismiyor", "olmadi", "bozuk", "duzelt", "fix")
        ):
            return "kod"
        return "genel"

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # ALT AJAN
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _alt_ajan(self, gorev: str, timeout: int = 30) -> str:
        """Basit alt ajan: ayri Python prosesinde gorev calistir."""
        import subprocess as _sp

        try:
            r = _sp.run(
                [sys.executable, "-c", f"print('Alt ajan: {gorev}', flush=True)"],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return (r.stdout or r.stderr).strip()[:500]
        except Exception as e:
            return f"HATA: {e}"

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # FRAMEWORK ADAPTOR (LangGraph / CrewAI / AutoGen)
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def _framework_calistir(self, framework: str, **kwargs) -> Dict[str, Any]:
        """Framework adaptorunu kullanarak islem yap.

        Args:
            framework: 'langgraph' | 'crewai' | 'autogen'
            **kwargs: Framework'e ozgu parametreler

        Returns:
            dict: Islem sonucu
        """
        try:
            if not _FRAMEWORK_ADAPTOR_AKTIF or not _framework_adaptor:
                return {"hata": "Framework adaptor yuklu degil", "sonuc": None}

            fw = framework.lower().strip()
            if fw == "langgraph":
                return _framework_adaptor.langgraph_calistir(
                    kwargs.get("graph"),
                    kwargs.get("inputs"),
                    kwargs.get("config"),
                )
            elif fw == "crewai":
                return _framework_adaptor.crewai_calistir(
                    kwargs.get("crew"),
                    kwargs.get("inputs"),
                )
            elif fw == "autogen":
                return _framework_adaptor.autogen_agent_calistir(
                    kwargs.get("agent"),
                    kwargs.get("mesaj", ""),
                )
            else:
                return {"hata": f"Bilinmeyen framework: {fw}", "sonuc": None}
        except Exception as e:
            logger.error("[Framework] Calistirma hatasi: %s", e)
            return {"hata": str(e), "sonuc": None}

    def _framework_durum(self) -> Dict[str, bool]:
        """Framework adaptor durumunu don."""
        try:
            if _FRAMEWORK_ADAPTOR_AKTIF and _framework_adaptor:
                return _framework_adaptor.aktif_frameworkler
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return {"langgraph": False, "crewai": False, "autogen": False}


# â”€â”€ CLI girdi noktasi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def run(**kwargs: Any) -> str:
    """CLI giris noktasi."""
    islem = kwargs.get("islem", "test")
    hedef = kwargs.get("hedef", "test")

    loop = ConversationLoop()
    if islem == "coz":
        sonuc = loop.coz(hedef)
        return json.dumps(sonuc, ensure_ascii=False)
    elif islem == "run":
        sonuc = loop.run_conversation(hedef)
        return json.dumps(sonuc, ensure_ascii=False)
    elif islem == "durum":
        return json.dumps(loop.istatistik(), ensure_ascii=False)
    else:
        return json.dumps(
            {"durum": "hazir", "mesaj": f"{islem} test"},
            ensure_ascii=False,
        )


# â”€â”€ Motor entegrasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def motor_kaydet(motor) -> None:
    """ConversationLoop'u motor'a tool olarak kaydet."""
    try:

        def _konusma_baslat(hedef: str, provider: str = "deepseek") -> str:
            """ConversationLoop ile bir konusma baslat."""
            from reymen.cereyan.conversation_loop import ConversationLoop as _CL

            try:
                cl = _CL(motor=motor, max_tur=5)
                sonuc = cl.run_conversation(hedef=hedef, provider=provider)
                if sonuc.get("basarili"):
                    return sonuc.get("yanit") or sonuc.get("sonuc", "")
                return "HATA: " + str(sonuc.get("hata", "Bilinmeyen hata"))
            except Exception as e:
                return "HATA: " + str(e)

        motor._plugin_arac_kaydet(
            "CONVERSATION_SOR",
            _konusma_baslat,
            "ConversationLoop ile kullanici sorusunu 5 kaynakli ensemble ile yanitla. "
            "Parametre: hedef (soru metni), provider (deepseek/xiaomi/xai/openrouter/...). "
            "OnceHafiza + web arama + cache + DeepSeek karsilastirmasi yapar.",
        )

        # Framework adaptor araclari (opsiyonel)
        try:
            if _FRAMEWORK_ADAPTOR_AKTIF and _framework_adaptor:
                fw_durum = _framework_adaptor.aktif_frameworkler

                if fw_durum.get("langgraph"):
                    motor._plugin_arac_kaydet(
                        "LANGGRAPH_CALISTIR",
                        lambda g, i=None, c=None: _framework_adaptor.langgraph_calistir(
                            g, i, c
                        ),
                        "LangGraph StateGraph calistir. Parametre: g=graph, i=inputs(dict), c=config(dict).",
                    )

                if fw_durum.get("crewai"):
                    motor._plugin_arac_kaydet(
                        "CREWAI_CALISTIR",
                        lambda c, i=None: _framework_adaptor.crewai_calistir(c, i),
                        "CrewAI Crew calistir. Parametre: c=crew, i=inputs(dict).",
                    )

                if fw_durum.get("autogen"):
                    motor._plugin_arac_kaydet(
                        "AUTOGEN_CALISTIR",
                        lambda a, m="": _framework_adaptor.autogen_agent_calistir(a, m),
                        "AutoGen agent calistir. Parametre: a=agent, m=mesaj(str).",
                    )
        except Exception as _e:
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] Framework tool kayit: %%s", type(_e).__name__
            )
    except Exception as _e:
        __import__("logging").getLogger(__name__).warning(
            "[SessizExcept] %%s: %%s", type(_e).__name__, _e
        )


# ── Out-of-band iptal sinyali gonderme ──────────────────────────────
from reymen.cereyan.signal import iptal_sinyali_gonder


if __name__ == "__main__":
    import sys

    print("=== ConversationLoop Basit Test ===")

    # --- Test 1: coz() eski API ---
    loop = ConversationLoop(motor=None, beyin=None, max_tur=3)
    s = loop.coz("test hedef")
    assert isinstance(s, dict), "coz() dict donmeli"
    assert s["hedef"] == "test hedef"
    print(f"coz() OK: basarili={s['basarili']}, tur={s['turlar']}")

    # --- Test 2: run_conversation() yeni API ---
    loop2 = ConversationLoop(max_tur=2)
    s2 = loop2.run_conversation("dosya olustur", provider="lmstudio")
    assert isinstance(s2, dict), "run_conversation() dict donmeli"
    assert "task_id" in s2
    assert "budget" in s2
    print(f"run_conversation() OK: task_id={s2['task_id']}, tur={s2['turlar']}")

    # --- Test 3: provider tipi ---
    loop3 = ConversationLoop()
    assert loop3._provider_tipi_belirle("anthropic") == "anthropic"
    assert loop3._provider_tipi_belirle("codex") == "codex"
    assert loop3._provider_tipi_belirle("deepseek") == "chat_completions"
    print("Provider tipi OK")

    # --- Test 4: tool_calls parse ---
    yanit_arac = {"content": 'DOSYA_OKU("test.txt")'}
    yanit_bitti = {"content": "Hedef tamamlandi. GOREV_BITTI(ozet)"}
    yanit_dusun = {"content": "DUSUN(icerik)"}
    assert len(loop3._tool_calls_al(yanit_arac)) == 1
    assert len(loop3._tool_calls_al(yanit_bitti)) == 0
    assert len(loop3._tool_calls_al(yanit_dusun)) == 0
    print("Tool call parse OK")

    print("\nTum testler gecti!")
    sys.exit(0)

# ── Tum ReYMeN modullerini yukle (Hermes parity) ────────────────────
def _tum_modulleri_yukle() -> None:
    """src/reymen/ altindaki tum modulleri dene, basarisizlari gormezden gel.
    
    Hermes'teki 94 modulun tamaminin ReYMeN'de karsilanmasi icin.
    Sifir Hermes bagimliligi.
    """
    _moduller = [
        # Provider adapter'lari
        "reymen.anthropic_adapter", "reymen.azure_identity_adapter",
        "reymen.bedrock_adapter", "reymen.gemini_cloudcode_adapter",
        "reymen.gemini_native_adapter", "reymen.gemini_schema",
        "reymen.codex_responses_adapter", "reymen.codex_runtime",
        "reymen.copilot_acp_client", "reymen.lmstudio_reasoning",
        "reymen.moonshot_schema",
        
        # Registry'ler
        "reymen.browser_provider", "reymen.browser_registry",
        "reymen.transcription_provider", "reymen.transcription_registry",
        "reymen.tts_provider", "reymen.tts_registry",
        "reymen.video_gen_provider", "reymen.video_gen_registry",
        "reymen.image_gen_provider", "reymen.image_gen_registry",
        "reymen.image_routing",
        "reymen.web_search_provider", "reymen.web_search_registry",
        
        # Conversation yardimcilari
        "reymen.rate_limit_tracker", "reymen.insights",
        "reymen.title_generator", "reymen.trajectory",
        "reymen.conversation_compression", "reymen.context_compressor",
        "reymen.context_engine", "reymen.think_scrubber",
        "reymen.onboarding", "reymen.markdown_tables",
        "reymen.errors", "reymen.redact", "reymen.ssl_guard",
        "reymen.tool_dispatch_helpers", "reymen.tool_result_classification",
        "reymen.coding_context", "reymen.secret_scope",
        "reymen.subdirectory_hints", "reymen.jiter_preload",
        "reymen.message_content", "reymen.models_dev",
        "reymen.nous_rate_guard", "reymen.manual_compression_feedback",
        "reymen.model_metadata", "reymen.display", "reymen.file_safety",
        "reymen.plugin_llm", "reymen.memory_manager",
        "reymen.retry_utils", "reymen.turn_finalizer",
        "reymen.usage_pricing", "reymen.error_classifier",
        "reymen.turn_retry_state",
        
        # Skill yonetimi
        "reymen.curator", "reymen.curator_backup",
        "reymen.skill_bundles", "reymen.skill_commands",
        "reymen.skill_preprocessing", "reymen.skill_utils",
        
        # Kimlik ve guvenlik
        "reymen.credential_persistence", "reymen.credential_pool",
        "reymen.credential_sources", "reymen.file_safety",
        "reymen.tool_guardrails",
        
        # Yardimci servisler
        "reymen.async_utils", "reymen.auxiliary_client",
        "reymen.billing_view", "reymen.account_usage",
        "reymen.portal_tags", "reymen.agent_runtime_helpers",
        "reymen.process_bootstrap", "reymen.runtime_cwd",
        "reymen.shell_hooks", "reymen.google_code_assist",
        "reymen.google_oauth", "reymen.i18n",
        "reymen.memory_provider", "reymen.weather",
    ]
    
    import importlib
    import logging as _lg
    _log = _lg.getLogger(__name__)
    
    for modul_adi in _moduller:
        try:
            importlib.import_module(modul_adi)
        except Exception:
            pass  # Sessiz gec - opsiyonel modul

# Otomatik yukle
_tum_modulleri_yukle()
