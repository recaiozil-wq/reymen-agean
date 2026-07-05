# -*- coding: utf-8 -*-
"""
reymen_stubs.py â€” ReYMeN ReYMeN Uyumluluk Katmani (birleÅŸtirilmiÅŸ).

Eski dosyalarÄ±n birleÅŸimi:
  - reymen/cron/hermes_stubs/__init__.py (329 satÄ±r)
  - reymen/cron/hermes_stubs/config.py (76 satÄ±r)
  - reymen/cron/hermes_stubs/account_usage.py (55 satÄ±r)
  - reymen/cron/hermes_stubs/i18n.py (46 satÄ±r)
  - reymen/sistem/hermes_uyum.py (126 satÄ±r)

Tüm ReYMeN API çaÄŸrÄ±larÄ± bu dosya üzerinden ReYMeN'e yönlendirilir.
Hermes Agent referans alÄ±nmÄ±ÅŸtÄ±r. Apache 2.0 LisansÄ±.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__file__)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 1: Yol ve Dizin Yönetimi (eski hermes_stubs/__init__.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

_REYMEN_DIR: Optional[Path] = None


def _get_reymen_root() -> Path:
    """ReYMeN proje kökünü döndür."""
    return Path(__file__).resolve().parent.parent  # sistem/ -> reymen/


def set_hermes_home_override(path: Union[str, Path]) -> Any:
    """Override mekanizmasÄ± â€” basit."""
    global _REYMEN_DIR
    _REYMEN_DIR = Path(path)
    return None


def get_reymen_home() -> Path:
    """ReYMeN proje kökünü döndür (ReYMeN'siz)."""
    if _REYMEN_DIR:
        return _REYMEN_DIR
    return _get_reymen_root()


# Backward compat alias â€” mevcut import'lar kÄ±rÄ±lmasÄ±n
get_hermes_home = get_reymen_home


def display_reymen_home() -> str:
    return str(get_reymen_home())


display_hermes_home = display_reymen_home


def get_reymen_dir(new_subpath: str, old_name: str) -> Path:
    return get_reymen_home() / new_subpath


get_hermes_dir = get_reymen_dir


def get_config_path() -> Path:
    return get_reymen_home() / "reymen" / "sistem" / "durum.json"


def get_skills_dir() -> Path:
    skills = get_reymen_home() / "reymen" / "cereyan" / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    return skills


def get_env_path() -> Path:
    return get_reymen_home() / ".env"


def secure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_default_reymen_root() -> Path:
    return get_reymen_home()


get_default_hermes_root = get_default_reymen_root


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 2: Zaman (eski hermes_stubs/__init__.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

_now_cache: Optional[datetime] = None


def now() -> datetime:
    global _now_cache
    _now_cache = datetime.now(timezone.utc).astimezone()
    return _now_cache


def reset_time_cache() -> None:
    global _now_cache
    _now_cache = None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 3: Atomik Dosya Ä°ÅŸlemleri (eski hermes_stubs/__init__.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def atomic_replace(tmp_path: Union[str, Path], target: Union[str, Path]) -> str:
    tmp = Path(tmp_path)
    tgt = Path(target)
    if tgt.exists():
        tgt.unlink()
    shutil.move(str(tmp), str(tgt))
    return str(tgt)


def atomic_json_write(data: Any, path: Union[str, Path], indent: int = 2) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        atomic_replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def atomic_yaml_write(data: Any, path: Union[str, Path], indent: int = 2) -> None:
    try:
        import yaml

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, indent=indent, allow_unicode=True)
    except Exception as e:
        logger.warning("[reymen_stubs] YAML yazma hatasi: %s", e)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 4: YardÄ±mcÄ± Fonksiyonlar (eski hermes_stubs/__init__.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def env_var_enabled(name: str, default: str = "") -> bool:
    return os.environ.get(name, default) not in ("", "0", "false", "no")


def base_url_host_matches(url1: str, url2: str) -> bool:
    from urllib.parse import urlparse

    try:
        h1 = urlparse(url1).hostname or ""
        h2 = urlparse(url2).hostname or ""
        return h1.lower() == h2.lower()
    except Exception:
        return False


def parse_reasoning_effort(effort: str) -> Optional[Dict]:
    return None


def apply_ipv4_preference(force: bool = False) -> None:
    pass


def is_truthy_value(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("1", "true", "yes", "on")
    return bool(value)


def normalize_proxy_url(url: Optional[str]) -> Optional[str]:
    return url


def is_safe_url(url: str) -> bool:
    return True


def to_agent_visible_cache_path(path: str) -> str:
    return path


def get_tool_emoji(tool_name: str) -> str:
    return "ğŸ› ï¸"


def get_label(provider: str, model: str) -> str:
    return f"{provider}/{model}"


def group_providers() -> dict:
    return {}


def expensive_model_warning(model: str, provider: str) -> Optional[str]:
    return None


def should_bypass_active_session(ctx: Any) -> bool:
    return False


def telegram_menu_commands() -> list:
    return []


def resolve_gateway_approval(ctx: Any, msg: str) -> bool:
    return True


def resolve_gateway_clarify(ctx: Any) -> Optional[str]:
    return None


def mark_awaiting_text(ctx: Any) -> None:
    pass


def has_usable_secret(provider: str) -> bool:
    return False


def text_to_speech_tool(text: str, **kw) -> str:
    return ""


def check_tts_requirements() -> bool:
    return False


def vision_analyze_tool(image: str, **kw) -> str:
    return ""


def ensure(pkg: str) -> bool:
    return True


def managed_scope(scope: str) -> Any:
    return None


def set_session_cwd(path: str) -> None:
    pass


def clear_session_cwd() -> None:
    pass


def get_session_env(key: str) -> Optional[str]:
    return os.environ.get(key)


def validate_within_dir(path: Union[str, Path], allowed_dirs: list = None) -> bool:
    return True


def has_named_custom_provider(name: str) -> bool:
    return False


def windows_hide_flags() -> int:
    return 0


def _expand_env_vars(cfg: Any) -> Any:
    return cfg


def load_config() -> Dict[str, Any]:
    """Basit config yükleme â€” .env dosyasÄ±ndan."""
    try:
        import dotenv

        env_path = get_env_path()
        if env_path.exists():
            dotenv.load_dotenv(env_path)
        return {"config": {"env_file": str(env_path)}}
    except Exception:
        return {}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 5: Config YardÄ±mcÄ±larÄ± (eski hermes_stubs/config.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def cfg_get(cfg: Optional[Dict[str, Any]], *keys: str, default: Any = None) -> Any:
    """Ä°ç içe dict'ten güvenli deÄŸer okuma."""
    if not cfg or not keys:
        return default
    current: Any = cfg
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current if current is not None else default


def save_config(cfg: Dict[str, Any], path: Optional[Path] = None) -> bool:
    logger.warning("[reymen_stubs] save_config: henuz desteklenmiyor")
    return False


def save_env_value(key: str, value: str) -> bool:
    logger.warning("[reymen_stubs] save_env_value: henuz desteklenmiyor")
    return False


def is_managed(cfg: Optional[Dict[str, Any]] = None) -> bool:
    return False


def format_managed_message() -> str:
    return ""


def get_compatible_custom_providers() -> list[Dict[str, Any]]:
    return []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 6: Account Usage StublarÄ± (eski hermes_stubs/account_usage.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class AccountUsageSnapshot:
    def __init__(self):
        self.available = False
        self.total_usage = 0.0
        self.total_limit = None
        self.remaining = 0.0
        self.usage_pct = 0.0
        self.reset_date = None
        self.model_group = None


class CreditsView:
    def __init__(self):
        self.lines: list[str] = []
        self.error: Optional[str] = None


def fetch_account_usage(*args, **kwargs) -> Optional[AccountUsageSnapshot]:
    return None


def render_account_usage_lines(snapshot, *, markdown=False) -> list[str]:
    return ["â„¹ï¸ Kullanim bilgisi alinamadi (ReYMeN stub)."]


def build_credits_view(*, markdown=False, timeout=10.0) -> CreditsView:
    view = CreditsView()
    view.lines = ["â„¹ï¸ Kredi bilgisi alinamadi (ReYMeN stub)."]
    return view


def nous_credits_lines(*, markdown=False, timeout=10.0) -> list[str]:
    return ["â„¹ï¸ Nous kredi bilgisi alinamadi (ReYMeN stub)."]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 7: i18n (eski hermes_stubs/i18n.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

_I18N_KNOWN: dict[str, str] = {
    "gateway.usage.label_model": "Model: {model}",
    "gateway.usage.label_total": "Total tokens: {count:,}",
    "gateway.usage.label_api_calls": "API calls: {count}",
    "gateway.insights.invalid_days": "Invalid value: {value}",
}


def t(key: str, **kwargs: Any) -> str:
    if not key:
        return ""
    template = _I18N_KNOWN.get(key)
    if template is None:
        if kwargs:
            parts = [f"{k}={v}" for k, v in kwargs.items()]
            return f"[{key}] ({', '.join(parts)})"
        return f"[{key}]"
    try:
        return template.format(**kwargs)
    except (KeyError, ValueError):
        return template


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 8: Hermes Uyumluluk KatmanÄ± (eski hermes_uyum.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def discover_plugins() -> list:
    """Plugin keÅŸfi â€” PluginManager.discover() üzerinden."""
    try:
        from reymen.sistem.plugin_manager import PluginManager

        pm = PluginManager()
        list(pm.discover())
        logger.debug("[reymen_stubs] Plugin keÅŸfi tamamlandÄ±")
    except Exception as e:
        logger.debug("[reymen_stubs] Plugin keÅŸfi baÅŸarÄ±sÄ±z: %s", e)
    return []


def has_hook(hook_name: str) -> bool:
    try:
        from reymen.sistem.hook_dispatcher import HookDispatcher

        hd = HookDispatcher()
        hooks = hd.listele(olay=hook_name) or []
        return len(hooks) > 0
    except Exception:
        return False


def invoke_hook(hook_name: str, **kwargs):
    try:
        from reymen.sistem.hook_dispatcher import HookDispatcher

        hd = HookDispatcher()
        return hd.tetikle(hook_name, **kwargs)
    except Exception as e:
        logger.debug("[reymen_stubs] Hook hatasi (%s): %s", hook_name, e)
        return None


def get_pre_tool_call_block_message(
    function_name, function_args, task_id="", session_id=""
):
    return None


def apply_tool_request_middleware(
    function_name, function_args, task_id="", session_id=""
):
    try:
        from reymen.sistem.hook_dispatcher import HookDispatcher

        hd = HookDispatcher()
        return hd.tetikle(
            "pre_tool_call",
            function_name=function_name,
            function_args=function_args,
            task_id=task_id,
            session_id=session_id,
        )
    except Exception:
        return None


def run_tool_execution_middleware(
    function_name, function_args, dispatch_fn, task_id="", session_id="", user_task=""
):
    try:
        from reymen.sistem.hook_dispatcher import HookDispatcher

        hd = HookDispatcher()
        hd.tetikle(
            "on_tool_execute",
            function_name=function_name,
            function_args=function_args,
            task_id=task_id,
            session_id=session_id,
            user_task=user_task,
        )
    except Exception:
        pass
    return dispatch_fn(function_name, function_args)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# BÃ–LÃœM 9: Eksik Stublar
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def clear_env_passthrough() -> None:
    """env_passthrough stub."""
    pass


def clear_credential_files() -> None:
    """credential_files stub."""
    pass


def get_random_tip() -> str:
    """tips stub."""
    return ""


def get_active_profile_name() -> str:
    """profiles stub."""
    return "default"


def run_slash(cmd: str, **kwargs) -> str:
    """kanban slash stub."""
    return ""


def format_banner_version_label(version: str = "") -> str:
    """banner stub."""
    return f"ReYMeN {version}" if version else "ReYMeN"


def gateway_help_lines() -> List[str]:
    """commands stub."""
    return ["ReYMeN Gateway â€” komut listesi mevcut deÄŸil (stub)."]


def get_skill_commands() -> List[Dict[str, str]]:
    """skill_commands stub."""
    return []


PROVIDER_GROUPS: Dict[str, list] = {}


_entries: List[Any] = []
_clarify_entries = _entries  # alias for telegram.py


def codex_runtime_switch(*args, **kwargs):
    """codex_runtime_switch stub."""
    return None


def write_approval(*args, **kwargs):
    """write_approval stub."""
    return True


class MemoryStore:
    """memory_tool stub."""
    def __init__(self, *a, **kw): pass
    def get(self, *a, **kw): return None
    def set(self, *a, **kw): pass


def model_supports_fast_mode(*a, **kw) -> bool:
    return False


def format_session_db_unavailable() -> str:
    return "Session DB kullanilamiyor (ReYMeN stub)."


class InsightsEngine:
    """insights stub."""
    def __init__(self, *a, **kw): pass
    def report(self, *a, **kw): return ""


def reload_skills(*a, **kw):
    pass


def kanban_decompose(*a, **kw):
    return None


def clarify_gateway(*a, **kw):
    return None


def switch_to_model(*a, **kw):
    return None


def get_model_info(*a, **kw):
    return {}


def clear_provider_models_cache():
    pass


def get_provider_models(*a, **kw):
    return []


def get_model_cost(*a, **kw):
    return 0.0


def check_model_cost_guard(*a, **kw):
    return None


def checkpoint_save(*a, **kw):
    return None


def checkpoint_list(*a, **kw):
    return []


def checkpoint_restore(*a, **kw):
    return None


def get_rate_limit_info(*a, **kw):
    return {}


def get_usage_pricing(*a, **kw):
    return {}


def get_model_metadata(*a, **kw):
    return {}


def get_partial_compress_prompt(*a, **kw):
    return ""


def get_manual_compression_feedback(*a, **kw):
    return ""


def get_session_listing(*a, **kw):
    return []


class SessionDB:
    """SessionDB wrapper â€” session_db.py'yi basit bir arayüzle sarar."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        if db_path is None:
            db_path = get_reymen_home() / "state.db"
        self.db_path = Path(db_path)
        self._conn = None

    def _get_conn(self):
        if self._conn is None:
            import sqlite3

            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self.db_path))
        return self._conn

    def get(self, key: str, default=None):
        try:
            conn = self._get_conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)"
            )
            row = conn.execute("SELECT value FROM kv WHERE key = ?", (key,)).fetchone()
            return row[0] if row else default
        except Exception:
            return default

    def set(self, key: str, value: str) -> None:
        try:
            conn = self._get_conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)"
            )
            conn.execute(
                "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)", (key, value)
            )
            conn.commit()
        except Exception as e:
            logger.debug("[reymen_stubs] SessionDB.set hatasi: %s", e)

    def delete(self, key: str) -> None:
        try:
            conn = self._get_conn()
            conn.execute("DELETE FROM kv WHERE key = ?", (key,))
            conn.commit()
        except Exception:
            pass

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


def _get_platform_tools() -> List[str]:
    """Mevcut tool'larÄ± listele."""
    tools = []
    try:
        from reymen.sistem.tools_registry import registry

        for name in registry.list_tools():
            tools.append(name)
    except Exception:
        pass
    return tools


def _kanban_db_stub():
    """kanban_db stub â€” findings_board benzeri."""
    try:
        from reymen.sistem.findings_board import FindingsBoard

        return FindingsBoard()
    except Exception:
        return None


kanban_db = _kanban_db_stub


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DOÄRULAMA
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _ensure_stubs() -> None:
    """Tüm stub'larÄ± doÄŸrula (sadece import kontrolü)."""
    _stubs = [
        get_reymen_home,
        get_hermes_home,
        atomic_replace,
        atomic_json_write,
        is_truthy_value,
        normalize_proxy_url,
        is_safe_url,
        to_agent_visible_cache_path,
        get_tool_emoji,
        get_label,
        group_providers,
        expensive_model_warning,
        should_bypass_active_session,
        telegram_menu_commands,
        resolve_gateway_approval,
        resolve_gateway_clarify,
        mark_awaiting_text,
        discover_plugins,
        has_usable_secret,
        text_to_speech_tool,
        check_tts_requirements,
        vision_analyze_tool,
        ensure,
        managed_scope,
        set_session_cwd,
        clear_session_cwd,
        cfg_get,
        load_config,
        save_config,
        t,
        SessionDB,
        _get_platform_tools,
        clear_env_passthrough,
    ]
    _ = _stubs  # noqa
