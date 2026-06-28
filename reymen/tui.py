"""🪟 TUI iyileştirme — Rich ile status bar, spinner, progress.

Rich kütüphanesi yüklüyse zengin terminal çıktısı (renk, spinner, progress
bar, status bar) sağlar; yüklü değilse düz metin fallback yapar. Tüm
public API her iki modda da aynı imzaya sahiptir.

Örnek::

    from ReYMeN.tui import StatusBar, with_spinner, progress_bar

    bar = StatusBar()
    bar.update("Çalışıyor...")
    with with_spinner("İndiriliyor"):
        ...
"""

from __future__ import annotations

import contextlib
import sys
import threading
import time
from typing import TYPE_CHECKING, Any, Callable, Iterator, Sequence

if TYPE_CHECKING:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TextColumn,
        TimeElapsedColumn,
    )
    from rich.spinner import Spinner
    from rich.table import Table
    from rich.text import Text

__all__ = [
    "RICH_AVAILABLE",
    "StatusBar",
    "with_spinner",
    "progress_bar",
    "info",
    "success",
    "warning",
    "error",
    "panel",
    "table",
]

# ---------------------------------------------------------------------------
# Rich varlık kontrolü
# ---------------------------------------------------------------------------
# ``Any`` tipi, Pylance'ın "possibly None / unbound" hatalarını önler.
# Değerler yalnızca ``RICH_AVAILABLE`` True iken kullanılır.
_Console: Any = None
_Panel: Any = None
_Progress: Any = None
_BarColumn: Any = None
_SpinnerColumn: Any = None
_TextColumn: Any = None
_TimeElapsedColumn: Any = None
_Spinner: Any = None
_Table: Any = None
_Text: Any = None

try:
    from rich.console import Console as _Console  # type: ignore[assignment]
    from rich.panel import Panel as _Panel  # type: ignore[assignment]
    from rich.progress import (
        BarColumn as _BarColumn,  # type: ignore[assignment]
        Progress as _Progress,  # type: ignore[assignment]
        SpinnerColumn as _SpinnerColumn,  # type: ignore[assignment]
        TextColumn as _TextColumn,  # type: ignore[assignment]
        TimeElapsedColumn as _TimeElapsedColumn,  # type: ignore[assignment]
    )
    from rich.spinner import Spinner as _Spinner  # type: ignore[assignment]
    from rich.table import Table as _Table  # type: ignore[assignment]
    from rich.text import Text as _Text  # type: ignore[assignment]

    RICH_AVAILABLE = True
except ImportError:  # pragma: no cover - opsiyonel bağımlılık
    RICH_AVAILABLE = False


# ---------------------------------------------------------------------------
# Console singleton
# ---------------------------------------------------------------------------
if RICH_AVAILABLE and _Console is not None:
    _console: Any = _Console()
else:
    _console = None


def get_console() -> "Console | None":
    """Global Rich console döndürür (Rich yoksa None)."""
    return _console


# ---------------------------------------------------------------------------
# StatusBar
# ---------------------------------------------------------------------------
class StatusBar:
    """Tek satırlık durum çubuğu.

    Rich varsa canlı güncellenen bir satır; yoksa ``print`` ile basit çıktı.
    """

    def __init__(self) -> None:
        self._text = ""
        self._lock = threading.Lock()
        self._live = None
        if RICH_AVAILABLE:
            try:
                from rich.live import Live
                from rich.text import Text as RichText

                self._live = Live(RichText(""), refresh_per_second=10, transient=True)
                self._live.start()
            except Exception:
                self._live = None

    def update(self, text: str, *, style: str = "") -> None:
        """Durum metnini günceller."""
        with self._lock:
            self._text = text
        if self._live is not None:
            from rich.text import Text as RichText

            self._live.update(RichText(text, style=style))
        else:
            sys.stdout.write(f"\r{text}")
            sys.stdout.flush()

    def clear(self) -> None:
        """Durum çubuğunu temizler."""
        with self._lock:
            self._text = ""
        if self._live is not None:
            from rich.text import Text as RichText

            self._live.update(RichText(""))
        else:
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()

    def stop(self) -> None:
        """Durum çubuğunu kapatır."""
        if self._live is not None:
            self._live.stop()
            self._live = None
        else:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def __enter__(self) -> "StatusBar":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.stop()


