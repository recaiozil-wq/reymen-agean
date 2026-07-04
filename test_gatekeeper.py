"""Agent Gatekeeper entegrasyon testi"""
import sys, os
sys.path.insert(0, os.path.abspath('.'))

from reymen.guvenlik.agent_gatekeeper import (
    init_log, run_and_log, has_real_execution,
    response_makes_numeric_claim, extract_code_blocks,
)

# Test 1: regex
tests = [
    ('Toplam 42 kayit bulundu', True),
    ('SELECT COUNT(*) FROM users', True),
    ('Bu bir testtir', False),
    ('Hata kodu: 500', True),
    ('İşlem başarılı', True),
    ('exit = 0', True),
]
print('=== SAYISAL IDDIA TESTI ===')
ok = True
for txt, bek in tests:
    s = response_makes_numeric_claim(txt)
    durum = "OK" if s == bek else "FAIL"
    if durum == "FAIL":
        ok = False
    print(f'  {durum} {txt} -> {s} (beklenen: {bek})')

# Test 2: extract_code_blocks
print()
print('=== KOD BLOGU CIKARMA ===')
test_text = 'once kod:\n```python\nprint("hello")\n```\nsonra aciklama'
blok = extract_code_blocks(test_text)
print(f'  Bulunan blok: {blok}')
if blok and 'print("hello")' in blok[0]:
    print('  OK')
else:
    print('  FAIL')
    ok = False

# Test 3: run_and_log
print()
print('=== RUN_AND_LOG ===')
init_log()
r = run_and_log('test-session', 'print(2+2)')
print(f'  Sonuc: {r}')
if has_real_execution('test-session', 0):
    print('  Kayit var: OK')
else:
    print('  Kayit var: FAIL')
    ok = False
if not has_real_execution('test-session', 9999999999):
    print('  Gelecek kayit yok: OK')
else:
    print('  Gelecek kayit: FAIL')
    ok = False

print()
if ok:
    print('TUM TESTLER GECTI')
else:
    print('BAZI TESTLER BASARISIZ')
