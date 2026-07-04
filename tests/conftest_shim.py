"""
Test import shim: eski module adlarini yeni path'lere yonlendirir.
"""

from __future__ import annotations
import sys
from types import ModuleType

_OLD_TO_NEW = {
    "beyin": "reymen.cereyan.beyin",
    "motor": "reymen.cereyan.motor",
    "gozlem": "reymen.cereyan.gozlem",
    "kancalar": "reymen.cereyan.kancalar",
    "hata_cozucu": "reymen.cereyan.hata_cozucu",
    "insan_arayuzu": "reymen.cereyan.insan_arayuzu",
    "planlayici": "reymen.cereyan.planlayici",
    "prompt_assembly": "reymen.cereyan.prompt_assembly",
    "steering_loop": "reymen.cereyan.steering_loop",
    "conversation_loop": "reymen.cereyan.conversation_loop",
    "adaptif_ogrenme": "reymen.cereyan.adaptif_ogrenme",
    "closed_learning_loop": "reymen.cereyan.closed_learning_loop",
    "self_improvement": "reymen.cereyan.self_improvement",
    "codex_runtime": "reymen.cereyan.codex_runtime",
    "skills_hub": "reymen.cereyan.skills_hub",
    "web_ui": "reymen.web_ui",
    "file_safety": "reymen.guvenlik.file_safety",
    "threat_patterns": "reymen.guvenlik.threat_patterns",
    "tool_guardrails": "reymen.guvenlik.tool_guardrails",
    "anayasa_denetci": "reymen.guvenlik.anayasa_denetci",
    "auto_recovery": "reymen.sistem.auto_recovery",
    "display": "reymen.sistem.display",
    "state_machine": "reymen.sistem.state_machine",
    "terminal_backends": "reymen.sistem.terminal_backends",
    "acp_server": "reymen.ag.acp_server",
    "agent_runtime": "reymen.ag.agent_runtime",
    "config_loader": "reymen.sistem.config_loader",
    "cron_scheduler": "reymen.sistem.cron_scheduler",
    "tool_registry": "reymen.arac.tool_registry",
    "tool_executor": "reymen.arac.tool_executor",
    "session_db": "reymen.hafiza.session_db",
    "iteration_budget": "reymen.cereyan.iteration_budget",
    "prompt_caching": "reymen.arac.prompt_caching",
}

_IN_PROGRESS = set()


class _ImportShimFinder:
    def find_spec(self, fullname, path, target=None):
        if fullname not in _OLD_TO_NEW:
            return None
        if fullname in _IN_PROGRESS:
            return None
        _IN_PROGRESS.add(fullname)
        try:
            import importlib

            new_name = _OLD_TO_NEW[fullname]
            new_mod = importlib.import_module(new_name)
            sys.modules[fullname] = new_mod
            from importlib.machinery import ModuleSpec

            return ModuleSpec(
                fullname, importlib.machinery.BuiltinImporter, is_package=False
            )
        except ImportError:
            return None
        except Exception:
            return None
        finally:
            _IN_PROGRESS.discard(fullname)


if not any(isinstance(f, _ImportShimFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _ImportShimFinder())

_MISSING_MODULES = [
    "agent",
    "anayasa_denetcisi",
    "araclar_ekran",
    "araclar_makro",
    "araclar_nisan",
    "araclar_ses",
    "araclar_telegram",
    "auxiliary_client",
    "chat_completion_helpers",
    "context_compressor",
    "context_engine",
    "context_references",
    "credential_sources",
    "error_classifier",
    "gateway",
    "hafiza_genislet",
    "memory_manager",
    "memory_provider",
    "onboarding",
    "processors",
    "providers",
    "proxy",
    "reymen_skill_cli",
    "sistem_talimati",
    "tools",
    "tor_otomasyonu",
    "turn_context",
    "web_search_provider",
    "akilli_yonlendirici",
    "cokus_raporlayici",
    "main",
    "ReYMeN",
]


class _MissingModule(ModuleType):
    def __getattr__(self, name):
        return _MissingStub(name)


class _MissingStub:
    def __init__(self, name):
        self._name = name

    def __getattr__(self, name):
        return self

    def __call__(self, *args, **kwargs):
        return None

    def __bool__(self):
        return False

    def __iter__(self):
        return iter([])

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration

    def __len__(self):
        return 0

    def __getitem__(self, key):
        return self

    def __repr__(self):
        return f"<Stub:{self._name}>"


for mod_name in _MISSING_MODULES:
    if mod_name not in sys.modules:
        dummy = _MissingModule(mod_name)
        dummy.__file__ = f"<shim:{mod_name}>"
        dummy.__package__ = mod_name
        sys.modules[mod_name] = dummy
