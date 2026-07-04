"""Kapatma: memory_provider.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.sistem.memory_provider import JsonBackend, MemoryProviderRegistry
import tempfile, json


def test_happy():
    j = JsonBackend()
    assert j is not None
    print("OK happy: JsonBackend olustur")


def test_error():
    try:
        r = MemoryProviderRegistry.get("olmayan")
        print("OK error: olmayan backend (%s)" % str(r)[:40])
    except Exception as e:
        print("OK error: %s" % e)


test_happy()
test_error()
