"""ReYMeN console CLI — ReYMeN'teki ``reymen_cli/`` paketinin ReYMeN karşılığı.

ReYMeN'te komutlar::

    reymen status         → hermes_cli/main.py → cmd_status()
    reymen model          → hermes_cli/model_cmd.py
    reymen cron list      → hermes_cli/cron_cmd.py

Bu modül, ``reymen_launcher.py``'deki argparse üzerinden çağrılır.
Kullanım::

    reymen status
    reymen model
    reymen cost summary
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


# ---------------------------------------------------------------------------
# Alt komutlar (hermes_cli/ cmd_* karşılığı)
# ---------------------------------------------------------------------------
def cmd_version(args: argparse.Namespace) -> int:
    """Versiyon bilgisi."""
    from reymen_launcher import _REYMEN_VERSION, _REYMEN_BUILD, _REYMEN_CONFIG, _KOK

    print(f"ReYMeN Agent v{_REYMEN_VERSION} ({_REYMEN_BUILD})")
    print(f"Proje: {_KOK}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Model: {_REYMEN_CONFIG['model']} ({_REYMEN_CONFIG['provider']})")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Genel durum raporu (ReYMeN'teki ``reymen status`` gibi)."""
    from reymen_launcher import _mevcut_model, _KOK, _REYMEN_VERSION, _g, _c, _d, _gb

    m, p = _mevcut_model()
    print(f"  {_gb('ReYMeN Agent Durumu')}")
    print(f"  {'─' * 50}")
    print(f"  Model:      {_g(m)}")
    print(f"  Provider:   {_c(p)}")
    print(f"  Versiyon:   {_d(_REYMEN_VERSION)}")
    print(f"  Çalışma:    {_KOK}")
    print(f"  Python:     {sys.executable}")
    return 0


def cmd_model(args: argparse.Namespace) -> int:
    """Model/Provider seçim ekranı (ReYMeN'teki ``reymen model`` gibi)."""
    from reymen_launcher import _api_kontrol_bekle, _model_sec

    api_sonuc = _api_kontrol_bekle(timeout=3)
    _model_sec(api_sonuc)
    return 0


def cmd_cost(args: argparse.Namespace) -> int:
    """API maliyet takibi (ReYMeN'teki ``reymen cost`` gibi)."""
    try:
        from reymen import cost_tracker
    except ImportError:
        print("[HATA] cost_tracker modülü bulunamadı.")
        return 1

    sub = getattr(args, "sub", None)
    if sub == "summary":
        print_json(cost_tracker.summary())
    elif sub == "log":
        print_json(cost_tracker.dump_log(limit=getattr(args, "limit", 20)))
    elif sub == "reset":
        count = cost_tracker.reset()
        print(f"{count} kayıt silindi.")
    else:
        print_json(cost_tracker.summary())
    return 0


# ---------------------------------------------------------------------------
# Parser (ReYMeN'teki _parser.py karşılığı)
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """Birleşik CLI parser."""
    parser = argparse.ArgumentParser(
        prog="reymen",
        description="ReYMeN Agent - AI assistant with tool-calling capabilities",
    )
    parser.set_defaults(func=None)

    sub = parser.add_subparsers(dest="command", required=True)

    # version
    p_ver = sub.add_parser("version", help="Versiyon bilgisi")
    p_ver.set_defaults(func=cmd_version)

    # status
    p_st = sub.add_parser("status", help="Genel durum raporu")
    p_st.set_defaults(func=cmd_status)

    # model
    p_mdl = sub.add_parser("model", help="Model/Provider seçimi")
    p_mdl.set_defaults(func=cmd_model)

    # cost
    p_cost = sub.add_parser("cost", help="API maliyet takibi")
    p_cost_sub = p_cost.add_subparsers(dest="sub")
    p_cost_sub.add_parser("summary", help="Maliyet özeti")
    p_log = p_cost_sub.add_parser("log", help="Ham kayıtlar")
    p_log.add_argument("--limit", type=int, default=20)
    p_cost_sub.add_parser("reset", help="Kayıtları temizle")
    p_cost.set_defaults(func=cmd_cost, sub="summary")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.func:
        return args.func(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
