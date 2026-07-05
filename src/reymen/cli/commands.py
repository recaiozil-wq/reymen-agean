# -*- coding: utf-8 -*-
"""commands.py â€” Slash komut registry ve handler yonlendirme.

Bu modul, ``ReYMeN_cli/commands.py`` ile ayni ``CommandDef`` yapisini kullanir,
ancak ReYMeN'in kendi CLI (``reymen.console`` / ``reymen.cli.tui``) icin
slak komutlari tanimlar. Handler'lar ``reymen.cli.subcommands.*`` altindaki
mevcut parser fonksiyonlarina yonlendirilir.

Kullanim::

    from reymen.cli.commands import (
        resolve_command,
        SLASH_COMMANDS,
        get_handler_for_command,
    )

    cmd = resolve_command("/help")       # -> CommandDef
    h = get_handler_for_command("/help")  # -> handler function
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CommandDef dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CommandDef:
    """Tek bir slash komut tanimi.

    Attributes:
        name:        Kanonik komut adi (slash yok) â€” orn: "help", "search".
        description: Insan-okunabilir aciklama.
        category:    Kategori adi â€” "Bilgi", "Oturum", "Yapilandirma", vb.
        aliases:    Alternatif adlar â€” orn: ("h", "yardim").
        args_hint:  Arguman ipucu â€” orn: "<sorgu>", "[model]".
        handler:    Komutu calistiracak fonksiyon (Callable[[str], str]).
    """

    name: str
    description: str
    category: str = "Genel"
    aliases: tuple[str, ...] = ()
    args_hint: str = ""
    handler: Callable[[str], str] | None = None


# ---------------------------------------------------------------------------
# Handler'lar â€” mevcut parser'lara yonlendirme
# ---------------------------------------------------------------------------

def _handler_help(args: str = "") -> str:
    """Yardim menusu (reymen.cli.tui'deki /yardim mantigi ile)."""
    from reymen.cli.subcommands._shared import c, g, y, d

    satirlar = [
        f"{g('ReYMeN Slash Komutlari')}",
        f"{d('â”€' * 45)}",
    ]
    # Mevcut kayitli komutlari listele
    for cmd in SLASH_COMMANDS.values():
        alias_str = f" ({', '.join('/' + a for a in cmd.aliases)})" if cmd.aliases else ""
        args_str = f" {cmd.args_hint}" if cmd.args_hint else ""
        satirlar.append(f"  {c('/' + cmd.name)}{args_str}{d(alias_str)}")
        satirlar.append(f"    {cmd.description}")
    satirlar.append("")
    satirlar.append(d("Detayli yardim icin: /help <komut_adi>"))
    return "\n".join(satirlar)


def _handler_status(args: str = "") -> str:
    """Genel durum raporu â€” parser_misc.add_status_parser yapisina yonlenir."""
    import argparse

    parser = argparse.ArgumentParser(prog="reymen")
    sub = parser.add_subparsers(dest="command")
    sub.required = False
    from reymen.cli.subcommands.parser_misc import add_status_parser
    add_status_parser(sub)
    try:
        ns = parser.parse_args(["status"] + (args.split() if args else []))
        from reymen.console import cmd_status

        return f"[Durum]\n{cmd_status(ns)}"
    except Exception as e:
        return "[Durum] ReYMeN calisiyor. Detay icin: reymen status"


def _handler_model(args: str = "") -> str:
    """Model secimi â€” parser_misc.add_model_parser yapisina yonlenir."""
    import argparse

    parser = argparse.ArgumentParser(prog="reymen")
    sub = parser.add_subparsers(dest="command")
    sub.required = False
    from reymen.cli.subcommands.parser_misc import add_model_parser
    add_model_parser(sub)
    try:
        ns = parser.parse_args(["model"] + (args.split() if args else []))
        # Model adi dogrudan positional arg'dan gelir
        model_name = getattr(ns, "model", None)
        provider = getattr(ns, "provider", None)
        from reymen.console import cmd_model

        return f"[Model] Model: {model_name or 'deepseek-v4-flash'}, Provider: {provider or 'deepseek'}"
    except Exception as e:
        return f"[Model] Kullanim: /model <ad> --provider <provider>\nHata: {e}"


def _handler_search(args: str = "") -> str:
    """Gecmis konusma arama â€” session_search_tool yapisina yonlenir."""
    if not args.strip():
        return (
            "[Arama] Kullanim: /search <sorgu> [--limit N]\n"
            "Gecmis konusmalarda FTS5 ile arama yapar."
        )
    try:
        from reymen.tools.session_search_tool import session_search_tool

        result = session_search_tool(query=args.strip())
        return f"[Arama: {args.strip()}]\n{result}"
    except ImportError:
        return f"[Arama] '{args.strip()}' icin sonuc bulunamadi (session_search_tool yuklu degil)."
    except Exception as e:
        return f"[Arama] Hata: {e}"


def _handler_backup(args: str = "") -> str:
    """Git yedekleme â€” parser_backup.add_backup_parser yapisina yonlenir."""
    import argparse

    parser = argparse.ArgumentParser(prog="reymen")
    sub = parser.add_subparsers(dest="command")
    sub.required = False
    from reymen.cli.subcommands.parser_backup import add_backup_parser
    add_backup_parser(sub)
    try:
        ns = parser.parse_args(["backup"] + (args.split() if args else ["status"]))
        sub_cmd = getattr(ns, "sub", None)
        from reymen.core.backup_manager import backup_manager

        if sub_cmd == "push":
            backup_manager.push()
            return "[Yedek] Git yedekleme tamamlandi."
        elif sub_cmd == "log":
            log = backup_manager.log()
            return f"[Yedek Logu]\n{log}"
        else:
            durum = backup_manager.status()
            return f"[Yedek Durumu]\n{durum}"
    except ImportError:
        return "[Yedek] backup_manager modulu bulunamadi."
    except Exception as e:
        return f"[Yedek] Hata: {e}"


def _handler_doctor(args: str = "") -> str:
    """Sistem saglik kontrolu â€” parser_misc.add_doctor_parser yapisina yonlenir."""
    import sys
    from pathlib import Path

    satirlar = ["ğŸ©º ReYMeN Sistem Saglik Kontrolu", "â”€" * 40]
    satirlar.append(f"  Python:    {sys.version.split()[0]}")
    env_paths = [Path.cwd() / ".env", Path.home() / ".reymen" / ".env"]
    for ep in env_paths:
        if ep.exists():
            satirlar.append(f"  .env:      {ep} (âœ“)")
            break
    else:
        satirlar.append("  .env:      Bulunamadi (âœ—)")
    try:
        from reymen.cli.profiles import list_profiles
        profiller = list_profiles()
        satirlar.append(f"  Profiller: {', '.join(profiller)}")
    except ImportError:
        satirlar.append("  Profiller: profil modulu yuklu degil")
    satirlar.append("")
    satirlar.append("âœ… Sistem saglikli gorunuyor.")
    return "\n".join(satirlar)


def _handler_config(args: str = "") -> str:
    """Config goruntuleme â€” parser_config.add_config_parser yapisina yonlenir."""
    import argparse

    parser = argparse.ArgumentParser(prog="reymen")
    sub = parser.add_subparsers(dest="command")
    sub.required = False
    from reymen.cli.subcommands.parser_config import add_config_parser
    add_config_parser(sub)
    try:
        ns = parser.parse_args(["config"] + (args.split() if args else ["show"]))
        sub_cmd = getattr(ns, "sub", None)
        from reymen.core.config_manager import config_manager

        if sub_cmd == "show":
            cfg = config_manager.get_all()
            lines = [f"  {k}: {v}" for k, v in cfg.items()]
            return "[Yapilandirma]\n" + "\n".join(lines)
        elif sub_cmd == "get" and hasattr(ns, "key"):
            val = config_manager.get(ns.key)
            return f"  {ns.key}: {val}"
        elif sub_cmd == "set" and hasattr(ns, "key") and hasattr(ns, "value"):
            config_manager.set(ns.key, ns.value)
            return f"  âœ… {ns.key} = {ns.value}"
        elif sub_cmd == "path":
            return f"  Config yolu: {config_manager.config_path or 'Bilinmiyor'}"
        elif sub_cmd in ("env", "list"):
            lines = [f"  {k}: {v}" for k, v in sorted(config_manager.get_all().items())]
            return "[Yapilandirma]\n" + "\n".join(lines)
        return "[Config] Kullanim: /config [show|get <key>|set <key> <value>|path|env|list]"
    except ImportError:
        return "[Config] config_manager modulu bulunamadi."
    except Exception as e:
        return f"[Config] Hata: {e}"


def _handler_session(args: str = "") -> str:
    """Session yonetimi â€” parser_session.add_session_parser yapisina yonlenir."""
    import argparse

    parser = argparse.ArgumentParser(prog="reymen")
    sub = parser.add_subparsers(dest="command")
    sub.required = False
    from reymen.cli.subcommands.parser_session import add_session_parser
    add_session_parser(sub)
    try:
        ns = parser.parse_args(["session"] + (args.split() if args else ["list"]))
        sub_cmd = getattr(ns, "sub", "list")
        limit = getattr(ns, "limit", 10)

        from reymen.hafiza.session_db import SessionDB

        db = SessionDB()
        if sub_cmd == "list":
            sessions = db.list_sessions(limit=limit)
            lines = [f"  {s.get('session_id', s.get('id', '?'))[:12]} | {s.get('title', s.get('name', 'Ä°simsiz'))}" for s in sessions]
            return f"[Oturumlar] ({len(sessions)} adet)\n" + "\n".join(lines)
        elif sub_cmd == "last":
            s = db.get_last_session()
            if s:
                return f"[Son Oturum] {s.get('session_id', s.get('id', '?'))[:12]} | {s.get('title', s.get('name', 'Ä°simsiz'))}"
            return "[Son Oturum] Bulunamadi."
        return "[Oturum] Kullanim: /session [list|last] [--limit N]"
    except ImportError:
        return "[Oturum] SessionDB modulu bulunamadi."
    except Exception as e:
        return f"[Oturum] Hata: {e}"


def _handler_skills(args: str = "") -> str:
    """Skill yonetimi â€” parser_misc.add_skills_parser yapisina yonlenir."""
    try:
        from reymen.core.skills_hub import SkillsHub

        hub = SkillsHub()
        skills = hub.list_skills()
        lines = []
        for s in skills:
            name = s.get("name", s.get("id", "?"))
            desc = s.get("description", "")[:60]
            lines.append(f"  {name:<20} {desc}")
        return f"[Skills] ({len(skills)} adet)\n" + "\n".join(lines) if lines else "[Skills] Henuz skill yuklu degil."
    except ImportError:
        return "[Skills] SkillsHub modulu bulunamadi."
    except Exception as e:
        return f"[Skills] Hata: {e}"


def _handler_gateway(args: str = "") -> str:
    """Gateway yonetimi â€” parser_gateway.add_gateway_parser yapisina yonlenir."""
    import argparse

    parser = argparse.ArgumentParser(prog="reymen")
    sub = parser.add_subparsers(dest="command")
    sub.required = False
    from reymen.cli.subcommands.parser_gateway import add_gateway_parser
    add_gateway_parser(sub)
    try:
        ns = parser.parse_args(["gateway"] + (args.split() if args else ["status"]))
        sub_cmd = getattr(ns, "sub", "status")
        from reymen.core.gateway_manager import GatewayManager

        gw = GatewayManager()
        if sub_cmd == "status":
            durum = gw.status()
            return f"[Gateway Durumu]\n{durum}"
        elif sub_cmd == "list":
            platforms = gw.list_platforms()
            lines = [f"  {p['name']:<20} {'ğŸŸ¢' if p.get('active') else 'ğŸ”´'}" for p in platforms]
            return f"[Gateway Platformlari]\n" + "\n".join(lines)
        elif sub_cmd == "start":
            profil = getattr(ns, "profil", None)
            gw.start(profil=profil)
            return f"[Gateway] Baslatildi (profil: {profil or 'default'})"
        elif sub_cmd == "stop":
            gw.stop()
            return "[Gateway] Durduruldu."
        elif sub_cmd == "restart":
            gw.restart()
            return "[Gateway] Yeniden baslatildi."
        return "[Gateway] Kullanim: /gateway [status|list|start|stop|restart] [--profil AD]"
    except ImportError:
        return "[Gateway] GatewayManager modulu bulunamadi."
    except Exception as e:
        return f"[Gateway] Hata: {e}"


def _handler_cron(args: str = "") -> str:
    """Cron yonetimi â€” parser_cron.add_cron_parser yapisina yonlenir."""
    import argparse

    parser = argparse.ArgumentParser(prog="reymen")
    sub = parser.add_subparsers(dest="command")
    sub.required = False
    from reymen.cli.subcommands.parser_cron import add_cron_parser
    add_cron_parser(sub)
    try:
        ns = parser.parse_args(["cron"] + (args.split() if args else ["list"]))
        sub_cmd = getattr(ns, "sub", "list")
        from reymen.core.cron_manager import CronManager

        cm = CronManager()
        if sub_cmd == "list":
            jobs = cm.list_jobs()
            lines = [f"  {j['id']:<20} {j.get('schedule', j.get('cron', '?')):<15} {j.get('status', '?')}" for j in jobs]
            return f"[Cron Gorevleri] ({len(jobs)} adet)\n" + "\n".join(lines) if lines else "[Cron] Henuz gorev yok."
        elif sub_cmd == "status":
            durum = cm.status()
            return f"[Cron Durumu]\n{durum}"
        elif sub_cmd == "create":
            prompt = getattr(ns, "prompt", args)
            if prompt:
                cm.create(prompt=prompt)
                return f"[Cron] Gorev olusturuldu: {prompt}"
            return "[Cron] Kullanim: /cron create <prompt>"
        elif sub_cmd == "pause":
            jid = getattr(ns, "job_id", None)
            cm.pause(jid)
            return f"[Cron] Gorev duraklatildi: {jid or 'mevcut'}"
        elif sub_cmd == "resume":
            jid = getattr(ns, "job_id", None)
            cm.resume(jid)
            return f"[Cron] Gorev devam ettirildi: {jid or 'mevcut'}"
        elif sub_cmd == "remove":
            jid = getattr(ns, "job_id", None)
            cm.remove(jid)
            return f"[Cron] Gorev silindi: {jid or 'mevcut'}"
        elif sub_cmd == "run":
            jid = getattr(ns, "job_id", None)
            cm.run(jid)
            return f"[Cron] Gorev calistiriliyor: {jid or 'mevcut'}"
        return "[Cron] Kullanim: /cron [list|status|create|pause|resume|remove|run]"
    except ImportError:
        return "[Cron] CronManager modulu bulunamadi."
    except Exception as e:
        return f"[Cron] Hata: {e}"


def _handler_image(args: str = "") -> str:
    """Gorsel olusturma."""
    if not args.strip():
        return "[Gorsel] Kullanim: /image <prompt> [--ratio square|portrait]\nFAL/OpenAI/xAI ile gorsel olusturur."
    try:
        from reymen.arac.araclar_gelismis import gorsel_olustur

        result = gorsel_olustur(prompt=args.strip())
        return f"[Gorsel: {args.strip()}]\n{result}"
    except ImportError:
        return f"[Gorsel] '{args.strip()}' â€” gorsel olusturma araci yuklu degil."
    except Exception as e:
        return f"[Gorsel] Hata: {e}"


# ---------------------------------------------------------------------------


def _handler_agents(args: str = "") -> str:
    """/agents â€” Show active agents and running tasks"""
    # TODO: implementasyon eklenecek
    return f"/agents stub â€” Show active agents and running tasks"


def _handler_approve(args: str = "") -> str:
    """/approve â€” Approve a pending dangerous command"""
    # TODO: implementasyon eklenecek
    return f"/approve stub â€” Approve a pending dangerous command"


def _handler_background(args: str = "") -> str:
    """/background â€” Run a prompt in the background"""
    # TODO: implementasyon eklenecek
    return f"/background stub â€” Run a prompt in the background"


def _handler_billing(args: str = "") -> str:
    """/billing â€” Manage Nous terminal billing â€” buy credits, auto-reload, limits"""
    # TODO: implementasyon eklenecek
    return f"/billing stub â€” Manage Nous terminal billing â€” buy credits, auto-reload, limits"


def _handler_blueprint(args: str = "") -> str:
    """/blueprint â€” Set up an automation from a blueprint template"""
    # TODO: implementasyon eklenecek
    return f"/blueprint stub â€” Set up an automation from a blueprint template"


def _handler_branch(args: str = "") -> str:
    """/branch â€” Branch the current session (explore a different path)"""
    # TODO: implementasyon eklenecek
    return f"/branch stub â€” Branch the current session (explore a different path)"


def _handler_browser(args: str = "") -> str:
    """/browser â€” Connect browser tools to your live Chromium-family browser via CDP"""
    # TODO: implementasyon eklenecek
    return f"/browser stub â€” Connect browser tools to your live Chromium-family browser via CDP"


def _handler_bundles(args: str = "") -> str:
    """/bundles â€” List skill bundles (aliases /<name> for multiple skills)"""
    # TODO: implementasyon eklenecek
    return f"/bundles stub â€” List skill bundles (aliases /<name> for multiple skills)"


def _handler_busy(args: str = "") -> str:
    """/busy â€” Control what Enter does while ReYMeN is working"""
    # TODO: implementasyon eklenecek
    return f"/busy stub â€” Control what Enter does while ReYMeN is working"


def _handler_clear(args: str = "") -> str:
    """/clear â€” Clear screen and start a new session"""
    # TODO: implementasyon eklenecek
    return f"/clear stub â€” Clear screen and start a new session"


def _handler_codex_runtime(args: str = "") -> str:
    """/codex-runtime â€” Toggle codex app-server runtime for OpenAI/Codex models"""
    # TODO: implementasyon eklenecek
    return f"/codex-runtime stub â€” Toggle codex app-server runtime for OpenAI/Codex models"


def _handler_commands(args: str = "") -> str:
    """/commands â€” Browse all commands and skills (paginated)"""
    # TODO: implementasyon eklenecek
    return f"/commands stub â€” Browse all commands and skills (paginated)"


def _handler_compress(args: str = "") -> str:
    """/compress â€” Compress conversation context (add 'here [N]' to keep recent N turns)"""
    # TODO: implementasyon eklenecek
    return f"/compress stub â€” Compress conversation context (add 'here [N]' to keep recent N turns)"


def _handler_copy(args: str = "") -> str:
    """/copy â€” Copy the last assistant response to clipboard"""
    # TODO: implementasyon eklenecek
    return f"/copy stub â€” Copy the last assistant response to clipboard"


def _handler_credits(args: str = "") -> str:
    """/credits â€” Show Nous credit balance and top up"""
    # TODO: implementasyon eklenecek
    return f"/credits stub â€” Show Nous credit balance and top up"


def _handler_curator(args: str = "") -> str:
    """/curator â€” Background skill maintenance (status, run, pin, archive, list-archived)"""
    # TODO: implementasyon eklenecek
    return f"/curator stub â€” Background skill maintenance (status, run, pin, archive, list-archived)"


def _handler_debug(args: str = "") -> str:
    """/debug â€” Upload debug report (system info + logs) and get shareable links"""
    # TODO: implementasyon eklenecek
    return f"/debug stub â€” Upload debug report (system info + logs) and get shareable links"


def _handler_deny(args: str = "") -> str:
    """/deny â€” Deny a pending dangerous command"""
    # TODO: implementasyon eklenecek
    return f"/deny stub â€” Deny a pending dangerous command"


def _handler_fast(args: str = "") -> str:
    """/fast â€” Toggle fast mode â€” OpenAI Priority Processing / Anthropic Fast Mode (Normal/Fast)"""
    # TODO: implementasyon eklenecek
    return f"/fast stub â€” Toggle fast mode â€” OpenAI Priority Processing / Anthropic Fast Mode (Normal/Fast)"


def _handler_footer(args: str = "") -> str:
    """/footer â€” Toggle gateway runtime-metadata footer on final replies"""
    # TODO: implementasyon eklenecek
    return f"/footer stub â€” Toggle gateway runtime-metadata footer on final replies"


def _handler_goal(args: str = "") -> str:
    """/goal â€” Set a standing goal ReYMeN works on across turns until achieved"""
    # TODO: implementasyon eklenecek
    return f"/goal stub â€” Set a standing goal ReYMeN works on across turns until achieved"


def _handler_gquota(args: str = "") -> str:
    """/gquota â€” Show Google Gemini Code Assist quota usage"""
    # TODO: implementasyon eklenecek
    return f"/gquota stub â€” Show Google Gemini Code Assist quota usage"


def _handler_handoff(args: str = "") -> str:
    """/handoff â€” Hand off this session to a messaging platform (Telegram, Discord, etc.)"""
    # TODO: implementasyon eklenecek
    return f"/handoff stub â€” Hand off this session to a messaging platform (Telegram, Discord, etc.)"


def _handler_history(args: str = "") -> str:
    """/history â€” Show conversation history"""
    # TODO: implementasyon eklenecek
    return f"/history stub â€” Show conversation history"


def _handler_indicator(args: str = "") -> str:
    """/indicator â€” Pick the TUI busy-indicator style"""
    # TODO: implementasyon eklenecek
    return f"/indicator stub â€” Pick the TUI busy-indicator style"


def _handler_insights(args: str = "") -> str:
    """/insights â€” Show usage insights and analytics"""
    # TODO: implementasyon eklenecek
    return f"/insights stub â€” Show usage insights and analytics"


def _handler_kanban(args: str = "") -> str:
    """/kanban â€” Multi-profile collaboration board (tasks, links, comments)"""
    # TODO: implementasyon eklenecek
    return f"/kanban stub â€” Multi-profile collaboration board (tasks, links, comments)"


def _handler_memory(args: str = "") -> str:
    """/memory â€” Review pending memory writes / toggle the approval gate"""
    # TODO: implementasyon eklenecek
    return f"/memory stub â€” Review pending memory writes / toggle the approval gate"


def _handler_new(args: str = "") -> str:
    """/new â€” Start a new session (fresh session ID + history)"""
    # TODO: implementasyon eklenecek
    return f"/new stub â€” Start a new session (fresh session ID + history)"


def _handler_paste(args: str = "") -> str:
    """/paste â€” Attach clipboard image from your clipboard"""
    # TODO: implementasyon eklenecek
    return f"/paste stub â€” Attach clipboard image from your clipboard"


def _handler_personality(args: str = "") -> str:
    """/personality â€” Set a predefined personality"""
    # TODO: implementasyon eklenecek
    return f"/personality stub â€” Set a predefined personality"


def _handler_platform(args: str = "") -> str:
    """/platform â€” Pause, resume, or list a failing gateway platform"""
    # TODO: implementasyon eklenecek
    return f"/platform stub â€” Pause, resume, or list a failing gateway platform"


def _handler_plugins(args: str = "") -> str:
    """/plugins â€” List installed plugins and their status"""
    # TODO: implementasyon eklenecek
    return f"/plugins stub â€” List installed plugins and their status"


def _handler_profile(args: str = "") -> str:
    """/profile â€” Show active profile name and home directory"""
    # TODO: implementasyon eklenecek
    return f"/profile stub â€” Show active profile name and home directory"


def _handler_queue(args: str = "") -> str:
    """/queue â€” Queue a prompt for the next turn (doesn't interrupt)"""
    # TODO: implementasyon eklenecek
    return f"/queue stub â€” Queue a prompt for the next turn (doesn't interrupt)"


def _handler_quit(args: str = "") -> str:
    """/quit â€” Exit the CLI (use --delete to also remove session history)"""
    # TODO: implementasyon eklenecek
    return f"/quit stub â€” Exit the CLI (use --delete to also remove session history)"


def _handler_reasoning(args: str = "") -> str:
    """/reasoning â€” Manage reasoning effort and display"""
    # TODO: implementasyon eklenecek
    return f"/reasoning stub â€” Manage reasoning effort and display"


def _handler_redraw(args: str = "") -> str:
    """/redraw â€” Force a full UI repaint (recovers from terminal drift)"""
    # TODO: implementasyon eklenecek
    return f"/redraw stub â€” Force a full UI repaint (recovers from terminal drift)"


def _handler_reload(args: str = "") -> str:
    """/reload â€” Reload .env variables into the running session"""
    # TODO: implementasyon eklenecek
    return f"/reload stub â€” Reload .env variables into the running session"


def _handler_reload_mcp(args: str = "") -> str:
    """/reload-mcp â€” Reload MCP servers from config"""
    # TODO: implementasyon eklenecek
    return f"/reload-mcp stub â€” Reload MCP servers from config"


def _handler_reload_skills(args: str = "") -> str:
    """/reload-skills â€” Re-scan .ReYMeN/skills/ for newly installed or removed skills"""
    # TODO: implementasyon eklenecek
    return f"/reload-skills stub â€” Re-scan .ReYMeN/skills/ for newly installed or removed skills"


def _handler_restart(args: str = "") -> str:
    """/restart â€” Gracefully restart the gateway after draining active runs"""
    # TODO: implementasyon eklenecek
    return f"/restart stub â€” Gracefully restart the gateway after draining active runs"


def _handler_resume(args: str = "") -> str:
    """/resume â€” Resume a previously-named session"""
    # TODO: implementasyon eklenecek
    return f"/resume stub â€” Resume a previously-named session"


def _handler_retry(args: str = "") -> str:
    """/retry â€” Retry the last message (resend to agent)"""
    # TODO: implementasyon eklenecek
    return f"/retry stub â€” Retry the last message (resend to agent)"


def _handler_rollback(args: str = "") -> str:
    """/rollback â€” List or restore filesystem checkpoints"""
    # TODO: implementasyon eklenecek
    return f"/rollback stub â€” List or restore filesystem checkpoints"


def _handler_save(args: str = "") -> str:
    """/save â€” Save the current conversation"""
    # TODO: implementasyon eklenecek
    return f"/save stub â€” Save the current conversation"


def _handler_sethome(args: str = "") -> str:
    """/sethome â€” Set this chat as the home channel"""
    # TODO: implementasyon eklenecek
    return f"/sethome stub â€” Set this chat as the home channel"


def _handler_skin(args: str = "") -> str:
    """/skin â€” Show or change the display skin/theme"""
    # TODO: implementasyon eklenecek
    return f"/skin stub â€” Show or change the display skin/theme"


def _handler_snapshot(args: str = "") -> str:
    """/snapshot â€” Create or restore state snapshots of ReYMeN config/state"""
    # TODO: implementasyon eklenecek
    return f"/snapshot stub â€” Create or restore state snapshots of ReYMeN config/state"


def _handler_start(args: str = "") -> str:
    """/start â€” Acknowledge platform start pings without a reply"""
    # TODO: implementasyon eklenecek
    return f"/start stub â€” Acknowledge platform start pings without a reply"


def _handler_statusbar(args: str = "") -> str:
    """/statusbar â€” Toggle the context/model status bar"""
    # TODO: implementasyon eklenecek
    return f"/statusbar stub â€” Toggle the context/model status bar"


def _handler_steer(args: str = "") -> str:
    """/steer â€” Inject a message after the next tool call without interrupting"""
    # TODO: implementasyon eklenecek
    return f"/steer stub â€” Inject a message after the next tool call without interrupting"


def _handler_stop(args: str = "") -> str:
    """/stop â€” Kill all running background processes"""
    # TODO: implementasyon eklenecek
    return f"/stop stub â€” Kill all running background processes"


def _handler_subgoal(args: str = "") -> str:
    """/subgoal â€” Add or manage extra criteria on the active goal"""
    # TODO: implementasyon eklenecek
    return f"/subgoal stub â€” Add or manage extra criteria on the active goal"


def _handler_suggestions(args: str = "") -> str:
    """/suggestions â€” Review suggested automations (accept/dismiss)"""
    # TODO: implementasyon eklenecek
    return f"/suggestions stub â€” Review suggested automations (accept/dismiss)"


def _handler_title(args: str = "") -> str:
    """/title â€” Set a title for the current session"""
    # TODO: implementasyon eklenecek
    return f"/title stub â€” Set a title for the current session"


def _handler_tools(args: str = "") -> str:
    """/tools â€” Manage tools: /tools [list|disable|enable] [name...]"""
    # TODO: implementasyon eklenecek
    return f"/tools stub â€” Manage tools: /tools [list|disable|enable] [name...]"


def _handler_toolsets(args: str = "") -> str:
    """/toolsets â€” List available toolsets"""
    # TODO: implementasyon eklenecek
    return f"/toolsets stub â€” List available toolsets"


def _handler_topic(args: str = "") -> str:
    """/topic â€” Enable or inspect Telegram DM topic sessions"""
    # TODO: implementasyon eklenecek
    return f"/topic stub â€” Enable or inspect Telegram DM topic sessions"


def _handler_undo(args: str = "") -> str:
    """/undo â€” Back up N user turns and re-prompt (default 1)"""
    # TODO: implementasyon eklenecek
    return f"/undo stub â€” Back up N user turns and re-prompt (default 1)"


def _handler_update(args: str = "") -> str:
    """/update â€” Update ReYMeN Agent to the latest version"""
    # TODO: implementasyon eklenecek
    return f"/update stub â€” Update ReYMeN Agent to the latest version"


def _handler_usage(args: str = "") -> str:
    """/usage â€” Show token usage and rate limits for the current session"""
    # TODO: implementasyon eklenecek
    return f"/usage stub â€” Show token usage and rate limits for the current session"


def _handler_verbose(args: str = "") -> str:
    """/verbose â€” Cycle tool progress display: off -> new -> all -> verbose"""
    # TODO: implementasyon eklenecek
    return f"/verbose stub â€” Cycle tool progress display: off -> new -> all -> verbose"


def _handler_version(args: str = "") -> str:
    """/version â€” Show ReYMeN Agent version"""
    # TODO: implementasyon eklenecek
    return f"/version stub â€” Show ReYMeN Agent version"


def _handler_voice(args: str = "") -> str:
    """/voice â€” Toggle voice mode"""
    # TODO: implementasyon eklenecek
    return f"/voice stub â€” Toggle voice mode"


def _handler_whoami(args: str = "") -> str:
    """/whoami â€” Show your slash command access (admin / user)"""
    # TODO: implementasyon eklenecek
    return f"/whoami stub â€” Show your slash command access (admin / user)"


def _handler_yolo(args: str = "") -> str:
    """/yolo â€” Toggle YOLO mode (skip all dangerous command approvals)"""
    # TODO: implementasyon eklenecek
    return f"/yolo stub â€” Toggle YOLO mode (skip all dangerous command approvals)"


# Handler yonlendirme tablosu: komut_adi -> handler fonksiyonu
# ---------------------------------------------------------------------------

HANDLER_TABLE: dict[str, Callable[[str], str]] = {
    "help": _handler_help,
    "search": _handler_search,
    "image": _handler_image,
    "config": _handler_config,
    "session": _handler_session,
    "backup": _handler_backup,
    "doctor": _handler_doctor,
    "skills": _handler_skills,
    "model": _handler_model,
    "status": _handler_status,
    "gateway": _handler_gateway,
    "cron": _handler_cron,

    "agents": _handler_agents,
    "approve": _handler_approve,
    "background": _handler_background,
    "billing": _handler_billing,
    "blueprint": _handler_blueprint,
    "branch": _handler_branch,
    "browser": _handler_browser,
    "bundles": _handler_bundles,
    "busy": _handler_busy,
    "clear": _handler_clear,
    "codex-runtime": _handler_codex_runtime,
    "commands": _handler_commands,
    "compress": _handler_compress,
    "copy": _handler_copy,
    "credits": _handler_credits,
    "curator": _handler_curator,
    "debug": _handler_debug,
    "deny": _handler_deny,
    "fast": _handler_fast,
    "footer": _handler_footer,
    "goal": _handler_goal,
    "gquota": _handler_gquota,
    "handoff": _handler_handoff,
    "history": _handler_history,
    "indicator": _handler_indicator,
    "insights": _handler_insights,
    "kanban": _handler_kanban,
    "memory": _handler_memory,
    "new": _handler_new,
    "paste": _handler_paste,
    "personality": _handler_personality,
    "platform": _handler_platform,
    "plugins": _handler_plugins,
    "profile": _handler_profile,
    "queue": _handler_queue,
    "quit": _handler_quit,
    "reasoning": _handler_reasoning,
    "redraw": _handler_redraw,
    "reload": _handler_reload,
    "reload-mcp": _handler_reload_mcp,
    "reload-skills": _handler_reload_skills,
    "restart": _handler_restart,
    "resume": _handler_resume,
    "retry": _handler_retry,
    "rollback": _handler_rollback,
    "save": _handler_save,
    "sethome": _handler_sethome,
    "skin": _handler_skin,
    "snapshot": _handler_snapshot,
    "start": _handler_start,
    "statusbar": _handler_statusbar,
    "steer": _handler_steer,
    "stop": _handler_stop,
    "subgoal": _handler_subgoal,
    "suggestions": _handler_suggestions,
    "title": _handler_title,
    "tools": _handler_tools,
    "toolsets": _handler_toolsets,
    "topic": _handler_topic,
    "undo": _handler_undo,
    "update": _handler_update,
    "usage": _handler_usage,
    "verbose": _handler_verbose,
    "version": _handler_version,
    "voice": _handler_voice,
    "whoami": _handler_whoami,
    "yolo": _handler_yolo,
}


def get_handler(command_name: str) -> Callable[[str], str] | None:
    """Komut adina gore handler fonksiyonunu doner.

    Args:
        command_name: Komut adi (slash'siz: \"help\", \"model\") veya slash'li (\"/help\", \"/model\").

    Returns:
        Handler fonksiyonu veya None (bulunamadiysa).
    """
    name = command_name.lower().strip().lstrip("/")
    # Once dogrudan ara
    if name in HANDLER_TABLE:
        return HANDLER_TABLE[name]
    # Alias'lardan ara
    for cmd_def in SLASH_COMMANDS.values():
        if name == cmd_def.name:
            return cmd_def.handler
        if name in cmd_def.aliases:
            return cmd_def.handler
    return None


# ---------------------------------------------------------------------------
# Slash komut registry â€” tek dogruluk kaynagi
# ---------------------------------------------------------------------------

SLASH_COMMANDS: dict[str, CommandDef] = {
    "help": CommandDef(
        name="help",
        description="Yardim menusunu goster",
        category="Bilgi",
        aliases=("yardim", "h", "?"),
        handler=_handler_help,
    ),
    "search": CommandDef(
        name="search",
        description="Gecmis konusmalarda FTS5 ile ara",
        category="Oturum",
        aliases=("ara", "s"),
        args_hint="<sorgu> [--limit N]",
        handler=_handler_search,
    ),
    "image": CommandDef(
        name="image",
        description="FAL/OpenAI/xAI ile gorsel olustur",
        category="Arac",
        aliases=("img", "gorsel", "resim"),
        args_hint="<prompt> [--ratio square|portrait]",
        handler=_handler_image,
    ),
    "config": CommandDef(
        name="config",
        description="Yapilandirma bilgilerini goruntule/degistir",
        category="Yapilandirma",
        aliases=("cfg", "ayarlar", "settings"),
        args_hint="[show|get <key>|set <key> <value>|path|env|list]",
        handler=_handler_config,
    ),
    "session": CommandDef(
        name="session",
        description="Oturum yonetimi (listele, son oturum)",
        category="Oturum",
        aliases=("oturum", "sessions", "s"),
        args_hint="[list|last] [--limit N]",
        handler=_handler_session,
    ),
    "backup": CommandDef(
        name="backup",
        description="Git yedekleme (yedekleme durumu/push/log)",
        category="Sistem",
        aliases=("yedek", "bk"),
        args_hint="[status|push|log]",
        handler=_handler_backup,
    ),
    "doctor": CommandDef(
        name="doctor",
        description="Sistem saglik kontrolu",
        category="Sistem",
        aliases=("saglik", "check", "d"),
        handler=_handler_doctor,
    ),
    "skills": CommandDef(
        name="skills",
        description="Yuklu skill'leri listele",
        category="Arac",
        aliases=("beceriler", "sk"),
        handler=_handler_skills,
    ),
    "model": CommandDef(
        name="model",
        description="Model/provider secimi",
        category="Yapilandirma",
        aliases=("m", "mod"),
        args_hint="[model] [--provider name]",
        handler=_handler_model,
    ),
    "status": CommandDef(
        name="status",
        description="Genel durum raporu",
        category="Bilgi",
        aliases=("durum", "st"),
        handler=_handler_status,
    ),
    "gateway": CommandDef(
        name="gateway",
        description="Gateway yonetimi (baslat/durdur/durum)",
        category="Sistem",
        aliases=("gw", "platforms"),
        args_hint="[status|list|start|stop|restart] [--profil AD]",
        handler=_handler_gateway,
    ),
    "cron": CommandDef(
        name="cron",
        description="Zamanlanmis gorev yonetimi",
        category="Sistem",
        aliases=("zamanlayici", "scheduler"),
        args_hint="[list|status|create|pause|resume|remove|run]",
        handler=_handler_cron,
    ),
    "plugin": CommandDef(
        name="plugin",
        description="Plugin yonetimi (list/yukle/kaldir)",
        category="Sistem",
        aliases=("eklenti", "plugins"),
        args_hint="[list|load|unload]",
        handler=_handler_plugins,
    ),
    "agents": CommandDef(
        name="agents",
        description="Show active agents and running tasks",
        category="Session",
        handler=_handler_agents,
    ),
    "approve": CommandDef(
        name="approve",
        description="Approve a pending dangerous command",
        category="Session",
        handler=_handler_approve,
    ),
    "background": CommandDef(
        name="background",
        description="Run a prompt in the background",
        category="Session",
        handler=_handler_background,
    ),
    "billing": CommandDef(
        name="billing",
        description="Manage Nous terminal billing â€” buy credits, auto-reload, limits",
        category="Info",
        handler=_handler_billing,
    ),
    "blueprint": CommandDef(
        name="blueprint",
        description="Set up an automation from a blueprint template",
        category="Tools & Skills",
        handler=_handler_blueprint,
    ),
    "branch": CommandDef(
        name="branch",
        description="Branch the current session (explore a different path)",
        category="Session",
        handler=_handler_branch,
    ),
    "browser": CommandDef(
        name="browser",
        description="Connect browser tools to your live Chromium-family browser via CDP",
        category="Tools & Skills",
        handler=_handler_browser,
    ),
    "bundles": CommandDef(
        name="bundles",
        description="List skill bundles (aliases /<name> for multiple skills)",
        category="Tools & Skills",
        handler=_handler_bundles,
    ),
    "busy": CommandDef(
        name="busy",
        description="Control what Enter does while ReYMeN is working",
        category="Configuration",
        handler=_handler_busy,
    ),
    "clear": CommandDef(
        name="clear",
        description="Clear screen and start a new session",
        category="Session",
        handler=_handler_clear,
    ),
    "codex-runtime": CommandDef(
        name="codex-runtime",
        description="Toggle codex app-server runtime for OpenAI/Codex models",
        category="Configuration",
        handler=_handler_codex_runtime,
    ),
    "commands": CommandDef(
        name="commands",
        description="Browse all commands and skills (paginated)",
        category="Info",
        handler=_handler_commands,
    ),
    "compress": CommandDef(
        name="compress",
        description="Compress conversation context (add 'here [N]' to keep recent N turns)",
        category="Session",
        handler=_handler_compress,
    ),
    "copy": CommandDef(
        name="copy",
        description="Copy the last assistant response to clipboard",
        category="Info",
        handler=_handler_copy,
    ),
    "credits": CommandDef(
        name="credits",
        description="Show Nous credit balance and top up",
        category="Info",
        handler=_handler_credits,
    ),
    "curator": CommandDef(
        name="curator",
        description="Background skill maintenance (status, run, pin, archive, list-archived)",
        category="Tools & Skills",
        handler=_handler_curator,
    ),
    "debug": CommandDef(
        name="debug",
        description="Upload debug report (system info + logs) and get shareable links",
        category="Info",
        handler=_handler_debug,
    ),
    "deny": CommandDef(
        name="deny",
        description="Deny a pending dangerous command",
        category="Session",
        handler=_handler_deny,
    ),
    "fast": CommandDef(
        name="fast",
        description="Toggle fast mode â€” OpenAI Priority Processing / Anthropic Fast Mode (Normal/Fast)",
        category="Configuration",
        handler=_handler_fast,
    ),
    "footer": CommandDef(
        name="footer",
        description="Toggle gateway runtime-metadata footer on final replies",
        category="Configuration",
        handler=_handler_footer,
    ),
    "goal": CommandDef(
        name="goal",
        description="Set a standing goal ReYMeN works on across turns until achieved",
        category="Session",
        handler=_handler_goal,
    ),
    "gquota": CommandDef(
        name="gquota",
        description="Show Google Gemini Code Assist quota usage",
        category="Info",
        handler=_handler_gquota,
    ),
    "handoff": CommandDef(
        name="handoff",
        description="Hand off this session to a messaging platform (Telegram, Discord, etc.)",
        category="Session",
        handler=_handler_handoff,
    ),
    "history": CommandDef(
        name="history",
        description="Show conversation history",
        category="Session",
        handler=_handler_history,
    ),
    "indicator": CommandDef(
        name="indicator",
        description="Pick the TUI busy-indicator style",
        category="Configuration",
        handler=_handler_indicator,
    ),
    "insights": CommandDef(
        name="insights",
        description="Show usage insights and analytics",
        category="Info",
        handler=_handler_insights,
    ),
    "kanban": CommandDef(
        name="kanban",
        description="Multi-profile collaboration board (tasks, links, comments)",
        category="Tools & Skills",
        handler=_handler_kanban,
    ),
    "memory": CommandDef(
        name="memory",
        description="Review pending memory writes / toggle the approval gate",
        category="Tools & Skills",
        handler=_handler_memory,
    ),
    "new": CommandDef(
        name="new",
        description="Start a new session (fresh session ID + history)",
        category="Session",
        handler=_handler_new,
    ),
    "paste": CommandDef(
        name="paste",
        description="Attach clipboard image from your clipboard",
        category="Info",
        handler=_handler_paste,
    ),
    "personality": CommandDef(
        name="personality",
        description="Set a predefined personality",
        category="Configuration",
        handler=_handler_personality,
    ),
    "platform": CommandDef(
        name="platform",
        description="Pause, resume, or list a failing gateway platform",
        category="Info",
        handler=_handler_platform,
    ),
    "plugins": CommandDef(
        name="plugins",
        description="List installed plugins and their status",
        category="Tools & Skills",
        handler=_handler_plugins,
    ),
    "profile": CommandDef(
        name="profile",
        description="Show active profile name and home directory",
        category="Info",
        handler=_handler_profile,
    ),
    "queue": CommandDef(
        name="queue",
        description="Queue a prompt for the next turn (doesn't interrupt)",
        category="Session",
        handler=_handler_queue,
    ),
    "quit": CommandDef(
        name="quit",
        description="Exit the CLI (use --delete to also remove session history)",
        category="Exit",
        handler=_handler_quit,
    ),
    "reasoning": CommandDef(
        name="reasoning",
        description="Manage reasoning effort and display",
        category="Configuration",
        handler=_handler_reasoning,
    ),
    "redraw": CommandDef(
        name="redraw",
        description="Force a full UI repaint (recovers from terminal drift)",
        category="Session",
        handler=_handler_redraw,
    ),
    "reload": CommandDef(
        name="reload",
        description="Reload .env variables into the running session",
        category="Tools & Skills",
        handler=_handler_reload,
    ),
    "reload-mcp": CommandDef(
        name="reload-mcp",
        description="Reload MCP servers from config",
        category="Tools & Skills",
        handler=_handler_reload_mcp,
    ),
    "reload-skills": CommandDef(
        name="reload-skills",
        description="Re-scan .ReYMeN/skills/ for newly installed or removed skills",
        category="Tools & Skills",
        handler=_handler_reload_skills,
    ),
    "restart": CommandDef(
        name="restart",
        description="Gracefully restart the gateway after draining active runs",
        category="Session",
        handler=_handler_restart,
    ),
    "resume": CommandDef(
        name="resume",
        description="Resume a previously-named session",
        category="Session",
        handler=_handler_resume,
    ),
    "retry": CommandDef(
        name="retry",
        description="Retry the last message (resend to agent)",
        category="Session",
        handler=_handler_retry,
    ),
    "rollback": CommandDef(
        name="rollback",
        description="List or restore filesystem checkpoints",
        category="Session",
        handler=_handler_rollback,
    ),
    "save": CommandDef(
        name="save",
        description="Save the current conversation",
        category="Session",
        handler=_handler_save,
    ),
    "sethome": CommandDef(
        name="sethome",
        description="Set this chat as the home channel",
        category="Session",
        handler=_handler_sethome,
    ),
    "skin": CommandDef(
        name="skin",
        description="Show or change the display skin/theme",
        category="Configuration",
        handler=_handler_skin,
    ),
    "snapshot": CommandDef(
        name="snapshot",
        description="Create or restore state snapshots of ReYMeN config/state",
        category="Session",
        handler=_handler_snapshot,
    ),
    "start": CommandDef(
        name="start",
        description="Acknowledge platform start pings without a reply",
        category="Session",
        handler=_handler_start,
    ),
    "statusbar": CommandDef(
        name="statusbar",
        description="Toggle the context/model status bar",
        category="Configuration",
        handler=_handler_statusbar,
    ),
    "steer": CommandDef(
        name="steer",
        description="Inject a message after the next tool call without interrupting",
        category="Session",
        handler=_handler_steer,
    ),
    "stop": CommandDef(
        name="stop",
        description="Kill all running background processes",
        category="Session",
        handler=_handler_stop,
    ),
    "subgoal": CommandDef(
        name="subgoal",
        description="Add or manage extra criteria on the active goal",
        category="Session",
        handler=_handler_subgoal,
    ),
    "suggestions": CommandDef(
        name="suggestions",
        description="Review suggested automations (accept/dismiss)",
        category="Tools & Skills",
        handler=_handler_suggestions,
    ),
    "title": CommandDef(
        name="title",
        description="Set a title for the current session",
        category="Session",
        handler=_handler_title,
    ),
    "tools": CommandDef(
        name="tools",
        description="Manage tools: /tools [list|disable|enable] [name...]",
        category="Tools & Skills",
        handler=_handler_tools,
    ),
    "toolsets": CommandDef(
        name="toolsets",
        description="List available toolsets",
        category="Tools & Skills",
        handler=_handler_toolsets,
    ),
    "topic": CommandDef(
        name="topic",
        description="Enable or inspect Telegram DM topic sessions",
        category="Session",
        handler=_handler_topic,
    ),
    "undo": CommandDef(
        name="undo",
        description="Back up N user turns and re-prompt (default 1)",
        category="Session",
        handler=_handler_undo,
    ),
    "update": CommandDef(
        name="update",
        description="Update ReYMeN Agent to the latest version",
        category="Info",
        handler=_handler_update,
    ),
    "usage": CommandDef(
        name="usage",
        description="Show token usage and rate limits for the current session",
        category="Info",
        handler=_handler_usage,
    ),
    "verbose": CommandDef(
        name="verbose",
        description="Cycle tool progress display: off -> new -> all -> verbose",
        category="Configuration",
        handler=_handler_verbose,
    ),
    "version": CommandDef(
        name="version",
        description="Show ReYMeN Agent version",
        category="Info",
        aliases=['v', ''],
        handler=_handler_version,
    ),
    "voice": CommandDef(
        name="voice",
        description="Toggle voice mode",
        category="Configuration",
        handler=_handler_voice,
    ),
    "whoami": CommandDef(
        name="whoami",
        description="Show your slash command access (admin / user)",
        category="Info",
        handler=_handler_whoami,
    ),
    "yolo": CommandDef(
        name="yolo",
        description="Toggle YOLO mode (skip all dangerous command approvals)",
        category="Configuration",
        handler=_handler_yolo,
    ),

}


# ---------------------------------------------------------------------------
# Yardimci fonksiyonlar
# ---------------------------------------------------------------------------


def resolve_command(text: str) -> CommandDef | None:
    """Slash komut adini veya alias'ini CommandDef'e cozumler.

    Args:
        text: Komut metni (slash'li veya slash'siz): "/help", "help", "/yardim".

    Returns:
        Eslesen CommandDef veya None.
    """
    name = text.lower().strip().lstrip("/")
    if not name:
        return None

    # Splitle ilk kelimeyi al (args varsa)
    base = name.split()[0] if " " in name else name

    if base in SLASH_COMMANDS:
        return SLASH_COMMANDS[base]

    # Alias ara
    for cmd in SLASH_COMMANDS.values():
        if base in cmd.aliases:
            return cmd
    return None


def execute_command(text: str) -> str:
    """Bir slash komut metnini calistirir.

    Args:
        text: Komut metni: "/help", "/search <sorgu>", "/model deepseek"

    Returns:
        Komutun ciktisi (string). Komut bulunamazsa hata mesaji doner.
    """
    name = text.strip().lstrip("/")
    if not name:
        return ""

    # Ayristir: komut_adi ve args
    parts = name.split(None, 1)
    cmd_name = parts[0].lower()
    cmd_args = parts[1] if len(parts) > 1 else ""

    handler = get_handler(cmd_name)
    if handler:
        try:
            return handler(cmd_args)
        except Exception as e:
            logger.exception("Slash command /%s failed: %s", cmd_name, e)
            return f"[HATA] /{cmd_name} komutu calisirken hata: {e}"

    # Bilinmeyen komut â€” ReYMeN_cli/commands.py registry'sinde de ara
    try:
        from ReYMeN_cli.commands import resolve_command as resolve_cli_cmd

        cli_cmd = resolve_cli_cmd(cmd_name)
        if cli_cmd:
            return f"[Bilinmeyen] /{cmd_name} â€” ReYMeN CLI'da tanimli ama henuz tasinmadi: {cli_cmd.description}"
    except ImportError:
        pass

    return f"[HATA] Bilinmeyen komut: /{cmd_name}. /help yazabilirsiniz."


def get_all_commands() -> list[CommandDef]:
    """Tum kayitli komutlari listeler."""
    return list(SLASH_COMMANDS.values())


def get_commands_by_category() -> dict[str, list[CommandDef]]:
    """Komutlari kategoriye gore gruplar."""
    cats: dict[str, list[CommandDef]] = {}
    for cmd in SLASH_COMMANDS.values():
        cats.setdefault(cmd.category, []).append(cmd)
    return cats
