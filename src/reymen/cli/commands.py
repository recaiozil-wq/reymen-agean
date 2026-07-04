# -*- coding: utf-8 -*-
"""commands.py — Slash komut registry ve handler yonlendirme.

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
        name:        Kanonik komut adi (slash yok) — orn: "help", "search".
        description: Insan-okunabilir aciklama.
        category:    Kategori adi — "Bilgi", "Oturum", "Yapilandirma", vb.
        aliases:    Alternatif adlar — orn: ("h", "yardim").
        args_hint:  Arguman ipucu — orn: "<sorgu>", "[model]".
        handler:    Komutu calistiracak fonksiyon (Callable[[str], str]).
    """

    name: str
    description: str
    category: str = "Genel"
    aliases: tuple[str, ...] = ()
    args_hint: str = ""
    handler: Callable[[str], str] | None = None


# ---------------------------------------------------------------------------
# Handler'lar — mevcut parser'lara yonlendirme
# ---------------------------------------------------------------------------

def _handler_help(args: str = "") -> str:
    """Yardim menusu (reymen.cli.tui'deki /yardim mantigi ile)."""
    from reymen.cli.subcommands._shared import c, g, y, d

    satirlar = [
        f"{g('ReYMeN Slash Komutlari')}",
        f"{d('─' * 45)}",
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
    """Genel durum raporu — parser_misc.add_status_parser yapisina yonlenir."""
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
    """Model secimi — parser_misc.add_model_parser yapisina yonlenir."""
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
    """Gecmis konusma arama — session_search_tool yapisina yonlenir."""
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
    """Git yedekleme — parser_backup.add_backup_parser yapisina yonlenir."""
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
    """Sistem saglik kontrolu — parser_misc.add_doctor_parser yapisina yonlenir."""
    import sys
    from pathlib import Path

    satirlar = ["🩺 ReYMeN Sistem Saglik Kontrolu", "─" * 40]
    satirlar.append(f"  Python:    {sys.version.split()[0]}")
    env_paths = [Path.cwd() / ".env", Path.home() / ".reymen" / ".env"]
    for ep in env_paths:
        if ep.exists():
            satirlar.append(f"  .env:      {ep} (✓)")
            break
    else:
        satirlar.append("  .env:      Bulunamadi (✗)")
    try:
        from reymen.cli.profiles import list_profiles
        profiller = list_profiles()
        satirlar.append(f"  Profiller: {', '.join(profiller)}")
    except ImportError:
        satirlar.append("  Profiller: profil modulu yuklu degil")
    satirlar.append("")
    satirlar.append("✅ Sistem saglikli gorunuyor.")
    return "\n".join(satirlar)


def _handler_config(args: str = "") -> str:
    """Config goruntuleme — parser_config.add_config_parser yapisina yonlenir."""
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
            return f"  ✅ {ns.key} = {ns.value}"
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
    """Session yonetimi — parser_session.add_session_parser yapisina yonlenir."""
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
            lines = [f"  {s.get('session_id', s.get('id', '?'))[:12]} | {s.get('title', s.get('name', 'İsimsiz'))}" for s in sessions]
            return f"[Oturumlar] ({len(sessions)} adet)\n" + "\n".join(lines)
        elif sub_cmd == "last":
            s = db.get_last_session()
            if s:
                return f"[Son Oturum] {s.get('session_id', s.get('id', '?'))[:12]} | {s.get('title', s.get('name', 'İsimsiz'))}"
            return "[Son Oturum] Bulunamadi."
        return "[Oturum] Kullanim: /session [list|last] [--limit N]"
    except ImportError:
        return "[Oturum] SessionDB modulu bulunamadi."
    except Exception as e:
        return f"[Oturum] Hata: {e}"


def _handler_skills(args: str = "") -> str:
    """Skill yonetimi — parser_misc.add_skills_parser yapisina yonlenir."""
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
    """Gateway yonetimi — parser_gateway.add_gateway_parser yapisina yonlenir."""
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
            lines = [f"  {p['name']:<20} {'🟢' if p.get('active') else '🔴'}" for p in platforms]
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
    """Cron yonetimi — parser_cron.add_cron_parser yapisina yonlenir."""
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
        return f"[Gorsel] '{args.strip()}' — gorsel olusturma araci yuklu degil."
    except Exception as e:
        return f"[Gorsel] Hata: {e}"


# ---------------------------------------------------------------------------
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
# Slash komut registry — tek dogruluk kaynagi
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

    # Bilinmeyen komut — ReYMeN_cli/commands.py registry'sinde de ara
    try:
        from ReYMeN_cli.commands import resolve_command as resolve_cli_cmd

        cli_cmd = resolve_cli_cmd(cmd_name)
        if cli_cmd:
            return f"[Bilinmeyen] /{cmd_name} — ReYMeN CLI'da tanimli ama henuz tasinmadi: {cli_cmd.description}"
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
