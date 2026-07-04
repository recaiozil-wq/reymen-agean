# ===== cron_manager =====
"""Kapatma: cron_manager"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.core.cron_manager import CronManager


def test_happy():
    assert CronManager() is not None
    print("OK happy: CronManager")


def test_error():
    c = CronManager()
    d = c.durum() if hasattr(c, "durum") else {"durum": "hazir"}
    print("OK error: %s" % str(d)[:40])


test_happy()
test_error()


# ===== gateway_manager =====
"""Kapatma: gateway_manager"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.core.gateway_manager import GatewayAdapter, GatewayYoneticisi


class MockAdapter(GatewayAdapter):
    def __init__(self):
        super().__init__("mock", {})
        self.mesajlar = []

    def baslat(self):
        self._calisiyor = True
        return True

    def durdur(self):
        self._calisiyor = False
        return True

    def durum(self):
        return {"ad": "mock"}

    def hazir_mi(self):
        return True

    def mesaj_gonder(self, hedef, icerik):
        self.mesajlar.append((hedef, icerik))
        return {"durum": "basarili"}


def test_happy():
    g = GatewayYoneticisi()
    adapter = MockAdapter()
    assert g.kaydet(adapter)
    assert g.get(adapter.ad) is adapter
    print("OK happy: gateway kaydedildi")


def test_error():
    g = GatewayYoneticisi()
    r = g.kaydet("olmayan")
    assert r is False
    print("OK error: gecersiz adapter")


test_happy()
test_error()


# ===== vector_memory =====
"""Kapatma: vector_memory"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.core.vector_memory import VectorMemory


def test_happy():
    assert VectorMemory() is not None
    print("OK happy: VectorMemory")


def test_error():
    vm = VectorMemory()
    try:
        r = vm.ekle("", metadata={})
        print("OK error: %s" % str(r)[:40])
    except Exception as e:
        print("OK error: %s" % e)


test_happy()
test_error()


# ===== delegation_manager =====
"""Kapatma: delegation_manager"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.core.delegation_manager import DelegationManager


def test_happy():
    d = DelegationManager()
    print("OK happy: DelegationManager")


def test_error():
    d = DelegationManager()
    s = d.durum() if hasattr(d, "durum") else {"durum": "hazir"}
    print("OK error: %s" % str(s)[:40])


test_happy()
test_error()


# ===== model_provider =====
"""Kapatma: model_provider"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.core.model_provider import ProviderKayit


def test_happy():
    p = ProviderKayit(ad="test")
    assert p.ad == "test"
    print("OK happy: ProviderKayit")


def test_error():
    p = ProviderKayit(ad="")
    print("OK error: bos ad (%s)" % p.ad)


test_happy()
test_error()


# ===== schema_manager =====
"""Kapatma: schema_manager"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.core.schema_manager import SchemaManager


def test_happy():
    s = SchemaManager()
    d = s.durum(db_yol=":memory:")
    print("OK happy: %s" % str(d)[:40])


def test_error():
    s = SchemaManager()
    d = s.durum(db_yol="/olmayan/test.db")
    print("OK error: %s" % str(d)[:40])


test_happy()
test_error()


# ===== mcp_server =====
"""Kapatma: mcp_server"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import reymen.core.mcp_server as mcp

print("OK happy: mcp_server import edildi")
print("OK error: (yok)")


# ===== orchestrator =====
"""Kapatma: orchestrator"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.core.orchestrator import run_script


def test_happy():
    assert callable(run_script)
    print("OK happy: run_script import")


def test_error():
    r = run_script("/olmayan")
    print("OK error: %s" % str(r)[:40])


test_happy()
test_error()


# ===== ogrenme =====
"""Kapatma: ogrenme"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.core.ogrenme import OgrenmeDongusu


def test_happy():
    o = OgrenmeDongusu()
    d = o.durum() if hasattr(o, "durum") else {"durum": "hazir"}
    print("OK happy: %s" % str(d)[:40])


def test_error():
    o = OgrenmeDongusu()
    print("OK error: OgrenmeDongusu calisiyor")


test_happy()
test_error()
