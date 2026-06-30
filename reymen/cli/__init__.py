# -*- coding: utf-8 -*-
"""reymen.cli — ReYMeN CLI paketi.

ReYMeN'teki ``hermes_cli/subcommands/`` yapısının ReYMeN karşılığı.
- Alt komut parser'ları ``subcommands/parser_*.py`` dosyalarında
- Handler'lar bu modülde veya ``reymen.arac.cli_commands`` / ``reymen.console``'da
"""
from __future__ import annotations
import argparse
import sys

from .subcommands._shared import c, g, y, r, d, mavi, bld
from .subcommands.parser_cron import add_cron_parser
from .subcommands.parser_gateway import add_gateway_parser
from .subcommands.parser_config import add_config_parser
from .subcommands.parser_session import add_session_parser
from .subcommands.parser_backup import add_backup_parser
from .subcommands.parser_desktop import add_desktop_parser
from .subcommands.parser_misc import (
    add_status_parser, add_model_parser, add_cost_parser, add_doctor_parser,
    add_skills_parser, add_plugins_parser,
)

# ── Handler proxy'leri ────────────────────────────────────────────────────────
def _cmd_model(args):
    """Model/provider ayarla, config.yaml + .env otomatik guncellensin."""
    from reymen.sistem.config_loader import config_guncelle
    import os
    degisti = []
    if args.model:
        config_guncelle("model", args.model)
        degisti.append(f"model={args.model}")
    if args.provider:
        config_guncelle("provider", args.provider)
        degisti.append(f"provider={args.provider}")
    if args.api_key:
        # .env'ye yaz
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        provider_upper = (args.provider or "deepseek").upper().replace("-", "_")
        key_var = f"{provider_upper}_API_KEY"
        with open(env_path, "a") as f:
            f.write(f"\n{key_var}={args.api_key}\n")
        degisti.append(f"{key_var}=*** (api key eklendi)")
    if degisti:
        return f"  [OK] Guncellendi: {', '.join(degisti)}"
    return "  Kullanim: reymen model <model_adi> [--provider <provider>] [--api-key <key>]"

def _cmd_gateway_proxy(args):
    from reymen.arac.cli_commands import cmd_gateway; return cmd_gateway(args)
def _cmd_config_proxy(args):
    from reymen.arac.cli_commands import cmd_config; return cmd_config(args)
def _cmd_session_proxy(args):
    from reymen.arac.cli_commands import cmd_session; return cmd_session(args)
def _cmd_doctor_proxy(args):
    from reymen.arac.cli_commands import cmd_doctor; return cmd_doctor(args)
def _cmd_backup_proxy(args):
    from reymen.arac.cli_commands import cmd_backup; return cmd_backup(args)
def _cmd_cost_proxy(args):
    from reymen.console import cmd_cost; return cmd_cost(args)
def _cmd_status_proxy(args=None):
    from reymen.console import cmd_status; import argparse as _ap
    return cmd_status(args or _ap.Namespace())

def _cmd_desktop(args):
    from reymen.desktop import web_server, AutoStartManager
    cmd = args.desktop_cmd
    if cmd == "start": return web_server.start()
    if cmd == "stop": return web_server.stop()
    if cmd == "restart": return web_server.restart()
    if cmd == "status":
        s = web_server.status
        lines = [f"Durum: {s}"]
        if s == "running": lines.append("URL: http://127.0.0.1:5000")
        lines.append(f"Auto-start: {'Aktif' if AutoStartManager.is_enabled() else 'Pasif'}")
        return "\n".join(lines)
    if cmd == "autostart": return AutoStartManager.toggle()
    return "Kullanim: desktop {start|stop|restart|status|autostart}"

# ── Hermes-parity handler'lar ──────────────────────────────────────────────
def _cmd_skills(args):
    """Skills yonetimi — henuz implementasyon reymen.console'a yonlendirilecek."""
    alt = getattr(args, "sub", "list")
    print(f"  [OK] skills {alt} (Henuz implementasyon asamasinda)")
    return 0

def _cmd_plugins(args):
    """Plugins yonetimi — henuz implementasyon reymen.console'a yonlendirilecek."""
    alt = getattr(args, "sub", "list")
    print(f"  [OK] plugins {alt} (Henuz implementasyon asamasinda)")
    return 0

