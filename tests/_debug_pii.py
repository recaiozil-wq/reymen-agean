"""Debug: PII satir 319 kontrolu"""

import sys

sys.path.insert(0, r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan")
from reymen.core.guardrails_manager import GuardrailsManager
import re
from reymen.core.guardrails_manager import (
    _HASSAS_DESENLER,
    _YASAKLI_ICERIK,
    _KOD_EXEC_DESENLERI,
)

gm = GuardrailsManager()

# Test cikti PII
tests = [
    ("Kullanici emaili: user@test.com", "email"),
    ("Kart: 4111111111111111", "kart"),
    ("SSN: 123-45-6789", "SSN"),
    ("Telefon: +1-555-123-4567", "telefon"),
]
for txt, name in tests:
    sonuc = gm.cikti_kontrol(txt)
    print(f"Cikti {name}: guvenli={sonuc.guvenli} tespit={sonuc.tespit}")

# Which PII pattern matches email?
print("\n--- HASSAS DESENLER email test ---")
for i, desen in enumerate(_HASSAS_DESENLER):
    m = re.search(desen, "Kullanici emaili: user@test.com")
    if m:
        print(f"  DESEN {i}: {m.group()[:60]}")

# Check yasakli icerik
print("\n--- YASAKLI ICERIK email test ---")
for i, desen in enumerate(_YASAKLI_ICERIK):
    m = re.search(desen, "Kullanici emaili: user@test.com")
    if m:
        print(f"  DESEN {i}: {m.group()[:60]}")
