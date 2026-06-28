#!/usr/bin/env python3
"""
MAB 7x100 Test — En iyi 7 skill 100'er kere test edilir.
"""
import sys, json, random
from pathlib import Path

RL_DIR = Path(__file__).parent
sys.path.insert(0, str(RL_DIR))

from rl_mab_engine import ContextualMAB, extract_context

# En iyi 7 skill + test sorgulari
TEST_BATTERY = [
    ("code-exec", "python script yaz", "kod"),
    ("windows-screen-capture", "ekran goruntusu al", "goruntu"),
    ("network-camera-discovery", "kamera tara", "guvenlik"),
    ("cronjob", "cron job kur", "yapilandirma"),
    ("obsidian", "obsidian not al", "genel"),
    ("screen-vision-analiz", "ekrana bak", "goruntu"),
    ("yardim", "yardim", "yardim"),
]

with open(RL_DIR / "skill_seed.json", "r", encoding="utf-8") as f:
    seed = json.load(f)

# Sadece bu 7 skill'i kullan
available = [s[0] for s in TEST_BATTERY]

results = {}

for skill_name, query, kategori in TEST_BATTERY:
    dogru = 0
    toplam = 100
    secimler = {}
    
    for i in range(toplam):
        mab = ContextualMAB()
        context = extract_context(query)
        # Force category to match
        context["category"] = kategori
        
        secilen = mab.select_arm(available, context)
        secimler[secilen] = secimler.get(secilen, 0) + 1
        
        if secilen == skill_name:
            dogru += 1
    
    results[skill_name] = {
        "dogru": dogru,
        "toplam": toplam,
        "oran": round(dogru / toplam * 100, 1),
        "secim_dagilimi": dict(sorted(secimler.items(), key=lambda x: -x[1]))
    }

print("=" * 70)
print("MAB 7x100 TEST SONUCLARI")
print("=" * 70)
print(f"\n{'Skill':<35} {'Dogru':>6} {'/100':>4} {'%':>5}  {'En cok secilen'}")
print("-" * 70)

for skill_name, r in sorted(results.items(), key=lambda x: -x[1]["oran"]):
    # En cok hangi skill secilmis?
    dagilim = r["secim_dagilimi"]
    top_skill = list(dagilim.keys())[0]
    top_count = dagilim[top_skill]
    
    # Bar
    bar = "█" * int(r["oran"] / 5) + "░" * (20 - int(r["oran"] / 5))
    
    print(f"{skill_name:<35} {r['dogru']:>6} /100  %{r['oran']:>4.1f}  {bar}")
    print(f"{'':>35} {'':>6} {'':>4} {'':>5}  En cok: {top_skill} ({top_count}/{r['toplam']})")

print()
print("=" * 70)

# Genel
toplam_dogru = sum(r["dogru"] for r in results.values())
toplam_test = sum(r["toplam"] for r in results.values())
genel = round(toplam_dogru / toplam_test * 100, 1)
print(f"GENEL BASARI: %{genel} ({toplam_dogru}/{toplam_test})")

if genel > 60:
    print("DEGERLENDIRME: MAB bu 7 skill icin calisiyor ✅")
elif genel > 30:
    print("DEGERLENDIRME: MAB orta duzey, daha fazla veri lazim ⚠️")
else:
    print("DEGERLENDIRME: MAB henuz ogrenmemis, veri toplamaya devam ❌")
