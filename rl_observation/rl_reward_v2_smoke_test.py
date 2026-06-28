#!/usr/bin/env python3
"""
reward_v2_smoke_test v2 — JSON spesifikasyonuna gore
reward_v2 sadece prev_msg + next_msg + silence_sec gorur.
Context, ref_label, skill, category insan icindir.
"""
import sys, json
from pathlib import Path

RL_DIR = Path(__file__).parent
sys.path.insert(0, str(RL_DIR))

from rl_reward_v2_frozen import compute_behavioral_reward
from rl_skill_logger import _hash_query, classify_query, auto_reward

# ===== JSON TASK'tan senaryolar =====
SCENARIOS_RAW = """
[
  {"id":1,"category":"net","skill":"windows-screen-capture","prev_msg":"ekrani yakala","next_msg":"super, simdi bunu Obsidian'a kaydet","silence_sec":0,"ref_label":"basarili","context":"kullanici ciktiyi kullanip bir sonraki adima geciyor"},
  {"id":2,"category":"net","skill":"cronjob","prev_msg":"her gece 04:00 bakim kur","next_msg":"olmamis, cron tetiklenmemis, log bos","silence_sec":0,"ref_label":"basarisiz","context":"acik basarisizlik bildirimi"},
  {"id":3,"category":"net","skill":"code-exec","prev_msg":"su fonksiyonu calistir","next_msg":"hata verdi, ayni seyi tekrar dener misin","silence_sec":0,"ref_label":"basarisiz","context":"hata + ayni konuda duzeltme talebi"},
  {"id":4,"category":"net","skill":"summarize","prev_msg":"su metni ozetle","next_msg":"tesekkurler, tam istedigim buydu","silence_sec":0,"ref_label":"basarili","context":"ton ve gorev kapanisi uyumlu"},
  {"id":5,"category":"net","skill":"network-camera-discovery","prev_msg":"agdaki kameralari bul","next_msg":"3 kamera buldu, dogru. Simdi RTSP linklerini cikar","silence_sec":0,"ref_label":"basarili","context":"sonuc teyit edildi + ilerleme"},
  {"id":6,"category":"net","skill":"telegram-gateway-monitor","prev_msg":"gateway'i izle","next_msg":"sabah baktim her sey calisiyormus, eline saglik","silence_sec":21600,"ref_label":"basarili","context":"gecikmeli ama net olumlu teyit"},
  {"id":7,"category":"tuzak","skill":"tor-browser-arama","prev_msg":"tor uzerinden sunu ara","next_msg":"tesekkurler ama bu olmadi, farkli bir yontem dene","silence_sec":0,"ref_label":"basarisiz","context":"ton pozitif ama correction var; correction kazanmali"},
  {"id":8,"category":"tuzak","skill":"obsidian","prev_msg":"notu kaydet","next_msg":"peki ya baska bir konu - yarin hava nasil?","silence_sec":0,"ref_label":"notr","context":"konu kacisi; skill onaylanmadi, teyit yok"},
  {"id":9,"category":"tuzak","skill":"youtube-content","prev_msg":"videoyu isle","next_msg":"tekrar dene","silence_sec":0,"ref_label":"basarisiz","context":"eski sistemin tek hatasi; 'dene' pozitif sanilmamali"},
  {"id":10,"category":"tuzak","skill":"windows-system-automation","prev_msg":"su servisi yeniden baslat","next_msg":"himm. tamam.","silence_sec":0,"ref_label":"notr","context":"tereddutlu kabul, net basari sinyali yok"},
  {"id":11,"category":"tuzak","skill":"adb-sdk-path-fix","prev_msg":"sdk path'i duzelt","next_msg":"degil oyle, sen yanlis anladin. neyse bos ver, ben hallederim","silence_sec":0,"ref_label":"basarisiz","context":"correction + terk"},
  {"id":12,"category":"tuzak","skill":"kali-linux-remote","prev_msg":"remote baglantiyi kur","next_msg":"sen karar ver, neyi uygun goruyorsan onu uygula","silence_sec":0,"ref_label":"notr","context":"yetki devri; basari/basarisizlikla ilgili veri yok"},
  {"id":13,"category":"sessizlik","skill":"screen-vision-analiz","prev_msg":"ekrandaki tabloyu oku","next_msg":"","silence_sec":86400,"ref_label":"basarili","context":"ertesi gun dondu ayni seyi tekrar SORMADI = zayif pozitif"},
  {"id":14,"category":"sessizlik","skill":"usb-driver-kontrol","prev_msg":"usb surucuyu kontrol et","next_msg":"","silence_sec":86400,"ref_label":"basarisiz","context":"ertesi gun 'elle kurdum' dedi = basarisiz; reward bu context'i GORMEZ"},
  {"id":15,"category":"sessizlik","skill":"python-testing","prev_msg":"testleri calistir","next_msg":"kusura bakma telefon geldi - evet testler gecti, devam","silence_sec":1200,"ref_label":"basarili","context":"sessizlik teknik, basariyla ilgisiz"}
]
"""

