"""
RL Görselleştirme — Skill Performans Grafiği
Çalıştır: python visualize_log.py

Skill'lerin başarı/başarısızlık dağılımını gösteren
bir bar chart oluşturur.
"""

import json
import os
import sys

LOG_FILE = r"C:\Users\marko\AppData\Local\hermes\rl_observation\skill_log.jsonl"

# matplotlib mevcut mu kontrol et
try:
    import matplotlib
    matplotlib.use("Agg")  # Headless mod
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


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


def build_chart(entries, output_path="rl_skill_chart.png"):
    if not HAS_MPL:
        print("⚠️ matplotlib kurulu değil. Grafik oluşturulamadı.")
        print("   Kurulum: pip install matplotlib numpy")
        return False

    # Skill bazlı alpha/beta hesapla
    skills_data = {}
    for e in entries:
        skill_list = e.get("selected_skills", [])
        if isinstance(skill_list, str):
            skill_list = [skill_list]
        for skill in skill_list:
            if not skill:
                continue
            if skill not in skills_data:
                skills_data[skill] = {"alpha": 0, "beta": 0}
            if e.get("reward", 0) >= 0:
                skills_data[skill]["alpha"] += 1
            else:
                skills_data[skill]["beta"] += 1

    if not skills_data:
        print("❌ Grafik için veri yok.")
        return False

    # Başarı oranına göre sırala (kötüden iyiye)
    sorted_skills = sorted(
        skills_data.items(),
        key=lambda x: -(x[1]["alpha"] / max(1, x[1]["alpha"] + x[1]["beta"]))
    )

    names = [f"{s[0]} ({s[1]['alpha']+s[1]['beta']})" for s in sorted_skills]
    totals = [s[1]["alpha"] + s[1]["beta"] for s in sorted_skills]
    alphas = [s[1]["alpha"] for s in sorted_skills]
    betas = [s[1]["beta"] for s in sorted_skills]
    rates = [a / max(1, a + b) * 100 for a, b in zip(alphas, betas)]

    # Yatay bar chart
    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(names))
    height = 0.6

    # Yığılmış bar — başarılı kısım
    bars_alpha = ax.barh(y, alphas, height, label="Başarılı", color="#2ecc71")
    # Başarısız kısım başarılı olanın üstüne
    bars_beta = ax.barh(y, betas, height, left=alphas, label="Başarısız", color="#e74c3c")

    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9)
    ax.set_xlabel("Kullanım Sayısı", fontsize=10)
    ax.set_title("RL Skill Performans Dağılımı (Başarı Oranına Göre)", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right")

    # Her bar'ın üstüne başarı yüzdesi
    for i, (a, b, rate) in enumerate(zip(alphas, betas, rates)):
        total = a + b
        if total == 0:
            continue
        # Yüzdeyi bar'ın sonuna yaz
        ax.text(total + 0.2, i, f"%{rate:.0f}", va="center", fontsize=8,
                color="#2c3e50", fontweight="bold")

        # Değerleri bar içine yaz
        if a > 0:
            ax.text(a / 2, i, str(a), va="center", ha="center", fontsize=8, color="white", fontweight="bold")
        if b > 0:
            ax.text(a + b / 2, i, str(b), va="center", ha="center", fontsize=8, color="white", fontweight="bold")

    # İnce bir dikey çizgi %50
    ax.axvline(x=0, color="black", linewidth=0.5)
    ax.set_xlim(0, max(alphas) + max(betas) + 4)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    # Kaydet
    output_path = os.path.abspath(output_path)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"✅ Grafik kaydedildi: {output_path}")
    print(f"   Toplam {len(names)} skill — başarı oranına göre sıralı, yatay yığılmış bar.")
    return True


def text_chart(entries):
    """Terminal için basit ASCII tablo"""
    skills_data = {}
    for e in entries:
        skill_list = e.get("selected_skills", [])
        if isinstance(skill_list, str):
            skill_list = [skill_list]
        for skill in skill_list:
            if not skill:
                continue
            if skill not in skills_data:
                skills_data[skill] = {"alpha": 0, "beta": 0}
            if e.get("reward", 0) >= 0:
                skills_data[skill]["alpha"] += 1
            else:
                skills_data[skill]["beta"] += 1

    print("\n📊 SKILL PERFORMANS (ASCII):")
    print(f"   {'SKILL':<30} {'BAŞARI':>6} {'HATA':>6} {'%':>6}  {'BAR':<15}")
    print(f"   {'-'*65}")

    for skill, data in sorted(skills_data.items(), key=lambda x: -(x[1]["alpha"] + x[1]["beta"])):
        total = data["alpha"] + data["beta"]
        rate = data["alpha"] / total * 100 if total > 0 else 0
        bar_len = int(data["alpha"] / max(1, total) * 15)
        bar = "█" * bar_len + "░" * (15 - bar_len)
        print(f"   {skill:<30} {data['alpha']:>6} {data['beta']:>6} {rate:>5.0f}%  {bar}")


if __name__ == "__main__":
    entries = load_logs()
    if not entries:
        sys.exit(1)

    print(f"\n{'='*52}")
    print(f"  RL GÖRSELLEŞTİRME — {len(entries)} kayıt")
    print(f"{'='*52}")

    text_chart(entries)
    print()
    build_chart(entries)
