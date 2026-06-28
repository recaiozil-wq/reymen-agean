# -*- coding: utf-8 -*-
# Entry point — gercek kod reymen/sistem/main.py icinde
import os, sys

# reymen/sistem/main.py, sys.stdout/stderr'i yeniden TextIOWrapper'a sariyor.
# run_path altinda eski wrapper GC olunca shared buffer kapaniyor.
# Referansi burada tutarak GC'yi engelliyoruz.
_stdout_ref = sys.stdout
_stderr_ref = sys.stderr

_proje_kok = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _proje_kok)

import runpy
runpy.run_path(
    os.path.join(_proje_kok, "reymen", "sistem", "main.py"),
    run_name="__main__",
)