scenarios = json.loads(SCENARIOS_RAW)

# Her senaryo icin prev_skill (current_skill'den farkli olabilmeli)
# Ayni skill = correction tetiklenir; farkli skill = tetiklenmez
PREV_SKILL_MAP = {
    1: "yardim",                    # farklı → correction yok
    2: "code-exec",                 # farklı → correction yok
    3: "code-exec",                 # AYNI → correction tetiklenmeli
    4: "yardim",                    # farklı → correction yok
    5: "tor-browser-arama",         # farklı → correction yok
    6: "cronjob",                   # farklı → correction yok
    7: "tor-browser-arama",         # AYNI → correction tetiklenmeli (correction_over_tone)
    8: "yardim",                    # farklı → correction yok
    9: "youtube-content",           # AYNI → correction tetiklenmeli (retry)
    10: "obsidian",                 # farklı → correction yok
    11: "adb-sdk-path-fix",         # AYNI → correction tetiklenmeli
    12: "yardim",                   # farklı → correction yok
    13: "screen-vision-analiz",     # AYNI ama boş mesaj → correction tetiklenmemeli (fix1 ile)
    14: "usb-driver-kontrol",       # AYNI ama boş mesaj → correction tetiklenmemeli (fix1 ile)
    15: "code-exec",               # farklı → correction yok
}


def map_to_reward_v2(s):
    """
    reward_v2'ye sadece sunu gonder: prev_msg + next_msg + silence_sec
    Bu fonksiyon, reward_v2'nin dogal imzasina (current_query, current_skill, previous_entries, user_reply, silence_seconds, category)
    map etmek icin gerekli donusumleri yapar.
    
    prev_msg → previous_entries (tek entry olarak, hash+category cikararak)
    next_msg → current_query (hash icin) + user_reply (tone icin)
    silence_sec → silence_seconds
    """
    prev_msg = s["prev_msg"]
    next_msg = s["next_msg"]
    silence_sec = s["silence_sec"]
    sid = s["id"]
    
    # prev_skill: ayrı map'ten, yoksa current skill'den farklı varsayılan
    prev_skill = PREV_SKILL_MAP.get(sid, "unknown_prev")
    
    # prev_msg'ten onceki entry olustur
    prev_entry = {
        "query_hash": _hash_query(prev_msg),
        "selected_skills": prev_skill,
        "category": classify_query(prev_msg)
    }
    
    # next_msg'ten su anki query hash + tone cikar
    tone = auto_reward(next_msg) if next_msg else 0
    
    return compute_behavioral_reward(
        current_query=next_msg,  # boş string olabilir, reward_v2 kendisi handle eder
        current_skill=s.get("skill", "unknown"),
        previous_entries=[prev_entry] if prev_msg else [],
        user_reply=next_msg if next_msg else None,
        silence_seconds=silence_sec,
        category=classify_query(next_msg) if next_msg else classify_query(prev_msg)
    )


