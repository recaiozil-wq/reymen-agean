# -*- coding: utf-8 -*-
"""tests/tools/conftest.py — Olmayan tool modüllerinin testlerini toplama aşamasında engelle."""
from pathlib import Path

# src/reymen/tools/ dizininde var olan modüller
TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "reymen" / "tools"


def pytest_ignore_collect(collection_path, config):
    """Olmayan tool modüllerinin test dosyalarını toplamayı reddet."""
    if collection_path.suffix == ".py" and collection_path.name.startswith("test_"):
        mod_name = collection_path.stem[5:]  # test_xxx.py -> xxx
        mod_file = TOOLS_DIR / f"{mod_name}.py"
        if not mod_file.exists():
            return True
    return None
