"""
RL Stress Test — Aşama 1.5 Uyumlu
Gece boyunca 100 sentetik senaryo üretip log dosyasını doldurur.
Amacı: MAB motoru için cold start problemini yenmek.
"""

import time
import random
import uuid

# V1.5 logger — doğru fonksiyon imzası
from rl_skill_logger import log_skill_decision

# Senaryo havuzu: (sorgu_metni, skill_listesi, beklenen_ödül, kategori, mod)
scenarios = [
    # --- Başarılı senaryolar (+1) ---
    {
        "query": "Python kod hatasını düzelt",
        "skills": ["code-exec"],
        "reward": 1,
        "category": "kod",
        "mode": "L99",
        "reply": "teşekkürler çalıştı"
    },
    {
        "query": "Bu makaleyi özetle",
        "skills": ["summarize"],
        "reward": 1,
        "category": "analiz",
        "mode": "COMPRESS",
        "reply": "harika özet"
    },
    {
        "query": "Bağlantı noktalarını tara",
        "skills": ["network-camera-discovery"],
        "reward": 1,
        "category": "guvenlik",
        "mode": "CLI",
        "reply": "çözüldü"
    },
    {
        "query": "Android APK逆向分析",
        "skills": ["android-apk-hardening"],
        "reward": 1,
        "category": "kod",
        "mode": "L99",
        "reply": "tamam oldu"
    },
    {
        "query": "Ekran görüntüsü al ve analiz et",
        "skills": ["screen-vision-analiz", "windows-screen-capture"],
        "reward": 1,
        "category": "goruntu",
        "mode": "FORENSIC",
        "reply": "mükemmel"
    },

    # --- Hatalı senaryolar (-1) ---
    {
        "query": "Tor üzerinden siteye gir",
        "skills": ["tor-browser-arama"],
        "reward": -1,
        "category": "arama",
        "mode": "CLI",
        "reply": "hayır bu site açılmadı"
    },
    {
        "query": "ADB ile cihaz bağla",
        "skills": ["adb-sdk-path-fix", "usb-driver-kontrol"],
        "reward": -1,
        "category": "guvenlik",
        "mode": "L99",
        "reply": "yanlış driver seçtin"
    },
    {
        "query": "Şifreyi kır",
        "skills": ["android-apk-hardening"],
        "reward": -1,
        "category": "kod",
        "mode": "L99",
        "reply": "yanlış metod"
    },
    {
        "query": "Kali VM'i başlat",
        "skills": ["kali-linux-remote"],
        "reward": -1,
        "category": "genel",
        "mode": "CLI",
        "reply": "hayır onu istemedim"
    },
    {
        "query": "YouTube videosunu indir",
        "skills": ["youtube-content"],
        "reward": -1,
        "category": "ogrenme",
        "mode": "CLI",
        "reply": "tekrar anlat"
    },

    # --- Nötr senaryolar (0) ---
    {
        "query": "Hava durumu nasıl?",
        "skills": ["none"],
        "reward": 0,
        "category": "genel",
        "mode": None,
        "reply": None
    },
    {
        "query": "Reinforcement learning nedir",
        "skills": ["none"],
        "reward": 0,
        "category": "ogrenme",
        "mode": "L99",
        "reply": "anladım"
    },
    {
        "query": "Notlarımda X'i ara",
        "skills": ["obsidian"],
        "reward": 0,
        "category": "analiz",
        "mode": None,
        "reply": None
    },
    {
        "query": "Cron job'ları listele",
        "skills": ["cronjob"],
        "reward": 0,
        "category": "genel",
        "mode": "CLI",
        "reply": "tamam"
    },
    {
        "query": "Diskte yer aç",
        "skills": ["windows-system-automation"],
        "reward": 0,
        "category": "genel",
        "mode": "CLI",
        "reply": None
    },
]


def run_stress_test():
    print("=== RL Stress Test v1.5 ===")
    print(f"Senaryo sayısı: {len(scenarios)}")
    print(f"Hedef: 100 kayıt ({len(scenarios)} senaryo × {100 // len(scenarios)} tekrar)")
    print("Başlıyor...\n")

    total = 0
    for batch in range(100 // len(scenarios)):
        for scenario in scenarios:
            # Her senaryoyu hafif varyasyonla tekrarla
            query = f"{scenario['query']} (batch {batch+1})"
            skills = scenario["skills"]

            # V1.5 logger çağrısı — doğru imza
            log_id = log_skill_decision(
                query=query,
                selected_skills=skills,
                rule_based=True,
                reward=scenario["reward"],
                category=scenario["category"],
                mode=scenario["mode"],
                user_reply=scenario["reply"]
            )

            total += 1
            if total % 20 == 0:
                print(f"  → {total} kayıt yazıldı...")

            time.sleep(0.05)  # 50ms bekle — sistemi yorma

    print(f"\n=== Stress Test Tamamlandı ===")
    print(f"Toplam kayıt: {total}")
    print("Log dosyası artık MAB motoru için zengin bir veri seti içeriyor.")


if __name__ == "__main__":
    run_stress_test()
