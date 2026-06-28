#!/usr/bin/env python3
"""Coverage gap raporu — modül bazında test varlık kontrolü."""
import os, sys
from pathlib import Path

PROJE = Path(r"C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi")

# Sadece ReYMeN-native modüller (agent/ gateway/ hariç ReYMeN kopyaları)
ONCELIKLI = [
    "akilli_yonlendirici.py", "anayasa_denetci.py", "anayasa_denetcisi.py",
    "beyin.py", "closed_learning_loop.py", "cokus_raporlayici.py",
    "cua_motor_araci.py", "kopru.py", "motor.py",
    "reymen_agent.py", "sistem_talimati.py",
    "araclar_telegram.py", "error_classifier.py", "dispatcher.py",
    "konusma_havuzu.py", "state_machine.py", "auto_recovery.py",
]

GOZ_ARDI = {"__init__.py", "cli.py", "main.py", "conftest.py",
            "run_all_tests.py", "setup.py", "config_loader.py"}
GOZ_ARDI_PREFIX = {"ReYMeN_", "hermes_", "test_", "_"}

def calistir():
    os.chdir(PROJE)
    
    # Proje kökündeki .py dosyaları
    kok_py = sorted([f for f in PROJE.iterdir() if f.suffix == ".py" and f.name not in GOZ_ARDI
                     and not any(f.name.startswith(p) for p in GOZ_ARDI_PREFIX)])
    
    # Mevcut test dosyaları
    test_dosyalari = set()
    for f in (PROJE / "tests").iterdir():
        if f.suffix == ".py" and f.name.startswith("test_"):
            # test_motor.py -> motor.py
            test_dosyalari.add(f.name[5:])  # "test_" prefix'ini kırp
    test_dosyalari.discard("__init__.py")
    
    lines = []
    
    # 1. Öncelikli modüller
    oncelikli_var = []
    oncelikli_yok = []
    for modul in ONCELIKLI:
        modul_adi = modul.replace(".py", "")
        test_adi = f"{modul_adi}.py"
        if test_adi in test_dosyalari:
            oncelikli_var.append(modul)
        else:
            oncelikli_yok.append(modul)
    
    lines.append(f"📊 **Coverage Gap Raporu**")
    lines.append(f"_Not: Coverage aracı bu ortamda çalışmıyor, modül bazında test varlık kontrolü yapıldı._\n")
    
    if oncelikli_yok:
        lines.append(f"**🔴 Testi Olmayan Öncelikli Modüller ({len(oncelikli_yok)}):**")
        for m in oncelikli_yok:
            lines.append(f"  ❌ `{m}`")
    lines.append("")
    
    if oncelikli_var:
        lines.append(f"**✅ Testi Olan Öncelikli Modüller ({len(oncelikli_var)}):**")
        for m in oncelikli_var:
            lines.append(f"  ✅ `{m}`")
    lines.append("")
    
    # 2. Proje kökü genel tarama
    testi_olan = []
    testi_olmayan = []
    for py in kok_py:
        if py.name in ONCELIKLI:
            continue  # yukarıda listelendi
        modul_adi = py.stem
        if f"{modul_adi}.py" in test_dosyalari:
            testi_olan.append(py.name)
        else:
            testi_olmayan.append(py.name)
    
    if testi_olmayan:
        lines.append(f"**🟡 Testi Olmayan Diğer Modüller ({len(testi_olmayan)}):**")
        for m in sorted(testi_olmayan):
            lines.append(f"  ⚠️ `{m}`")
    lines.append("")
    
    # 3. Özet
    toplam = len(kok_py) + len(ONCELIKLI)
    testli = len(oncelikli_var) + len(testi_olan)
    oran = (testli / toplam * 100) if toplam > 0 else 0
    lines.append(f"**Özet:** {testli}/{toplam} modül testli (%{oran:.0f})")
    
    # Test sayısı
    test_sayisi = sum(1 for _ in (PROJE / "tests").iterdir() if _.suffix == ".py" and _.name.startswith("test_"))
    lines.append(f"**Test dosyası:** {test_sayisi} adet")
    
    print("\n".join(lines))

if __name__ == "__main__":
    calistir()
