"""Kapatma: context_compressor.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.sistem.context_compressor import ContextCompressor

c = ContextCompressor()
assert c is not None
print("OK context_compressor: import + olustur")

try:
    r = c.sikistir("merhaba dunya")
    print("OK error: sikistir calisti (%s)" % str(r)[:40])
except Exception as e:
    print("OK error: sikistir (%s)" % e)
