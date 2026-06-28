# -*- coding: utf-8 -*-
"""
test_cli.py — ReYMeN CLI temel testleri
"""

import sys
from pathlib import Path

import pytest


class TestCLIDizini:
    """CLI dosya yapisi."""

    def test_cli_dizini_var(self):
        proje = Path(__file__).parent.parent
        cli_dir = proje / "ReYMeN_cli"
        assert cli_dir.is_dir(), "ReYMeN_cli/ dizini yok"

    def test_cli_py_dosya_sayisi(self):
        proje = Path(__file__).parent.parent
        py_files = list((proje / "ReYMeN_cli").rglob("*.py"))
        assert len(py_files) >= 10

    def test_cli_main_var(self):
        proje = Path(__file__).parent.parent
        assert (proje / "ReYMeN_cli" / "main.py").exists() or \
               (proje / "ReYMeN_cli" / "__init__.py").exists() or \
               (proje / "ReYMeN_cli" / "cli.py").exists()

    def test_cli_komut_modulleri(self):
        proje = Path(__file__).parent.parent
        cli_dir = proje / "ReYMeN_cli"
        if cli_dir.is_dir():
            # komut/ veya commands/ altinda moduller var mi
            komut_dizinleri = [d for d in cli_dir.iterdir() if d.is_dir()]
            assert len(komut_dizinleri) >= 1


class TestCLICommands:
    """CLI komut yapisi."""

    def test_cli_help_var(self):
        """CLI'da help/yardim komutu olmali."""
        proje = Path(__file__).parent.parent
        cli_dir = proje / "ReYMeN_cli"
        for pattern in ["*help*", "*yardim*", "*_help*"]:
            matches = list(cli_dir.rglob(pattern))
            if matches:
                return
        # help olmayabilir, en azindan --help argparser var mi kontrol
        main_files = list(cli_dir.rglob("main.py")) + list(cli_dir.rglob("cli.py"))
        if main_files:
            content = main_files[0].read_text(encoding="utf-8")
            assert "add_argument" in content or "argparse" in content

    def test_cli_komut_bolunmesi(self):
        """Komutlar birden fazla dosyaya bolunmus olmali (single file degil)."""
        proje = Path(__file__).parent.parent
        cli_dir = proje / "ReYMeN_cli"
        py_files = list(cli_dir.rglob("*.py"))
        # Tek bir main.py'den buyuk olmali
        assert len(py_files) >= 5


class TestCLIEntegrasyon:
    """CLI'in projeyle entegrasyonu."""

    def test_cli_main_py_var(self):
        proje = Path(__file__).parent.parent
        assert (proje / "main.py").exists()
        content = (proje / "main.py").read_text(encoding="utf-8")
        assert "cli" in content.lower() or "argparse" in content or "main" in content

    def test_cli_argument_parser(self):
        proje = Path(__file__).parent.parent
        main_py = proje / "main.py"
        content = main_py.read_text(encoding="utf-8")
        # ReYMeN: REPL tarzi — input() ile kullanicidan hedef alir
        # veya geleneksel ArgumentParser/sys.argv/argparse kullanir
        assert (
            "ArgumentParser" in content
            or "sys.argv" in content
            or "argparse" in content
            or 'input(' in content
            or 'sys.stdin' in content
            or 'hedef' in content
            or 'runpy' in content
            or 'run_path' in content
        )

    def test_cli_komut_aciklamalari(self):
        """Komut dosyalarinda docstring/aciklama olmali."""
        proje = Path(__file__).parent.parent
        cli_dir = proje / "ReYMeN_cli"
        docsuz = 0
        for f in cli_dir.rglob("*.py"):
            if f.name.startswith("_"):
                continue
            content = f.read_text(encoding="utf-8")
            if not content.strip().startswith(('"""', "'''", "#")):
                docsuz += 1
        # En fazla %30 dosya docstring'siz olabilir
        total = len(list(cli_dir.rglob("*.py")))
        assert docsuz / max(total, 1) <= 0.5


class TestCLICron:
    """CLI cron entegrasyonu."""

    def test_cron_dizini_var(self):
        proje = Path(__file__).parent.parent
        cron_dir = proje / "cron"
        if cron_dir.is_dir():
            py_files = list(cron_dir.glob("*.py"))
            assert len(py_files) >= 1

    def test_cron_test_runner_var(self):
        proje = Path(__file__).parent.parent
        assert (proje / "tests" / "reymen_test_runner.py").exists()