# ---------------------------------------------------------------------------
# Spinner context manager
# ---------------------------------------------------------------------------
@contextlib.contextmanager
def with_spinner(
    text: str = "Çalışıyor",
    *,
    spinner_name: str = "dots",
) -> Iterator[None]:
    """Spinner ile uzun süren işlem context manager.

    Rich yoksa basit ``print`` + ``time.sleep`` benzeri davranış.
    """
    if RICH_AVAILABLE and _console is not None:
        with _console.status(text, spinner=spinner_name):
            yield
    else:
        sys.stdout.write(f"... {text}\n")
        sys.stdout.flush()
        try:
            yield
        finally:
            sys.stdout.write("   bitti\n")
            sys.stdout.flush()


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------
@contextlib.contextmanager
def progress_bar(
    total: int,
    description: str = "İlerleme",
) -> Iterator[Callable[[int], None]]:
    """Progress bar context manager.

    Kullanım::

        with progress_bar(100, "İndiriliyor") as advance:
            for _ in range(100):
                advance(1)

    Rich yoksa yüzde olarak ``print`` eder.
    """
    if RICH_AVAILABLE and _console is not None and _Progress is not None:
        progress = _Progress(
            _SpinnerColumn(),
            _TextColumn("[progress.description]{task.description}"),
            _BarColumn(),
            _TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            _TimeElapsedColumn(),
            console=_console,
        )
        task_id = progress.add_task(description, total=total)
        progress.start()
        try:
            def advance(n: int = 1) -> None:
                progress.update(task_id, advance=n)
            yield advance
        finally:
            progress.stop()
    else:
        state = {"current": 0}

        def advance(n: int = 1) -> None:
            state["current"] = min(state["current"] + n, total)
            pct = int(state["current"] / total * 100) if total else 100
            sys.stdout.write(f"\r{description}: %{pct}")
            sys.stdout.flush()

        try:
            yield advance
        finally:
            sys.stdout.write("\n")
            sys.stdout.flush()


# ---------------------------------------------------------------------------
# Renkli çıktı yardımcıları
# ---------------------------------------------------------------------------
def info(msg: str) -> None:
    """Bilgi mesajı (mavi)."""
    if RICH_AVAILABLE and _console is not None:
        _console.print(f"[blue]ℹ[/blue] {msg}")
    else:
        print(f"[INFO] {msg}")


def success(msg: str) -> None:
    """Başarı mesajı (yeşil)."""
    if RICH_AVAILABLE and _console is not None:
        _console.print(f"[green]✓[/green] {msg}")
    else:
        print(f"[OK] {msg}")


def warning(msg: str) -> None:
    """Uyarı mesajı (sarı)."""
    if RICH_AVAILABLE and _console is not None:
        _console.print(f"[yellow]⚠[/yellow] {msg}")
    else:
        print(f"[WARN] {msg}")


def error(msg: str) -> None:
    """Hata mesajı (kırmızı)."""
    if RICH_AVAILABLE and _console is not None:
        _console.print(f"[red]✗[/red] {msg}")
    else:
        print(f"[ERROR] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Panel ve tablo
# ---------------------------------------------------------------------------
def panel(
    content: str,
    *,
    title: str | None = None,
    style: str = "cyan",
) -> None:
    """Panel içinde içerik gösterir."""
    if RICH_AVAILABLE and _console is not None and _Panel is not None:
        _console.print(_Panel(content, title=title, border_style=style))
    else:
        header = f"== {title} ==" if title else "========"
        print(header)
        print(content)
        print("=" * len(header))


def table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    *,
    title: str | None = None,
) -> None:
    """Tablo gösterir."""
    if RICH_AVAILABLE and _console is not None and _Table is not None:
        t = _Table(title=title)
        for h in headers:
            t.add_column(str(h))
        for row in rows:
            t.add_row(*[str(c) for c in row])
        _console.print(t)
    else:
        if title:
            print(title)
        print(" | ".join(str(h) for h in headers))
        print("-" * 40)
        for row in rows:
            print(" | ".join(str(c) for c in row))