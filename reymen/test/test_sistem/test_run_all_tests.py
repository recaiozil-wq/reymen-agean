# Otomatik üretilmiştir — elle düzenleme.
# Kaynak modül: reymen.sistem.run_all_tests

import pytest
import reymen.sistem.run_all_tests as _modul

def test_import():
    # reymen.sistem.run_all_tests modülünün import edilebilir olduğunu doğrular
    assert _modul is not None