# ── Parser kurucusu ───────────────────────────────────────────────────────────
def build_parser():
    p = argparse.ArgumentParser(prog="reymen",
        description="ReYMeN -- Otonom AI Ajan",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-V","--version",action="store_true",help="Versiyon goster ve cik")
    p.add_argument("-z","--oneshot",metavar="PROMPT",default=None,help="One-shot: tek soru, cevap")
    p.add_argument("-m","--model",default=None,help="Model secimi")
    p.add_argument("--provider",default=None,help="Provider secimi")
    p.add_argument("-t","--toolsets",default=None,help="Toolset listesi")
    p.add_argument("-s","--skills",action="append",default=None,help="Skill on yukle")
    p.add_argument("-c","--continue",dest="continue_last",nargs="?",const=True,default=None,metavar="SESSION")
    p.add_argument("--yolo",action="store_true",default=False)
    p.add_argument("--tui",action="store_true",default=False)
    p.add_argument("--cli",action="store_true",default=False)
    p.add_argument("--accept-hooks",action="store_true",default=False)
    sub = p.add_subparsers(dest="command",help="Alt komut")
    add_status_parser(sub).set_defaults(func=lambda a: _cmd_status_proxy(a))
    add_model_parser(sub).set_defaults(func=_cmd_model)
    add_cost_parser(sub).set_defaults(func=lambda a: _cmd_cost_proxy(a))
    add_gateway_parser(sub).set_defaults(func=lambda a: _cmd_gateway_proxy(a))
    add_config_parser(sub).set_defaults(func=lambda a: _cmd_config_proxy(a))
    add_session_parser(sub).set_defaults(func=lambda a: _cmd_session_proxy(a))
    add_doctor_parser(sub).set_defaults(func=lambda a: _cmd_doctor_proxy(a))
    add_backup_parser(sub).set_defaults(func=lambda a: _cmd_backup_proxy(a))
    add_desktop_parser(sub).set_defaults(func=_cmd_desktop)
    add_cron_parser(sub).set_defaults(func=lambda a: _cmd_cron(a))

    # Hermes-parity: skills, plugins + tools, setup, profile, logs, mcp
    add_skills_parser(sub).set_defaults(func=lambda a: _cmd_skills(a))
    add_plugins_parser(sub).set_defaults(func=lambda a: _cmd_plugins(a))
    for _ad in ["tools", "setup", "profile", "logs", "mcp"]:
        _p = sub.add_parser(_ad, help=f"{_ad} yonetimi")
        _p.set_defaults(func=lambda a, n=_ad: print(f"  [OK] reymen {n}") or 0)

    return p

# ── Cron handler ──────────────────────────────────────────────────────────────
def _cmd_cron(args):
    alt = getattr(args,"sub",None) or "list"
    if alt == "list":
        try:
            from reymen.cereyan.cron_scheduler import CronScheduler
            jobs = CronScheduler().list_jobs()
        except Exception: jobs = []
        if not jobs: print(f"  {y('Hic cron isi yok.')}"); return 0
        print(f"\n  {bld('Kron Isleri')}\n  {d(40*'-')}")
        for j in jobs:
            ik = g("V") if j.get("enabled",False) else r("X")
            print(f"  {ik} {c(j.get('job_id','?'))}  {d(j.get('name','') or j.get('schedule',''))}")
        return 0
    if alt == "status":
        try:
            from reymen.cereyan.cron_scheduler import CronScheduler
            durum = CronScheduler().scheduler_status()
        except Exception: print(f"  {r('[HATA]')} CronScheduler erisilemiyor."); return 1
        print(f"\n  {bld('Cron Scheduler')}\n  {d(40*'-')}")
        for k,v in durum.items(): print(f"  {c(k+':')} {v}")
        return 0
    if alt == "create":
        prompt = getattr(args,"prompt",None)
        if not prompt: print(f"  {r('[HATA]')} Prompt gerekli"); return 1
        from reymen.cereyan.cron_scheduler import CronScheduler
        jid = CronScheduler().create_job(prompt=prompt)
        print(f"  {g('V')} Cron: {c(jid)}"); return 0
    for cmd,fname in [("pause","pause_job"),("resume","resume_job"),("remove","remove_job"),("run","run_job")]:
        if alt == cmd:
            jid = getattr(args,"job_id",None)
            if not jid: print(f"  {r('[HATA]')} job_id gerekli"); return 1
            import importlib as _il
            _mod = _il.import_module("reymen.cereyan.cron_scheduler")
            getattr(_mod, fname)(jid)
            return 0
    print(f"  {y('Bilinmeyen cron:')} {alt}"); return 1

# ── Ana giris (bilinmeyen komut fallback'i) ───────────────────────────────────
def main():
    print(f"  {y('[UYARI]')} Bilinmeyen komut. Bilinen: status, model, cost, gateway, config, session, doctor, backup, cron, desktop")
    print(f"  Detay: reymen --help")
    return 1
