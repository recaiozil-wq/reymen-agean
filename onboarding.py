# -*- coding: utf-8 -*-
# SHIM — agent/onboarding.py yönlendirir
from agent.onboarding import *  # noqa: F401, F403

# Private name export — test patching için
import importlib as _imp_on, sys as _sys_on
_src_on = _imp_on.import_module('agent.onboarding')
_sys_on.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src_on).items() if k.startswith('_') and not k.startswith('__')}
)


class OnboardingWizard:
    """Kullanıcı karşılama sihirbazı stub."""

    def baslat(self):
        pass

    def config_kontrol(self):
        return True

    def config_kontrol_et(self):
        return True
