#!/usr/bin/env python3
"""Auto-Reward Dogrulama Testi — 15 ornek cümle, karsilastirmali"""
import sys
from pathlib import Path

RL_DIR = Path(__file__).parent
sys.path.insert(0, str(RL_DIR))

# Eski auto_reward (degisiklikten once)
ESKI_POZ = ["tesekkur", "tamam", "oldu", "harika", "cozuldu", "mukemmel", "dogru", "super", "guzel", "eyvallah", "saol", "tşk", "helal", "iyi", "sorun kalmadi", "oldubitti", "hallettim", "bitti", "works"]
ESKI_NEG = ["yanlis", "hayir", "istemedi", "anlamadin", "tekrar", "duzelt", "hatali", "olmamis", "olmadi", "olmaz", "degil", "sorun var", "calismadi", "hata", "bozuk"]

# Yeni auto_reward (bugunku)
YENI_POZ = ["tesekkur", "tamam", "oldu", "harika", "cozuldu", "mukemmel", "dogru", "super", "guzel", "eyvallah", "saol", "tşk", "helal", "iyi", "sorun kalmadi", "oldubitti", "hallettim", "bitti", "works", "evet", "anladim", "devam", "güzel", "başarılı", "sen karar ver", "uygula", "yap", "dene", "tmm"]
YENI_NEG = ["yanlis oldu", "yanlis yaptin", "istemedigim", "anlamadin beni", "anlamadin", "duzelt bunu", "hatali calisiyor", "olmamis bu", "calismadi", "sorun var", "hata verdi", "bozuk bu", "yanlis anladin", "dogru degil", "olmadi yani"]

def eski_auto_reward(msg):
    m = msg.lower()
    for kw in ESKI_NEG:
        if kw in m:
            return -1
    for kw in ESKI_POZ:
        if kw in m:
            return 1
    return 0

def yeni_auto_reward(msg):
    m = msg.lower()
    for kw in YENI_NEG:
        if kw in m:
            return -1
    for kw in YENI_POZ:
        if kw in m:
            return 1
    return 0

# Test cumleleri — gercek kullanici mesajlarina benzer
test_cases = [
    # (cümle, beklenen_reward, aciklama)
    ("tesekkurler oldu", 1, "tesekkur + oldu → pozitif"),
    ("harika cozuldu", 1, "harika + cozuldu → pozitif"),
    ("eyvallah saol", 1, "eyvallah + saol → pozitif"),
    ("sen karar ver", 1, "yetki devri → pozitif"),
    ("tmm uygula", 1, "onay → pozitif"),
    ("yanlis oldu bunu duzelt", -1, "hata bildirimi → negatif"),
    ("calismadi hata var", -1, "calismadi + hata → negatif"),
    ("anlamadin beni", -1, "yanlis anlama → negatif"),
    ("olmadi yani", -1, "olumsuz → negatif"),
    ("degil oyle", 0, "gunluk konusma → notr (eski sistemde -1'di)"),
    ("hayir su degil", 0, "duzeltme ama kizma yok → notr"),
    ("tekrar dene", 0, "tekrar istiyor, negatif degil → notr"),
    ("nasilsin", 0, "selam → notr"),
    ("python kod yaz", 0, "istek → notr"),
    ("nedir bu", 0, "soru → notr"),
]

print("=" * 80)
print("AUTO-REWARD DOGRULUK TESTI")
print("=" * 80)
print(f"\n{'#':>2} {'Cumle':<40} {'Beklenen':>8} {'Eski':>6} {'Yeni':>6} {'Eski D':>7} {'Yeni D':>7}")
print("-" * 80)

eski_dogru = 0
yeni_dogru = 0

for i, (cumle, beklenen, aciklama) in enumerate(test_cases, 1):
    eski_r = eski_auto_reward(cumle)
    yeni_r = yeni_auto_reward(cumle)
    eski_d = "✅" if eski_r == beklenen else "❌"
    yeni_d = "✅" if yeni_r == beklenen else "❌"
    if eski_r == beklenen: eski_dogru += 1
    if yeni_r == beklenen: yeni_dogru += 1
    print(f"{i:>2} {cumle:<40} {beklenen:>8} {eski_r:>6} {yeni_r:>6} {eski_d:>7} {yeni_d:>7}")

print("-" * 80)
print(f"\nEski sistem: {eski_dogru}/{len(test_cases)} dogru = %{round(eski_dogru/len(test_cases)*100)}")
print(f"Yeni sistem: {yeni_dogru}/{len(test_cases)} dogru = %{round(yeni_dogru/len(test_cases)*100)}")
print()

# Hata analizi
print("=== ESKI SISTEM HATALARI ===")
for cumle, beklenen, _ in test_cases:
    r = eski_auto_reward(cumle)
    if r != beklenen:
        print(f"  ❌ {cumle:<40} → {r} (beklenen: {beklenen})")
print()
print("=== YENI SISTEM HATALARI ===")
for cumle, beklenen, _ in test_cases:
    r = yeni_auto_reward(cumle)
    if r != beklenen:
        print(f"  ❌ {cumle:<40} → {r} (beklenen: {beklenen})")
