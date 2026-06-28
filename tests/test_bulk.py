# -*- coding: utf-8 -*-
"""Bulk test — 10 parametrize edilmis test (5000 trivial test yerine)."""
import pytest

ISLEMLER = [
    (0, '+', 1, 1), (1, '-', 1, 0), (2, '*', 1, 2),
    (4, '/', 2, 2), (3, '+', 7, 10), (10, '-', 5, 5),
    (6, '*', 2, 12), (9, '/', 3, 3), (5, '+', 5, 10),
    (100, '-', 50, 50),
]

@pytest.mark.parametrize('a,op,b,beklenen', ISLEMLER)
def test_islem(a, op, b, beklenen):
    if op == '+': sonuc = a + b
    elif op == '-': sonuc = a - b
    elif op == '*': sonuc = a * b
    elif op == '/': sonuc = a / b
    assert sonuc == beklenen
    assert isinstance(sonuc, (int, float))
