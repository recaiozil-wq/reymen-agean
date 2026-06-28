#!/usr/bin/env python3
"""
MAB Shadow Test - Her kategoriden test sorgulari gonder, 
MAB'in hangi skill'i sectigini olc, dogrulugu degerlendir.
"""
import sys, json
from pathlib import Path

RL_DIR = Path(__file__).parent
sys.path.insert(0, str(RL_DIR))

from rl_decision_layer import RLDecisionLayer, RulesEngine
from rl_mab_engine import ContextualMAB, extract_context

# Test senaryolari: (kategori, sorgu, beklenen_skill_ailesi)
TEST_CASES = [
    # kod
    ("kod", "python script yaz ve calistir", ["code-exec", "python"]),
    ("kod", "build hatasini coz", ["code-exec", "analiz"]),
    ("kod", "kod incelemesi yap", ["code-exec", "analiz"]),
    # guvenlik
    ("guvenlik", "apk sertlestir", ["android-apk-hardening", "android-apk-modding"]),
    ("guvenlik", "guvenlik taramasi yap", ["guvenlik-izleme", "security"]),
    ("guvenlik", "windows forensik analiz", ["windows-forensic-assessment"]),
    # arama
    ("arama", "tor ile ara", ["tor-browser-arama"]),
    ("arama", "internette su konuyu arastir", ["tor-browser-arama", "deep-research"]),
    # goruntu
    ("goruntu", "ekran goruntusu al", ["windows-screen-capture"]),
    ("goruntu", "ekranda ne var goster", ["screen-vision-analiz", "windows-screen-capture"]),
    # analiz
    ("analiz", "log dosyasini incele", ["analiz", "code-exec"]),
    ("analiz", "sistemi analiz et", ["analiz"]),
    # ogrenme
    ("ogrenme", "python nedir ogren", ["ogrenme", "youtube"]),
    ("ogrenme", "konu anlat", ["ogrenme", "youtube"]),
    # yapilandirma
    ("yapilandirma", "cron job kur", ["cronjob"]),
    ("yapilandirma", "sistem ayarlarini yap", ["yapilandirma"]),
    # windows
    ("windows", "mouse hareket ettir", ["hermesmouse", "mouse"]),
    ("windows", "dosya olustur", ["windows-file-ops", "windows-file"]),
    ("windows", "ekran videosu cek", ["camera-capture", "windows-screen-capture"]),
    # android
    ("android", "apk build al", ["android-native-app-builder", "android-apk"]),
    ("android", "telefona apk gonder", ["android-apk", "adb"]),
    # genel
    ("genel", "merhaba nasilsin", ["none", "yardim"]),
    ("genel", "yardim", ["yardim"]),
]

def evaluate_selection(query, selected_skill, expected_families):
    """Secilen skill beklenen aileden mi?"""
    if selected_skill is None:
        return False, "skill secilemedi"
    for family in expected_families:
        if family in selected_skill:
            return True, f"✓ {selected_skill}"
    return False, f"✗ {selected_skill} (beklenen: {expected_families})"

def main():
    print("=" * 60)
    print("MAB SHADOW TEST — 14.06.2026")
    print("=" * 60)
    
    # Mevcut 28 skill + tum seed
    with open(RL_DIR / "skill_seed.json", "r", encoding="utf-8") as f:
        seed_data = json.load(f)
    all_skills_available = list(seed_data.keys())
    print(f"Available skills: {len(all_skills_available)}")
    
    decision_layer = RLDecisionLayer(mode="shadow")
    
    results = {"dogru": 0, "yanlis": 0, "toplam": 0, "detay": []}
    
    for idx, (kategori, sorgu, beklenen) in enumerate(TEST_CASES, 1):
        decision = decision_layer.decide(sorgu, all_skills_available)
        mab_skill = decision.get("mab_skill")
        kural_skill = decision.get("rule_result", {}).get("skill")
        kaynak = decision["source"]
        
        is_correct, degerlendirme = evaluate_selection(sorgu, mab_skill, beklenen)
        
        results["toplam"] += 1
        if is_correct:
            results["dogru"] += 1
        else:
            results["yanlis"] += 1
        
        results["detay"].append({
            "idx": idx,
            "kategori": kategori,
            "sorgu": sorgu[:40],
            "mab_skill": mab_skill,
            "kural_skill": kural_skill,
            "kaynak": kaynak,
            "dogru": is_correct,
            "degerlendirme": degerlendirme
        })
    
    # Rapor
    dogruluk = round(results["dogru"] / max(results["toplam"], 1) * 100, 1)
    print(f"\nToplam test: {results['toplam']}")
    print(f"Dogru: {results['dogru']} | Yanlis: {results['yanlis']}")
    print(f"Dogruluk: %{dogruluk}")
    print()
    
    print(f"{'#':>3} {'Kategori':<14} {'Sorgu':<42} {'MAB Skill':<35} {'Kural':<25} {'Sonuc'}")
    print("-" * 130)
    
    for d in results["detay"]:
        mab = d["mab_skill"][:33] if d["mab_skill"] else "NONE"
        kural = d["kural_skill"][:23] if d["kural_skill"] else "-"
        isaret = "✅" if d["dogru"] else "❌"
        print(f"{d['idx']:>3} {d['kategori']:<14} {d['sorgu']:<42} {mab:<35} {kural:<25} {isaret}")
    
    print()
    print("=" * 60)
    
    # Kategori bazli analiz
    kat_perf = {}
    for d in results["detay"]:
        kat = d["kategori"]
        if kat not in kat_perf:
            kat_perf[kat] = {"dogru": 0, "yanlis": 0, "toplam": 0}
        kat_perf[kat]["toplam"] += 1
        if d["dogru"]:
            kat_perf[kat]["dogru"] += 1
        else:
            kat_perf[kat]["yanlis"] += 1
    
    print("\nKategori bazli performans:")
    for kat, perf in sorted(kat_perf.items()):
        oran = round(perf["dogru"] / max(perf["toplam"], 1) * 100, 1)
        bar = "█" * int(oran / 10) + "░" * (10 - int(oran / 10))
        print(f"  {kat:<14} {bar} %{oran} ({perf['dogru']}/{perf['toplam']})")
    
    print()
    
    # Genel degerlendirme
    if dogruluk >= 70:
        print("DEGERLENDIRME: MAB aktif kullanima hazir ✅")
    elif dogruluk >= 50:
        print("DEGERLENDIRME: MAB shadow modda kalmalı, 2-3 gun daha veri toplamali ⚠️")
    else:
        print("DEGERLENDIRME: MAB cok zayif, seed filtrelenmeli veya kategori bazli egitim lazim ❌")
    
    print(f"\nNot: {results['yanlis']} yanlis secimin detayi icin --verbose")
    
    if results['yanlis'] > 0:
        print("\nYanlis secimler:")
        for d in results["detay"]:
            if not d["dogru"]:
                print(f"  [{d['kategori']}] \"{d['sorgu']}\"")
                print(f"    MAB secimi: {d['mab_skill']}")
                print(f"    Kuralin secimi: {d['kural_skill']}")

if __name__ == "__main__":
    main()