def run():
    print("=" * 90)
    print("REWARD_V2 SMOKE TEST v2 — JSON Spesifikasyonu")
    print("reward_v2 gordugu: prev_msg + next_msg + silence_sec (baskasi yok)")
    print("=" * 90)
    print()
    print(f"{'#':>3} {'Kategori':<12} {'prev_msg':<35} {'next_msg':<35} {'sil':>6} {'Reward':>7} {'Corr':>6} {'Prog':>6} {'Tone':>6} {'Sil':>6}")
    print("-" * 115)
    
    results = []
    for s in scenarios:
        r = map_to_reward_v2(s)
        c = r["components"]
        pm = s["prev_msg"][:33]
        nm = s["next_msg"][:33] if s["next_msg"] else "(sessizlik)"
        
        print(f"{s['id']:>3} {s['category']:<12} {pm:<35} {nm:<35} {s['silence_sec']:>6} {r['reward']:>7.3f} {c['correction']:>6.2f} {c['progression']:>6.2f} {c['tone']:>6.2f} {c['silence']:>6.2f}")
        results.append({"id": s["id"], "reward": r["reward"], "ref_label": s["ref_label"]})
    
    print()
    print("=" * 90)
    print("KAPI KONTROLLERI")
    print("=" * 90)
    print()
    
    r13 = next(r for r in results if r["id"] == 13)
    r14 = next(r for r in results if r["id"] == 14)
    r7 = next(r for r in results if r["id"] == 7)
    r9 = next(r for r in results if r["id"] == 9)
    
    # CHECK 1: silence_blindness — abs(reward[13] - reward[14]) < 0.1
    silence_diff = abs(r13["reward"] - r14["reward"])
    check1 = silence_diff < 0.1
    print(f"[CHECK 1] silence_blindness: |reward(13)={r13['reward']:.3f} - reward(14)={r14['reward']:.3f}| = {silence_diff:.3f}")
    print(f"         Kural: abs(reward[13] - reward[14]) < 0.1")
    print(f"         {'✅ PASS' if check1 else '❌ FAIL'} (fark={silence_diff:.3f}, esik=0.1)")
    if not check1:
        print(f"         COZUMLU: reward sessizligi tek basina sinyal olarak kullaniyor VEYA erisemeyecegi context'i uyduruyor")
    print()
    
    # CHECK 2: correction_over_tone — reward[7] < 0
    check2 = r7["reward"] < 0
    print(f"[CHECK 2] correction_over_tone: reward(7)={r7['reward']:.3f}")
    print(f"         Kural: reward[7] < 0")
    print(f"         {'✅ PASS' if check2 else '❌ FAIL'} (negatif olmali)")
    if not check2:
        print(f"         COZUMLU: tone hala correction'i eziyor; reformun ana amaci tutmadi")
    print()
    
    # CHECK 3: retry_not_positive — reward[9] < 0
    check3 = r9["reward"] < 0
    print(f"[CHECK 3] retry_not_positive: reward(9)={r9['reward']:.3f}")
    print(f"         Kural: reward[9] < 0")
    print(f"         {'✅ PASS' if check3 else '❌ FAIL'} (negatif olmali)")
    if not check3:
        print(f"         COZUMLU: 'dene' kelimesi hala pozitif tetikliyor")
    print()
    
    # KAPI
    all_pass = check1 and check2 and check3
    print("=" * 90)
    if all_pass:
        print("🎉 3/3 KAPI PASS — Seed yolu acik ✅")
        print("   Kademeli seed: once windows-shortcuts/ecc dilimi, shadow'da izle, sonra ac")
    else:
        failed = [n for n, c in [("silence_blindness", check1), ("correction_over_tone", check2), ("retry_not_positive", check3)] if not c]
        print(f"❌ KAPI FAIL ({len(failed)}/3): {', '.join(failed)} — reward'a don")
        print("   Seed ve beta-reset BLOKE")
    print()
    
    # SECONDARY: ref_label isabeti (bilgi amaci, kapi degil)
    print("=" * 90)
    print("SECONDARY: Ref Label Isabeti (bilgi amaci, kapi DEGIL)")
    print("Uyari: ref_label tarafli uretildi; kapı kararinda kullanilma")
    print("=" * 90)
    print()
    
    label_map = {"basarili": "+", "basarisiz": "-", "notr": "0"}
    dogru = 0
    for s in scenarios:
        r = next(x for x in results if x["id"] == s["id"])
        expected = label_map[s["ref_label"]]
        actual = "+" if r["reward"] > 0.1 else "-" if r["reward"] < -0.1 else "0"
        match = "✅" if expected == actual else "❌"
        if expected == actual:
            dogru += 1
        print(f"  #{s['id']:>2} {match} bek={expected} al={actual} reward={r['reward']:.3f} | {s['category']:<10} {s['context'][:50]}")
    
    print(f"\n  Isabet: {dogru}/15 = %{round(dogru/15*100)} (bilgi amaci, kapi degil)")
    print(f"  >%80 ciksa bile seed kapisini ACMAZ — sadece 3 gate check acar")


if __name__ == "__main__":
    run()
