# -*- coding: utf-8 -*-
"""BrowserTool._sayfa_al() testi — GERCEK sinif ile."""
import sys, os, time, subprocess

PROJE = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
PYTHON = os.path.join(PROJE, "venv", "Scripts", "python.exe")

test_kodu = r"""
import sys, os, time
sys.path = [p for p in sys.path if 'hermes' not in p.lower()]
os.chdir(r'%(proje)s')
sys.path.insert(0, os.getcwd())

import json
from reymen.arac.araclar_gelismis import BrowserTool

bt = BrowserTool(headless=True)
sonuclar = {}
hatalar = []

# ADIM 1-3
try:
    A = id(bt._sayfa_al())
    B = id(bt._sayfa_al())
    sonuclar["t1"] = {
        "test": "Ayni sekme tekrar kullanimi",
        "beklenen": "A == B",
        "gerceklesen": f"A={A}, B={B}, {'A==B' if A==B else 'A!=B'}",
        "durum": "✅" if A == B else "❌"
    }
except Exception as e:
    import traceback; hatalar.append(("Adim 1-3", traceback.format_exc()))

# ADIM 4-6
try:
    sayfa = bt._page
    A_id = id(sayfa)
    sayfa.close()
    time.sleep(0.5)
    C = bt._sayfa_al()
    C_id = id(C)
    saglikli = False
    try:
        C.evaluate("1")
        saglikli = True
    except: pass
    sonuclar["t2"] = {
        "test": "Kapatma sonrasi yenileme",
        "beklenen": "C saglikli, C != A",
        "gerceklesen": f"A={A_id}, C={C_id}, saglikli={saglikli}, {'A!=C' if A_id!=C_id else 'A=C'}",
        "durum": "✅" if (saglikli and A_id != C_id) else "❌"
    }
except Exception as e:
    import traceback; hatalar.append(("Adim 4-6", traceback.format_exc()))

# ADIM 7
try:
    yeni_sekme_sayaci = 0
    orijinal = bt._context.new_page
    def sayan():
        global yeni_sekme_sayaci
        yeni_sekme_sayaci += 1
        return orijinal()
    bt._context.new_page = sayan
    ids = []
    for i in range(10):
        p = bt._sayfa_al()
        ids.append(id(p))
    benzersiz = len(set(ids))
    sonuclar["t3"] = {
        "test": "10x cagrida acilan sekme sayisi",
        "beklenen": "<= 1 (cache)",
        "gerceklesen": f"{benzersiz} farkli, {yeni_sekme_sayaci} new_page()",
        "durum": "✅" if benzersiz <= 1 else "❌"
    }
except Exception as e:
    import traceback; hatalar.append(("Adim 7", traceback.format_exc()))

# Temizlik
try: bt._browser.close()
except: pass
try: bt._pw.stop()
except: pass

print("###RAPOR###")
print(json.dumps({"sonuclar": sonuclar, "hatalar": hatalar}, ensure_ascii=False))
""" % {"proje": PROJE}

os.chdir(PROJE)
print("1/2: Calistiriliyor...", flush=True)
r = subprocess.run([PYTHON, "-u", "-c", test_kodu], capture_output=True, text=True, timeout=90)
print("2/2: Cikti isleniyor...", flush=True)

import re, json
m = re.search(r'###RAPOR###\s*\n(\{.+})', r.stdout, re.DOTALL)
if m:
    rapor = json.loads(m.group(1))
    sonuc = rapor["sonuclar"]
    hatalar = rapor["hatalar"]
    print("\n| Test | Beklenen | Gerçekleşen | Durum |")
    print("|------|----------|-------------|-------|")
    for k in ["t1","t2","t3"]:
        v = sonuc.get(k, {})
        print(f"| {v.get('test',k)} | {v.get('beklenen','')} | {v.get('gerceklesen','')} | {v.get('durum','❌')} |")
    if hatalar:
        print(f"\n❌ HATALAR ({len(hatalar)}):")
        for adim, tb in hatalar:
            print(f"\n--- {adim} ---")
            for l in tb.strip().split('\n')[-8:]:
                print(l)
    else:
        print("\n✅ Tum testler basarili")
else:
    print("JSON bulunamadi!")
    print(f"exit={r.returncode}")
    if r.stderr.strip():
        print(f"STDERR: {r.stderr[-500:]}")
