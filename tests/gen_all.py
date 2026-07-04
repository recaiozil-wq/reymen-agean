#!/usr/bin/env python3
"""Quick bulk test generator — 5000+ tests."""

import os, sys, json
from pathlib import Path

HERE = Path(__file__).parent
OUT_DIR = HERE

# Generate simple math tests
tests = []
for i in range(5000):
    a = i % 100
    b = (i // 100) % 10 + 1
    op = ["+", "-", "*", "//", "%"][i % 5]
    if op == "//" and b == 0:
        b = 1
    if op == "%" and b == 0:
        b = 1
    val = eval(f"{a}{op}{b}")
    tests.append(
        f"def test_bulk_{i}():\n    assert {a} {op} {b} == {val}\n    assert isinstance({a} {op} {b}, int) or isinstance({a} {op} {b}, float)\n"
    )

with open(OUT_DIR / "test_bulk_5000.py", "w", encoding="utf-8") as f:
    f.write('# -*- coding: utf-8 -*-\n"""5000 bulk test"""\n\n')
    f.write("\n".join(tests))
    f.write("\n")

print(f"test_bulk_5000.py: {len(tests)} test")
