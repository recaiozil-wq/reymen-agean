"""BrowserTool._sayfa_al() testi - bagimsiz process"""
import sys, os, time, json

# Proje kökü
PROJE_KOK = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
sys.path.insert(0, PROJE_KOK)
os.chdir(PROJE_KOK)

from reymen.arac.araclar_gelismis import BrowserTool
import logging
logging.basicConfig(level=logging.WARNING)

sonuc = {"test1": None, "test2": None, "test3": None}

try:
    print("=== BrowserTool._sayfa_al() TEST ===\n")
    bt = BrowserTool(headless=True)

    # ADIM 1-3
    print("[ADIM 1-3] Ayni sekme tekrar kullanimi...")
    A = bt._sayfa_al()
    id_A = id(A)
    B = bt._sayfa_al()
    id_B = id(B)
    t1 = (id_A == id_B)
    sonuc["test1"] = {"beklenen": "A==B", "gerceklesen": f"id esit={t1}", "durum": "OK" if t1 else "FAIL"}
    print(f"  A id={id_A}, B id={id_B}, A==B: {t1}")

    # ADIM 4-6
    print("\n[ADIM 4-6] Kapatma sonrasi yenileme...")
    B.close()
    time.sleep(0.3)
    C = bt._sayfa_al()
    id_C = id(C)
    t2_saglikli = not C.is_closed()
    t2_farkli = (id_C != id_A)
    t2 = t2_saglikli and t2_farkli
    sonuc["test2"] = {"beklenen": "C saglikli, C!=A", "gerceklesen": f"saglikli={t2_saglikli}, farkli={t2_farkli}", "durum": "OK" if t2 else "FAIL"}
    print(f"  C id={id_C}, saglikli={t2_saglikli}, C!=A={t2_farkli}")

    # ADIM 7
    print("\n[ADIM 7] 10x cagri...")
    bt2 = BrowserTool(headless=True)
    ids = []
    for i in range(10):
        p = bt2._sayfa_al()
        ids.append(id(p))
    uniq = len(set(ids))
    t3 = (uniq <= 1)
    sonuc["test3"] = {"beklenen": "<=1 yeni sekme", "gerceklesen": f"{uniq} farkli", "durum": "OK" if t3 else "FAIL"}
    print(f"  10 cagrida {uniq} farkli sekme")

    bt.kapat()
    bt2.kapat()

except Exception as e:
    import traceback
    sonuc["hata"] = str(e)
    sonuc["traceback"] = traceback.format_exc()
    print(f"\nHATA: {e}")

# JSON cikti
print("\n---JSON_SONUC---")
print(json.dumps(sonuc, indent=2))
print("---JSON_SONUC_END---")
