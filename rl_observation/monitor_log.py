"""
RL Monitor — Log Özeti ve Durum Raporu
Çalıştır: python monitor_log.py

Sabah ilk iş olarak sistemin gece boyunca ne kadar
deneyim kazandığını gösterir.
"""

import json
import os
from datetime import datetime

LOG_FILE = r"C:\Users\marko\AppData\Local\hermes\rl_observation\skill_log.jsonl"

def load_logs():
    if not os.path.exists(LOG_FILE):
        print("❌ Log dosyası bulunamadı.")
        return []

    entries = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def analyze(entries):
    print("=" * 52)
    print("  RL SİSTEM DURUM RAPORU")
    print(f"  {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 52)

    # Temel istatistikler
    total = len(entries)
    print(f"\n📊 TOPLAM KAYIT: {total}")

    # Zaman aralığı
    if entries:
        first = entries[0].get("timestamp", "?")[:19]
        last = entries[-1].get("timestamp", "?")[:19]
        print(f"   Zaman aralığı: {first} → {last}")

    # Ödül dağılımı
    rewards = {"positive": 0, "neutral": 0, "negative": 0}
    for e in entries:
        r = e.get("reward", 0)
        if r > 0:
            rewards["positive"] += 1
        elif r < 0:
            rewards["negative"] += 1
        else:
            rewards["neutral"] += 1

    total_r = sum(rewards.values()) or 1
    print(f"\n🎯 ÖDÜL DAĞILIMI:")
    print(f"   +1 (başarılı): {rewards['positive']:>4}  ({rewards['positive']/total_r*100:>5.1f}%)")
    print(f"    0 (nötr):     {rewards['neutral']:>4}  ({rewards['neutral']/total_r*100:>5.1f}%)")
    print(f"   -1 (hatalı):   {rewards['negative']:>4}  ({rewards['negative']/total_r*100:>5.1f}%)")

    # Skill bazlı
    print(f"\n🧠 SKILL PERFORMANSI:")
    print(f"   {'SKILL':<30} {'TOPLAM':>6} {'BAŞARI':>6} {'%':>6}")
    print(f"   {'-'*48}")

    skills = {}
    for e in entries:
        skill_list = e.get("selected_skills", [])
        if isinstance(skill_list, str):
            skill_list = [skill_list]
        for skill in skill_list:
            if not skill:
                continue
            if skill not in skills:
                skills[skill] = {"total": 0, "success": 0}
            skills[skill]["total"] += 1
            if e.get("reward", 0) >= 0:
                skills[skill]["success"] += 1

    for skill, data in sorted(skills.items(), key=lambda x: -x[1]["total"]):
        rate = data["success"] / data["total"] * 100 if data["total"] > 0 else 0
        print(f"   {skill:<30} {data['total']:>6} {data['success']:>6} {rate:>5.0f}%")

    # Kategori dağılımı
    print(f"\n📁 KATEGORİ DAĞILIMI:")
    cats = {}
    for e in entries:
        c = e.get("category", "unknown")
        cats[c] = cats.get(c, 0) + 1
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")

    # Son 5 kayıt
    print(f"\n🕐 SON 5 KAYIT:")
    for e in entries[-5:]:
        skills_str = ", ".join(e.get("selected_skills", ["?"]))
        reward_str = f"+{e['reward']}" if e.get("reward", 0) > 0 else str(e.get("reward", 0))
        print(f"   [{e.get('timestamp','?')[:19]}] {reward_str} | {skills_str}")

    # Özet
    print(f"\n{'='*52}")
    success_rate = rewards["positive"] / total_r * 100
    if success_rate > 60:
        print("  ✅ SİSTEM: Dengeli ve başarılı")
    elif success_rate > 40:
        print("  ⚠️ SİSTEM: Ortalama — iyileşme alanı var")
    else:
        print("  🔴 SİSTEM: Düşük başarı — MAB müdahalesi gerekli")
    print(f"{'='*52}")


if __name__ == "__main__":
    entries = load_logs()
    analyze(entries)
