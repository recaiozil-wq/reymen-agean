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

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
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
        """Konusma dongusu â€” ReYMeN-style ReAct loop (birebir ayni akis).

        Akis (ReYMeN ReAct):
          1. SETUP (task_id + session + budget + sistem_prompt)
          2. BUILD messages (system + gecmis + user + context)
          3. REACT LOOP (max_tur):
             a. API cagrisi (retry + fallback ile)
             b. tool_calls varsa -> _arac_calistir -> append -> loop
             c. text response -> break
          4. POST-PROCESS (kaydet + session kapat + log)

        ReYMeN'ten farkli olan (ReYMeN'e ozgu):
          - Sistem prompt _sistem_promptu_olustur ile build edilir (profil+SOUL)
          - Tool'lar motor.py uzerinden calisir (reymen motor)
          - OnceHafiza'ya sonuc otomatik kaydedilir (ogrenme)
          - A2A broadcast destegi

        Args:
            hedef:    Kullanicinin hedefi.
            baglam:   Ek baglam dicti (opsiyonel).
            provider: Provider override.

        Returns:
            Sonuc dicti (task_id, basarili, turlar, sure, yanit, ...).
        """
        # -- 1. SETUP ------------------------------------------------
        task_id = str(uuid.uuid4())[:8]
        try:
            if _CL_AKTIF:
                _cl_baslat(task_id)
        except Exception as _e:
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] %%s: %%s", type(_e).__name__, _e
            )
        log.info("[%s] run_conversation basladi: %.60s", task_id, hedef)

        baslama = time.time()
        self._durum = "calisiyor"
        self._iptal_istegi = False
        self._arti_arda_tool_hatasi = 0
        self._tool_hata_zorla_cevap = False
        self._tool_call_sayaci = 0
        self._onceki_tool_cagrilari: list[tuple[str, str]] = []
        self._force_low_temp = False
        self._web_hata = 0  # Web arama circuit breaker'ini her gorevde sifirla
        api_call_count = 0
        max_tur = self.max_tur

        sonuc: dict = {
            "task_id": task_id,
            "hedef": hedef,
            "basarili": False,
            "turlar": 0,
            "hata": None,
            "provider": provider,
            "yanit": None,
        }

        # Session baslat
        session_id = None
        _storage = None
        if _SESSION_AKTIF and _SessionStorage:
            try:
                _db_yol = str(Path(__file__).resolve().parent.parent.parent.parent / "merkez_db" / "session.db")
                _storage = _SessionStorage(_db_yol)
                model_adi = getattr(self.beyin, "model", None) if self.beyin else None
                session_id = _storage.session_baslat(
                    source="run_conversation",
                    model=model_adi,
                    system_prompt=hedef[:500] if hedef else None,
                    billing_provider=provider,
                )
                sonuc["session_id"] = session_id
                log.info("[%s] Session acildi: %s", task_id, session_id)
                if _HOOK_AKTIF and _oturum_baslat_tetikle is not None:
                    try:
                        _oturum_baslat_tetikle(
                            session_id=session_id, task_id=task_id, agent_adi="reymen"
                        )
                    except Exception:
                        logger.warning("[hook] sessiz_except")
                # Plugin: on_session_start
                if _PLUGIN_AKTIF and _PLUGIN_SISTEMI is not None:
                    try:
                        _PLUGIN_SISTEMI.hook_cagir(
                            "on_session_start",
                            session_id=session_id or task_id,
                            user_id=baglam.get("user_id", "unknown")
                            if baglam
                            else "unknown",
                        )
                    except Exception:
                        logger.warning("[plugin] on_session_start sessiz_except")
            except Exception as _se:
                log.warning("[%s] Session baslatma hatasi: %s", task_id, _se)

        budget = self._budget_olustur(hedef)

        if _HOOK_AKTIF and _tur_baslat_tetikle is not None:
            try:
                _tur_baslat_tetikle(tur=1, task_id=task_id, hedef=hedef[:100])
            except Exception:
                logger.warning("[hook] sessiz_except")

        # -- A2A mesaj kontrolu ------------------------------------------
        if self._a2a_agent is not None:
            try:
                a2a_msg = self._a2a_agent.receive(timeout=0.1)
                if a2a_msg is not None:
                    log.info(
                        "[%s] A2A mesaj alindi: sender=%s icerik=%.60s",
                        task_id,
                        a2a_msg.sender,
                        str(a2a_msg.content),
                    )
                    self._konusma_gecmisi.append(
                        {
                            "role": "user",
                            "content": f"[A2A: {a2a_msg.sender}] {a2a_msg.content}",
                        }
                    )
            except Exception as _e:
                __import__("logging").getLogger(__name__).warning(
                    "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                )

        # -- 2. BUILD messages -------------------------------------------
        # System prompt: TEK sefer build edilir
        sistem_prompt = self._sistem_promptu_olustur(hedef, baglam)
        provider_tipi = self._provider_tipi_belirle(provider)
        sonuc["provider"] = provider_tipi

        # ReYMeN pattern: messages = [system] + conversation_history + [user]
        messages = [{"role": "system", "content": sistem_prompt}]

        # Konusma gecmisini ekle (son N mesaj)
        for m in self._konusma_gecmisi:
            if isinstance(m, dict) and m.get("role") in ("user", "assistant"):
                messages.append(m)

        # Session context injection
        if _storage and session_id:
            try:
                session_baglam = self._session_context_injection(session_id, _storage)
                if session_baglam:
                    messages.append({"role": "user", "content": session_baglam})
            except Exception as _e:
                __import__("logging").getLogger(__name__).warning(
                    "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                )

        # Skill tarama (FTS5)
        try:
            skill_icerik = self._skill_tara(hedef)
            if skill_icerik:
                messages.append({"role": "user", "content": skill_icerik})
        except Exception as _e:
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] %%s: %%s", type(_e).__name__, _e
            )

        # -- @file/@url Referans Isleme (ref_processor) -----------------
        if (
            _REF_PROCESSOR_AKTIF
            and _ref_isle is not None
            and _ref_context_olustur is not None
        ):
            try:
                ref_zengin_metin, ref_liste = _ref_isle(hedef)
                if ref_liste:
                    ref_context = _ref_context_olustur(ref_liste)
                    if ref_context:
                        messages.append({"role": "user", "content": ref_context})
                        log.info(
                            "[%s] %d referans eklendi (file=%d url=%d)",
                            task_id,
                            len(ref_liste),
                            sum(
                                1
                                for r in ref_liste
                                if r.get("tip") == "file" and r.get("basarili")
                            ),
                            sum(
                                1
                                for r in ref_liste
                                if r.get("tip") == "url" and r.get("basarili")
                            ),
                        )
                    # Basarisiz referanslari logla
                    for ref in ref_liste:
                        if not ref.get("basarili"):
                            log.warning(
                                "[%s] Ref basarisiz: %s=%s â€” %s",
                                task_id,
                                ref["tip"],
                                ref["kaynak"],
                                ref.get("hata", "?"),
                            )
                    # Orijinal mesajdaki @file/@url'leri [REF:] ile degistir
                    hedef = ref_zengin_metin
            except Exception as _ref_e:
                log.warning("[%s] RefProcessor hatasi: %s", task_id, _ref_e)

        # Kullanici mesaji (en son)
        # Plugin: on_message â€” mesaji deÄŸiÅŸtirme ÅŸansÄ±
        if _PLUGIN_AKTIF and _PLUGIN_SISTEMI is not None:
            try:
                plugin_context = {"task_id": task_id, "baglam": baglam or {}}
                hedef = _PLUGIN_SISTEMI.hook_cagir_mesaj(
                    "on_message",
                    message=hedef,
                    context=plugin_context,
                )
            except Exception:
                logger.warning("[plugin] on_message sessiz_except")

        user_msg = hedef
        if baglam:
            import json as _json

            baglam_str = _json.dumps(baglam, ensure_ascii=False)
            user_msg = f"{baglam_str}\n\n{hedef}"
        messages.append({"role": "user", "content": user_msg})

        # ── OTOMATIK WEB ARAMASI (guncel bilgi gerektiren sorgular) ──────
        _web_var = False
        try:
            _guncel_kelimeler = [
                "fiyat", "dolar", "euro", "altin", "ons", "doviz", "borsa",
                "bitcoin", "kripto", "hava", "sıcaklik", "yagmur",
                "bugun", "yarin", "saat", "tarih", "2025", "2026",
                "haber", "guncel", "son dakika", "skor", "mac sonucu",
                "kazandi", "kaybetti", "canli", "anlik",
                "turnuva", "kupa", "sampiyon", "final", "lig", "puan",
                "kim kazandi", "durum ne", "sonuc", "dunya kupasi",
                "secim", "devlet baskani", "basbakan", "cumhurbaskani",
            ]
            _hedef_lower = (hedef or "").lower()
            if any(_kw in _hedef_lower for _kw in _guncel_kelimeler):
                _web_sonuc = self._web_ara(_hedef, maks_sonuc=5)
                if _web_sonuc and len(_web_sonuc) > 20:
                    # Web sonucunu user mesajina zorunlu dille enjekte et
                    from datetime import datetime as _dt
                    _zaman = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
                    _context_block = (
                        f"[GUNCEL VERI - {_zaman}]\n"
                        f"{_web_sonuc}\n"
                        "[/GUNCEL VERI]\n\n"
                        "Yukaridaki [GUNCEL VERI] blogunu tek bilgi kaynagi olarak KULLAN. "
                        "Kendi egitim verindeki eski/tahmini bilgiyi KULLANMA. "
                        "Veri yetersizse 'guncel veri bulunamadi' de, tahmin URETME.\n\n"
                        "CEVAP FORMATI:\n"
                        "1. Soruya dogrudan cevap ver (fiyat/deger varsa soyle)\n"
                        "2. Kaynak linkleri ekle (kisaltma, tıkla-izle formatinda)\n"
                        "3. Son olarak 'Detayli bilgi icin linklere tiklayabilirsin' ekle\n\n"
                        f"Soru: {hedef}"
                    )
                    # Son user mesajini guncel veriyle degistir
                    messages[-1] = {"role": "user", "content": _context_block}
                    _web_var = True
                    self._force_low_temp = True
                    log.info("[%s] Web verisi eklendi, LLM zorunlu kullanacak (t=0.2)", task_id)
        except Exception:
            pass

        # Tarih/saat sorgulari icin: DeepSeek sistem prompt'taki tarihi bazen gormezden gelir
        # User mesajina direkt tarih ekle
        if not _web_var:
            _zaman_soru_kelimeleri = [
                "hangi yıl", "hangi yılda", "hangi yıldayız",
                "bugün", "bugun", "tarih", "saat kaç", "saat kac",
                "günlerden ne", "gunlerden ne", "su an", "şu an",
                "zaman", "tarih nedir",
            ]
            _hedef_lower = (hedef or "").lower()
            if any(_kw in _hedef_lower for _kw in _zaman_soru_kelimeleri):
                from datetime import datetime as _dt
                _simdi = _dt.now().strftime("%d %B %Y %H:%M")
                _zaman_msg = (
                    f"[SU ANKI TARIH]\n{_simdi}\n[/SU ANKI TARIH]\n\n"
                    f"Yukaridaki tarih bilgisini kullan. "
                    f"Kendi egitim verindeki tarihi KULLANMA.\n\n"
                    f"Soru: {hedef}"
                )
                messages[-1] = {"role": "user", "content": _zaman_msg}
                self._force_low_temp = True
                log.info("[%s] Tarih bilgisi user mesajina eklendi", task_id)

        # Session Search: kullanici mesajini kaydet
        self._session_search_kaydet(session_id, user_msg, "user")

        # -- 3. REACT LOOP -----------------------------------------------
        final_yanit = None
        interrupted = False

        # Delegasyon kontrolu (subagent) â€” eger hedef subagent gerektiriyorsa
        # direkt conversation loop'a girmeden coz
        if _DELEGASYON_AKTIF and _delegasyon_sistemi_al is not None:
            try:
                delegasyon_sonuc = self._delegasyon_kontrol(hedef)
                if delegasyon_sonuc and delegasyon_sonuc.get("basarili"):
                    sonuc["basarili"] = True
                    sonuc["yanit"] = delegasyon_sonuc.get("yanit", "")
                    sonuc["delegasyon"] = delegasyon_sonuc
                    sonuc["turlar"] = 0
                    sonuc["sure"] = round(time.time() - baslama, 2)
                    self._durum = "tamamlandi"
                    log.info(
                        "[%s] Delegasyon ile cozuldu: mod=%s sure=%.1fs",
                        task_id,
                        delegasyon_sonuc.get("mod", "?"),
                        sonuc["sure"],
                    )
                    return sonuc
            except Exception as _de:
                log.warning("[%s] Delegasyon kontrol hatasi: %s", task_id, _de)

        while api_call_count < max_tur and budget.devam_etmeli_mi():
            api_call_count += 1

            if self._iptal_istegi:
                interrupted = True
                log.info("[%s] Interrupt istegi alindi (flag)", task_id)
                break

            # Hermes-style: out-of-band stop sinyali (dosya tabanli)
            if _STOP_SINYAL_DOSYASI.exists() or _STOP_SINYAL_ALTERNATIF.exists():
                self._iptal_istegi = True
                interrupted = True
                # Sinyal dosyasini temizle
                try:
                    if _STOP_SINYAL_DOSYASI.exists():
                        _STOP_SINYAL_DOSYASI.unlink()
                    if _STOP_SINYAL_ALTERNATIF.exists():
                        _STOP_SINYAL_ALTERNATIF.unlink()
                except Exception:
                    pass
                log.warning("[%s] Out-of-band iptal sinyali yakalandi", task_id)
                break

            budget.tur_basla()

            # API cagrisi (ReYMeN pattern: retry + fallback ile)
            api_yanit = None

            # â”€â”€ Rules Engine: API cagrisi kontrolu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            if _RULES_AKTIF and _RULES_ENGINE is not None:
                try:
                    import re as _re

                    # Provider/model adini bul
                    provider_info = provider_tipi or provider or "bilinmiyor"
                    api_hedef = f"llm_call:{provider_info}"
                    # Son kullanici mesajindan kisa bir kesit al
                    if messages and len(messages) > 1:
                        son_mesaj = str(messages[-1].get("content", ""))[:100]
                        if son_mesaj:
                            api_hedef = f"{api_hedef} {son_mesaj}"
                    kural_sonuc = _RULES_ENGINE.kontrol("api_cagrisi", api_hedef)
                    if not kural_sonuc.get("izin"):
                        log.warning(
                            "[%s] [Rules] API cagrisi ENGELLENDI: %s",
                            task_id,
                            kural_sonuc.get("sebep", ""),
                        )
                        sonuc["hata"] = (
                            f"API cagrisi engellendi: {kural_sonuc.get('sebep', '')}"
                        )
                        sonuc["kural"] = kural_sonuc
                        budget.tur_bitir(basarili=False)
                        break
                except Exception as _re:
                    log.debug(
                        "[%s] [Rules] API kontrol hatasi (sessiz): %s", task_id, _re
                    )

            # Plugin: pre_llm_call â€” mesajlarÄ± deÄŸiÅŸtirme ÅŸansÄ±
            try:
                if _PLUGIN_AKTIF and _PLUGIN_SISTEMI is not None:
                    plugin_ctx = {"task_id": task_id, "tur": api_call_count}
                    messages, _ = _PLUGIN_SISTEMI.hook_cagir_pre_llm(
                        messages, plugin_ctx
                    )
            except Exception:
                logger.warning("[plugin] pre_llm_call sessiz_except")
            try:
                # ONCE tools'suz dene: selam/chat icin DeepSeek direkt cevap versin
                api_yanit = self._direct_api_call(messages, tools_bos=True, session_id=session_id)
                if api_yanit:
                    icerik = self._yanit_icerigi_al(api_yanit)
                    tcalls = self._tool_calls_al(api_yanit)
                    # tools'suz yanit geldi ve bos degil -> kullan
                    if icerik and icerik.strip():
                        pass  # tools_bos=True ile gelen yanit, kullan
                    elif tcalls:
                        pass  # tool_calls geldi, isle
                    else:
                        # tools'suz bos yanit -> tools ILE tekrar dene
                        log.debug("[%s] tools_bos=True bos yanit, tools ILE deneniyor", task_id)
                        api_yanit = self._direct_api_call(messages, tools_bos=False, session_id=session_id)
                else:
                    # tools'suz basarisiz -> tools ILE dene
                    api_yanit = self._direct_api_call(messages, tools_bos=False, session_id=session_id)
            except Exception as _ae:
                log.warning(
                    "[%s] API cagri hatasi (tur %d): %s", task_id, api_call_count, _ae
                )
                try:
                    from reymen.cereyan.beyin import _provider_rotate

                    yeni_provider = _provider_rotate(provider_tipi)
                    if yeni_provider:
                        sonuc["provider"] = yeni_provider
                        log.info("[%s] Fallback provider: %s", task_id, yeni_provider)
                        api_yanit = self._direct_api_call(messages, tools_bos=False, session_id=session_id)
                except Exception:
                    logger.warning("[fix_01_sessiz_except] Exception")

            # Plugin: post_llm_call â€” yanÄ±tÄ± iÅŸleme ÅŸansÄ±
            try:
                if (
                    _PLUGIN_AKTIF
                    and _PLUGIN_SISTEMI is not None
                    and api_yanit is not None
                ):
                    plugin_ctx = {"task_id": task_id, "tur": api_call_count}
                    api_yanit = _PLUGIN_SISTEMI.hook_cagir_post_llm(
                        api_yanit, plugin_ctx
                    )
            except Exception:
                logger.warning("[plugin] post_llm_call sessiz_except")

            # Bos yanit kontrolu: icerik yok + tool_calls yoksa kisa prompt ile tekrar dene
            if api_yanit is not None:
                _yc = self._yanit_icerigi_al(api_yanit)
                _tc = self._tool_calls_al(api_yanit)
                if (not _yc or not _yc.strip()) and not _tc:
                    log.debug("[%s] Bos yanit alindi, kisa prompt ile tekrar deneniyor", task_id)
                    kisa_prompt = "Sen yardimci bir asistansin. Kisa ve oz cevap ver."
                    kisa_messages = [{"role": "system", "content": kisa_prompt}]
                    for m in messages:
                        if m.get("role") in ("user", "assistant"):
                            kisa_messages.append(m)
                    api_yanit = self._direct_api_call(kisa_messages, tools_bos=True)
                    if api_yanit:
                        _yc2 = self._yanit_icerigi_al(api_yanit)
                        _tc2 = self._tool_calls_al(api_yanit)
                        if (not _yc2 or not _yc2.strip()) and not _tc2:
                            # Hala bos -> tools ILE dene
                            api_yanit = self._direct_api_call(kisa_messages, tools_bos=False)

            if api_yanit is None:
                sonuc["hata"] = f"API cagrisi basarisiz (tur {api_call_count})"
                log.warning("[%s] %s", task_id, sonuc["hata"])
                self._hata_cozumle(sonuc["hata"], kaynak="api_call")
                budget.tur_bitir(basarili=False)
                break

            # API yaniti: _direct_api_call simplified format dondurur
            # {"role": "assistant", "content": "...", "tool_calls": [...]}
            # NOT: OpenAI full response degil, direkt message dict
            tool_calls = self._tool_calls_al(api_yanit)
            yanit_icerik = self._yanit_icerigi_al(api_yanit)

            if tool_calls:
                # Hermes pattern: art arda tool hatasi limiti asildiysa
                # tool_calls'i yoksay, modeli toolsuz cevap vermeye zorla
                if self._tool_hata_zorla_cevap:
                    log.warning(
                        "[%s] Tool hatasi limiti asildi (%d), toolsuz cevap zorlamasi",
                        task_id,
                        self._arti_arda_tool_hatasi,
                    )
                    # Tool_calls'i mesaj olarak ekle ama zorla cevap al
                    zorla_prompt = (
                        "UYARI: Kullandigin araclar calismadi. "
                        "ARTIK HICBIR ARAC KULLANMA. "
                        "Sahip oldugun bilgiyle dogrudan cevap ver. "
                        "Araba kullanma, sadece konus."
                    )
                    messages.append({"role": "user", "content": zorla_prompt})
                    # tool_calls'i atla, loop basina don - model toolsuz cevap versin
                    budget.tur_bitir(basarili=True)
                    continue

                # Once assistant mesajini ekle (tool_calls iceren)
                msg_kopya = dict(api_yanit)
                messages.append(msg_kopya)

                # Hermes-style: max_tool_calls limiti
                self._tool_call_sayaci += len(tool_calls)
                if self._tool_call_sayaci > MAX_TOOL_CALLS:
                    log.warning(
                        "[%s] max_tool_calls asildi (%d > %d), tool'lar bloklandi",
                        task_id,
                        self._tool_call_sayaci,
                        MAX_TOOL_CALLS,
                    )
                    zorla_prompt = (
                        f"UYARI: Tool cagri limiti asildi ({MAX_TOOL_CALLS}). "
                        "ARTIK HICBIR ARAC KULLANMA. Sadece konusarak cevap ver."
                    )
                    messages.append({"role": "user", "content": zorla_prompt})
                    budget.tur_bitir(basarili=True)
                    continue

                for tc in tool_calls:
                    # OpenAI tool call -> ReYMeN eylem formatina cevir
                    fn = tc.get("function", {}) if isinstance(tc, dict) else {}
                    arac_adi = fn.get("name", "")
                    try:
                        import json as _json

                        parametreler = _json.loads(fn.get("arguments", "{}"))
                    except Exception:
                        parametreler = {}
                    eylem = {
                        "arac": arac_adi,
                        "parametreler": parametreler,
                        "tur": "arac",
                    }

                    arac_sonuc = self._arac_calistir(eylem)

                    # Hermes-style: duplicate detection
                    _tool_key = (arac_adi, str(parametreler))
                    if _tool_key in self._onceki_tool_cagrilari:
                        log.warning(
                            "[%s] Duplicate tool cagrisi tespit edildi: %s %s (es geciliyor)",
                            task_id, arac_adi, str(parametreler)[:60],
                        )
                        tool_msg = {
                            "role": "tool",
                            "tool_call_id": tc.get("id", str(uuid.uuid4())[:8]),
                            "content": "[DUPLICATE] Bu arac daha once cagrildi. Sonucu tekrar kullan: " + arac_sonuc.get("cikti", ""),
                        }
                        messages.append(tool_msg)
                        continue
                    self._onceki_tool_cagrilari.append(_tool_key)

                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tc.get("id", str(uuid.uuid4())[:8]),
                        "content": arac_sonuc.get("cikti", str(arac_sonuc)),
                    }
                    messages.append(tool_msg)

                    # Hermes pattern: tool sonucu modele gider, model karar verir
                    # tamamlandi flag'i loop kontrolu icin KULLANILMAZ
                    if not arac_sonuc.get("basarili") and arac_sonuc.get("hata"):
                        self._arti_arda_tool_hatasi += 1
                        self._hata_cozumle(arac_sonuc["hata"], kaynak="tool")
                        log.warning(
                            "[%s] Tool hatasi #%d: %s -> %s",
                            task_id,
                            self._arti_arda_tool_hatasi,
                            arac_adi,
                            arac_sonuc.get("hata", "")[:80],
                        )
                        # Hermes pattern: esik asildi -> zorla cevap modu
                        if self._arti_arda_tool_hatasi >= ARTI_ARDA_TOOL_HATA_LIMIT:
                            self._tool_hata_zorla_cevap = True
                            log.warning(
                                "[%s] Tool hata limiti asildi (%d) -> zorla cevap modu",
                                task_id,
                                self._arti_arda_tool_hatasi,
                            )
                    else:
                        # Basarili tool -> sayaci sifirla
                        self._arti_arda_tool_hatasi = 0

                # Hermes pattern: tum tool sonuclari modele gitsin, model devam/dur kararini versin
                budget.tur_bitir(basarili=True)
                continue
            elif yanit_icerik:
                # Basarili metin cevap -> tool hata sayacini sifirla
                self._arti_arda_tool_hatasi = 0
                self._tool_hata_zorla_cevap = False
                # Minimum anlamli yanit kontrolu (bosluk/\\\\n gibi yanitlari atla)
                yanit_stripped = yanit_icerik.strip()
                if len(yanit_stripped) < 2:
                    sonuc["hata"] = f"Bos yanit (tur {api_call_count})"
                    self._hata_cozumle(sonuc["hata"], kaynak="bos_yanit")
                    budget.tur_bitir(basarili=False)
                    break
                final_yanit = self._yanit_temizle(yanit_icerik)
                sonuc["basarili"] = True
                messages.append({"role": "assistant", "content": final_yanit})
                # Session Search: asistan yanitini kaydet
                self._session_search_kaydet(session_id, final_yanit, "assistant")
                budget.tur_bitir(basarili=True)
                break

            else:
                sonuc["hata"] = f"Bos yanit (tur {api_call_count})"
                self._hata_cozumle(sonuc["hata"], kaynak="bos_yanit")
                budget.tur_bitir(basarili=False)
                break

        if interrupted:
            self._durum = "iptal"
            sonuc["hata"] = "Kullanici tarafindan iptal edildi"

        sonuc["turlar"] = api_call_count
        sonuc["sure"] = round(time.time() - baslama, 2)
        if final_yanit:
            sonuc["yanit"] = final_yanit
        self._durum = "tamamlandi" if sonuc["basarili"] else "hata"

        # Yanit dogrulama
        if sonuc["basarili"] and final_yanit:
            yanit_metin = str(final_yanit)
            if not yanit_metin or len(yanit_metin.strip()) < 5:
                log.warning(
                    "[%s] DOGRULA: yanit cok kisa (%d char) - basarisiz sayiliyor",
                    task_id,
                    len(yanit_metin.strip()),
                )
                sonuc["basarili"] = False
                sonuc["dogrulama_uyarisi"] = "yanit_cok_kisa"

        # -- 4. POST-PROCESS (Hermes-style: Memory + ogrenme + skills + self_heal) --

        # OnceHafiza'ya kaydet (ogrenme)
        if sonuc["basarili"] and final_yanit and len(str(final_yanit).strip()) > 20:
            try:
                self._gorev_sonrasi_hafiza(
                    hedef=hedef,
                    yanit=str(final_yanit)[:500],
                    task_id=task_id,
                )
                sonuc["kaydedildi"] = True
            except Exception as _ke:
                log.warning("[%s] KAYDET hatasi: %s", task_id, _ke)
                sonuc["kaydedildi"] = False

        # SelfHeal istatistik kaydet (basarisiz turlar analiz icin)
        if sonuc.get("hata") and len(str(sonuc.get("hata", ""))) > 5:
            try:
                from reymen.core.self_heal import SelfHeal
                _sh = SelfHeal()
                _sh.coz(
                    hedef=hedef[:100],
                    hata=str(sonuc["hata"])[:500],
                    kod="",
                    dosya_yolu="conversation_loop",
                )
                sonuc["self_heal_denendi"] = True
            except Exception:
                sonuc["self_heal_denendi"] = False

        # MEMORY.md'ye kalici kayit (ogrenme + skills + memory tek nokta)
        if sonuc["basarili"] and final_yanit:
            try:
                from reymen.hafiza.memory_manager import MemoryManager
                _mm = MemoryManager()
                _mm.kaydet(
                    konu=hedef[:100],
                    icerik=str(final_yanit)[:500],
                    kaynak="conversation_loop",
                    etiketler=["konusma", "ogrenme"],
                )
                sonuc["memory_kaydedildi"] = True
            except Exception:
                sonuc["memory_kaydedildi"] = False

        # Konusmadan skill cikar
        if sonuc["basarili"] and _SKILL_CIKAR_AKTIF:
            try:
                _skill_cikar(
                    messages=self._konusma_gecmisi,
                    basari=True,
                    konu=hedef[:60],
                )
            except Exception as _sce:
                log.debug("[%s] Skill cikarma atlandi: %s", task_id, _sce)

        # Konusma gecmisini guncelle
        self._gecmis_mesajlar = [
            dict(m)
            for m in messages
            if m.get("role") in ("user", "assistant") and m.get("content")
        ][-self._max_gecmis_mesaj :]
        # fix #10: _konusma_gecmisi de guncellensin (REPL'de hafiza kaybolmasin)
        self._konusma_gecmisi = list(self._gecmis_mesajlar)

        # Hook: tur bitisi
        if _HOOK_AKTIF and _tur_bitir_tetikle is not None:
            try:
                _tur_bitir_tetikle(
                    tur=api_call_count,
                    basarili=sonuc["basarili"],
                    task_id=task_id,
                    kaynak="react_loop",
                )
            except Exception:
                logger.warning("[hook] sessiz_except")

        # A2A broadcast
        if self._a2a_agent is not None and final_yanit:
            try:
                self._a2a_broker.broadcast(
                    "conversation_loop",
                    {"task_id": task_id, "yanit": str(final_yanit)[:200]},
                    exclude={self._a2a_agent.id},
                )
            except Exception as _e:
                __import__("logging").getLogger(__name__).warning(
                    "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                )

        # Session kapat
        if _storage and session_id:
            try:
                end_reason = (
                    "completed"
                    if sonuc["basarili"]
                    else ("cancelled" if self._durum == "iptal" else "error")
                )
                _storage.session_bitir(session_id, end_reason=end_reason)
                log.info(
                    "[%s] Session kapatildi: %s (%s)", task_id, session_id, end_reason
                )
                # Plugin: on_session_end
                if _PLUGIN_AKTIF and _PLUGIN_SISTEMI is not None:
                    try:
                        _PLUGIN_SISTEMI.hook_cagir(
                            "on_session_end",
                            session_id=session_id or task_id,
                            reason=end_reason,
                        )
                    except Exception:
                        logger.warning("[plugin] on_session_end sessiz_except")
                if _HOOK_AKTIF and _oturum_bitir_tetikle is not None:
                    try:
                        _oturum_bitir_tetikle(
                            session_id=session_id,
                            tur_sayisi=api_call_count,
                            basarili=sonuc["basarili"],
                            task_id=task_id,
                        )
                    except Exception:
                        logger.warning("[hook] sessiz_except")
            except Exception as _se:
                log.warning("[%s] Session bitirme hatasi: %s", task_id, _se)

        log.info(
            "[%s] run_conversation bitti: basarili=%s, tur=%d, sure=%.1fs",
            task_id,
            sonuc["basarili"],
            api_call_count,
            sonuc["sure"],
        )

        try:
            from reymen.self_improve import record_step, QualityMetric

            record_step(
                QualityMetric(
                    success=sonuc.get("basarili", False),
                    step_name=hedef[:60] if hedef else "",
                    errors=1 if not sonuc.get("basarili") else 0,
                    retries=getattr(self, "_retry_sayaci", 0),
                    duration=sonuc.get("sure", 0),
                    tokens_used=getattr(budget, "kullanilan_token", 0),
                )
            )
        except Exception as _e:
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] %%s: %%s", type(_e).__name__, _e
            )

        # â”€â”€ Proaktif kontrol: her cevap sonrasÄ± eksik analizi â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if _PROAKTIF_AKTIF and hedef and sonuc and sonuc.get("yanit"):
            try:
                _proaktif_kontrol(hedef, str(sonuc.get("yanit", "")))
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

        # â”€â”€ Hafif compaction kontrolu: her konusma sonrasi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # MEMORY.md/USER.md %80 doluluk esigini gecerse otomatik compaction
        try:
            from reymen.cereyan.memory_compaction import hafif_compaction_kontrol

            _comp_sonuc = hafif_compaction_kontrol()
            if _comp_sonuc.get("islem_yapildi"):
                log.info(
                    "[%s] Compaction yapildi: %s",
                    task_id,
                    _comp_sonuc.get("compaction", {}),
                )
                sonuc["compaction"] = _comp_sonuc
        except ImportError:
            pass  # memory_compaction modulu yoksa sessiz gec
        except Exception as _comp_e:
            log.debug("[%s] Compaction kontrol hatasi (sessiz): %s", task_id, _comp_e)

        return sonuc

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
