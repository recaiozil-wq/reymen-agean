# -*- coding: utf-8 -*-
"""delegate_task_tool.py — Görevi alt process'e devret."""

from __future__ import annotations
import subprocess
import sys
import json
from pathlib import Path
import logging
logger = logging.getLogger(__name__)


_MAIN_PY = Path(__file__).resolve().parent.parent / "main.py"
_TIMEOUT  = 60  # saniye


def run(
    gorev: str = "",
    zaman_asimi: int = _TIMEOUT,
    json_cikti: bool = False,
) -> str:
    gorev = gorev.strip()
    if not gorev:
        return "[Hata]: gorev parametresi gerekli."

    if not _MAIN_PY.exists():
        return f"[Hata]: main.py bulunamadı — {_MAIN_PY}"

    try:
        zaman_asimi = max(5, min(int(zaman_asimi), 300))
    except (TypeError, ValueError):
        zaman_asimi = _TIMEOUT

    try:
        proc = subprocess.run(
            [sys.executable, str(_MAIN_PY), "--gorev", gorev],
            capture_output=True,
            text=True,
            timeout=zaman_asimi,
            # Çocuk process ana process'in env'ini miras alır;
            # güvenlik gereği kısıtlama: env={"PATH": os.environ["PATH"]}
        )
    except subprocess.TimeoutExpired:
        return f"[Hata]: Görev {zaman_asimi}s içinde tamamlanamadı."
    except FileNotFoundError:
        return f"[Hata]: Python yorumlayıcısı veya main.py bulunamadı."
    except Exception as e:
        return f"[Hata]: Alt process başlatılamadı — {e}"

    # Return code kontrolü
    if proc.returncode != 0:
        stderr = proc.stderr.strip()[:500] if proc.stderr else "—"
        return (
            f"[Hata]: Process {proc.returncode} koduyla çıktı.\n"
            f"Stderr: {stderr}"
        )

    cikti = proc.stdout.strip()
    if not cikti:
        return "[Tamam] Process tamamlandı; çıktı yok."

    # JSON parse dene
    if json_cikti:
        try:
            veri = json.loads(cikti)
            return json.dumps(veri, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pass  # JSON değilse ham döndür

    return f"[Sonuç]\n{cikti[:3000]}"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet(
        "GOREV_DEVRET", run, "Görevi alt main.py process'ine devret"
    )
