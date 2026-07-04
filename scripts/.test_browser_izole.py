# -*- coding: utf-8 -*-
"""BrowserTool._sayfa_al() testi — timeout'lu."""

import sys, os, time, json, threading

sys.path = [p for p in sys.path if "hermes" not in p.lower()]
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from reymen.arac.araclar_gelismis import BrowserTool


def timeout_cagir(fn, args=(), kwargs={}, sure=15):
    """Bir fonksiyonu sure ile calistir, timeout'ta exception."""
    sonuc = [None]
    hata = [None]
    done = [False]

    def runner():
        try:
            sonuc[0] = fn(*args, **kwargs)
        except Exception as e:
            hata[0] = e
        finally:
            done[0] = True

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    t.join(sure)
    if not done[0]:
        raise TimeoutError(f"Fonksiyon {sure}s sonra timeout")
    if hata[0]:
        raise hata[0]
    return sonuc[0]


bt = BrowserTool(headless=True)
sonuclar = {}
hatalar = []

# ADIM 1-3: Ayni sekme tekrar kullanimi
try:
    A = id(bt._sayfa_al())
    B = id(bt._sayfa_al())
    sonuclar["t1"] = {
        "test": "Ayni sekme tekrar kullanimi",
        "beklenen": "A == B",
        "gerceklesen": f"A={A}, B={B}, {'A==B' if A==B else 'A!=B'}",
        "durum": "✅" if A == B else "❌",
    }
except Exception as e:
    import traceback

    hatalar.append(("Adim 1-3", traceback.format_exc()))

# ADIM 4-6: Kapatma sonrasi yenileme
try:
    sayfa = bt._page
    A_id = id(sayfa)
    sayfa.close()
    time.sleep(0.5)
    # _sayfa_al()'i timeout ile cagir (15sn)
    C = timeout_cagir(bt._sayfa_al, sure=15)
    C_id = id(C)
    saglikli = False
    try:
        C.evaluate("1")
        saglikli = True
    except Exception as e:
        saglikli = False
    sonuclar["t2"] = {
        "test": "Kapatma sonrasi yenileme",
        "beklenen": "C saglikli, C != A",
        "gerceklesen": f"A={A_id}, C={C_id}, saglikli={saglikli}, {'A!=C' if A_id!=C_id else 'A=C'}",
        "durum": "✅" if (saglikli and A_id != C_id) else "❌",
    }
except TimeoutError:
    import traceback

    hatalar.append(
        (
            "Adim 4-6",
            "TIMEOUT: _sayfa_al() 15sn sonra donmedi! sync_playwright().start() 2. kez cagrildiginda bloke oldu.",
        )
    )
    sonuclar["t2"] = {
        "test": "Kapatma sonrasi yenileme",
        "beklenen": "C saglikli, C != A",
        "gerceklesen": "TIMEOUT — sync_playwright().start() ikinci kez bloke oldu",
        "durum": "❌",
    }
except Exception as e:
    import traceback

    hatalar.append(("Adim 4-6", traceback.format_exc()))
    sonuclar["t2"] = {
        "test": "Kapatma sonrasi yenileme",
        "beklenen": "C saglikli, C != A",
        "gerceklesen": f"HATA: {e}",
        "durum": "❌",
    }

# ADIM 7: 10x cagri (sayfa hala acikken, kapatmadan)
try:
    yeni_sekme_sayaci = 0
    orijinal_new_page = bt._context.new_page

    def sayan_new_page():
        global yeni_sekme_sayaci
        yeni_sekme_sayaci += 1
        return orijinal_new_page()

    bt._context.new_page = sayan_new_page

    ids = []
    for i in range(10):
        p = bt._sayfa_al()
        ids.append(id(p))

    benzersiz_id = len(set(ids))
    sonuclar["t3"] = {
        "test": "10x cagrida acilan sekme sayisi",
        "beklenen": "<= 1 (cache kullanilmali)",
        "gerceklesen": f"{benzersiz_id} farkli sayfa, {yeni_sekme_sayaci} yeni_sekme() cagrisi",
        "durum": "✅" if benzersiz_id <= 1 else "❌",
    }
except Exception as e:
    import traceback

    hatalar.append(("Adim 7", traceback.format_exc()))

# Temizlik
try:
    bt._browser.close()
except Exception:
    pass  # Temizlik hatasi — browser zaten kapali olabilir
try:
    bt._pw.stop()
except Exception:
    pass  # Temizlik hatasi — pw zaten durmus olabilir

# RAPOR
print("\n| Test | Beklenen | Gerçekleşen | Durum |")
print("|------|----------|-------------|-------|")
for k in ["t1", "t2", "t3"]:
    v = sonuclar.get(
        k, {"test": k, "beklenen": "-", "gerceklesen": "CALISTIRILAMADI", "durum": "❌"}
    )
    print(f"| {v['test']} | {v['beklenen']} | {v['gerceklesen']} | {v['durum']} |")

if hatalar:
    print(f"\n❌ HATALAR ({len(hatalar)}):")
    for adim, tb in hatalar:
        print(f"\n--- {adim} ---")
        print(tb)
else:
    print("\n✅ Tum testler basarili")
